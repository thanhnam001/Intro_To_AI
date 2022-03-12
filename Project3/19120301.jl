using DelimitedFiles
using Random

# Chia tập dữ liệu thành X_train, y_train, X_test, y_test
function train_test_split(data,partition,rng)
    n = size(data,1)
    idx = shuffle(rng,1:n)
    train_idX = view(idx, 1:floor(Int, partition*n))
    test_idX = view(idx, (floor(Int,partition*n)+1):n)
    return data[train_idX,1:end-1], data[train_idX,end], data[test_idX,1:end-1],data[test_idX,end]
end

# Kiểm tra xem dữ liệu có cùng 1 loại hay không
function checkPurity(data)
    label = data[:,end]
    return length(unique(label)) == 1
end

# Chọn ra mode của tập dữ liệu
function classify(data)
    label = data[:,end]
    # Tạo ra dict (value => count)
    uniqueCount = Dict((i,count(==(i),label)) for i in unique(label))
    # Trả về value có count lớn nhất
    return collect(keys(uniqueCount))[argmax(collect(values(uniqueCount)))]
end

# Chọn ra các split value của từng cột
function GetPotentialSplits(data)
    potentialSplits = Dict()
    nCol = size(data,2)
    for i=1:nCol-1
        values = data[:,i]
        uniqueVal = sort(unique(values)) # split là các giá trị unique sắp xếp tăng dần
        potentialSplits[i] = uniqueVal
    end
    return potentialSplits
end

# Chia dữ liệu với cột và giá trị split cho trước
function splitData(data, splitCol, splitVal)
    splitColVal = data[:, splitCol]
    dataBelow = data[splitColVal .<= splitVal,:] # Phần dữ liệu <=split
    dataAbove = data[splitColVal .>  splitVal,:] # Phần dữ liệu >split
    return dataBelow, dataAbove
end

# Tính entropy
function Entropy(data)
    c = Dict((i, count(==(i), data)) for i in unique(data))
    entropy = 0
    for k in keys(c)
        p = c[k]/sum(values(c))
        entropy += -p*log2(p)
    end
    return entropy
end

# Tính entropy overall
function AvgEntropy(dataBelow, dataAbove)
    n = size(dataAbove,1)+ size(dataBelow,1)
    pDataBelow = size(dataBelow,1)/n
    pDataAbove = size(dataAbove,1)/n
    return pDataBelow*Entropy(dataBelow[:,end]) + pDataAbove*Entropy(dataAbove[:,end])
end

# Tìm cột tối ưu nhất để chia và giá trị chia
function determineBestSplit(data, potentialSplits)
    bestSplitCol = -1
    bestSplitVal = -1
    minEntropy = 10
    # Với mỗi cột, chọn một giá trị trong cột làm split 
    # và chia thành 2 phần rồi tính entropy overall
    for col in keys(potentialSplits)
        for value in potentialSplits[col]
            dataBelow, dataAbove = splitData(data, col, value)
            curEntropy = AvgEntropy(dataBelow,dataAbove)
            # Lưu lại cột có overall entropy nhỏ nhất và giá trị split
            if curEntropy <= minEntropy
                minEntropy = curEntropy
                bestSplitCol = col
                bestSplitVal = value
            end
        end 
    end 
    return bestSplitCol, bestSplitVal
end

# Xây dựng cây quyết định
function DecisionTree(data,labels,parent=nothing)
    if size(data,2)==1 # Nếu không còn thuộc tính để chia
        return parent
    elseif checkPurity(data) # Nếu phân loại trong cột là đồng nhất
        return classify(data)
    else
        parent = classify(data) # Tìm mode của thuộc tính phân loại
        potentialSplits = GetPotentialSplits(data) # Tìm các split cho từng cột
        splitCol, splitVal = determineBestSplit(data,potentialSplits) # Tìm cột split tốt nhất và giá trị split
        lower, higher = splitData(data, splitCol, splitVal) # Chia dữ liệu thành hai phần
        attr = (labels[splitCol], splitVal) # Xác định thuộc tính được dùng để chia và giá trị split
        subtree = Dict(attr=>Dict())

        remainingCol = [i for i=1:length(labels) if i!=splitCol] # Xác định các cột còn lại
        labels = [labels[i] for i=1:length(labels) if i!=splitCol] # Xác định thuộc tính còn lại
        higherPart = DecisionTree(higher[:,remainingCol],labels,parent) # Xác định subtree cho dữ liệu >split
        lowerPart = DecisionTree(lower[:,remainingCol],labels,parent) # Xác định subtree cho dữ liệu <=split
        # Nếu kết quả của phần dữ liệu lớn hơn và nhỏ hơn là như nhau thì ta chỉ cần trả về một
        if higherPart == lowerPart
            return higherPart
        end
        # Xác định hai nhánh của cây
        subtree[attr][">"] = higherPart
        subtree[attr]["<="] = lowerPart
        return subtree
    end
end
# Hàm in cây
function prettyPrint(d::Dict, pre=1)
    for (k,v) in d
        if typeof(v) <: Dict
            s = "$(repr(k)) => "
            println(join(fill(" ", pre)) * s)
            prettyPrint(v, pre+1+length(s))
        else
            println(join(fill(" ", pre)) * "$(repr(k)) => $(repr(v))")
        end
    end
    nothing
end
# Hàm dự đoán đối với 1 sample
function MakePredict(x,tree,labels)
    result = tree
    while true
        if !isa(result,Dict)
            return result
        end
        k = collect(keys(result))
        if x[findfirst(==(k[1][1]),labels)]>k[1][2]
            result = result[k[1]][">"]
        else
            result = result[k[1]]["<="]
        end
    end
end
# Hàm dự đoán cho tập dữ liệu
function Predict(data,tree,labels)
    predictions = []
    for i = 1:size(data,1)
        push!(predictions,MakePredict(data[i,:],tree,labels))
    end
    return predictions
end
# Tính Accuracy
function Score(predictions, y_test)
    return sum(predictions .== y_test)/length(y_test)
end

function main()
    rng = MersenneTwister(1234)
    open(raw"iris.csv") do io
        read(io,3)
        df =readdlm(io,',',header=true)

        data = df[1]
        labels = df[2][:]
        X_train, y_train, X_test, y_test = train_test_split(data,2/3,rng) # Chia tập dữ liệu với tỉ lệ train = 2/3, test = 1/3

        data_train = hcat(X_train, y_train)
        tree = DecisionTree(data_train,labels)
        prettyPrint(tree)

        predictions = Predict(X_test,tree,labels)
        acc = Score(predictions,y_test)
        println("Accuracy ",acc)
    end
end

main()
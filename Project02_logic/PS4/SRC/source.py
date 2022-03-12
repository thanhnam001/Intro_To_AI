import copy
import os
import re
# Hàm dùng để đọc file
def readFile(filename):
    clause=list()
    with open(filename,'r') as filein:
        lines=filein.read().splitlines()
        cl=[ele.replace(' ','').split('OR') for ele in lines]
        clause.extend(cl[2:])
        clause.append(cl[0])
    return clause

# Hàm dùng để ghi kết quả vào file
def writeFile(filename,re,ans):
    with open(filename,'w') as fileout:
        for i in re:
            fileout.write(str(len(i))+'\n')
            for j in i:
                if j!=[]:
                    fileout.write(' OR '.join(sorted(j,key=lambda x:x.strip('-')))+'\n')
                else:
                    fileout.write('{}\n')
        fileout.write(ans)

# Hàm dùng để phủ định một literal
def Negative(i):
    if '-' in i:
        i=i[1:]
    else:
        i='-'+i
    return i

# Hàm dùng để xét phép hợp của hai tập hợp
def Union(sa,sb):
    for b in sb:
        check=True
        for a in sa:
            if(set(a)==set(b)):
                check=False
                break
        if(check):
            sa.append(b)

# Hàm dùng để xét xem một tập hợp có là tập hợp con 
# của tập còn lại hay không
def subset(sa,sb):
    for a in sa:
        check=False
        for b in sb:
            if set(a)==set(b):
                check=True
                break
        if not check:
            return False
    return True

# Hàm hợp giải logic 2 mệnh đề
def PL_Resolve(Ci,Cj):
    ci=copy.deepcopy(Ci)
    cj=copy.deepcopy(Cj)
    count=0
    if len(cj)>len(ci):
        ci,cj=cj,ci
    # Duyệt qua các literal trong ci
    for i in ci:
        # Nếu phủ định của literal i có trong cj
        # thì loại bỏ phủ định của literal i trong cj
        # Nếu literal i không nằm trong cj thì thêm vào cj
        if Negative(i) in cj:
            cj.remove(Negative(i))
            count+=1
        elif i not in cj:
            cj.append(i)
    # Nếu chỉ có 1 literal i bị lược bỏ trong cj thì trả về cj
    # nếu nhiều hơn hoặc không có thì trả về True
    if count==1:
        return sorted(cj,key=lambda x:x.strip('-')) 
    return True

# Hàm hợp giải knowledge base với mệnh đề alpha
def PL_Resolution(KB,alpha):
    # Hàm nhận vào tham số knowledge base và mệnh đề phủ định của alpha
    # Thêm mệnh đề phủ định vào KB 
    for a in alpha:
        KB.append([a])
    clause=KB
    
    new=[] #  Tất cả mệnh đề đã phát sinh
    re=[] # Mệnh đề phát sinh ở mỗi vòng lặp của tất cả vòng lặp
    # Thực hiện vòng lặp
    while(True):
        resolvents=[] # Mảng mệnh đề phát sinh trong mỗi vòng lặp
        # Với mỗi cặp mệnh đề trong clause, ta thực hiện hợp giải
        for i in range(len(clause)):
            for j in range(i+1,len(clause)):
                # Hợp giải 2 mệnh đề
                temp=PL_Resolve(clause[i],clause[j])
                # Nếu kết quả trả về là True 
                # (mệnh đề đúng hoặc mệnh đề vô ích) thì tiếp tục vòng lặp
                if temp==True:
                    continue
                # Nếu kết quả trả về chưa có trong clause hoặc
                # chưa có trong resolvents thì thêm temp vào resolvents
                if (not subset([temp],clause)) and (not subset([temp],resolvents)):
                    resolvents.append(temp)
                # Thêm resolvents vào mảng tất cả mệnh đề đã phát sinh
                Union(new,resolvents)
        # Thêm resolvents vào mảng các mệnh đề phát sinh của các vòng lặp
        re.append(resolvents)
        # Nếu trong reoslvents có mệnh đề rỗng thì trả về re và True
        for i in resolvents:
            if set()==set(i):
                return re,True
        # Nếu mảng mệnh đề phát sinh là con của clause thì trả về re và False
        if subset(new,clause):
            return re,False
        # Hợp new vào clause
        Union(clause,new)

# Hàm main
def main():
    for filename in os.listdir('./input'):
        filenum=re.search(r'input(\d+).txt',filename).group(1)
        # Đọc vào các mệnh đề ở dạng mảng 2 chiều với mỗi mảng con
        # là một mệnh đề
        clause=readFile(os.path.join('./input',filename))
        # Phủ định mệnh đề alpha
        last=[]
        for j in clause[-1]:
            last.append(Negative(j))
        clause.pop()

        # Hợp giải
        track,answ=PL_Resolution(clause,last)
        # Kết luận và ghi vào file
        if(answ):
            ans='YES'
        else:
            ans='NO'
        writeFile(f'output/output{filenum}.txt',track,ans)
    return

if __name__=="__main__":
    main()
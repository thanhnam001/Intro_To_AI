import os
import matplotlib.pyplot as plt
from heapq import heappop
from heapq import heappush

def visualize_maze(matrix, bonus, start, end, route=None):
    """
    Args:
      1. matrix: The matrix read from the input file,
      2. bonus: The array of bonus points,
      3. start, end: The starting and ending points,
      4. route: The route from the starting point to the ending one, defined by an array of (x, y), e.g. route = [(1, 2), (1, 3), (1, 4)]
    """
    #1. Define walls and array of direction based on the route
    walls=[(i,j) for i in range(len(matrix)) for j in range(len(matrix[0])) if matrix[i][j]=='x']

    if route:
        direction=[]
        for i in range(1,len(route)):
            if route[i][0]-route[i-1][0]>0:
                direction.append('v') #^
            elif route[i][0]-route[i-1][0]<0:
                direction.append('^') #v        
            elif route[i][1]-route[i-1][1]>0:
                direction.append('>')
            else:
                direction.append('<')

        direction.pop(0)

    #2. Drawing the map
    ax=plt.figure(dpi=100).add_subplot(111)

    for i in ['top','bottom','right','left']:
        ax.spines[i].set_visible(False)

    plt.scatter([i[1] for i in walls],[-i[0] for i in walls],
                marker='X',s=100,color='black')
    
    plt.scatter([i[1] for i in bonus],[-i[0] for i in bonus],
                marker='P',s=100,color='green')

    plt.scatter(start[1],-start[0],marker='*',
                s=100,color='gold')

    if route:
        for i in range(len(route)-2):
            plt.scatter(route[i+1][1],-route[i+1][0],
                        marker=direction[i],color='silver')

    plt.text(end[1],-end[0],'EXIT',color='red',
        horizontalalignment='center',
        verticalalignment='center')
    plt.xticks([])
    plt.yticks([])
    plt.show()

    print(f'Starting point (x, y) = {start[0], start[1]}')
    print(f'Ending point (x, y) = {end[0], end[1]}')
    
    for _, point in enumerate(bonus):
        print(f'Bonus point at position (x, y) = {point[0], point[1]} with point {point[2]}')

def read_file(file_name: str = 'maze.txt'):
    f=open(file_name,'r')
    n_bonus_points = int(next(f)[:-1])
    bonus_points = []
    for i in range(n_bonus_points):
        x, y, reward = map(int, next(f)[:-1].split(' '))
        bonus_points.append((x, y, reward))

    text=f.read()
    matrix=[list(i) for i in text.splitlines()]
    f.close()

    return bonus_points, matrix

# Tìm kiếm mù
def dfs(graph, start, end):
    tracking={start:(0,0)}
    stack=[start]
    path=[]
    while len(stack):   # Còn phần tử trong stack
        current=stack.pop()     # Lấy phần tử cuối stack
        if current==end:    # Đã đến đích thì break
            break
        for neighbor in graph[current]:     # Xét 4 vị trí liền kề vị trí đang xét current
            if neighbor not in tracking:    # Nếu vị trí neighbor chưa được xét trước đó
                tracking[neighbor]=current  # Đánh dấu vị trí cha đi đến neighbor là current
                stack.append(neighbor)      # Thêm vị trí neighbor vào stack
    
    # Backtracking
    temp=end
    while temp!=(0,0):
        path.insert(0,tracking[temp])
        temp=tracking[temp]
    path.append(end)
    return path[1:]

def bfs(graph, start, end):
    queue=[]
    tracking={start:(0,0)}
    path=[]
    current=start
    while current!=end:     # Tìm khi vẫn chưa đến đích
        for neighbor in graph[current]:     # Xét 4 vị trí liền kề vị trí đang xét current
            if neighbor not in tracking:    # Nếu vị trí neighbor chưa được xét trước đó
                queue.append(neighbor)      # Thêm vị trí neighbor vào queue
                tracking[neighbor]=current  # Đánh dấu vị trí cha đi đến neighbor là current
        current=queue.pop(0)        # Lấy phần tử đầu queue
    
    # Backtracking
    temp=end
    while temp!=(0,0):
        path.insert(0,tracking[temp])
        temp=tracking[temp]
    path.append(end)
    return path[1:]

# Tìm kiếm có thông tin

# Hàm Heuristic - khoảng cách Manhattan: |end.X - pos.X| + |end.Y - pos.Y|
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# GBFS
def GBFS(graph, start, end):
    heap = []       # Priority Queue lưu các biên, phần tử có dạng (h,(x,y)) -> h = heuristic của (x,y)
    parent = {start:(0,0)}    # Dict để truy vết: (x,y):(a,b) -> Nút cha đi tới (x,y) là (a,b)
    current = start
    while current!=end:         # Khi chưa đến đích
        for neighbor in graph[current]:     # Xét 4 vị trí liền kề vị trí đang xét current
            if neighbor not in parent:      # Nếu vị trí neighbor chưa được xét (chưa có nút nào đi tới)
                heappush(heap, (heuristic(neighbor, end),neighbor))      # Thêm neighbor vào heap
                parent[neighbor] = current      # Đánh dấu cha của neighbor là current
        current = heappop(heap)[1]     # Lấy phần tử đầu heap

    # Backtracking
    path = []
    track = end
    while track!=(0,0):
        path.insert(0, track)
        track = parent[track]
    return path

# A*    F(n) = G(n) + H(n)      -> G(n) = bước đi từ start đến n
def A_star(graph, start, end):
    heap = []       # Priority Queue lưu các biên, phần tử có dạng (f,(x,y)) -> f = g+h
    # Dict lưu thông tin của (x,y):[g,h,(a,b)] -> thông tin g, h và nút cha (a,b) của (x,y)
    info = {start:[0,heuristic(start, end),(0,0)]}
    current = start

    while current!=end:         # Khi chưa đến đích
        for neighbor in graph[current]:     # Xét 4 vị trí liền kề vị trí đang xét current
            if neighbor not in info:      # Nếu vị trí neighbor chưa được xét (chưa có thông tin)
                info[neighbor] = [info[current][0]+1, heuristic(neighbor, end), current] # Thêm thông tin neighbor
                heappush(heap, (info[neighbor][0] + info[neighbor][1],neighbor))      # Thêm neighbor vào heap
            # Nếu neighbor đã được xét, cần kiểm tra lại g để tối ưu đường đi
            elif info[neighbor][0] > info[current][0] + 1:
                info[neighbor][0] = info[current][0] + 1    # Cập nhật lại g
                info[neighbor][2] = current                 # Cập nhật lại cha
        current = heappop(heap)[1]     # Lấy phần tử đầu heap

    # Backtracking
    path = []
    track = end
    while track!=(0,0):
        path.insert(0, track)
        track = info[track][2]
    return path

# Bonus Map
"""Hàm tìm đường đi ngắn nhất có thể từ begin đến end, với past_point là đường đi từ start -> begin.
Hàm dựa trên thuật toán A*, đường đi chỉ là ngắn nhất trong phạm vi mở biên của A*,
nên nếu có điểm thưởng tạo ra đường đi ngắn hơn nhưng ở cách xa thì coi như bỏ qua"""
def find_path(graph, begin, end, past_point, bonus_points):
    heap = [(0, begin)]
    # (x,y):[g,h,b,(u,v)] -> [0]: số bước đi từ begin đến là g, [1]: heuristic khoảng cách (x,y) đến end là h
    # [2]: giá trị điểm thưởng tại (x,y), [3]: (u,v) là nút cha đi đến (x,y)
    info = {begin:[0,heuristic(begin, end),0,(0,0)]}
    way_out = False     # Biến cho biết có đường đi từ begin đến end hay không

    while (len(heap)):      # Vẫn còn biên chưa mở
        current = heappop(heap)[1]      # Mở biên có f = g + h + b là nhỏ nhất, current =  vị trí (x,y) tại đó
        
        if current==end:
            way_out = True      # Tìm được đến end -> có đường đi
            break               # Dừng vòng lặp

        # Tương tự thuật toán A*
        for neighbor in graph[current]:
            if neighbor not in info:
                g = info[current][0] + 1
                h = heuristic(neighbor, end)
                b = 0       # Mặc định các vị trí đều có điểm thưởng b = 0
                if neighbor not in past_point:      # Nếu đó là vị trí điểm thưởng
                    for pts in bonus_points:        # và chưa được ăn (không có trong đoạn đường start->begin đã đi qua)
                        if pts[0]==neighbor[0] and pts[1]==neighbor[1]:
                            b = pts[2]              # b = giá trị điểm thưởng lấy từ list bonus_points
                            break
                info[neighbor] = [g, h, b, current]
                heappush(heap,(g+h+b, neighbor))
            elif info[neighbor][0] > info[current][0] + 1:
                info[neighbor][0] = info[current][0] + 1
                info[neighbor][3] = current

    path = []
    cost = 0
    track = end
    # Nếu có đường đi thì backtracking tìm path và cost
    if way_out:
        while track!=(0,0):
            path.insert(0, track)
            cost += 1 + info[track][2]
            track = info[track][3]
        cost -= 1       # Dư 1 bước do đã ở sẵn vị trí begin chứ không phải bước đến từ (0,0)
    return [way_out, cost, path]

# Tìm đường đi từ start -> end mà tốn ít chi phí nhất trên bản đồ mê cung có điểm thưởng
def solve_bonus_map(graph, start, end, rows, cols, bonus_points):
    queue = [start]
    # short_matrix là dictionary lưu các key là start, end và các bonus point
    # value gồm [0]: chi phí đi từ start đến key, [1]: đường đi đến key
    short_matrix = {(x[0],x[1]):[rows*cols, []] for x in bonus_points}
    short_matrix[start] = [0, [start]]
    short_matrix[end] = [rows*cols, []]

    while len(queue):
        current = queue.pop(0)
        for point in short_matrix:
            # Chỉ xét các điểm không nằm trong đoạn đường start->current đã đi qua
            if point not in short_matrix[current][1]:
                wayout = find_path(graph,current, point, short_matrix[current][1],bonus_points)
                
                if not wayout[0]:       # Nếu không tìm được đường đi current->point thì bỏ qua
                    continue

                # Nếu đường đi cũ lớn hơn đường đi mới thông qua current thì update đường đi nhỏ hơn
                # (start -> point) > (start -> current -> point)
                if short_matrix[point][0] >= short_matrix[current][0] + wayout[1]:
                    short_matrix[point][0] = short_matrix[current][0] + wayout[1]
                    short_matrix[point][1] = short_matrix[current][1] + wayout[2][1:]
                    # Vì point vừa được update nên thêm vào queue để xét đường đi mới đến các điểm khác
                    if point!=end and point not in queue:
                        queue.append(point)
    return short_matrix[end]

def main():
    print("Nhap 1 de chon map khong co diem thuong")
    print("Nhap 2 de chon map co diem thuong")
    mapType=int(input("Nhap loai map: "))
    if mapType==1:
        mapId=int(input("Nhap map muon kiem tra (1-6): "))
        bonus_points, matrix = read_file(f'./Maps/maze_map{mapId}.txt')
    elif mapType==2:
        print("1-Map co 2 diem thuong")
        print("2-Map co 3 diem thuong")
        print("3-Map co 4 diem thuong")
        print("4-Map co 5 diem thuong")
        print("5-Map co 10 diem thuong")
        mapId=int(input("Nhap map muon kiem tra (1-5): "))
        bonus_points, matrix = read_file(f'./Maps/bonus_map{mapId}.txt')
    else:
        return
    print(f'The height of the matrix: {len(matrix)}')
    print(f'The width of the matrix: {len(matrix[0])}')

    # Xác định 2 điểm đầu cuối
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j]=='S':
                start=(i,j)

            elif matrix[i][j]==' ':
                if (i==0) or (i==len(matrix)-1) or (j==0) or (j==len(matrix[0])-1):
                    end=(i,j)
                    
            else:
                pass

    # Graph lưu vị trí liền kề có thể đi tới được từ vị trí (i,j)
    rows=len(matrix)
    cols=len(matrix[0])
    graph={}
    for i in range(1,rows-1):
        for j in range(1,cols-1):
            if matrix[i][j]!='x':
                adj=[]
                for loc in [(i,j+1),(i,j-1),(i+1,j),(i-1,j)]:
                    if matrix[loc[0]][loc[1]]!='x':
                        adj.append(loc)
                graph[(i,j)]=adj
    if end[0]==0:
        graph[end] = [(end[0]+1,end[1])]
    elif end[0]==rows-1:
        graph[end] = [(end[0]-1,end[1])]
    elif end[1]==0:
        graph[end] = [(end[0],end[1]+1)]
    else:
        graph[end] = [(end[0],end[1]-1)]

    # Map bình thường
    if mapType==1:
        wayoutDFS=dfs(graph, start, end)
        visualize_maze(matrix,bonus_points,start,end,wayoutDFS)
        print(f'DFS: Cost = {len(wayoutDFS)-1}\n')

        wayoutBFS=bfs(graph, start, end)
        visualize_maze(matrix,bonus_points,start,end,wayoutBFS)
        print(f'BFS: Cost = {len(wayoutBFS)-1}\n')

        sol_GBFS = GBFS(graph, start, end)
        visualize_maze(matrix,bonus_points,start,end,sol_GBFS)
        print(f'GBFS: Cost = {len(sol_GBFS)-1}\n')

        sol_Astar = A_star(graph, start, end)
        visualize_maze(matrix,bonus_points,start,end,sol_Astar)
        print(f'A*: Cost = {len(sol_Astar)-1}')

    # Map có điểm thưởng
    if mapType==2:
        ans = solve_bonus_map(graph, start, end,rows,cols,bonus_points)
        visualize_maze(matrix,bonus_points,start,end,ans[1])
        print(f'Cost = {ans[0]}')

if __name__=="__main__":
    main()

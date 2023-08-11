# DBSCAN

import sys
# to avoid recrusion error when testing input1.txt
sys.setrecursionlimit(10**6)

input_data = []
clus_result = []
eps_n = []

# to check whether q is in p's epsilon neighbor
def is_eps_nb(p, q, eps):
    if ((float(p[1]) - float(q[1])) ** 2 + (float(p[2]) - float(q[2])) ** 2) <= eps * eps:
        return True
    return False

# check datapoint is core or not
def isCore(datapoint, minpts):
    return len(eps_n[int(datapoint[0])]) + 1 >= minpts

def density_reachable(p, cluster, minpts):
    # targets are data that is in p's epsilon-neighbor
    for q in eps_n[int(p[0])]:
        if visited[q] == False:
            visited[q] = True
            cluster.append(q)

            # if q is also core, there is possibility to expand cluster
            if isCore(input_data[q], minpts):
                density_reachable(input_data[q], cluster, minpts)

def dbscan(visited, minpts):
    # check every datapoints
    for p in input_data:
        # target is the datapoint that is never visited and 
        # also satisfy the minimum standard to be density reachable
        if visited[int(p[0])] == False and isCore(p, minpts):
            newC = []
            visited[int(p[0])] = True
            density_reachable(p, newC, minpts)
            clus_result.append(newC)

def write_output(input_num, num_out):
    for i in range(num_out):
        file_name = "input" + str(input_num) + "_cluster_" + str(i) + ".txt"

        with open(file_name, 'w') as f:
            for j in range(len(clus_result[i])):
                f.write(str(clus_result[i][j]) + "\n")

if __name__ == '__main__':
    # input arg order: txt, N, EPS, MinPts
    n = int(sys.argv[2])
    eps = float(sys.argv[3])
    minPts = int(sys.argv[4])

    with open(sys.argv[1], 'r') as f:
        lines = f.read().split('\n')
        for line in lines:
            arr = line.split('\t')
            input_data.append(arr)

    input_data = input_data[:-1]
    visited = [False for _ in range(len(input_data))]
    eps_n = [[] for _ in range(len(input_data))]

    # find epsilon neighbor for every datapoints
    for p in input_data:
        for q in input_data:
            if p == q:
                continue

            if is_eps_nb(p, q, eps):
                eps_n[int(p[0])].append(int(q[0]))

    dbscan(visited, minPts)

    input_case = sys.argv[1][5]
    
    # as there is limitation for number of clustering,
    # i need to sort by biggest clustering
    clus_result.sort(key=lambda c: len(c), reverse=True)

    write_output(input_case, n)

    # print("Clustering completed and output files generated.")
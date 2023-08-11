import sys
from itertools import combinations

trans = list()

# combinations 결과값 요소를 빼서 list로 바꿔주기 위한 함수
def tuple_to_list(tup):
    result = list()

    # 값을 하나씩 꺼내서 list로 붙이기
    for item in tup:
        result.append(set(item))
    
    return result

# fucntion for filtering by minimum support value
def min_sup_filter(cand):
    global trans
    cnt = min_sup * len(trans)

    # support가 min_sup 기준보다 크거나 같은 item만 뽑아내기
    freq_set = {key: cand[key] for key in cand.keys() if cand[key] >= cnt}
    
    # filter로 걸러진 애가 하나라도 있으면 ok
    if len(freq_set) >= 1:
        return freq_set
    
    else:
        exit()

# generate first frequent itemset
def first_freq_set():
    global trans

    itemset = dict()
    for tr in trans:
        for item in tr:
            # 없으면 dict에 넣고
            if item not in itemset.keys():
                itemset[item] = 1

            # 있으면 counting 해주기
            else:
                itemset[item] += 1
    
    return min_sup_filter(itemset)

def self_joining(pre_freq, leng):
    dup_items = list()

    # 2이면 바로 합쳐버리기
    if leng == 2:
        return tuple_to_list(list(combinations(pre_freq, leng)))

    else:
        # previous frequency itemset을 중복 없이 복제하고
        for set_item in pre_freq:
            for item in set_item:
                if item not in dup_items:
                    dup_items.append(item)
        
        # nCk 조합 만들기
        can_tup = list(combinations(dup_items, leng))
        result = tuple_to_list(can_tup)

        return result
    
def pruning(pre_freq, next_freq, leng):
    global trans
    freq_set = dict()

    if leng == 2:
        temp = list()

        for item in pre_freq:
            temp.append(list([item,]))
        
        pre_freq = temp
    
    else:
        pre_freq = tuple_to_list(pre_freq)

    for set_item in next_freq:
        cnt = 0

        for item in list(combinations(set_item, leng - 1)):
            if leng == 2:
                item = list(item)
            
            else:
                item = set(item)
            
            if item not in pre_freq:
                break
            cnt += 1

        if cnt == leng:
            freq_set[tuple(set_item)] = 0
        
    for key in freq_set.keys():
        for tr in trans:
            if set(key) <= set(tr):
                freq_set[key] += 1
        
    return min_sup_filter(freq_set)

def write_output(line):
    with open(sys.argv[3], 'a') as f:
        f.write(line)
        
def association_rule(freq_set, leng):
    for set_item, freq in freq_set.items():
        freq_len = leng

        while freq_len > 1:
            combi = list(combinations(set_item, freq_len - 1))

            for item in combi:
                item = set(item)

                # 차집합 이용하기
                counter = set(set_item) - set(item)

                support = freq / len(trans) * 100
                cnt = 0
                for tr in trans:
                    if set(tr) >= item:
                        cnt += 1
                
                confidence = freq / cnt * 100

                # str -> int, 채점 format 맞추기
                counter = set(map(int, counter))
                item = set(map(int, item))

                line = str(item) + '\t' + str(counter) + '\t' + str('%.2f' % round(support, 2)) + '\t' + str('%.2f' %round(confidence, 2) + '\n')
                write_output(line)
            
            freq_len -= 1

if __name__ == '__main__':

    # get arguments from cmd
    min_sup = float(sys.argv[1]) / 100
    out_f = sys.argv[3]

    # tranfer input data to array structure
    with open(sys.argv[2], 'r') as f:
        line = f.read().split('\n')
        for arr in line:
            arr = arr.split('\t')
            trans.append(arr)
    
    # list for frequent itemset
    freq_set = ['',]
    freq_set.append(first_freq_set())

    length = 2
    while True:
        # kth frequent list key 뽑기
        prev_freq_set = list(freq_set[length - 1].keys())
        # step 1. self-join
        next_freq_set = self_joining(prev_freq_set, length)
        
        # 더 이상 안만들어지면 while stop
        if len(next_freq_set) == 0:
            exit()
        
        # step 2. pruning
        next_freq_set = pruning(prev_freq_set, next_freq_set, length)

        # step 3. association rule 적용
        association_rule(next_freq_set, length)

        # 후보 없으면 while 끝
        if next_freq_set == -1:
            exit()
        
        # 있으면 freq_set에 붙여주고 k+1번째 진행
        else:
            freq_set.append(next_freq_set)
            length += 1
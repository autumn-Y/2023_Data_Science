import sys
import numpy as np
import pandas as pd
from pprint import pprint

train_set = []
test_set = []
data_attr = []
attr_value = {}
    
# calculate entropy
# : -sum(pi * log2pi)
# pi = ith class / entire
def entropy(target_attr):
    values, count = np.unique(target_attr, return_counts= True)

    entropy = -np.sum([(count[i] / np.sum(count)) * np.log2(count[i] / np.sum(count)) for i in range(len(values))])
    return entropy

# get gain ratio
def gainRatio(data, split_target_attr, class_attr):
    # Info(D)
    total_entropy = entropy(data[class_attr])
    
    # Info_a(D)
    values, count = np.unique(data[split_target_attr], return_counts= True)
    info_a = np.sum([(count[i] / np.sum(count)) * entropy(data.where(data[split_target_attr] == values[i]).dropna()[class_attr]) 
                     for i in range(len(values))])

    # SplitInfo_a(D)
    split_info = -np.sum([(count[i] / np.sum(count)) * np.log2((count[i] / np.sum(count))) for i in range(len(values))])

    # to avoid RuntimeWarning caused by division by zero
    if split_info == 0:
        gain_ratio = 0.0
        return gain_ratio

    # information gain, gain ratio
    info_gain = total_entropy - info_a
    gain_ratio = info_gain / split_info
    
    return gain_ratio
    

# tree generation: dictionary
def decision_tree(data, class_attr, original_data, attr, parent_class = None):
    # no data -> majority voting of all cases
    if len(data) == 0:
        return np.unique(original_data[class_attr])[np.argmax(np.unique(original_data[class_attr], return_counts = True)[1])]

    # all same class
    elif len(np.unique(data[class_attr])) <= 1:
        return np.unique(data[class_attr])[0]
    
    # no more feature
    elif len(attr) == 0:
        return parent_class
    
    # else: expand tree
    else:
        parent_class = np.unique(data[class_attr])[np.argmax(np.unique(data[class_attr], return_counts = True)[1])]

        # best feature selection
        gain_value = [gainRatio(data, f, class_attr) for f in attr]
        best_feature = attr[np.argmax(gain_value)]

        # make tree as dictionary format
        tree = {best_feature:{}}

        # remove used feature
        attr = [i for i in attr if i != best_feature]

        # generate branch using best feature
        # make path for every values even there is no exactly same case in the train dataset
        for value in attr_value[best_feature]:
            sub_data = data.where(data[best_feature] == value).dropna()

            # execute decistion tree after divide by best feature
            subtree = decision_tree(sub_data, class_attr, data, attr, parent_class)
            tree[best_feature][value] = subtree

        return(tree)

# 전체 data만큼 for문 돌리고, 그 안에 while 문으로 dict끝날 때까지 돌리면서 predict
def predict(test_data, dt):
    for i in range(test_data.shape[0]):
        temp_dt = dt

        while(True):
            key = list(temp_dt.keys())[0]
            temp_dt = temp_dt[key].get(test_data.iloc[i, data_attr.index(key)])

            # if data is classified, write on output file
            if type(temp_dt) == type(''):
                line = ''
                for k in range(len(data_attr) - 1):
                    line = line + test_data.iloc[i, k] + '\t'
                line = line + temp_dt + '\n'

                write_output(line)
                break

# write output
def write_output(line):
    with open(sys.argv[3], 'a') as f:
        f.write(line)    

# main funtion
if __name__ == '__main__':
    # get arguments from cmd: train set, test set, result    
    # tranfer train data to array structure
    with open(sys.argv[1], 'r') as f:
        line = f.read().split('\n')
        for arr in line:
            arr = arr.split('\t')
            if '' not in arr:
                train_set.append(arr)

    # tranfer test data to array structure 
    with open(sys.argv[2], 'r') as f:
        line = f.read().split('\n')
        for arr in line:
            arr = arr.split('\t')
            if '' not in arr:
                test_set.append(arr)

    data_attr = train_set[0]
    attr_len = len(data_attr)

    tr_df = pd.DataFrame(train_set, columns = data_attr)
    tr_df.drop(0, axis = 0, inplace= True)
    
    ts_df = pd.DataFrame(test_set, columns = data_attr[:attr_len - 1])
    ts_df.drop(0, axis = 0, inplace= True)

    # extract attributes and values
    j = 0
    for i in range(attr_len):
        attr_value[data_attr[j]] = tr_df[data_attr[j]].unique()
        j = j + 1

    tree = decision_tree(tr_df, data_attr[-1], tr_df, data_attr[:attr_len - 1])
    # pprint(tree)

    # write attributes(1st line) in output file
    f_line = ''
    for i in range(attr_len - 1):
        f_line = f_line + data_attr[i] + '\t'
    f_line = f_line + data_attr[-1] + '\n'

    with open(sys.argv[3], 'a') as f:
        f.write(f_line)

    predict(ts_df, tree)
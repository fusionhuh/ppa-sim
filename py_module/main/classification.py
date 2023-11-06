from .globals import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from .constants import *
from sklearn.cluster import KMeans
import statistics as stats
from .profile import *

def classify(features: str, temp_weight):
    if da.curr_results_profile == None:
        print("Please set a profile or simulate something before classification.")
        return

    curr_results_profile: Profile = da.data[da.curr_results_profile]
    working_adder_list = curr_results_profile.get_adder_list()
    working_description_list = curr_results_profile.get_adder_str_list()
    working_area_list = curr_results_profile.get_area_list()

    for i, adder in enumerate(working_adder_list):
        description: str = working_description_list[i]
        for j, area in enumerate(working_area_list):
            _classify_helper(features, adder, description, area, temp_weight)

def bool_classify(features: str):
    if da.curr_results_profile == None:
        print("Please set a profile or simulate something before classification.")
        return
    
    curr_results_profile: Profile = da.data[da.curr_results_profile]
    working_adder_list = curr_results_profile.get_adder_list()
    working_description_list = curr_results_profile.get_adder_str_list()
    working_area_list = curr_results_profile.get_area_list()

    for i, adder in enumerate(working_adder_list):
        description: str = working_description_list[i]
        for j, area in enumerate(working_area_list):
            _bool_classify_helper(features, adder, description, area)

def parse_feature_list(features: str) -> list: # returns list of (feature_func, feature_name)
    multi_bitwise_funcs = ["AND", "OR", "NAND", "NOR", "XOR", "BIT_HIGH", "ACROSS_DIFF", "BIT_HIGH"]
    multi_abstracted_funcs = ["BITS_OVERLAPPING", "NUM_BITS", "MAGNITUDE", "COMPLEX"]
    multi_funcs = multi_bitwise_funcs + multi_abstracted_funcs
    single_abstracted_funcs = ["IS_LARGE", "IS_MEDIUM", "IS_SMALL", "IS_TINY"]
    single_funcs = single_abstracted_funcs

    def parse_range_to_list(bit_range: str) -> list:
        if ":" not in bit_range:
            return int(bit_range)
        high, low = parse_range(bit_range)
        bit_list = [i for i in range(high, low-1,-1)]
        return bit_list

    def get_format_str(action: str, op_list: str) -> str:
        return f"test {action} {op_list}"

    def separate_description(description) -> tuple: # returns tuple of (group, action, format_str), group is tuple of (operands, selected_bits), action is (func_name, type)
        group, action = (None, None)
        action_type = None
        if "." in description:
            group, action = description.split(".")
            action = action.upper()
            if action[-1] == "!":
                action_type = "multi_abstracted" if action[0:-1] in multi_abstracted_funcs else "multi"
            elif action[-1] == "?":
                action_type = "single"
                assert "," not in group
            else:
                raise Exception(f"main.separate_description(): Invalid action qualifier '{action[-1]}' specified in feature list")
            action = action[:-1].upper()
        else:
            group = description
            assert "," not in group # high shouldn't operate on multiple operands
            action = "BIT_HIGH"

        if action in multi_abstracted_funcs or action in single_abstracted_funcs:
            assert "[" not in group
            op_list = group.split(",")
            return ((op_list, None), (action, action_type), get_format_str(action, op_list))


        op_list, bit_selection_str = group.split("[")
        bit_selection_str = bit_selection_str[:-1] # remove last ]
        op_list = op_list.split(",")
        selection_list = []
        if "," in bit_selection_str:
            selection_list = bit_selection_str.split(",")
        else:
            selection_list = [bit_selection_str]
        if ":" in bit_selection_str:
            selection_list = [parse_range_to_list(selection) for selection in selection_list]
        else:
            selection_list = [[i] for i in list(map(int, selection_list))]

        selected_bits = []
        for bit_list in selection_list: selected_bits+=bit_list
        return ((op_list, selected_bits), (action, action_type), get_format_str(action, group))

    def create_abstracted_feature_func(op_list, action):
        all_ones = 0xFFFFFFFFFFFFFFFF
        def feature_func(op1=0, op2=0,op3=0,op4=0):
            #def IS_LARGE(op) -> bool:
            #    return (not IS_MEDIUM(op)) and (not IS_SMALL(op)) and (not IS_TINY(op))

            def IS_LARGE(op) -> bool:
                return op >= 2**16
                

            def IS_MEDIUM(op) -> bool:
                in_range = op & 0x0000FFFFFFFFFFFF > 0
                out_range = op & 0xFFFF000000000000 != 0
                return in_range and not out_range
            
            #def IS_SMALL(op) -> bool:
            #    in_range = op & 0x00000000FFFFFFFF > 0
            #    out_range = op & 0xFFFFFFFF00000000 != 0
            #    return in_range and not out_range
            def IS_SMALL(op) -> bool:
                return op < 256

            def IS_TINY(op) -> bool:
                in_range = op & 0x000000000000FFFF > 0
                out_range = op & 0xFFFFFFFFFFFF0000 != 0
                return in_range and not out_range
            
            def BITS_OVERLAPPING(op1=all_ones,op2=all_ones,op3=all_ones,op4=all_ones):
                return (op1&op2&op3&op4).bit_count()

            def NUM_BITS(op) -> int:
                return op.bit_count()

            def COMPLEX(op1,op2,op3,op4):
                diff1 = op1^op3
                diff2 = op2^op4
                return (diff1&diff2).bit_count()

            def SOMETHING(op1=all_ones,op2=all_ones,op3=all_ones,op4=all_ones):
                return ((op1^op3)&(op2^op4)).bit_count()
            
            def MAGNITUDE(op) -> int:
                return op


            if len(op_list) > 1:
                keyworded_op_list = ",".join([f"{op}={op}" for op in op_list])
            else:
                keyworded_op_list = f"op={op_list[0]}"
            result = eval(f"{action}({keyworded_op_list})")
            return result
        return feature_func

    def create_bit_feature_func(op_list, action, bit):
        all_ones = 0xFFFFFFFFFFFFFFFF
        def feature_func(op1=0,op2=0,op3=0,op4=0):
            def AND(op1=1,op2=1,op3=1,op4=1):
                return op1&op2&op3&op4

            def OR(op1=0,op2=0,op3=0,op4=0):
                return op1|op2|op3|op4

            def XOR(op1=0,op2=0,op3=0,op4=0):
                return op1^op2^op3^op4

            def NAND(op1=1,op2=1,op3=1,op4=1):
                return ~(op1&op2&op3&op4)
            
            def NOR(op1=0,op2=0,op3=0,op4=0):
                return ~(op1|op2|op3|op4)
            
            def ACROSS_DIFF(op1=0,op2=0,op3=0,op4=0):
                return (op1^op3)&(op2^op4)

            def BIT_HIGH(op1=all_ones,op2=all_ones,op3=all_ones,op4=all_ones):
                return int(op1&op2&op3&op4 >= 1)

            mask = 2**bit
            op1 = 1 if (op1&mask) > 0 else 0
            op2 = 1 if (op2&mask) > 0 else 0
            op3 = 1 if (op3&mask) > 0 else 0
            op4 = 1 if (op4&mask) > 0 else 0
            keyworded_op_list = ",".join([f"{op}={op}" for op in op_list])
            result = eval(f"{action}({keyworded_op_list})")
            return result
        return feature_func

    def parse_feature_tup(feature_tup: tuple) -> tuple: # returns list of (feature_func, feature_name)
        op_info, action_info, format_str = feature_tup
        feature_func_list: list = []
        feature_name_list: list = []
        op_list, selected_bits = op_info
        action, action_type = action_info
        if action_type == None: # bit high
            format_str = f"BIT_HIGH({op_list[0]}[{{bit}}])"
            for bit in selected_bits:
                feature_name_list.append(format_str.format(bit=bit))
                #feature_func_list.append(lambda op)
        elif action_type == "multi_abstracted" or action_type == "single":
            name_str = f"{action}({op_list})"
            feature_func_list.append(create_abstracted_feature_func(op_list, action))
            feature_name_list.append(name_str)
        elif action_type == "multi":
            format_str = f"{action}({op_list}[{{bit}}])"
            for bit in selected_bits:
                feature_name_list.append(format_str.format(bit=bit))
                feature_func_list.append(create_bit_feature_func(op_list, action, int(bit)))
        else:
            raise Exception(f"main.parse_feature_tup(): Invalid action type {action_type} provided")
        return (feature_func_list, feature_name_list)

    #feature_list: list = []
    description_list = features.split("+")
    description_list = [description[1:-1] for description in description_list]
    feature_tup_list = [separate_description(description) for description in description_list]
    parsed_feature_list = [parse_feature_tup(feature_tup) for feature_tup in feature_tup_list]
    feature_func_list, feature_name_list = ([], [])
    for result in parsed_feature_list: 
        feature_func_list += result[0]
        feature_name_list += result[1]

    return (feature_func_list, feature_name_list)

def _bool_classify_helper(features: str, adder, description, area):
    profile: Profile = da.data[da.curr_results_profile]
    delays = profile.get_delays(description, area)

    (feature_func_list, feature_name_list) = parse_feature_list(features)
    operands = profile.get_operands()

    true_delays = []
    false_delays = []

    for i, op_vector in enumerate(operands):
        op1, op2, op3, op4 = list(map(int, [op_vector[0]["a"], op_vector[0]["b"], op_vector[1]["a"], op_vector[1]["b"]]))
        new_row = [func(op1,op2,op3,op4) for func in feature_func_list]
        if 0 not in new_row:
            true_delays.append(delays[i])
            print(f"TRUE: op1: {op1}, op2: {op2}, op3: {op3}, op4: {op4}, delay: {delays[i]}")
        else:
            false_delays.append(delays[i])
            print(f"FALSE: op1: {op1}, op2: {op2}, op3: {op3}, op4: {op4}, delay: {delays[i]}")

    def analyze_delay_group(delays, group_name):
        mean = stats.mean(delays)
        median = stats.median(delays)
        stdev = stats.stdev(delays)
        occurrences = len(delays)
        print(f"{group_name}:")
        print(f" Mean delay: {mean}")
        print(f" Median delay: {median}")
        print(f" Standard deviation: {stdev}")
        print(f" Number of occurrences: {occurrences}")

    analyze_delay_group(true_delays, "True matches")
    analyze_delay_group(false_delays, "False matches")


    

def parse_range(bit_range: str) -> tuple:
    high, low = list(map(int, bit_range.split(":")))
    assert high <= 63 and high >= 0
    assert low <= 63 and low >= 0
    if high <= low:
        print("main.parse_feature_list: Reversing high and low of specified range (should be like [high:low]) (Warning)")
        temp = high
        high = low
        low = temp
    return (high, low)

def _classify_helper(features: str, adder, description, area, temp_weight):

    single_op_funcs = ["is_large?", "is_medium?", "is_small?", "is_tiny?"]
    multi_op_funcs = ["bits_overlapping!", "and!", "xor!", "or!", "nor!", "nand!"]


    profile: Profile = da.data[da.curr_results_profile]
    delays = profile.get_delays()
    mat = np.zeros((len(delays), 2))
    mat[:,0] = delays
    #mat = np.matrix(np.reshape(np.array(delays), (-1,1)))
    #print(mat)

    df = pd.DataFrame(mat, columns=["Delays", "null"])
    decision = "no"
    cluster_centers, ids = None, None
    #while decision != "yes":
        #(cluster_centers, delay_ids) = _get_centers_and_ids(df)
        #print(f"Worst case delay: {profile['worst_delays'][description][area]}")
        #print(f"Best case delay: {profile['best_delays'][description][area]}")
        #print("Cluster centers:")
        #print(cluster_centers[:,0])
    #    decision = prompt("If the clusters are satisfactory, please enter 'yes'. If not, enter 'no' to compute the clusters with another elbow point.\n")
    


    # print cluster info


    #cluster_indices: list = eval(prompt("Please select the clusters you would like to analyze.\n"))    
    (feature_func_list, feature_name_list) = parse_feature_list(features)
    operands = profile.get_operands()

    mat = np.empty((len(operands), len(feature_name_list)))
    for i, op_vector in enumerate(operands):
        op1, op2, op3, op4 = list(map(int, [op_vector[0]["a"], op_vector[0]["b"], op_vector[1]["a"], op_vector[1]["b"]]))
        new_row = [func(op1,op2,op3,op4) for func in feature_func_list]

        mat[i]=np.array(new_row)
 
    delays = np.array(delays)
    mat = np.append(mat, delays[:,np.newaxis]*temp_weight, axis=1)
    feature_name_list += ["delay"]



    df = pd.DataFrame(mat, columns = feature_name_list)

    reduced_df = _apply_linear_projection(df) if len(feature_func_list) > 2 else df
    (reduced_centers, ids) = _get_centers_and_ids(reduced_df)

    global fig_num
    fig = plt.figure(fig_num)
    ax = plt.axes(projection='3d')
    #ax = fig.subplots()
    fig_num += 1

    print(reduced_df)

    for i in range(0, 500):
        #ax.scatter([reduced_df.iat[i, 0]], [reduced_df.iat[i, 1]], [reduced_df.iat[i, 2]], color=COLORS[ids[i]], s=25)
        ax.scatter(reduced_df.iat[i,0], reduced_df.iat[i,1], delays[i], color=COLORS[ids[i]], s=25)
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")
    ax.set_zlabel("Delay")
    ax.set_title(f"Plot of cluster points with delay weight = {temp_weight}")

def _apply_linear_projection(df: pd.DataFrame):
    rand_dim = (df.shape[1], 2)
    rand_mat = np.random.uniform(-1,1, rand_dim)
    return pd.DataFrame(np.matmul(df.to_numpy(), rand_mat), columns=["X", "Y"])

def _get_centers_and_ids(df: pd.DataFrame):
    inertias = []
    for i in range(1, 11):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kmeans = KMeans(n_clusters=i)
            kmeans.fit(df[df.columns])
            inertias.append(kmeans.inertia_)

    for i, intertia in enumerate(inertias):
        print(f"{i+1} Clusters:")
        print(f" {intertia}")
    
    elbow_point = int(input("Please select the elbow point based on the listed data.\n"))
    kmeans, y = None, None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kmeans = KMeans(n_clusters=elbow_point)
        kmeans.fit(df[df.columns])
        y = kmeans.fit_predict(df[df.columns])
    return (kmeans.cluster_centers_, y)  

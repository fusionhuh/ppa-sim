from .helpers import _get_minimum_scale_factors
from .globals import *
from .constants import *
from random import randint
from .environment import *
import os
import numpy as np
import statistics
import matplotlib.pyplot as plt
from py_module.main.profile import Profile

# TEMPORARY
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import matplotlib.ticker as ticker

def _read_cases_from_file(filename: str):
    text = open(filename).read()
    lines = text.split("\n")
    cases: list = [None]*len(lines)
    for i, line in enumerate(lines):
        ops = line.split(" ")
        if len(ops) != 3:
            raise Exception("Formatting error with supplied operands")
        a, b, cin = list(map(_base_independent_str_to_int, ops))
        if cin not in [0,1]:
            raise Exception("Invalid cin value")
        cases[i] = {"a":a, "b":b, "cin":cin}
    return cases

def _base_independent_str_to_int(num: str) -> int:
    if not num.isnumeric(): return int(num, base=16)
    else: return int(num)

def simulate(mode, results_profile, **kwargs):
    if len(da.adder_list) == 0:
        print("Please add an adder to proceed with simulation.")
        return
    if len(da.area_list) == 0:
        print("Please set the area list to proceed with simulation.")
        return
    if results_profile in da.results_profiles:
        print("Please specify a different results profile.")
        return
    if da.curr_program == None:
        print("Please set a program before simulating.")
    if mode not in SIMULATE_MODES:
        print(f"Specified mode not in supported modes: {SIMULATE_MODES}")
        return
    results = dict()

    cases: list = []
    skip_mode = False
    if mode == "random":
        cases = _generate_random_cases(64, SIM_MAX_CASES) # change width later
    elif mode == "program":
        print(f"Running '{da.curr_program}'...")
        if (os.system(f"pin -t simulation/pintool/obj-intel64/MyPinTool.so -- {da.curr_program}") != 0):
            raise Exception("simulation.py: Something went wrong while extracting operand data from program")
        os.system(f"rm {PIN_OPERANDS_PATH}")
        os.system(f"mv {PIN_OPERANDS_FILENAME} {PIN_OPERANDS_PATH}")

        os.system(f"rm {PIN_CONTEXT_PATH}")
        os.system(f"mv {PIN_CONTEXT_FILENAME} {PIN_CONTEXT_PATH}")
        exp_sub: bool = False
        if "exp_sub" in kwargs.keys():
            exp_sub = kwargs["exp_sub"]

        cases = _convert_pin_output_to_cases(exp_sub=exp_sub)[da.ins_category]
        if len(cases) > 1.5*SIM_MAX_CASES:
            cases = _perform_random_sampling(cases)
    elif mode == "custom":
        if "source" not in kwargs.keys():
            print("Source for custom cases needs to be specified using 'source={filename,input}'")
        if kwargs["source"] == "input":
            skip_mode = False
            in_line = ""
            while True:
                in_line = input("Please input a set of operands: ")
                if in_line == "END":
                    break
                ops = in_line.split(" ")
                if len(ops) != 3:
                    print("Formatting error with supplied operands")
                    continue
                a, b, cin = list(map(_base_independent_str_to_int, ops))
                if cin not in [0,1]:
                    print("Invalid cin value")
                cases.append({"a":a, "b":b, "cin":cin})
        else:
            cases = _read_cases_from_file(kwargs["source"])

    start = 1 if skip_mode == True else 0
    stride = 2 if skip_mode == True else 1
    operands: list = [(cases[i-1],cases[i]) for i in range(start,len(cases),stride)]
    context: list = _convert_pin_output_to_context()
    context = [(context[i-1],context[i]) for i in range(start, len(cases), stride)]
    results = Profile(mode, cases, operands, context, da.adder_list, da.adder_str_list, da.area_list)


    scale_factors = _get_minimum_scale_factors(da.adder_list) if da.match else [1]*len(da.adder_list)
    for i, a in enumerate(da.adder_list):
        area_list = [round(area*scale_factors[i],3) for area in da.area_list]
        #if not a.is_optimized(area_list): a.optimize(area_list)
        delays = a.simulate(area_list, cases, clear=False, target="individual", skip_accidentals=skip_mode)

        sta_worst_delays = a.get_worst_case_delays(area_list)
        description = da.adder_str_list[i]

        for j, delay_list in enumerate(delays):
            results.add_delay_list(delay_list, description, area_list[j])
            results.add_worst_case_delay(sta_worst_delays[j], description, area_list[i])

    da.results_profiles.append(results_profile)
    da.data[results_profile] = results
    set_profile(results_profile)

def parametrize_ops(case1_def, case2_def) -> list:
    if len(da.adder_list) == 0:
        print("Please add an adder before proceeding with this action.")
        return

    if len(da.adder_list) > 1:
        print("Warning: Adder list contains more than one adder. This operation will only use the first but will still perform area matching.")

    if len(da.area_list != [1]):
        print("Warning: This operation currently only supports simulating one area at a time with minimum area or matching area.")

    var_indices = []
    func_indices = []
    funcs = {}
    names = []

    curr_def = -1
    def expand_op_def(op_def):
        nonlocal curr_def
        curr_def += 1

        if callable(op_def):
            func_indices.append(curr_def)
            funcs[curr_def] = op_def
            return [-1]

        if not isinstance(op_def, tuple):
            return [_base_independent_str_to_int(op_def)]
        start, end = _base_independent_str_to_int(op_def[0]), _base_independent_str_to_int(op_def[1])

        var_indices.append(curr_def)

        iter_info = op_def[2]
        names.append(op_def[3])
        method, extent = iter_info.split(".")
        extent = int(extent)
        assert extent > 0

        grow_funcs = ["lsl", "incr"]
        shrink_funcs = ["lsr", "decr"]
        def lsr(op: int, shifts: int) -> int:
            return op >> shifts

        def lsl(op: int, shifts: int) -> int:
            return op << shifts

        def incr(op: int, val: int) -> int:
            return op + val

        def decr(op: int, val: int) -> int:
            return op - val

        op_list: list = []
        if method in grow_funcs:
            assert start < end
            curr = start
            while curr < end:
                print(curr)
                op_list.append(curr)
                curr = eval(f"{method}({curr}, {extent})")
        elif method in shrink_funcs:
            assert start > end
            curr = start
            while curr > end:
                print(curr)
                op_list.append(curr)
                curr = eval(f"{method}({curr}, {extent})")
        else:
            raise Exception("Method not in supported functions")
        
        return op_list


    op1_def, op2_def, cin1_def = case1_def
    op3_def, op4_def, cin2_def = case2_def

    op_def_list = [expand_op_def(op_def) for op_def in [op1_def,op2_def,op3_def,op4_def]]
    #var_indices = [i for i in range(0, len(op_def_list)) if len(op_def_list[i]) > 1]
    max_vals = list(map(lambda x: len(x)-1, op_def_list))
    assert -1 not in max_vals
    assert len(var_indices) < 3
    assert len(var_indices) > 0 

    operands = []
    cases = []
    # operates only using indices, don't need to worry about negative operand values!
    def loop_helper(indices, pos, cases):
        if pos == len(indices):
            for index, func in funcs.items():
                #print(func)
                op_def_list[index][indices[index]] = func()

            vec1 = {"a":op_def_list[0][indices[0]], "b":op_def_list[1][indices[1]], "cin":0} # assume cin=0 for now
            vec2 = {"a":op_def_list[2][indices[2]], "b":op_def_list[3][indices[3]], "cin":0}




            nonlocal operands
            operands += [[op_def_list[i][indices[i]] for i in range(0, len(indices))]]
            cases+=[vec1,vec2]
            return
        old_indices = list(indices)
        loop_helper(indices, pos+1, cases)

        while indices[pos] > 0:
            indices[pos]-=1
            for i in range(pos+1,4): indices[i] = old_indices[i]
            loop_helper(indices, pos+1, cases)

    loop_helper(max_vals, 0, cases)

    operands = np.matrix(operands)

    scale_factors = _get_minimum_scale_factors(da.adder_list) if da.match else [1]*len(da.adder_list)

    adder = da.adder_list[0]
    delays = np.array(adder.simulate([1*scale_factors[0]], cases, clear=False, target="individual", skip_accidentals=True)[0])

    x,y = [operands[:,index].transpose().tolist()[0] for index in var_indices]
    x = np.array(x)
    y = np.array(y)

    z = delays

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = fig.add_subplot()

    cntr = ax.tricontourf(x,y,z, cmap="viridis")
    fig.colorbar(cntr,ax=ax)
    #xlabels = list(map(lambda t: "0x%08X" % int(2**t), ax.get_xticks()))
    #ylabels = list(map(lambda t: "0x%08X" % int(2**t), ax.get_yticks()))

    #ax.set_xticklabels(xlabels)
    #ax.set_yticklabels(ylabels)
    ax.set_xlabel(names[0])
    ax.set_ylabel(names[1])
    plt.show()


def quicksim(op1,op2,op3,op4, cin1=0,cin2=0):
    if len(da.adder_list) == 0:
        print("Please add an adder to proceed with simulation.")
        return
    if len(da.area_list) == 0:
        print("Please set the area list to proceed with simulation.")
        return
    scale_factors = _get_minimum_scale_factors(da.adder_list) if da.match else [1]*len(da.adder_list)
    cases = [{"a":op1,"b":op2, "cin":cin1}, {"a":op3, "b":op4, "cin":cin2}]
    for i, a in enumerate(da.adder_list):
        area_list = [round(area*scale_factors[i],3) for area in da.area_list]
        #if not a.is_optimized(area_list): a.optimize(area_list)
        delays = a.simulate(area_list, cases, clear=False, target="individual")

        sta_worst_delays = a.get_worst_case_delays(area_list)

        description = da.adder_str_list[i]

        real_areas = [a.get_min_area()*scalar for scalar in area_list]
        for j, area in enumerate(real_areas):
            print(f" {description}, area {area}: {delays[j][0]}")
            print(f" As proportion of worst case: {round(delays[j][0]/sta_worst_delays[j],2)}")
            print(f" Sum of first op vector (op1,op2): {op1+op2+cin1}")
            print(f" Sum of second op vector (op3,op4): {op3+op4+cin2}")
            

def _generate_random_cases(width: int, count: int) -> list:
    cases_list: list = []
    #upper_bound = 2**16
    for i in range(0, int(count/2)):
        if np.random.rand() > 0.5:
            cases_list.append({"a":int(abs(np.random.normal(scale=100))), "b":int(abs(np.random.normal(scale=100))), "cin" : randint(0,0)})
            cases_list.append({"a":int(abs(np.random.normal(scale=100))), "b":int(abs(np.random.normal(scale=100))), "cin" : randint(0,0)})
        else:
            cases_list.append({"a":randint(0,2**64), "b":randint(0,2**64), "cin" : 0})
            cases_list.append({"a":randint(0,2**64), "b":randint(0,2**64), "cin" : 0})


    return cases_list


def _convert_pin_output_to_context() -> dict:
    output: str = open(PIN_CONTEXT_PATH).read()
    lines = output.split("\n")
    context = [None]*(len(lines)-1)
    for i, line in enumerate(lines):
        if line == "": continue
        context[i] = line.split("/")
    return context


prev_case_list = None
def _convert_pin_output_to_cases(**kwargs) -> dict:
    output = open(PIN_OPERANDS_PATH).read()
    lines = output.split("\n")
    case_list: dict = {}
    case_list["SUB"] = []
    case_list["ADD"] = []
    case_list["LEA"] = []
    case_list["MOV"] = []
    case_list["MEM"] = []
    case_list["all"] = []


    experimental_sub: bool = False
    if "exp_sub" in kwargs.keys():
        experimental_sub = kwargs["exp_sub"]


    for line in lines:
        if "\\" not in line: continue
        info = line.split("\\")
        opcode = info[2]
        info[0] = int(int(info[0],base=16))
        info[1] = int(int(info[1],base=16))
        if opcode == "SUB":
            op1 = info[0]
            op2 = ~info[1]
            cin = 1
            if experimental_sub:
                if op1 % 2 == 0:
                    op1 |= 1
                    cin = 0
                elif op2 % 2 == 0:
                    op2 |= 1
                    cin = 0
            case_list["SUB"].append({"a":info[0],"b":op2,"cin":cin})
        elif opcode == "ADD":
            case_list["ADD"].append({"a":info[0], "b":info[1], "cin":0})
        elif opcode == "LEA":
            case_list["LEA"].append({"a":info[0], "b":info[1], "cin":0})
            #case_list["MEM"].append({"a":info[0], "b":info[1], "cin":0})
        elif opcode == "MOV":
            case_list["MOV"].append({"a":info[0], "b":info[1], "cin":0})
      
        elif opcode == "MEM":
            case_list["MEM"].append({"a":info[0], "b":info[1], "cin":0})  
        else:
            print("main.convert_pin_output_to_cases(): Error (unrecognized opcode)")
            exit()
    case_list["all"] = case_list["ADD"] + case_list["SUB"] + case_list["MOV"] + case_list["LEA"]
    prev_case_list = case_list
    return case_list

def _perform_random_sampling(cases: list):
    new_cases = [None]*SIM_MAX_CASES
    visited, index = set(), 0
    while index < SIM_MAX_CASES:
        sample: int = randint(0,SIM_MAX_CASES-2)
        while sample in visited:
            sample: int = randint(0, SIM_MAX_CASES-2)
        new_cases[index] = cases[sample]
        new_cases[index+1] = cases[sample+1]
        index += 2
        visited.add(sample)
        visited.add(sample+1)
    return new_cases
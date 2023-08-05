import math
import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.append("py_module/")
sys.path.append("py_module/adder/GateSize/")

from py_module.adder import Adder

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Toggles visual graph generation.", action="store_true")

parser.add_argument("-v", "--verilog", help="Regenerates high-level verilog for specified design", action="store_true")
parser.add_argument("-s", "--synthesize", help="Synthesizes high-level verilog of the specified design into a structural design consisting of basic gates.", action="store_true")
parser.add_argument("-o", "--optimize", help="TBD", action="store_true")
parser.add_argument("-t", "--test", help="Tests high-level verilog for the specified design with a suite of test cases.", action="store_true")
parser.add_argument("-r", "--run", help="TBD", action="store_true")
parser.add_argument("-a", "--area_list", help="TBD", action="store")
parser.add_argument("-c", "--case", help="TBD", action="store")

args = parser.parse_args()
description = args.description

draw: bool = False

adder_list: list
mode: str = "single"
if "^" in description and "," in description:
    print("Error, cannot do two contradictory actions (^ and ,)")
    exit()
elif "^" in description: 
    adder_list = description.split("^")
    mode = "compare"
elif "," in description:
    adder_list = description.split(",")
    mode = "concatenate"
else:
    adder_list = [description]

print(adder_list)

fig, ax = plt.subplots()

for i in range(0, len(adder_list)):
    a: Adder = Adder(adder_list[i])
    if args.verilog:
        a.generate_verilog()
        print("Done generating verilog")
    if args.synthesize:
        a.synthesize()
        print("Done synthesizing")
    if args.area_list == None:
        continue
    area_list = list(eval("np.arange("+args.area_list+")"))

    if args.optimize:
        a.optimize(area_list)
        print("Done optimizing")
    if args.run and (mode == "compare" or mode == "single"):
        worst_case: dict = {"a": -1, "b":0, "cin":1}
        results: list = []
        results.append(a.simulate(area_list, [worst_case]))
        results = [result for result in results[0]]
        opt_results = a.get_optimizer_delays(area_list)
        worst_results = a.get_worst_case_delays(area_list)
        ratio = worst_results[0]/opt_results[0]
        opt_results = [result*ratio for result in opt_results]
        ax.plot(a.get_real_cell_counts(area_list), results)
        ax.plot(a.get_real_cell_counts(area_list), worst_results, label=a.get_verbose_name())
        ax.set(xlabel='area', ylabel='time')

        #print(results)
plt.legend(loc="upper right")
plt.show()
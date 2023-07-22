import math
import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("py_module/")
sys.path.append("py_module/GateSize/")
from adder import adder

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
parser.add_argument("-m", "--no_multithreading", help="TBD", action="store_true")

args = parser.parse_args()
description = args.description

draw: bool = False
#if args.graph:
#    draw = True

if description != "all":
    a: adder = adder(description)
    if args.verilog:
        a.generate_verilog()
        print("Done generating verilog")
    if args.synthesize:
        a.synthesize()
        print("Done synthesizing")
    if args.area_list == None:
        exit()
    area_list = list(eval("np.arange("+args.area_list+")"))
    #area_list = [1,50,50.1]
    if args.optimize:
        multithreading_enable = True if not args.no_multithreading else False
        a.optimize(area_list, multithreading=multithreading_enable)
        print("Done optimizing")
    if args.run:
        worst_case: dict = {"a": -1, "b":1, "cin":0}
        results = (a.simulate(area_list, [worst_case]))
        result_vec = [result[0] for result in results]
        #print(result_vec)       
        fig, ax = plt.subplots()
        ax.plot(area_list, result_vec)
        plt.show()


import math
import argparse
import sys
import numpy as np

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

    if args.optimize:
        a.optimize(area_list)
        print("Done optimizing")
    if args.run:
        worst_case: dict = {"a": -1, "b":0, "cin":1}
        results: list = []
        results.append(a.simulate(area_list, [worst_case]))
        print(results)

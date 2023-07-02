import math
import argparse
import sys

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
    if args.optimize:
        a.optimize([1])
        print("Done optimizing")
        #print(delays)

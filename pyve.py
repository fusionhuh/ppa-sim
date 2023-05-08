import math
import argparse
import sys
sys.path.append("py_module/")
import graph
import visual
import verilog

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Toggles visual graph generation.", action="store_true")

args = parser.parse_args()

description = args.description

#draw: bool = False
#if args.graph:
#    draw = True

a: verilog.adder = verilog.adder(description)

verilog: str

#if a.structure == "basic":
#    verilog = verilog.generate_basic_adder(a)
#else:
#    verilog = verilog.generate_structured_adder(a)

#if draw:
#    visual.draw_node_graph(a.graph, a.width)

import math
import argparse
import sys

sys.path.append("py_module/")
sys.path.append("py_module/GateSize")
import graph
import visual
import verilog
import synthesis
import cktopt

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Generates a graph visualization for basic adder types (bk, ks, skl, etc.).", action="store_true")
parser.add_argument("-t", "--test", help="Tests generated verilog for an adder before proceeding with synthesis.", action="store_true")
parser.add_argument("-v", "--verilog", help="Generates new verilog for the specified adder design.", action="store_true")
parser.add_argument("-s", "--synthesize", help="Synthesizes the specified adder design using Genus tools. Genus must be installed + on path and the verilog must already be generated for the provided adder.", action="store_true")
parser.add_argument("-o", "--optimize", help="Optimizes synthesized adder design. The provided adder must have already been synthesized using the -s option.", action="store_true")
parser.add_argument("-a", "--all", help="Performs all the verilog generation, synthesization, and optimization steps for the provided adder.", action="store_true")

args = parser.parse_args()
description = args.description

draw: bool = False
if args.graph:
    draw = True

if not args.verilog and not args.synthesize and not args.optimize and not args.all:
    print("No action specified.")
    exit()

a: verilog.adder
if args.verilog or args.all:
    a = verilog.adder(description=description, test=args.test)
if args.synthesize or args.all:
    synthesis.generate_synthesis_script(a)
    synthesis.execute_synthesis_script()
if args.optimize or args.all:
    cktopt.optimize(a.synthesized_file_path, [1], None)


# if description != "all":
#     a: verilog.adder = verilog.adder(description)
#     synthesis.generate_synthesis_script(a)
#     synthesis.execute_synthesis_script()
# else:
#     num_adders_generated:int = 0
#     for width_power in range(3, 6):
#         adder_width: int = 2 ** width_power
#         for structure in ["basic", "rc", "cla", "cskip"]:
#             for base_type in ["bk", "ks", "serial", "skl"]:
#                 for block_width_power in range(2, width_power):
#                     block_width: int = 2 ** block_width_power
#                     if structure == "cla":
#                         if adder_width != 16 or adder_width != 64:
#                             continue
#                         if block_width != 4:
#                             continue
#                     description: str
#                     if structure != "basic":
#                         description = f"{base_type}.{adder_width}.{structure}-{block_width}"
#                     else:
#                         description = f"{base_type}.{adder_width}.{structure}"
#                     a: verilog.adder = verilog.adder(description)
#                     num_adders_generated += 1
#     print(num_adders_generated)



#if a.structure == "basic":
#    verilog = verilog.generate_basic_adder(a)
#else:
#    verilog = verilog.generate_structured_adder(a)

if draw:
    visual.draw_node_graph(a.graph, a.width)

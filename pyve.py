import math
import argparse
import sys

sys.path.append("py_module/")
import graph
import visual
import verilog
import synthesis

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Toggles visual graph generation.", action="store_true")
parser.add_argument("-o", "--output", help="Toggles terminal text output.")

args = parser.parse_args()
description = args.description


draw: bool = False
if args.graph:
    draw = True

if description != "all":
    a: verilog.adder = verilog.adder(description)
    synthesis.generate_synthesis_script(a)
    synthesis.execute_synthesis_script()
else:
    num_adders_generated:int = 0
    for width_power in range(3, 6):
        adder_width: int = 2 ** width_power
        for structure in ["basic", "rc", "cla", "cskip"]:
            for base_type in ["bk", "ks", "serial", "skl"]:
                for block_width_power in range(2, width_power):
                    block_width: int = 2 ** block_width_power
                    if structure == "cla":
                        if adder_width != 16 or adder_width != 64:
                            continue
                        if block_width != 4:
                            continue
                    description: str
                    if structure != "basic":
                        description = f"{base_type}.{adder_width}.{structure}-{block_width}"
                    else:
                        description = f"{base_type}.{adder_width}.{structure}"
                    a: verilog.adder = verilog.adder(description)
                    num_adders_generated += 1
    print(num_adders_generated)



#if a.structure == "basic":
#    verilog = verilog.generate_basic_adder(a)
#else:
#    verilog = verilog.generate_structured_adder(a)

if draw:
    visual.draw_node_graph(a.graph, a.width)

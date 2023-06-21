import math
import argparse
import sys

sys.path.append("py_module/")
sys.path.append("py_module/GateSize/")
import graph
import visual
import verilog
import synthesis
import cktopt
import matplotlib
import matplotlib.pyplot as plt

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
    a.generate_verilog()
    a.synthesize()
    #cell_count = a.get_synthesized_cell_count()
    cell_count = 100
    two_powers = list(map(lambda x : 2**x, range(0, 5)))
    area_sizes = list(map(lambda x : (cell_count+1) * x, two_powers))
    delays = a.calculate_worst_case_delay(area_sizes)
    #plt.plot(area_sizes, delays)
    #plt.ion()
    #synthesis.generate_synthesis_script(a)
    #synthesis.execute_synthesis_script()
    #cktopt.optimize(a, [608])

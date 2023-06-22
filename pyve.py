import math
import argparse
import sys

sys.path.append("py_module/")
sys.path.append("py_module/GateSize/")
from adder import adder

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Toggles visual graph generation.", action="store_true")

args = parser.parse_args()
description = args.description

draw: bool = False
if args.graph:
    draw = True

if description != "all":
    a: adder = adder(description)
    a.generate_verilog()
    a.synthesize()
    cell_count = 100
    two_powers = list(map(lambda x : 2**x, range(0, 5)))
    area_sizes = list(map(lambda x : (cell_count+1) * x, two_powers))
    delays = a.calculate_worst_case_delay(area_sizes)

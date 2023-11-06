
import sys
sys.path.append("../py_module/")
from py_module.file_structure import *

COLORS = ["blue", "red", "green", "purple", "orange","yellow","cyan", "black", "turquoise", "gold", "darkcyan", "rosybrown", "darkseagreen", "slategrey", "purple"]*10

SIMULATE_MODES = ["random", "program", "custom"]
INSTRUCTION_CATEGORIES = ["all", "MOV", "LEA", "RW", "SUB", "ADD", "MEM"]

SIM_MAX_CASES = 10000000000

from numpy import arange
from .globals import *
from .constants import *
from .helpers import _get_minimum_scale_factors
from pathlib import Path
import sys
sys.path.append("../py_module")
from py_module.adder import Adder

# public API funcs
def add_adder(adder: str):
    if adder in da.adder_str_list:
        return
    da.adder_str_list.append(adder)
    a = Adder(adder)
    if not a.is_generated():
        a.generate_verilog()
    if not a.is_synthesized():
        a.synthesize()
    da.adder_list.append(Adder(adder))

def remove_adder(adder):
    if isinstance(adder, int):
        del da.adder_list[adder]
        del da.adder_str_list[adder]
        return

    if adder not in da.adder_str_list:
        print("Provided adder not in working list.")
        return
    for i, description in enumerate(da.adder_str_list):
        if adder != description: continue
        del da.adder_str_list[i]
        del da.adder_list[i]
        return

def print_adder_list():
    print(da.adder_str_list)
    if da.curr_results_profile == None:
        return

def set_area_list(start, end, stride=1):
    area_list = arange(start, end, stride)
    da.area_list = area_list
    scale_factors = _get_minimum_scale_factors(da.adder_list) if da.match else [1]*len(da.adder_list)
    for i, a in enumerate(da.adder_list):
        area_list = [round(area*scale_factors[i],3) for area in da.area_list]
        if not a.is_optimized(area_list): a.optimize(area_list)

def set_match(match: bool):
    da.match = match

def print_area_list():
    print(da.area_list)


def print_match():
    print(da.match)

def set_path(path: str):
    da.path = path

def print_path():
    print(da.path)

def set_program(program: str):
    path = da.path + program
    if not Path(path).is_file():
        print("Specified binary doesn't exist.")
        return
    da.curr_program = path

def print_program():
    print(da.curr_program)

def set_instruction_category(category: str):
    if category not in INSTRUCTION_CATEGORIES:
        print(f"Instruction must be in {INSTRUCTION_CATEGORIES}")
        return
    da.ins_category = category

def print_instruction_category():
    print(da.ins_category)

def print_profiles():
    print(da.results_profiles)

def set_profile(profile: str):
    da.curr_results_profile = profile

def refresh():
    pass

def set_feature_list():
    pass

def append_feature():
    pass

def remove_feature():
    pass

def print_feature_list():
    pass

def set_var():
    pass

def print_var():
    pass

def clear_var():
    pass


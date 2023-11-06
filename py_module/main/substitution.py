from .helpers import _get_minimum_scale_factors
from .globals import *
from .constants import *
from .environment import *
from py_module.main.profile import Profile


def synthesize_hls_file(path: str, top_fname: str):
    hlsynthesizer.synthesize_file(path, top_fname)

def substitute_adders():
    #profile: Profile = da.data[da.curr_results_profile]
    adders = da.adder_list
    areas = da.area_list
    hlsynthesizer.substitute_adders(adders, areas)

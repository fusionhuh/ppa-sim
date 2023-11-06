from .data_agg import DataAggregator
from py_module.hlsynthesizer import HLSynthesizer

da = DataAggregator()

hlsynthesizer = HLSynthesizer()

da.add_field("adder_list", [], private=True)
da.add_field("adder_str_list", [], private=True)
da.add_field("match", False, private=True)
da.add_field("ghost_match", None, private=True)
da.add_field("area_list", [], private=True)
da.add_field("working_program", "", private=True)
da.add_field("cached_program_data", dict(), private=True)
da.add_field("cached_random_data", dict(), private=True)
da.add_field("results_profiles", [], private=True)
da.add_field("curr_results_profile", None, private=True)
da.add_field("data", dict(), private=True)
da.add_field("path", "simulation/bin/embench-iot/bd/src/", private=True)
da.add_field("curr_program", f"{da.path}crc32/crc32", private=True)
da.add_field("ins_category", "all", private=True)
da.add_field("feature_list", [], private=True)

fig_num = 0
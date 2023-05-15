read_hdl ../verilog/logic/pos_operator.v ../verilog/logic/neg_operator.v ../verilog/logic/carry_operator.v ../verilog/base/ks/ks32.v
set_db library ./NangateOpenCellLibrary_typical.lib
set_db lef_library ./NangateOpenCellLibrary.lef
elaborate
current_design designs/ks32
read_sdc ./hardware_info.sdc
syn_generic
syn_map
syn_opt
write_hdl > synthesized/base/ks//ks32.v
report_area > synthesized/base/ks//ks32_area
report_timing > synthesized/base/ks//ks32_timing


read_hdl ../verilog/logic/pos_operator.v ../verilog/logic/neg_operator.v ../verilog/logic/carry_operator.v ../verilog/base/serial/serial32.v
set_db library ./NangateOpenCellLibrary_typical.lib
set_db lef_library ./NangateOpenCellLibrary.lef
elaborate
current_design designs/serial32
read_sdc ./hardware_info.sdc
syn_generic
syn_map
syn_opt
write_hdl > synthesized/base/serial//serial32.v
report_area > synthesized/base/serial//serial32_area
report_timing > synthesized/base/serial//serial32_timing


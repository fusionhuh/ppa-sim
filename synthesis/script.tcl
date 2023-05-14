read_hdl ../verilog/logic/pos_operator.v ../verilog/logic/neg_operator.v ../verilog/logic/carry_operator.v ../verilog/base/bk/bk32.v
set_db library ./NangateOpenCellLibrary_typical.lib
set_db lef_library ./NangateOpenCellLibrary.lef
elaborate
current_design designs/bk32
read_sdc ./hardware_info.sdc
syn_generic
syn_map
syn_opt
write_hdl > synthesized/verilog/base/bk/bk32.v

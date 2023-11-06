yosys -import
read_verilog {in_path}; 

#blackbox ui_plus_expr_FU
#blackbox plus_expr_FU
opt
hierarchy -check -top {design_name}
synth -top {design_name}
flatten
dfflibmap -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
abc -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib;  
techmap
opt_clean -purge
#yosys proc
write_verilog -noattr {out_path}
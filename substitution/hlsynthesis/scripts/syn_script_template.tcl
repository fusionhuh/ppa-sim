yosys -import
read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
read_verilog {in_path}; 
blackbox ui_plus_expr_FU;
blackbox plus_expr_FU;
blackbox ui_minus_expr_FU;
blackbox minus_expr_FU;
#opt
hierarchy -check -top {design_name};
synth -top {design_name};
#memory_bram;
dfflibmap -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
abc -D 1000000 -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib;  
techmap;
opt_clean -purge;
flatten;
check;
write_verilog -noattr {out_path};
yosys -import
read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
read_verilog {in_path}; 
hierarchy -check -top {design_name};
synth -top {design_name};
dfflibmap -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
abc -D 10000000 -liberty substitution/hardware/NangateOpenCellLibrary_typical.lib;  
techmap;
opt_clean -purge;
flatten
check;
write_verilog -noattr {out_path};
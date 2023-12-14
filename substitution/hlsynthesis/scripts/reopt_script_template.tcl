yosys -import;
read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
read_verilog {in_path};
opt;
write_verilog -noattr {in_path}
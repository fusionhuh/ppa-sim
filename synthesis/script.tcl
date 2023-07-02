yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/serial/serial8.v
#read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top serial8
synth -top serial8
flatten
opt
flatten
opt_clean -purge
exec mkdir -p synthesis/verilog/base/serial
write_verilog -noattr -noexpr synthesis/verilog/base/serial/serial8.v
tee -o synthesis/verilog/base/serial/serial8_stats.json stat -json
exit

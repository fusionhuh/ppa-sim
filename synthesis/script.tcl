yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/bk/bk8.v
#read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top bk8
synth -top bk8
flatten
opt
flatten
opt_clean -purge
exec mkdir -p synthesis/verilog/base/bk
write_verilog -noattr -noexpr synthesis/verilog/base/bk/bk8.v
tee -o synthesis/verilog/base/bk/bk8_stats.json stat -json
exit

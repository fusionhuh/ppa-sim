yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/skl/skl16.v
#read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top skl16
synth -top skl16
flatten
opt
flatten
opt_clean -purge
exec mkdir -p synthesis/verilog/base/skl
write_verilog -noattr -noexpr synthesis/verilog/base/skl/skl16.v
tee -o synthesis/verilog/base/skl/skl16_stats.json stat -json
exit

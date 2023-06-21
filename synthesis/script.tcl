yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/bk/bk8.v
read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top bk8
synth -top bk8
flatten
opt
#techmaps
techmap
flatten
opt -fine
opt_clean -purge
#techmap -lib synthesis/NangateOpenCellLibrary_typical.lib
exec mkdir -p synthesis/verilog/base/bk
write_blif synthesis/verilog/base/bk/bk8.blif
write_verilog -noattr -noexpr synthesis/verilog/base/bk/bk8.v
stat
exit

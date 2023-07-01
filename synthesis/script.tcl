yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/ks/ks8.v verilog/structured/cskip/ks8_16_cskip.v
#read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top ks8_16_cskip
synth -top ks8_16_cskip
flatten
opt
flatten
opt_clean -purge
exec mkdir -p synthesis/verilog/structured/cskip
write_verilog -noattr -noexpr synthesis/verilog/structured/cskip/ks8_16_cskip.v
stat
exit

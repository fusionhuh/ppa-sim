yosys -import
read_verilog verilog/logic/pos_operator.v verilog/logic/neg_operator.v verilog/logic/carry_operator.v verilog/base/ks/ks4.v verilog/structured/rc/ks_16_rc_4.v
read_liberty synthesis/NangateOpenCellLibrary_typical.lib
hierarchy -check -top ks_16_rc_4
synth -top ks_16_rc_4
flatten
opt
#techmaps
techmap
flatten
opt -fine
opt_clean -purge
#techmap -lib synthesis/NangateOpenCellLibrary_typical.lib
exec mkdir -p synthesis/verilog/structured/rc
write_blif synthesis/verilog/structured/rc/ks_16_rc_4.blif
write_verilog -noattr -noexpr synthesis/verilog/structured/rc/ks_16_rc_4.v
stat
exit

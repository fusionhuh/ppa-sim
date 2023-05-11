testbench: verilog/testbench.v
	iverilog -Iverilog/logic/ -Iverilog/base/ -Iverilog/structured/ -Iverilog/base/bk -Iverilog/base/ks -Iverilog/base/hybrid -Iverilog/base/serial -Iverilog/base/skl -o verilog/testbench verilog/testbench.v
	vvp verilog/testbench

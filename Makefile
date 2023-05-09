testbench: verilog/testbench.v
	iverilog -Iverilog/logic/ -Iverilog/base/ -Iverilog/structured/ -o verilog/testbench verilog/testbench.v
	vvp verilog/testbench

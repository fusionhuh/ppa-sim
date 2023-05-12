testbench: verilog/testbench.v
	iverilog -Iverilog/logic/ -Iverilog/base/ -Iverilog/structured/ -Iverilog/base/bk -Iverilog/base/ks -Iverilog/base/hybrid -Iverilog/base/serial -Iverilog/base/skl -o verilog/testbench verilog/testbench.v > testbench_test.txt
	vvp verilog/testbench

clean:
	rm -rf __pycache__
	rm -f log.txt
	rm -f */log.txt
	rm -f */*.vcd
	
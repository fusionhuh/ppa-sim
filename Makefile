IVERILOG_INCLUDES=-Iverilog/logic/ -Iverilog/base/ -Iverilog/structured/ -Iverilog/base/bk -Iverilog/base/ks -Iverilog/base/hybrid -Iverilog/base/serial -Iverilog/base/skl

testbench: verilog/testbench.v
	iverilog $(IVERILOG_INCLUDES) -o verilog/testbench verilog/testbench.v > testbench_test.txt
	vvp verilog/testbench

compile_test:
	iverilog $(IVERILOG_INCLUDES) -o verilog/test verilog/test.v > verilog/test_out.txt

compile_test_clean:
	rm -f verilog/test.v
	rm -f verilog/test
	rm -f verilog/test_out.txt

run_test:
	iverilog $(IVERILOG_INCLUDES) -o verilog/tb verilog/tb.v
	vvp verilog/tb

synthesis_test:
	source /vol/ece303/genus_tutorial/cadence.env

clean:
	rm -rf __pycache__
	rm -f log.txt
	rm -f */log.txt
	rm -f ./*.vcd
	rm -f */*.vcd
	rm -rf verilog/base/
	rm -rf verilog/structured/
	rm -f verilog/testbench
	rm -f verilog/testbench.v
	rm -f verilog/tb.v
	rm -f verilog/tb
	rm -f genus.*
	

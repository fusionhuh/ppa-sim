IVERILOG_INCLUDES=-Isimulation/ -Ioptimization/verilog/base/ -Iverilog/-Iverilog/logic/ -Iverilog/base/ -Iverilog/structured/ -Iverilog/base/bk -Iverilog/base/ks -Iverilog/base/hybrid -Iverilog/base/serial -Iverilog/base/skl

testbench: verilog/testbench.v
	iverilog $(IVERILOG_INCLUDES) -o verilog/testbench verilog/testbench.v > testbench_test.txt
	vvp verilog/testbench

compile_test:
	iverilog -g specify $(IVERILOG_INCLUDES) -o test test.v > test_out.txt

compile_test_clean:
	rm -f test.v
	rm -f test
	rm -f test_out.txt

run_test:
	iverilog $(IVERILOG_INCLUDES) -o verilog/tb verilog/tb.v
	vvp verilog/tb

synthesis_test:
	source /vol/ece303/genus_tutorial/cadence.env

clean_general:
	rm -f log.txt
	rm -f */log.txt

clean_verilog:
	rm -rf verilog/base/
	rm -rf verilog/structured/
	rm -rf verilog/tb*

clean_synthesis:
	rm -rf synthesis/verilog/

clean_optimize:
	rm -rf optimization/size_data/
	rm -rf optimization/verilog/
	rm -rf optimization/sdf/

clean_all: clean_general clean_verilog clean_synthesis clean_optimize

clean_log:
	rm -r *.log
	rm -r log.txt
	
	

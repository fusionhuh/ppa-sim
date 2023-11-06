`timescale 1ns/1ns
`include "substitution/hardware/NangateOpenCellLibrary_typical_conditional.v"

module tb;

	reg clk=0;
	reg reset = 0;
	reg start = 0;
	wire done;
	wire [63:0] return_val;
	reg [63:0] x1, x2;
	

	dfadd mainmod(.clock(clk), .reset(reset), .start_port(start), .x1(x1), .x2(x2), .done_port(done), .return_port(return_val));
	
	
	always #500 clk = ~clk;

	always@(posedge clk) begin
		i = i + 1;
		if (i == 1000) $finish;
	end
	
	
	integer i = 0;
	initial begin
		//#100;
		//#100;
		$sdf_annotate("temp.sdf", tb.mainmod);	
		$dumpfile("test.vcd");

		$monitor($realtime,,"result: %d", return_val);
		start = 1;
		x1=64'h4000000000000000;
		x2=64'h3FF0000000000000;

		$dumpvars(0, tb);
		wait(done);
		$finish;
	end 

endmodule

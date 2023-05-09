
`include "cla/bk_16_cla_4.v"
`include "cla/serial_64_cla_4.v"

`define WIDTH 64

module tb;
	reg [`WIDTH-1:0]x1;
	reg [`WIDTH-1:0]x2;
	wire [`WIDTH-1:0]s;
	reg cin;
	wire cout;
	serial_64_cla_4 test(.x1(x1), .x2(x2), .s(s), .cin(cin), .cout(cout));

	initial begin
		$monitor($time,,"x1: %d, x2: %d, s: %d, cout: %d", x1, x2, s, cout);
 		
		$dumpfile("test.vcd");
		$dumpvars(s, test);
		#100
		x1 = 999;
		x2 = -1;
		cin = 1;
		$display("x1=%d", x1);
		$display("x2=%d", x2);
//		$display("sum=%d", s);
    	#100
		$finish;

	end


endmodule
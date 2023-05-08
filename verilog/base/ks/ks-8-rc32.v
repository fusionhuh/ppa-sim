`include "ks32.v"
// number of levels: 4
// number of nodes: 17
// NAND count: 68, AND count: 44
// NOR count: 68, OR count: 24
// NOT count: 36, Transistor count: 1024
module ks8rc32(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	wire block0_cout;
	ks32 block0(.x1(x1[7:0]), .x2(x2[7:0]), .s(s[7:0]), .cin(cin), .cout(block0_cout));
	wire block1_cout;
	ks32 block1(.x1(x1[15:8]), .x2(x2[15:8]), .s(s[15:8]), .cin(block0_cout), .cout(block1_cout));
	wire block2_cout;
	ks32 block2(.x1(x1[23:16]), .x2(x2[23:16]), .s(s[23:16]), .cin(block1_cout), .cout(block2_cout));
	wire block3_cout;
	ks32 block3(.x1(x1[31:24]), .x2(x2[31:24]), .s(s[31:24]), .cin(block2_cout), .cout(cout));
endmodule


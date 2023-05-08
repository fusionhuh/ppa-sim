`include "ks16.v"
// number of levels: 5
// number of nodes: 98
// NAND count: 98, AND count: 54
// NOR count: 98, OR count: 44
// NOT count: 30, Transistor count: 1432
module ks16cskip32(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	wire[31:0]p = x1 ^ x2;

	wire block0_cout;
	ks16 block0(.x1(x1[15:0]), .x2(x2[15:0]), .s(s[15:0]), .cin(cin), .cout(block0_cout));
	wire block0_real_cout;
	wire block0_group_p;
	and gate0(block0_group_p, p[15:0]);
	assign block0_real_cout = block0_group_p ? cin : block0_cout;

	wire block1_cout;
	ks16 block1(.x1(x1[31:16]), .x2(x2[31:16]), .s(s[31:16]), .cin(block0_real_cout), .cout(block1_cout));
	wire block1_real_cout;
	wire block1_group_p;
	and gate1(block1_group_p, p[31:16]);
	assign block1_real_cout = block1_group_p ? block0_real_cout : block1_cout;

	assign cout = block1_real_cout;
endmodule


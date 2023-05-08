`include "bk8.v"
// number of levels: 5
// number of nodes: 44
// NAND count: 44, AND count: 24
// NOR count: 44, OR count: 20
// NOT count: 52, Transistor count: 720
module bk8cskip32(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	wire[31:0]p = x1 ^ x2;

	wire block0_cout;
	bk8 block0(.x1(x1[7:0]), .x2(x2[7:0]), .s(s[7:0]), .cin(cin), .cout(block0_cout));
	wire block0_real_cout;
	wire block0_group_p;
	and gate0(block0_group_p, p[7:0]);
	assign block0_real_cout = block0_group_p ? cin : block0_cout;

	wire block1_cout;
	bk8 block1(.x1(x1[15:8]), .x2(x2[15:8]), .s(s[15:8]), .cin(block0_real_cout), .cout(block1_cout));
	wire block1_real_cout;
	wire block1_group_p;
	and gate1(block1_group_p, p[15:8]);
	assign block1_real_cout = block1_group_p ? block0_real_cout : block1_cout;

	wire block2_cout;
	bk8 block2(.x1(x1[23:16]), .x2(x2[23:16]), .s(s[23:16]), .cin(block1_real_cout), .cout(block2_cout));
	wire block2_real_cout;
	wire block2_group_p;
	and gate2(block2_group_p, p[23:16]);
	assign block2_real_cout = block2_group_p ? block1_real_cout : block2_cout;

	wire block3_cout;
	bk8 block3(.x1(x1[31:24]), .x2(x2[31:24]), .s(s[31:24]), .cin(block2_real_cout), .cout(block3_cout));
	wire block3_real_cout;
	wire block3_group_p;
	and gate3(block3_group_p, p[31:24]);
	assign block3_real_cout = block3_group_p ? block2_real_cout : block3_cout;

	assign cout = block3_real_cout;

endmodule


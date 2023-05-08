`include "bk4.v"
// number of levels: 3
// number of nodes: 32
// NAND count: 32, AND count: 16
// NOR count: 32, OR count: 16
// NOT count: 24, Transistor count: 496
module bk4cskip32(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	p = x1 ^ x2;

	wire block0_cout;
	bk4 block0(.x1(x1[3:0]), .x2(x2[3:0]), .s(s[3:0]), .cin(cin), .cout(block0_cout));
	wire block0_real_cout;
	wire block0_group_p;
	and gate0(block0_group_p, p[3:0]);
	assign block0_real_cout = block0_group_p ? cin : block0_cout;

	wire block1_cout;
	bk4 block1(.x1(x1[7:4]), .x2(x2[7:4]), .s(s[7:4]), .cin(block0_real_cout), .cout(block1_cout));
	wire block1_real_cout;
	wire block1_group_p;
	and gate1(block1_group_p, p[7:4]);
	assign block1_real_cout = block1_group_p ? block0_real_cout : block1_cout;

	wire block2_cout;
	bk4 block2(.x1(x1[11:8]), .x2(x2[11:8]), .s(s[11:8]), .cin(block1_real_cout), .cout(block2_cout));
	wire block2_real_cout;
	wire block2_group_p;
	and gate2(block2_group_p, p[11:8]);
	assign block2_real_cout = block2_group_p ? block1_real_cout : block2_cout;

	wire block3_cout;
	bk4 block3(.x1(x1[15:12]), .x2(x2[15:12]), .s(s[15:12]), .cin(block2_real_cout), .cout(block3_cout));
	wire block3_real_cout;
	wire block3_group_p;
	and gate3(block3_group_p, p[15:12]);
	assign block3_real_cout = block3_group_p ? block2_real_cout : block3_cout;

	wire block4_cout;
	bk4 block4(.x1(x1[19:16]), .x2(x2[19:16]), .s(s[19:16]), .cin(block3_real_cout), .cout(block4_cout));
	wire block4_real_cout;
	wire block4_group_p;
	and gate4(block4_group_p, p[19:16]);
	assign block4_real_cout = block4_group_p ? block3_real_cout : block4_cout;

	wire block5_cout;
	bk4 block5(.x1(x1[23:20]), .x2(x2[23:20]), .s(s[23:20]), .cin(block4_real_cout), .cout(block5_cout));
	wire block5_real_cout;
	wire block5_group_p;
	and gate5(block5_group_p, p[23:20]);
	assign block5_real_cout = block5_group_p ? block4_real_cout : block5_cout;

	wire block6_cout;
	bk4 block6(.x1(x1[27:24]), .x2(x2[27:24]), .s(s[27:24]), .cin(block5_real_cout), .cout(block6_cout));
	wire block6_real_cout;
	wire block6_group_p;
	and gate6(block6_group_p, p[27:24]);
	assign block6_real_cout = block6_group_p ? block5_real_cout : block6_cout;

	wire block7_cout;
	bk4 block7(.x1(x1[31:28]), .x2(x2[31:28]), .s(s[31:28]), .cin(block6_real_cout), .cout(block7_cout));
	wire block7_real_cout;
	wire block7_group_p;
	and gate7(block7_group_p, p[31:28]);
	assign block7_real_cout = block7_group_p ? block6_real_cout : block7_cout;

endmodule


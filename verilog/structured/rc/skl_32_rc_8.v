`ifndef SKL8
`include "skl8.v"
`endif
// number of levels: 4
// number of nodes: 48
// NAND count: 48, AND count: 32
// NOR count: 48, OR count: 16
// NOT count: 44, Transistor count: 760
module skl_32_rc_8(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	wire block0_cout;
	skl8 block0(.x1(x1[7:0]), .x2(x2[7:0]), .s(s[7:0]), .cin(cin), .cout(block0_cout));
	wire block1_cout;
	skl8 block1(.x1(x1[15:8]), .x2(x2[15:8]), .s(s[15:8]), .cin(block0_cout), .cout(block1_cout));
	wire block2_cout;
	skl8 block2(.x1(x1[23:16]), .x2(x2[23:16]), .s(s[23:16]), .cin(block1_cout), .cout(block2_cout));
	wire block3_cout;
	skl8 block3(.x1(x1[31:24]), .x2(x2[31:24]), .s(s[31:24]), .cin(block2_cout), .cout(cout));
endmodule

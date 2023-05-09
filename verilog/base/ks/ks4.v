`ifndef CARRY_OPERATOR
`include "carry_operator.v"
`endif
`ifndef NEG_CARRY_OPERATOR
`include "neg_operator.v"
`endif
`ifndef POS_CARRY_OPERATOR
`include "pos_operator.v"
`endif
`define KS4
// number of levels: 3
// number of nodes: 40
// NAND count: 40, AND count: 24
// NOR count: 40, OR count: 16
// NOT count: 24, Transistor count: 608
module ks4(x1, x2, s, cin, cout, p_out, g_out);
	input[3:0]x1;
	input[3:0]x2;
	input cin;
	wire[3:0]p_in;
	wire[3:0]g_in;
	output[3:0]s;
	output cout;

	output[3:0]p_out;
	output[3:0]g_out;
	assign p_in = x1 ^ x2;
	assign p_out = p_in;
	assign g_in[3:1] = x1[3:1] & x2[3:1];
	assign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);
	assign g_out = g_in;
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	neg_operator node_level1_pos1(.p1(p_in[1]), .g1(g_in[1]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos2_outg;
	wire node_level1_pos2_outp;
	neg_operator node_level1_pos2(.p1(p_in[2]), .g1(g_in[2]), .p0(p_in[1]), .g0(g_in[1]), .gp(node_level1_pos2_outg), .pp(node_level1_pos2_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	neg_operator node_level1_pos3(.p1(p_in[3]), .g1(g_in[3]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level2_pos2_outg;
	wire node_level2_pos2_outp;
	pos_operator node_level2_pos2(.p1(node_level1_pos2_outp), .g1(node_level1_pos2_outg), .p0(~p_in[0]), .g0(~g_in[0]), .gp(node_level2_pos2_outg), .pp(node_level2_pos2_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	pos_operator node_level2_pos3(.p1(node_level1_pos3_outp), .g1(node_level1_pos3_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));


	assign s[0] = p_in[0] ^ cin;
	assign s[1] = p_in[1] ^ g_in[0];
	assign s[2] = p_in[2] ^ ~node_level1_pos1_outg;
	assign s[3] = p_in[3] ^ node_level2_pos2_outg;
	assign cout = (x1[3] & x2[3]) | (~s[3] & (x1[3] | x2[3]));
endmodule

`ifndef CARRY_OPERATOR
`include "carry_operator.v"
`endif
`ifndef NEG_CARRY_OPERATOR
`include "neg_operator.v"
`endif
`ifndef POS_CARRY_OPERATOR
`include "pos_operator.v"
`endif
`define BK8
// number of levels: 5
// number of nodes: 44
// NAND count: 44, AND count: 24
// NOR count: 44, OR count: 20
// NOT count: 52, Transistor count: 720
module bk8(x1, x2, s, cin, cout, p_out, g_out);
	input[7:0]x1;
	input[7:0]x2;
	input cin;
	wire[7:0]p_in;
	wire[7:0]g_in;
	output[7:0]s;
	output cout;

	output[7:0]p_out;
	output[7:0]g_out;
	assign p_in = x1 ^ x2;
	assign p_out = p_in;
	assign g_in[7:1] = x1[7:1] & x2[7:1];
	assign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);
	assign g_out = g_in;
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	neg_operator node_level1_pos1(.p1(p_in[1]), .g1(g_in[1]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	neg_operator node_level1_pos3(.p1(p_in[3]), .g1(g_in[3]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level1_pos5_outg;
	wire node_level1_pos5_outp;
	neg_operator node_level1_pos5(.p1(p_in[5]), .g1(g_in[5]), .p0(p_in[4]), .g0(g_in[4]), .gp(node_level1_pos5_outg), .pp(node_level1_pos5_outp));
	wire node_level1_pos7_outg;
	wire node_level1_pos7_outp;
	neg_operator node_level1_pos7(.p1(p_in[7]), .g1(g_in[7]), .p0(p_in[6]), .g0(g_in[6]), .gp(node_level1_pos7_outg), .pp(node_level1_pos7_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	pos_operator node_level2_pos3(.p1(node_level1_pos3_outp), .g1(node_level1_pos3_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));
	wire node_level2_pos7_outg;
	wire node_level2_pos7_outp;
	pos_operator node_level2_pos7(.p1(node_level1_pos7_outp), .g1(node_level1_pos7_outg), .p0(node_level1_pos5_outp), .g0(node_level1_pos5_outg), .gp(node_level2_pos7_outg), .pp(node_level2_pos7_outp));
	wire node_level3_pos7_outg;
	wire node_level3_pos7_outp;
	neg_operator node_level3_pos7(.p1(node_level2_pos7_outp), .g1(node_level2_pos7_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos7_outg), .pp(node_level3_pos7_outp));
	wire node_level3_pos5_outg;
	wire node_level3_pos5_outp;
	neg_operator node_level3_pos5(.p1(~node_level1_pos5_outp), .g1(~node_level1_pos5_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos5_outg), .pp(node_level3_pos5_outp));
	wire node_level4_pos2_outg;
	wire node_level4_pos2_outp;
	pos_operator node_level4_pos2(.p1(~p_in[2]), .g1(~g_in[2]), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level4_pos2_outg), .pp(node_level4_pos2_outp));
	wire node_level4_pos4_outg;
	wire node_level4_pos4_outp;
	pos_operator node_level4_pos4(.p1(~p_in[4]), .g1(~g_in[4]), .p0(~node_level2_pos3_outp), .g0(~node_level2_pos3_outg), .gp(node_level4_pos4_outg), .pp(node_level4_pos4_outp));
	wire node_level4_pos6_outg;
	wire node_level4_pos6_outp;
	pos_operator node_level4_pos6(.p1(~p_in[6]), .g1(~g_in[6]), .p0(node_level3_pos5_outp), .g0(node_level3_pos5_outg), .gp(node_level4_pos6_outg), .pp(node_level4_pos6_outp));


	assign s[0] = p_in[0] ^ cin;
	assign s[1] = p_in[1] ^ g_in[0];
	assign s[2] = p_in[2] ^ ~node_level1_pos1_outg;
	assign s[3] = p_in[3] ^ node_level4_pos2_outg;
	assign s[4] = p_in[4] ^ node_level2_pos3_outg;
	assign s[5] = p_in[5] ^ node_level4_pos4_outg;
	assign s[6] = p_in[6] ^ ~node_level3_pos5_outg;
	assign s[7] = p_in[7] ^ node_level4_pos6_outg;
	assign cout = (x1[7] & x2[7]) | (~s[7] & (x1[7] | x2[7]));
endmodule

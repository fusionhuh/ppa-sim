`ifndef CARRY_OPERATOR
`include "carry_operator.v"
`endif
`ifndef NEG_CARRY_OPERATOR
`include "neg_operator.v"
`endif
`ifndef POS_CARRY_OPERATOR
`include "pos_operator.v"
`endif
// number of levels: 5
// number of nodes: 49
// NAND count: 49, AND count: 27
// NOR count: 49, OR count: 22
// NOT count: 15, Transistor count: 716
module ks16(x1, x2, s, cin, cout);
	input[15:0]x1;
	input[15:0]x2;
	input cin;
	wire[15:0]p_in;
	wire[15:0]g_in;
	output[15:0]s;
	output cout;

	assign p_in = x1 ^ x2;
	assign g_in[15:1] = x1[15:1] & x2[15:1];
	assign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	neg_operator node_level1_pos1(.p1(p_in[1]), .g1(g_in[1]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos2_outg;
	wire node_level1_pos2_outp;
	neg_operator node_level1_pos2(.p1(p_in[2]), .g1(g_in[2]), .p0(p_in[1]), .g0(g_in[1]), .gp(node_level1_pos2_outg), .pp(node_level1_pos2_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	neg_operator node_level1_pos3(.p1(p_in[3]), .g1(g_in[3]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level1_pos4_outg;
	wire node_level1_pos4_outp;
	neg_operator node_level1_pos4(.p1(p_in[4]), .g1(g_in[4]), .p0(p_in[3]), .g0(g_in[3]), .gp(node_level1_pos4_outg), .pp(node_level1_pos4_outp));
	wire node_level1_pos5_outg;
	wire node_level1_pos5_outp;
	neg_operator node_level1_pos5(.p1(p_in[5]), .g1(g_in[5]), .p0(p_in[4]), .g0(g_in[4]), .gp(node_level1_pos5_outg), .pp(node_level1_pos5_outp));
	wire node_level1_pos6_outg;
	wire node_level1_pos6_outp;
	neg_operator node_level1_pos6(.p1(p_in[6]), .g1(g_in[6]), .p0(p_in[5]), .g0(g_in[5]), .gp(node_level1_pos6_outg), .pp(node_level1_pos6_outp));
	wire node_level1_pos7_outg;
	wire node_level1_pos7_outp;
	neg_operator node_level1_pos7(.p1(p_in[7]), .g1(g_in[7]), .p0(p_in[6]), .g0(g_in[6]), .gp(node_level1_pos7_outg), .pp(node_level1_pos7_outp));
	wire node_level1_pos8_outg;
	wire node_level1_pos8_outp;
	neg_operator node_level1_pos8(.p1(p_in[8]), .g1(g_in[8]), .p0(p_in[7]), .g0(g_in[7]), .gp(node_level1_pos8_outg), .pp(node_level1_pos8_outp));
	wire node_level1_pos9_outg;
	wire node_level1_pos9_outp;
	neg_operator node_level1_pos9(.p1(p_in[9]), .g1(g_in[9]), .p0(p_in[8]), .g0(g_in[8]), .gp(node_level1_pos9_outg), .pp(node_level1_pos9_outp));
	wire node_level1_pos10_outg;
	wire node_level1_pos10_outp;
	neg_operator node_level1_pos10(.p1(p_in[10]), .g1(g_in[10]), .p0(p_in[9]), .g0(g_in[9]), .gp(node_level1_pos10_outg), .pp(node_level1_pos10_outp));
	wire node_level1_pos11_outg;
	wire node_level1_pos11_outp;
	neg_operator node_level1_pos11(.p1(p_in[11]), .g1(g_in[11]), .p0(p_in[10]), .g0(g_in[10]), .gp(node_level1_pos11_outg), .pp(node_level1_pos11_outp));
	wire node_level1_pos12_outg;
	wire node_level1_pos12_outp;
	neg_operator node_level1_pos12(.p1(p_in[12]), .g1(g_in[12]), .p0(p_in[11]), .g0(g_in[11]), .gp(node_level1_pos12_outg), .pp(node_level1_pos12_outp));
	wire node_level1_pos13_outg;
	wire node_level1_pos13_outp;
	neg_operator node_level1_pos13(.p1(p_in[13]), .g1(g_in[13]), .p0(p_in[12]), .g0(g_in[12]), .gp(node_level1_pos13_outg), .pp(node_level1_pos13_outp));
	wire node_level1_pos14_outg;
	wire node_level1_pos14_outp;
	neg_operator node_level1_pos14(.p1(p_in[14]), .g1(g_in[14]), .p0(p_in[13]), .g0(g_in[13]), .gp(node_level1_pos14_outg), .pp(node_level1_pos14_outp));
	wire node_level1_pos15_outg;
	wire node_level1_pos15_outp;
	neg_operator node_level1_pos15(.p1(p_in[15]), .g1(g_in[15]), .p0(p_in[14]), .g0(g_in[14]), .gp(node_level1_pos15_outg), .pp(node_level1_pos15_outp));
	wire node_level2_pos2_outg;
	wire node_level2_pos2_outp;
	pos_operator node_level2_pos2(.p1(node_level1_pos2_outp), .g1(node_level1_pos2_outg), .p0(~p_in[0]), .g0(~g_in[0]), .gp(node_level2_pos2_outg), .pp(node_level2_pos2_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	pos_operator node_level2_pos3(.p1(node_level1_pos3_outp), .g1(node_level1_pos3_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));
	wire node_level2_pos4_outg;
	wire node_level2_pos4_outp;
	pos_operator node_level2_pos4(.p1(node_level1_pos4_outp), .g1(node_level1_pos4_outg), .p0(node_level1_pos2_outp), .g0(node_level1_pos2_outg), .gp(node_level2_pos4_outg), .pp(node_level2_pos4_outp));
	wire node_level2_pos5_outg;
	wire node_level2_pos5_outp;
	pos_operator node_level2_pos5(.p1(node_level1_pos5_outp), .g1(node_level1_pos5_outg), .p0(node_level1_pos3_outp), .g0(node_level1_pos3_outg), .gp(node_level2_pos5_outg), .pp(node_level2_pos5_outp));
	wire node_level2_pos6_outg;
	wire node_level2_pos6_outp;
	pos_operator node_level2_pos6(.p1(node_level1_pos6_outp), .g1(node_level1_pos6_outg), .p0(node_level1_pos4_outp), .g0(node_level1_pos4_outg), .gp(node_level2_pos6_outg), .pp(node_level2_pos6_outp));
	wire node_level2_pos7_outg;
	wire node_level2_pos7_outp;
	pos_operator node_level2_pos7(.p1(node_level1_pos7_outp), .g1(node_level1_pos7_outg), .p0(node_level1_pos5_outp), .g0(node_level1_pos5_outg), .gp(node_level2_pos7_outg), .pp(node_level2_pos7_outp));
	wire node_level2_pos8_outg;
	wire node_level2_pos8_outp;
	pos_operator node_level2_pos8(.p1(node_level1_pos8_outp), .g1(node_level1_pos8_outg), .p0(node_level1_pos6_outp), .g0(node_level1_pos6_outg), .gp(node_level2_pos8_outg), .pp(node_level2_pos8_outp));
	wire node_level2_pos9_outg;
	wire node_level2_pos9_outp;
	pos_operator node_level2_pos9(.p1(node_level1_pos9_outp), .g1(node_level1_pos9_outg), .p0(node_level1_pos7_outp), .g0(node_level1_pos7_outg), .gp(node_level2_pos9_outg), .pp(node_level2_pos9_outp));
	wire node_level2_pos10_outg;
	wire node_level2_pos10_outp;
	pos_operator node_level2_pos10(.p1(node_level1_pos10_outp), .g1(node_level1_pos10_outg), .p0(node_level1_pos8_outp), .g0(node_level1_pos8_outg), .gp(node_level2_pos10_outg), .pp(node_level2_pos10_outp));
	wire node_level2_pos11_outg;
	wire node_level2_pos11_outp;
	pos_operator node_level2_pos11(.p1(node_level1_pos11_outp), .g1(node_level1_pos11_outg), .p0(node_level1_pos9_outp), .g0(node_level1_pos9_outg), .gp(node_level2_pos11_outg), .pp(node_level2_pos11_outp));
	wire node_level2_pos12_outg;
	wire node_level2_pos12_outp;
	pos_operator node_level2_pos12(.p1(node_level1_pos12_outp), .g1(node_level1_pos12_outg), .p0(node_level1_pos10_outp), .g0(node_level1_pos10_outg), .gp(node_level2_pos12_outg), .pp(node_level2_pos12_outp));
	wire node_level2_pos13_outg;
	wire node_level2_pos13_outp;
	pos_operator node_level2_pos13(.p1(node_level1_pos13_outp), .g1(node_level1_pos13_outg), .p0(node_level1_pos11_outp), .g0(node_level1_pos11_outg), .gp(node_level2_pos13_outg), .pp(node_level2_pos13_outp));
	wire node_level2_pos14_outg;
	wire node_level2_pos14_outp;
	pos_operator node_level2_pos14(.p1(node_level1_pos14_outp), .g1(node_level1_pos14_outg), .p0(node_level1_pos12_outp), .g0(node_level1_pos12_outg), .gp(node_level2_pos14_outg), .pp(node_level2_pos14_outp));
	wire node_level2_pos15_outg;
	wire node_level2_pos15_outp;
	pos_operator node_level2_pos15(.p1(node_level1_pos15_outp), .g1(node_level1_pos15_outg), .p0(node_level1_pos13_outp), .g0(node_level1_pos13_outg), .gp(node_level2_pos15_outg), .pp(node_level2_pos15_outp));
	wire node_level3_pos4_outg;
	wire node_level3_pos4_outp;
	neg_operator node_level3_pos4(.p1(node_level2_pos4_outp), .g1(node_level2_pos4_outg), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level3_pos4_outg), .pp(node_level3_pos4_outp));
	wire node_level3_pos5_outg;
	wire node_level3_pos5_outp;
	neg_operator node_level3_pos5(.p1(node_level2_pos5_outp), .g1(node_level2_pos5_outg), .p0(~node_level1_pos1_outp), .g0(~node_level1_pos1_outg), .gp(node_level3_pos5_outg), .pp(node_level3_pos5_outp));
	wire node_level3_pos6_outg;
	wire node_level3_pos6_outp;
	neg_operator node_level3_pos6(.p1(node_level2_pos6_outp), .g1(node_level2_pos6_outg), .p0(node_level2_pos2_outp), .g0(node_level2_pos2_outg), .gp(node_level3_pos6_outg), .pp(node_level3_pos6_outp));
	wire node_level3_pos7_outg;
	wire node_level3_pos7_outp;
	neg_operator node_level3_pos7(.p1(node_level2_pos7_outp), .g1(node_level2_pos7_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos7_outg), .pp(node_level3_pos7_outp));
	wire node_level3_pos8_outg;
	wire node_level3_pos8_outp;
	neg_operator node_level3_pos8(.p1(node_level2_pos8_outp), .g1(node_level2_pos8_outg), .p0(node_level2_pos4_outp), .g0(node_level2_pos4_outg), .gp(node_level3_pos8_outg), .pp(node_level3_pos8_outp));
	wire node_level3_pos9_outg;
	wire node_level3_pos9_outp;
	neg_operator node_level3_pos9(.p1(node_level2_pos9_outp), .g1(node_level2_pos9_outg), .p0(node_level2_pos5_outp), .g0(node_level2_pos5_outg), .gp(node_level3_pos9_outg), .pp(node_level3_pos9_outp));
	wire node_level3_pos10_outg;
	wire node_level3_pos10_outp;
	neg_operator node_level3_pos10(.p1(node_level2_pos10_outp), .g1(node_level2_pos10_outg), .p0(node_level2_pos6_outp), .g0(node_level2_pos6_outg), .gp(node_level3_pos10_outg), .pp(node_level3_pos10_outp));
	wire node_level3_pos11_outg;
	wire node_level3_pos11_outp;
	neg_operator node_level3_pos11(.p1(node_level2_pos11_outp), .g1(node_level2_pos11_outg), .p0(node_level2_pos7_outp), .g0(node_level2_pos7_outg), .gp(node_level3_pos11_outg), .pp(node_level3_pos11_outp));
	wire node_level3_pos12_outg;
	wire node_level3_pos12_outp;
	neg_operator node_level3_pos12(.p1(node_level2_pos12_outp), .g1(node_level2_pos12_outg), .p0(node_level2_pos8_outp), .g0(node_level2_pos8_outg), .gp(node_level3_pos12_outg), .pp(node_level3_pos12_outp));
	wire node_level3_pos13_outg;
	wire node_level3_pos13_outp;
	neg_operator node_level3_pos13(.p1(node_level2_pos13_outp), .g1(node_level2_pos13_outg), .p0(node_level2_pos9_outp), .g0(node_level2_pos9_outg), .gp(node_level3_pos13_outg), .pp(node_level3_pos13_outp));
	wire node_level3_pos14_outg;
	wire node_level3_pos14_outp;
	neg_operator node_level3_pos14(.p1(node_level2_pos14_outp), .g1(node_level2_pos14_outg), .p0(node_level2_pos10_outp), .g0(node_level2_pos10_outg), .gp(node_level3_pos14_outg), .pp(node_level3_pos14_outp));
	wire node_level3_pos15_outg;
	wire node_level3_pos15_outp;
	neg_operator node_level3_pos15(.p1(node_level2_pos15_outp), .g1(node_level2_pos15_outg), .p0(node_level2_pos11_outp), .g0(node_level2_pos11_outg), .gp(node_level3_pos15_outg), .pp(node_level3_pos15_outp));
	wire node_level4_pos8_outg;
	wire node_level4_pos8_outp;
	pos_operator node_level4_pos8(.p1(node_level3_pos8_outp), .g1(node_level3_pos8_outg), .p0(~p_in[0]), .g0(~g_in[0]), .gp(node_level4_pos8_outg), .pp(node_level4_pos8_outp));
	wire node_level4_pos9_outg;
	wire node_level4_pos9_outp;
	pos_operator node_level4_pos9(.p1(node_level3_pos9_outp), .g1(node_level3_pos9_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level4_pos9_outg), .pp(node_level4_pos9_outp));
	wire node_level4_pos10_outg;
	wire node_level4_pos10_outp;
	pos_operator node_level4_pos10(.p1(node_level3_pos10_outp), .g1(node_level3_pos10_outg), .p0(~node_level2_pos2_outp), .g0(~node_level2_pos2_outg), .gp(node_level4_pos10_outg), .pp(node_level4_pos10_outp));
	wire node_level4_pos11_outg;
	wire node_level4_pos11_outp;
	pos_operator node_level4_pos11(.p1(node_level3_pos11_outp), .g1(node_level3_pos11_outg), .p0(~node_level2_pos3_outp), .g0(~node_level2_pos3_outg), .gp(node_level4_pos11_outg), .pp(node_level4_pos11_outp));
	wire node_level4_pos12_outg;
	wire node_level4_pos12_outp;
	pos_operator node_level4_pos12(.p1(node_level3_pos12_outp), .g1(node_level3_pos12_outg), .p0(node_level3_pos4_outp), .g0(node_level3_pos4_outg), .gp(node_level4_pos12_outg), .pp(node_level4_pos12_outp));
	wire node_level4_pos13_outg;
	wire node_level4_pos13_outp;
	pos_operator node_level4_pos13(.p1(node_level3_pos13_outp), .g1(node_level3_pos13_outg), .p0(node_level3_pos5_outp), .g0(node_level3_pos5_outg), .gp(node_level4_pos13_outg), .pp(node_level4_pos13_outp));
	wire node_level4_pos14_outg;
	wire node_level4_pos14_outp;
	pos_operator node_level4_pos14(.p1(node_level3_pos14_outp), .g1(node_level3_pos14_outg), .p0(node_level3_pos6_outp), .g0(node_level3_pos6_outg), .gp(node_level4_pos14_outg), .pp(node_level4_pos14_outp));
	wire node_level4_pos15_outg;
	wire node_level4_pos15_outp;
	pos_operator node_level4_pos15(.p1(node_level3_pos15_outp), .g1(node_level3_pos15_outg), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level4_pos15_outg), .pp(node_level4_pos15_outp));


	assign s[0] = p_in[0] ^ cin;
	assign s[1] = p_in[1] ^ g_in[0];
	assign s[2] = p_in[2] ^ ~node_level1_pos1_outg;
	assign s[3] = p_in[3] ^ node_level2_pos2_outg;
	assign s[4] = p_in[4] ^ node_level2_pos3_outg;
	assign s[5] = p_in[5] ^ ~node_level3_pos4_outg;
	assign s[6] = p_in[6] ^ ~node_level3_pos5_outg;
	assign s[7] = p_in[7] ^ ~node_level3_pos6_outg;
	assign s[8] = p_in[8] ^ ~node_level3_pos7_outg;
	assign s[9] = p_in[9] ^ node_level4_pos8_outg;
	assign s[10] = p_in[10] ^ node_level4_pos9_outg;
	assign s[11] = p_in[11] ^ node_level4_pos10_outg;
	assign s[12] = p_in[12] ^ node_level4_pos11_outg;
	assign s[13] = p_in[13] ^ node_level4_pos12_outg;
	assign s[14] = p_in[14] ^ node_level4_pos13_outg;
	assign s[15] = p_in[15] ^ node_level4_pos14_outg;
	assign cout = (x1[15] & x2[15]) | (~s[15] & (x1[15] | x2[15]));
endmodule


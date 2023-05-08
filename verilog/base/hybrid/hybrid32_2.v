`ifndef CARRY_OPERATOR
`include "carry_operator.v"
`endif
`ifndef NEG_CARRY_OPERATOR
`include "neg_operator.v"
`endif
`ifndef POS_CARRY_OPERATOR
`include "pos_operator.v"
`endif
// number of levels: 8
// number of nodes: 63
// NAND count: 63, AND count: 42
// NOR count: 63, OR count: 21
// NOT count: 41, Transistor count: 964
module hybrid32_2(x1, x2, s, cin, cout);
	input[31:0]x1;
	input[31:0]x2;
	input cin;
	wire[31:0]p_in;
	wire[31:0]g_in;
	output[31:0]s;
	output cout;

	assign p_in = x1 ^ x2;
	assign g_in[31:1] = x1[31:1] & x2[31:1];
	assign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	neg_operator node_level1_pos1(.p1(p_in[0]), .g1(g_in[0]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	neg_operator node_level1_pos3(.p1(p_in[2]), .g1(g_in[2]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level1_pos5_outg;
	wire node_level1_pos5_outp;
	neg_operator node_level1_pos5(.p1(p_in[4]), .g1(g_in[4]), .p0(p_in[4]), .g0(g_in[4]), .gp(node_level1_pos5_outg), .pp(node_level1_pos5_outp));
	wire node_level1_pos7_outg;
	wire node_level1_pos7_outp;
	neg_operator node_level1_pos7(.p1(p_in[6]), .g1(g_in[6]), .p0(p_in[6]), .g0(g_in[6]), .gp(node_level1_pos7_outg), .pp(node_level1_pos7_outp));
	wire node_level1_pos9_outg;
	wire node_level1_pos9_outp;
	neg_operator node_level1_pos9(.p1(p_in[8]), .g1(g_in[8]), .p0(p_in[8]), .g0(g_in[8]), .gp(node_level1_pos9_outg), .pp(node_level1_pos9_outp));
	wire node_level1_pos11_outg;
	wire node_level1_pos11_outp;
	neg_operator node_level1_pos11(.p1(p_in[10]), .g1(g_in[10]), .p0(p_in[10]), .g0(g_in[10]), .gp(node_level1_pos11_outg), .pp(node_level1_pos11_outp));
	wire node_level1_pos13_outg;
	wire node_level1_pos13_outp;
	neg_operator node_level1_pos13(.p1(p_in[12]), .g1(g_in[12]), .p0(p_in[12]), .g0(g_in[12]), .gp(node_level1_pos13_outg), .pp(node_level1_pos13_outp));
	wire node_level1_pos15_outg;
	wire node_level1_pos15_outp;
	neg_operator node_level1_pos15(.p1(p_in[14]), .g1(g_in[14]), .p0(p_in[14]), .g0(g_in[14]), .gp(node_level1_pos15_outg), .pp(node_level1_pos15_outp));
	wire node_level1_pos17_outg;
	wire node_level1_pos17_outp;
	neg_operator node_level1_pos17(.p1(p_in[16]), .g1(g_in[16]), .p0(p_in[16]), .g0(g_in[16]), .gp(node_level1_pos17_outg), .pp(node_level1_pos17_outp));
	wire node_level1_pos19_outg;
	wire node_level1_pos19_outp;
	neg_operator node_level1_pos19(.p1(p_in[18]), .g1(g_in[18]), .p0(p_in[18]), .g0(g_in[18]), .gp(node_level1_pos19_outg), .pp(node_level1_pos19_outp));
	wire node_level1_pos21_outg;
	wire node_level1_pos21_outp;
	neg_operator node_level1_pos21(.p1(p_in[20]), .g1(g_in[20]), .p0(p_in[20]), .g0(g_in[20]), .gp(node_level1_pos21_outg), .pp(node_level1_pos21_outp));
	wire node_level1_pos23_outg;
	wire node_level1_pos23_outp;
	neg_operator node_level1_pos23(.p1(p_in[22]), .g1(g_in[22]), .p0(p_in[22]), .g0(g_in[22]), .gp(node_level1_pos23_outg), .pp(node_level1_pos23_outp));
	wire node_level1_pos25_outg;
	wire node_level1_pos25_outp;
	neg_operator node_level1_pos25(.p1(p_in[24]), .g1(g_in[24]), .p0(p_in[24]), .g0(g_in[24]), .gp(node_level1_pos25_outg), .pp(node_level1_pos25_outp));
	wire node_level1_pos27_outg;
	wire node_level1_pos27_outp;
	neg_operator node_level1_pos27(.p1(p_in[26]), .g1(g_in[26]), .p0(p_in[26]), .g0(g_in[26]), .gp(node_level1_pos27_outg), .pp(node_level1_pos27_outp));
	wire node_level1_pos29_outg;
	wire node_level1_pos29_outp;
	neg_operator node_level1_pos29(.p1(p_in[28]), .g1(g_in[28]), .p0(p_in[28]), .g0(g_in[28]), .gp(node_level1_pos29_outg), .pp(node_level1_pos29_outp));
	wire node_level1_pos31_outg;
	wire node_level1_pos31_outp;
	neg_operator node_level1_pos31(.p1(p_in[30]), .g1(g_in[30]), .p0(p_in[30]), .g0(g_in[30]), .gp(node_level1_pos31_outg), .pp(node_level1_pos31_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	pos_operator node_level2_pos3(.p1(node_level1_pos1_outp), .g1(node_level1_pos1_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));
	wire node_level2_pos7_outg;
	wire node_level2_pos7_outp;
	pos_operator node_level2_pos7(.p1(node_level1_pos5_outp), .g1(node_level1_pos5_outg), .p0(node_level1_pos5_outp), .g0(node_level1_pos5_outg), .gp(node_level2_pos7_outg), .pp(node_level2_pos7_outp));
	wire node_level2_pos11_outg;
	wire node_level2_pos11_outp;
	pos_operator node_level2_pos11(.p1(node_level1_pos9_outp), .g1(node_level1_pos9_outg), .p0(node_level1_pos9_outp), .g0(node_level1_pos9_outg), .gp(node_level2_pos11_outg), .pp(node_level2_pos11_outp));
	wire node_level2_pos15_outg;
	wire node_level2_pos15_outp;
	pos_operator node_level2_pos15(.p1(node_level1_pos13_outp), .g1(node_level1_pos13_outg), .p0(node_level1_pos13_outp), .g0(node_level1_pos13_outg), .gp(node_level2_pos15_outg), .pp(node_level2_pos15_outp));
	wire node_level2_pos19_outg;
	wire node_level2_pos19_outp;
	pos_operator node_level2_pos19(.p1(node_level1_pos17_outp), .g1(node_level1_pos17_outg), .p0(node_level1_pos17_outp), .g0(node_level1_pos17_outg), .gp(node_level2_pos19_outg), .pp(node_level2_pos19_outp));
	wire node_level2_pos23_outg;
	wire node_level2_pos23_outp;
	pos_operator node_level2_pos23(.p1(node_level1_pos21_outp), .g1(node_level1_pos21_outg), .p0(node_level1_pos21_outp), .g0(node_level1_pos21_outg), .gp(node_level2_pos23_outg), .pp(node_level2_pos23_outp));
	wire node_level2_pos27_outg;
	wire node_level2_pos27_outp;
	pos_operator node_level2_pos27(.p1(node_level1_pos25_outp), .g1(node_level1_pos25_outg), .p0(node_level1_pos25_outp), .g0(node_level1_pos25_outg), .gp(node_level2_pos27_outg), .pp(node_level2_pos27_outp));
	wire node_level2_pos31_outg;
	wire node_level2_pos31_outp;
	pos_operator node_level2_pos31(.p1(node_level1_pos29_outp), .g1(node_level1_pos29_outg), .p0(node_level1_pos29_outp), .g0(node_level1_pos29_outg), .gp(node_level2_pos31_outg), .pp(node_level2_pos31_outp));
	wire node_level3_pos7_outg;
	wire node_level3_pos7_outp;
	neg_operator node_level3_pos7(.p1(node_level2_pos3_outp), .g1(node_level2_pos3_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos7_outg), .pp(node_level3_pos7_outp));
	wire node_level3_pos11_outg;
	wire node_level3_pos11_outp;
	neg_operator node_level3_pos11(.p1(node_level2_pos7_outp), .g1(node_level2_pos7_outg), .p0(node_level2_pos7_outp), .g0(node_level2_pos7_outg), .gp(node_level3_pos11_outg), .pp(node_level3_pos11_outp));
	wire node_level3_pos15_outg;
	wire node_level3_pos15_outp;
	neg_operator node_level3_pos15(.p1(node_level2_pos11_outp), .g1(node_level2_pos11_outg), .p0(node_level2_pos11_outp), .g0(node_level2_pos11_outg), .gp(node_level3_pos15_outg), .pp(node_level3_pos15_outp));
	wire node_level3_pos19_outg;
	wire node_level3_pos19_outp;
	neg_operator node_level3_pos19(.p1(node_level2_pos15_outp), .g1(node_level2_pos15_outg), .p0(node_level2_pos15_outp), .g0(node_level2_pos15_outg), .gp(node_level3_pos19_outg), .pp(node_level3_pos19_outp));
	wire node_level3_pos23_outg;
	wire node_level3_pos23_outp;
	neg_operator node_level3_pos23(.p1(node_level2_pos19_outp), .g1(node_level2_pos19_outg), .p0(node_level2_pos19_outp), .g0(node_level2_pos19_outg), .gp(node_level3_pos23_outg), .pp(node_level3_pos23_outp));
	wire node_level3_pos27_outg;
	wire node_level3_pos27_outp;
	neg_operator node_level3_pos27(.p1(node_level2_pos23_outp), .g1(node_level2_pos23_outg), .p0(node_level2_pos23_outp), .g0(node_level2_pos23_outg), .gp(node_level3_pos27_outg), .pp(node_level3_pos27_outp));
	wire node_level3_pos31_outg;
	wire node_level3_pos31_outp;
	neg_operator node_level3_pos31(.p1(node_level2_pos27_outp), .g1(node_level2_pos27_outg), .p0(node_level2_pos27_outp), .g0(node_level2_pos27_outg), .gp(node_level3_pos31_outg), .pp(node_level3_pos31_outp));
	wire node_level4_pos11_outg;
	wire node_level4_pos11_outp;
	pos_operator node_level4_pos11(.p1(~node_level2_pos3_outp), .g1(~node_level2_pos3_outg), .p0(~node_level2_pos3_outp), .g0(~node_level2_pos3_outg), .gp(node_level4_pos11_outg), .pp(node_level4_pos11_outp));
	wire node_level4_pos15_outg;
	wire node_level4_pos15_outp;
	pos_operator node_level4_pos15(.p1(node_level3_pos7_outp), .g1(node_level3_pos7_outg), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level4_pos15_outg), .pp(node_level4_pos15_outp));
	wire node_level4_pos19_outg;
	wire node_level4_pos19_outp;
	pos_operator node_level4_pos19(.p1(node_level3_pos11_outp), .g1(node_level3_pos11_outg), .p0(node_level3_pos11_outp), .g0(node_level3_pos11_outg), .gp(node_level4_pos19_outg), .pp(node_level4_pos19_outp));
	wire node_level4_pos23_outg;
	wire node_level4_pos23_outp;
	pos_operator node_level4_pos23(.p1(node_level3_pos15_outp), .g1(node_level3_pos15_outg), .p0(node_level3_pos15_outp), .g0(node_level3_pos15_outg), .gp(node_level4_pos23_outg), .pp(node_level4_pos23_outp));
	wire node_level4_pos27_outg;
	wire node_level4_pos27_outp;
	pos_operator node_level4_pos27(.p1(node_level3_pos19_outp), .g1(node_level3_pos19_outg), .p0(node_level3_pos19_outp), .g0(node_level3_pos19_outg), .gp(node_level4_pos27_outg), .pp(node_level4_pos27_outp));
	wire node_level4_pos31_outg;
	wire node_level4_pos31_outp;
	pos_operator node_level4_pos31(.p1(node_level3_pos23_outp), .g1(node_level3_pos23_outg), .p0(node_level3_pos23_outp), .g0(node_level3_pos23_outg), .gp(node_level4_pos31_outg), .pp(node_level4_pos31_outp));
	wire node_level5_pos19_outg;
	wire node_level5_pos19_outp;
	neg_operator node_level5_pos19(.p1(node_level2_pos3_outp), .g1(node_level2_pos3_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level5_pos19_outg), .pp(node_level5_pos19_outp));
	wire node_level5_pos23_outg;
	wire node_level5_pos23_outp;
	neg_operator node_level5_pos23(.p1(~node_level3_pos7_outp), .g1(~node_level3_pos7_outg), .p0(~node_level3_pos7_outp), .g0(~node_level3_pos7_outg), .gp(node_level5_pos23_outg), .pp(node_level5_pos23_outp));
	wire node_level5_pos27_outg;
	wire node_level5_pos27_outp;
	neg_operator node_level5_pos27(.p1(node_level4_pos11_outp), .g1(node_level4_pos11_outg), .p0(node_level4_pos11_outp), .g0(node_level4_pos11_outg), .gp(node_level5_pos27_outg), .pp(node_level5_pos27_outp));
	wire node_level5_pos31_outg;
	wire node_level5_pos31_outp;
	neg_operator node_level5_pos31(.p1(node_level4_pos15_outp), .g1(node_level4_pos15_outg), .p0(node_level4_pos15_outp), .g0(node_level4_pos15_outg), .gp(node_level5_pos31_outg), .pp(node_level5_pos31_outp));
	wire node_level6_pos5_outg;
	wire node_level6_pos5_outp;
	pos_operator node_level6_pos5(.p1(~node_level2_pos3_outp), .g1(~node_level2_pos3_outg), .p0(~node_level2_pos3_outp), .g0(~node_level2_pos3_outg), .gp(node_level6_pos5_outg), .pp(node_level6_pos5_outp));
	wire node_level6_pos9_outg;
	wire node_level6_pos9_outp;
	pos_operator node_level6_pos9(.p1(node_level3_pos7_outp), .g1(node_level3_pos7_outg), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level6_pos9_outg), .pp(node_level6_pos9_outp));
	wire node_level6_pos13_outg;
	wire node_level6_pos13_outp;
	pos_operator node_level6_pos13(.p1(~node_level4_pos11_outp), .g1(~node_level4_pos11_outg), .p0(~node_level4_pos11_outp), .g0(~node_level4_pos11_outg), .gp(node_level6_pos13_outg), .pp(node_level6_pos13_outp));
	wire node_level6_pos17_outg;
	wire node_level6_pos17_outp;
	pos_operator node_level6_pos17(.p1(~node_level4_pos15_outp), .g1(~node_level4_pos15_outg), .p0(~node_level4_pos15_outp), .g0(~node_level4_pos15_outg), .gp(node_level6_pos17_outg), .pp(node_level6_pos17_outp));
	wire node_level6_pos21_outg;
	wire node_level6_pos21_outp;
	pos_operator node_level6_pos21(.p1(node_level5_pos19_outp), .g1(node_level5_pos19_outg), .p0(node_level5_pos19_outp), .g0(node_level5_pos19_outg), .gp(node_level6_pos21_outg), .pp(node_level6_pos21_outp));
	wire node_level6_pos25_outg;
	wire node_level6_pos25_outp;
	pos_operator node_level6_pos25(.p1(node_level5_pos23_outp), .g1(node_level5_pos23_outg), .p0(node_level5_pos23_outp), .g0(node_level5_pos23_outg), .gp(node_level6_pos25_outg), .pp(node_level6_pos25_outp));
	wire node_level6_pos29_outg;
	wire node_level6_pos29_outp;
	pos_operator node_level6_pos29(.p1(node_level5_pos27_outp), .g1(node_level5_pos27_outg), .p0(node_level5_pos27_outp), .g0(node_level5_pos27_outg), .gp(node_level6_pos29_outg), .pp(node_level6_pos29_outp));
	wire node_level7_pos2_outg;
	wire node_level7_pos2_outp;
	neg_operator node_level7_pos2(.p1(p_in[1]), .g1(g_in[1]), .p0(~node_level1_pos1_outp), .g0(~node_level1_pos1_outg), .gp(node_level7_pos2_outg), .pp(node_level7_pos2_outp));
	wire node_level7_pos4_outg;
	wire node_level7_pos4_outp;
	neg_operator node_level7_pos4(.p1(p_in[3]), .g1(g_in[3]), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level7_pos4_outg), .pp(node_level7_pos4_outp));
	wire node_level7_pos6_outg;
	wire node_level7_pos6_outp;
	neg_operator node_level7_pos6(.p1(p_in[5]), .g1(g_in[5]), .p0(node_level6_pos5_outp), .g0(node_level6_pos5_outg), .gp(node_level7_pos6_outg), .pp(node_level7_pos6_outp));
	wire node_level7_pos8_outg;
	wire node_level7_pos8_outp;
	neg_operator node_level7_pos8(.p1(p_in[7]), .g1(g_in[7]), .p0(~node_level3_pos7_outp), .g0(~node_level3_pos7_outg), .gp(node_level7_pos8_outg), .pp(node_level7_pos8_outp));
	wire node_level7_pos10_outg;
	wire node_level7_pos10_outp;
	neg_operator node_level7_pos10(.p1(p_in[9]), .g1(g_in[9]), .p0(node_level6_pos9_outp), .g0(node_level6_pos9_outg), .gp(node_level7_pos10_outg), .pp(node_level7_pos10_outp));
	wire node_level7_pos12_outg;
	wire node_level7_pos12_outp;
	neg_operator node_level7_pos12(.p1(p_in[11]), .g1(g_in[11]), .p0(node_level4_pos11_outp), .g0(node_level4_pos11_outg), .gp(node_level7_pos12_outg), .pp(node_level7_pos12_outp));
	wire node_level7_pos14_outg;
	wire node_level7_pos14_outp;
	neg_operator node_level7_pos14(.p1(p_in[13]), .g1(g_in[13]), .p0(node_level6_pos13_outp), .g0(node_level6_pos13_outg), .gp(node_level7_pos14_outg), .pp(node_level7_pos14_outp));
	wire node_level7_pos16_outg;
	wire node_level7_pos16_outp;
	neg_operator node_level7_pos16(.p1(p_in[15]), .g1(g_in[15]), .p0(node_level4_pos15_outp), .g0(node_level4_pos15_outg), .gp(node_level7_pos16_outg), .pp(node_level7_pos16_outp));
	wire node_level7_pos18_outg;
	wire node_level7_pos18_outp;
	neg_operator node_level7_pos18(.p1(p_in[17]), .g1(g_in[17]), .p0(node_level6_pos17_outp), .g0(node_level6_pos17_outg), .gp(node_level7_pos18_outg), .pp(node_level7_pos18_outp));
	wire node_level7_pos20_outg;
	wire node_level7_pos20_outp;
	neg_operator node_level7_pos20(.p1(p_in[19]), .g1(g_in[19]), .p0(~node_level5_pos19_outp), .g0(~node_level5_pos19_outg), .gp(node_level7_pos20_outg), .pp(node_level7_pos20_outp));
	wire node_level7_pos22_outg;
	wire node_level7_pos22_outp;
	neg_operator node_level7_pos22(.p1(p_in[21]), .g1(g_in[21]), .p0(node_level6_pos21_outp), .g0(node_level6_pos21_outg), .gp(node_level7_pos22_outg), .pp(node_level7_pos22_outp));
	wire node_level7_pos24_outg;
	wire node_level7_pos24_outp;
	neg_operator node_level7_pos24(.p1(p_in[23]), .g1(g_in[23]), .p0(~node_level5_pos23_outp), .g0(~node_level5_pos23_outg), .gp(node_level7_pos24_outg), .pp(node_level7_pos24_outp));
	wire node_level7_pos26_outg;
	wire node_level7_pos26_outp;
	neg_operator node_level7_pos26(.p1(p_in[25]), .g1(g_in[25]), .p0(node_level6_pos25_outp), .g0(node_level6_pos25_outg), .gp(node_level7_pos26_outg), .pp(node_level7_pos26_outp));
	wire node_level7_pos28_outg;
	wire node_level7_pos28_outp;
	neg_operator node_level7_pos28(.p1(p_in[27]), .g1(g_in[27]), .p0(~node_level5_pos27_outp), .g0(~node_level5_pos27_outg), .gp(node_level7_pos28_outg), .pp(node_level7_pos28_outp));
	wire node_level7_pos30_outg;
	wire node_level7_pos30_outp;
	neg_operator node_level7_pos30(.p1(p_in[29]), .g1(g_in[29]), .p0(node_level6_pos29_outp), .g0(node_level6_pos29_outg), .gp(node_level7_pos30_outg), .pp(node_level7_pos30_outp));


	assign s[0] = p_in[0] ^ cin;
	assign s[1] = p_in[1] ^ g_in[0];
	assign s[2] = p_in[2] ^ ~node_level1_pos1_outg;
	assign s[3] = p_in[3] ^ ~node_level7_pos2_outg;
	assign s[4] = p_in[4] ^ node_level2_pos3_outg;
	assign s[5] = p_in[5] ^ ~node_level7_pos4_outg;
	assign s[6] = p_in[6] ^ node_level6_pos5_outg;
	assign s[7] = p_in[7] ^ ~node_level7_pos6_outg;
	assign s[8] = p_in[8] ^ ~node_level3_pos7_outg;
	assign s[9] = p_in[9] ^ ~node_level7_pos8_outg;
	assign s[10] = p_in[10] ^ node_level6_pos9_outg;
	assign s[11] = p_in[11] ^ ~node_level7_pos10_outg;
	assign s[12] = p_in[12] ^ node_level4_pos11_outg;
	assign s[13] = p_in[13] ^ ~node_level7_pos12_outg;
	assign s[14] = p_in[14] ^ node_level6_pos13_outg;
	assign s[15] = p_in[15] ^ ~node_level7_pos14_outg;
	assign s[16] = p_in[16] ^ node_level4_pos15_outg;
	assign s[17] = p_in[17] ^ ~node_level7_pos16_outg;
	assign s[18] = p_in[18] ^ node_level6_pos17_outg;
	assign s[19] = p_in[19] ^ ~node_level7_pos18_outg;
	assign s[20] = p_in[20] ^ ~node_level5_pos19_outg;
	assign s[21] = p_in[21] ^ ~node_level7_pos20_outg;
	assign s[22] = p_in[22] ^ node_level6_pos21_outg;
	assign s[23] = p_in[23] ^ ~node_level7_pos22_outg;
	assign s[24] = p_in[24] ^ ~node_level5_pos23_outg;
	assign s[25] = p_in[25] ^ ~node_level7_pos24_outg;
	assign s[26] = p_in[26] ^ node_level6_pos25_outg;
	assign s[27] = p_in[27] ^ ~node_level7_pos26_outg;
	assign s[28] = p_in[28] ^ ~node_level5_pos27_outg;
	assign s[29] = p_in[29] ^ ~node_level7_pos28_outg;
	assign s[30] = p_in[30] ^ node_level6_pos29_outg;
	assign s[31] = p_in[31] ^ ~node_level7_pos30_outg;
	assign cout = (x1[31] & x2[31]) | (~s[31] & (x1[31] | x2[31]));
endmodule


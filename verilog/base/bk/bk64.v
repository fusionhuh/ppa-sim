`ifndef CARRY_OPERATOR
`include "carry_operator.v"
`endif
`ifndef NEG_CARRY_OPERATOR
`include "neg_operator.v"
`endif
`ifndef POS_CARRY_OPERATOR
`include "pos_operator.v"
`endif
// number of levels: 11
// number of nodes: 120
// AND count: 60, NAND count: 120
// OR count: 60, NOR count: 120
// NOT count: 114
// Transistor count: 1908
module bkadder64(x1, x2, s);
	input[63:0]x1;
	input[63:0]x2;
	output[63:0]s;
	wire[63:0]p_in = x1 ^ x2;
	wire[63:0]g_in = x1 & x2;
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
	wire node_level1_pos33_outg;
	wire node_level1_pos33_outp;
	neg_operator node_level1_pos33(.p1(p_in[32]), .g1(g_in[32]), .p0(p_in[32]), .g0(g_in[32]), .gp(node_level1_pos33_outg), .pp(node_level1_pos33_outp));
	wire node_level1_pos35_outg;
	wire node_level1_pos35_outp;
	neg_operator node_level1_pos35(.p1(p_in[34]), .g1(g_in[34]), .p0(p_in[34]), .g0(g_in[34]), .gp(node_level1_pos35_outg), .pp(node_level1_pos35_outp));
	wire node_level1_pos37_outg;
	wire node_level1_pos37_outp;
	neg_operator node_level1_pos37(.p1(p_in[36]), .g1(g_in[36]), .p0(p_in[36]), .g0(g_in[36]), .gp(node_level1_pos37_outg), .pp(node_level1_pos37_outp));
	wire node_level1_pos39_outg;
	wire node_level1_pos39_outp;
	neg_operator node_level1_pos39(.p1(p_in[38]), .g1(g_in[38]), .p0(p_in[38]), .g0(g_in[38]), .gp(node_level1_pos39_outg), .pp(node_level1_pos39_outp));
	wire node_level1_pos41_outg;
	wire node_level1_pos41_outp;
	neg_operator node_level1_pos41(.p1(p_in[40]), .g1(g_in[40]), .p0(p_in[40]), .g0(g_in[40]), .gp(node_level1_pos41_outg), .pp(node_level1_pos41_outp));
	wire node_level1_pos43_outg;
	wire node_level1_pos43_outp;
	neg_operator node_level1_pos43(.p1(p_in[42]), .g1(g_in[42]), .p0(p_in[42]), .g0(g_in[42]), .gp(node_level1_pos43_outg), .pp(node_level1_pos43_outp));
	wire node_level1_pos45_outg;
	wire node_level1_pos45_outp;
	neg_operator node_level1_pos45(.p1(p_in[44]), .g1(g_in[44]), .p0(p_in[44]), .g0(g_in[44]), .gp(node_level1_pos45_outg), .pp(node_level1_pos45_outp));
	wire node_level1_pos47_outg;
	wire node_level1_pos47_outp;
	neg_operator node_level1_pos47(.p1(p_in[46]), .g1(g_in[46]), .p0(p_in[46]), .g0(g_in[46]), .gp(node_level1_pos47_outg), .pp(node_level1_pos47_outp));
	wire node_level1_pos49_outg;
	wire node_level1_pos49_outp;
	neg_operator node_level1_pos49(.p1(p_in[48]), .g1(g_in[48]), .p0(p_in[48]), .g0(g_in[48]), .gp(node_level1_pos49_outg), .pp(node_level1_pos49_outp));
	wire node_level1_pos51_outg;
	wire node_level1_pos51_outp;
	neg_operator node_level1_pos51(.p1(p_in[50]), .g1(g_in[50]), .p0(p_in[50]), .g0(g_in[50]), .gp(node_level1_pos51_outg), .pp(node_level1_pos51_outp));
	wire node_level1_pos53_outg;
	wire node_level1_pos53_outp;
	neg_operator node_level1_pos53(.p1(p_in[52]), .g1(g_in[52]), .p0(p_in[52]), .g0(g_in[52]), .gp(node_level1_pos53_outg), .pp(node_level1_pos53_outp));
	wire node_level1_pos55_outg;
	wire node_level1_pos55_outp;
	neg_operator node_level1_pos55(.p1(p_in[54]), .g1(g_in[54]), .p0(p_in[54]), .g0(g_in[54]), .gp(node_level1_pos55_outg), .pp(node_level1_pos55_outp));
	wire node_level1_pos57_outg;
	wire node_level1_pos57_outp;
	neg_operator node_level1_pos57(.p1(p_in[56]), .g1(g_in[56]), .p0(p_in[56]), .g0(g_in[56]), .gp(node_level1_pos57_outg), .pp(node_level1_pos57_outp));
	wire node_level1_pos59_outg;
	wire node_level1_pos59_outp;
	neg_operator node_level1_pos59(.p1(p_in[58]), .g1(g_in[58]), .p0(p_in[58]), .g0(g_in[58]), .gp(node_level1_pos59_outg), .pp(node_level1_pos59_outp));
	wire node_level1_pos61_outg;
	wire node_level1_pos61_outp;
	neg_operator node_level1_pos61(.p1(p_in[60]), .g1(g_in[60]), .p0(p_in[60]), .g0(g_in[60]), .gp(node_level1_pos61_outg), .pp(node_level1_pos61_outp));
	wire node_level1_pos63_outg;
	wire node_level1_pos63_outp;
	neg_operator node_level1_pos63(.p1(p_in[62]), .g1(g_in[62]), .p0(p_in[62]), .g0(g_in[62]), .gp(node_level1_pos63_outg), .pp(node_level1_pos63_outp));
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
	wire node_level2_pos35_outg;
	wire node_level2_pos35_outp;
	pos_operator node_level2_pos35(.p1(node_level1_pos33_outp), .g1(node_level1_pos33_outg), .p0(node_level1_pos33_outp), .g0(node_level1_pos33_outg), .gp(node_level2_pos35_outg), .pp(node_level2_pos35_outp));
	wire node_level2_pos39_outg;
	wire node_level2_pos39_outp;
	pos_operator node_level2_pos39(.p1(node_level1_pos37_outp), .g1(node_level1_pos37_outg), .p0(node_level1_pos37_outp), .g0(node_level1_pos37_outg), .gp(node_level2_pos39_outg), .pp(node_level2_pos39_outp));
	wire node_level2_pos43_outg;
	wire node_level2_pos43_outp;
	pos_operator node_level2_pos43(.p1(node_level1_pos41_outp), .g1(node_level1_pos41_outg), .p0(node_level1_pos41_outp), .g0(node_level1_pos41_outg), .gp(node_level2_pos43_outg), .pp(node_level2_pos43_outp));
	wire node_level2_pos47_outg;
	wire node_level2_pos47_outp;
	pos_operator node_level2_pos47(.p1(node_level1_pos45_outp), .g1(node_level1_pos45_outg), .p0(node_level1_pos45_outp), .g0(node_level1_pos45_outg), .gp(node_level2_pos47_outg), .pp(node_level2_pos47_outp));
	wire node_level2_pos51_outg;
	wire node_level2_pos51_outp;
	pos_operator node_level2_pos51(.p1(node_level1_pos49_outp), .g1(node_level1_pos49_outg), .p0(node_level1_pos49_outp), .g0(node_level1_pos49_outg), .gp(node_level2_pos51_outg), .pp(node_level2_pos51_outp));
	wire node_level2_pos55_outg;
	wire node_level2_pos55_outp;
	pos_operator node_level2_pos55(.p1(node_level1_pos53_outp), .g1(node_level1_pos53_outg), .p0(node_level1_pos53_outp), .g0(node_level1_pos53_outg), .gp(node_level2_pos55_outg), .pp(node_level2_pos55_outp));
	wire node_level2_pos59_outg;
	wire node_level2_pos59_outp;
	pos_operator node_level2_pos59(.p1(node_level1_pos57_outp), .g1(node_level1_pos57_outg), .p0(node_level1_pos57_outp), .g0(node_level1_pos57_outg), .gp(node_level2_pos59_outg), .pp(node_level2_pos59_outp));
	wire node_level2_pos63_outg;
	wire node_level2_pos63_outp;
	pos_operator node_level2_pos63(.p1(node_level1_pos61_outp), .g1(node_level1_pos61_outg), .p0(node_level1_pos61_outp), .g0(node_level1_pos61_outg), .gp(node_level2_pos63_outg), .pp(node_level2_pos63_outp));
	wire node_level3_pos7_outg;
	wire node_level3_pos7_outp;
	neg_operator node_level3_pos7(.p1(node_level2_pos3_outp), .g1(node_level2_pos3_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos7_outg), .pp(node_level3_pos7_outp));
	wire node_level3_pos15_outg;
	wire node_level3_pos15_outp;
	neg_operator node_level3_pos15(.p1(node_level2_pos11_outp), .g1(node_level2_pos11_outg), .p0(node_level2_pos11_outp), .g0(node_level2_pos11_outg), .gp(node_level3_pos15_outg), .pp(node_level3_pos15_outp));
	wire node_level3_pos23_outg;
	wire node_level3_pos23_outp;
	neg_operator node_level3_pos23(.p1(node_level2_pos19_outp), .g1(node_level2_pos19_outg), .p0(node_level2_pos19_outp), .g0(node_level2_pos19_outg), .gp(node_level3_pos23_outg), .pp(node_level3_pos23_outp));
	wire node_level3_pos31_outg;
	wire node_level3_pos31_outp;
	neg_operator node_level3_pos31(.p1(node_level2_pos27_outp), .g1(node_level2_pos27_outg), .p0(node_level2_pos27_outp), .g0(node_level2_pos27_outg), .gp(node_level3_pos31_outg), .pp(node_level3_pos31_outp));
	wire node_level3_pos39_outg;
	wire node_level3_pos39_outp;
	neg_operator node_level3_pos39(.p1(node_level2_pos35_outp), .g1(node_level2_pos35_outg), .p0(node_level2_pos35_outp), .g0(node_level2_pos35_outg), .gp(node_level3_pos39_outg), .pp(node_level3_pos39_outp));
	wire node_level3_pos47_outg;
	wire node_level3_pos47_outp;
	neg_operator node_level3_pos47(.p1(node_level2_pos43_outp), .g1(node_level2_pos43_outg), .p0(node_level2_pos43_outp), .g0(node_level2_pos43_outg), .gp(node_level3_pos47_outg), .pp(node_level3_pos47_outp));
	wire node_level3_pos55_outg;
	wire node_level3_pos55_outp;
	neg_operator node_level3_pos55(.p1(node_level2_pos51_outp), .g1(node_level2_pos51_outg), .p0(node_level2_pos51_outp), .g0(node_level2_pos51_outg), .gp(node_level3_pos55_outg), .pp(node_level3_pos55_outp));
	wire node_level3_pos63_outg;
	wire node_level3_pos63_outp;
	neg_operator node_level3_pos63(.p1(node_level2_pos59_outp), .g1(node_level2_pos59_outg), .p0(node_level2_pos59_outp), .g0(node_level2_pos59_outg), .gp(node_level3_pos63_outg), .pp(node_level3_pos63_outp));
	wire node_level4_pos15_outg;
	wire node_level4_pos15_outp;
	pos_operator node_level4_pos15(.p1(node_level3_pos7_outp), .g1(node_level3_pos7_outg), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level4_pos15_outg), .pp(node_level4_pos15_outp));
	wire node_level4_pos31_outg;
	wire node_level4_pos31_outp;
	pos_operator node_level4_pos31(.p1(node_level3_pos23_outp), .g1(node_level3_pos23_outg), .p0(node_level3_pos23_outp), .g0(node_level3_pos23_outg), .gp(node_level4_pos31_outg), .pp(node_level4_pos31_outp));
	wire node_level4_pos47_outg;
	wire node_level4_pos47_outp;
	pos_operator node_level4_pos47(.p1(node_level3_pos39_outp), .g1(node_level3_pos39_outg), .p0(node_level3_pos39_outp), .g0(node_level3_pos39_outg), .gp(node_level4_pos47_outg), .pp(node_level4_pos47_outp));
	wire node_level4_pos63_outg;
	wire node_level4_pos63_outp;
	pos_operator node_level4_pos63(.p1(node_level3_pos55_outp), .g1(node_level3_pos55_outg), .p0(node_level3_pos55_outp), .g0(node_level3_pos55_outg), .gp(node_level4_pos63_outg), .pp(node_level4_pos63_outp));
	wire node_level5_pos31_outg;
	wire node_level5_pos31_outp;
	neg_operator node_level5_pos31(.p1(node_level4_pos15_outp), .g1(node_level4_pos15_outg), .p0(node_level4_pos15_outp), .g0(node_level4_pos15_outg), .gp(node_level5_pos31_outg), .pp(node_level5_pos31_outp));
	wire node_level5_pos63_outg;
	wire node_level5_pos63_outp;
	neg_operator node_level5_pos63(.p1(node_level4_pos47_outp), .g1(node_level4_pos47_outg), .p0(node_level4_pos47_outp), .g0(node_level4_pos47_outg), .gp(node_level5_pos63_outg), .pp(node_level5_pos63_outp));
	wire node_level6_pos63_outg;
	wire node_level6_pos63_outp;
	pos_operator node_level6_pos63(.p1(node_level5_pos31_outp), .g1(node_level5_pos31_outg), .p0(node_level5_pos31_outp), .g0(node_level5_pos31_outg), .gp(node_level6_pos63_outg), .pp(node_level6_pos63_outp));
	wire node_level6_pos47_outg;
	wire node_level6_pos47_outp;
	pos_operator node_level6_pos47(.p1(node_level5_pos31_outp), .g1(node_level5_pos31_outg), .p0(node_level5_pos31_outp), .g0(node_level5_pos31_outg), .gp(node_level6_pos47_outg), .pp(node_level6_pos47_outp));
	wire node_level7_pos23_outg;
	wire node_level7_pos23_outp;
	neg_operator node_level7_pos23(.p1(node_level4_pos15_outp), .g1(node_level4_pos15_outg), .p0(node_level4_pos15_outp), .g0(node_level4_pos15_outg), .gp(node_level7_pos23_outg), .pp(node_level7_pos23_outp));
	wire node_level7_pos39_outg;
	wire node_level7_pos39_outp;
	neg_operator node_level7_pos39(.p1(~node_level5_pos31_outp), .g1(~node_level5_pos31_outg), .p0(~node_level5_pos31_outp), .g0(~node_level5_pos31_outg), .gp(node_level7_pos39_outg), .pp(node_level7_pos39_outp));
	wire node_level7_pos55_outg;
	wire node_level7_pos55_outp;
	neg_operator node_level7_pos55(.p1(node_level6_pos47_outp), .g1(node_level6_pos47_outg), .p0(node_level6_pos47_outp), .g0(node_level6_pos47_outg), .gp(node_level7_pos55_outg), .pp(node_level7_pos55_outp));
	wire node_level8_pos11_outg;
	wire node_level8_pos11_outp;
	pos_operator node_level8_pos11(.p1(node_level3_pos7_outp), .g1(node_level3_pos7_outg), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level8_pos11_outg), .pp(node_level8_pos11_outp));
	wire node_level8_pos19_outg;
	wire node_level8_pos19_outp;
	pos_operator node_level8_pos19(.p1(~node_level4_pos15_outp), .g1(~node_level4_pos15_outg), .p0(~node_level4_pos15_outp), .g0(~node_level4_pos15_outg), .gp(node_level8_pos19_outg), .pp(node_level8_pos19_outp));
	wire node_level8_pos27_outg;
	wire node_level8_pos27_outp;
	pos_operator node_level8_pos27(.p1(node_level7_pos23_outp), .g1(node_level7_pos23_outg), .p0(node_level7_pos23_outp), .g0(node_level7_pos23_outg), .gp(node_level8_pos27_outg), .pp(node_level8_pos27_outp));
	wire node_level8_pos35_outg;
	wire node_level8_pos35_outp;
	pos_operator node_level8_pos35(.p1(node_level5_pos31_outp), .g1(node_level5_pos31_outg), .p0(node_level5_pos31_outp), .g0(node_level5_pos31_outg), .gp(node_level8_pos35_outg), .pp(node_level8_pos35_outp));
	wire node_level8_pos43_outg;
	wire node_level8_pos43_outp;
	pos_operator node_level8_pos43(.p1(node_level7_pos39_outp), .g1(node_level7_pos39_outg), .p0(node_level7_pos39_outp), .g0(node_level7_pos39_outg), .gp(node_level8_pos43_outg), .pp(node_level8_pos43_outp));
	wire node_level8_pos51_outg;
	wire node_level8_pos51_outp;
	pos_operator node_level8_pos51(.p1(~node_level6_pos47_outp), .g1(~node_level6_pos47_outg), .p0(~node_level6_pos47_outp), .g0(~node_level6_pos47_outg), .gp(node_level8_pos51_outg), .pp(node_level8_pos51_outp));
	wire node_level8_pos59_outg;
	wire node_level8_pos59_outp;
	pos_operator node_level8_pos59(.p1(node_level7_pos55_outp), .g1(node_level7_pos55_outg), .p0(node_level7_pos55_outp), .g0(node_level7_pos55_outg), .gp(node_level8_pos59_outg), .pp(node_level8_pos59_outp));
	wire node_level9_pos5_outg;
	wire node_level9_pos5_outp;
	neg_operator node_level9_pos5(.p1(node_level2_pos3_outp), .g1(node_level2_pos3_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level9_pos5_outg), .pp(node_level9_pos5_outp));
	wire node_level9_pos9_outg;
	wire node_level9_pos9_outp;
	neg_operator node_level9_pos9(.p1(~node_level3_pos7_outp), .g1(~node_level3_pos7_outg), .p0(~node_level3_pos7_outp), .g0(~node_level3_pos7_outg), .gp(node_level9_pos9_outg), .pp(node_level9_pos9_outp));
	wire node_level9_pos13_outg;
	wire node_level9_pos13_outp;
	neg_operator node_level9_pos13(.p1(node_level8_pos11_outp), .g1(node_level8_pos11_outg), .p0(node_level8_pos11_outp), .g0(node_level8_pos11_outg), .gp(node_level9_pos13_outg), .pp(node_level9_pos13_outp));
	wire node_level9_pos17_outg;
	wire node_level9_pos17_outp;
	neg_operator node_level9_pos17(.p1(node_level4_pos15_outp), .g1(node_level4_pos15_outg), .p0(node_level4_pos15_outp), .g0(node_level4_pos15_outg), .gp(node_level9_pos17_outg), .pp(node_level9_pos17_outp));
	wire node_level9_pos21_outg;
	wire node_level9_pos21_outp;
	neg_operator node_level9_pos21(.p1(node_level8_pos19_outp), .g1(node_level8_pos19_outg), .p0(node_level8_pos19_outp), .g0(node_level8_pos19_outg), .gp(node_level9_pos21_outg), .pp(node_level9_pos21_outp));
	wire node_level9_pos25_outg;
	wire node_level9_pos25_outp;
	neg_operator node_level9_pos25(.p1(~node_level7_pos23_outp), .g1(~node_level7_pos23_outg), .p0(~node_level7_pos23_outp), .g0(~node_level7_pos23_outg), .gp(node_level9_pos25_outg), .pp(node_level9_pos25_outp));
	wire node_level9_pos29_outg;
	wire node_level9_pos29_outp;
	neg_operator node_level9_pos29(.p1(node_level8_pos27_outp), .g1(node_level8_pos27_outg), .p0(node_level8_pos27_outp), .g0(node_level8_pos27_outg), .gp(node_level9_pos29_outg), .pp(node_level9_pos29_outp));
	wire node_level9_pos33_outg;
	wire node_level9_pos33_outp;
	neg_operator node_level9_pos33(.p1(~node_level5_pos31_outp), .g1(~node_level5_pos31_outg), .p0(~node_level5_pos31_outp), .g0(~node_level5_pos31_outg), .gp(node_level9_pos33_outg), .pp(node_level9_pos33_outp));
	wire node_level9_pos37_outg;
	wire node_level9_pos37_outp;
	neg_operator node_level9_pos37(.p1(node_level8_pos35_outp), .g1(node_level8_pos35_outg), .p0(node_level8_pos35_outp), .g0(node_level8_pos35_outg), .gp(node_level9_pos37_outg), .pp(node_level9_pos37_outp));
	wire node_level9_pos41_outg;
	wire node_level9_pos41_outp;
	neg_operator node_level9_pos41(.p1(~node_level7_pos39_outp), .g1(~node_level7_pos39_outg), .p0(~node_level7_pos39_outp), .g0(~node_level7_pos39_outg), .gp(node_level9_pos41_outg), .pp(node_level9_pos41_outp));
	wire node_level9_pos45_outg;
	wire node_level9_pos45_outp;
	neg_operator node_level9_pos45(.p1(node_level8_pos43_outp), .g1(node_level8_pos43_outg), .p0(node_level8_pos43_outp), .g0(node_level8_pos43_outg), .gp(node_level9_pos45_outg), .pp(node_level9_pos45_outp));
	wire node_level9_pos49_outg;
	wire node_level9_pos49_outp;
	neg_operator node_level9_pos49(.p1(node_level6_pos47_outp), .g1(node_level6_pos47_outg), .p0(node_level6_pos47_outp), .g0(node_level6_pos47_outg), .gp(node_level9_pos49_outg), .pp(node_level9_pos49_outp));
	wire node_level9_pos53_outg;
	wire node_level9_pos53_outp;
	neg_operator node_level9_pos53(.p1(node_level8_pos51_outp), .g1(node_level8_pos51_outg), .p0(node_level8_pos51_outp), .g0(node_level8_pos51_outg), .gp(node_level9_pos53_outg), .pp(node_level9_pos53_outp));
	wire node_level9_pos57_outg;
	wire node_level9_pos57_outp;
	neg_operator node_level9_pos57(.p1(~node_level7_pos55_outp), .g1(~node_level7_pos55_outg), .p0(~node_level7_pos55_outp), .g0(~node_level7_pos55_outg), .gp(node_level9_pos57_outg), .pp(node_level9_pos57_outp));
	wire node_level9_pos61_outg;
	wire node_level9_pos61_outp;
	neg_operator node_level9_pos61(.p1(node_level8_pos59_outp), .g1(node_level8_pos59_outg), .p0(node_level8_pos59_outp), .g0(node_level8_pos59_outg), .gp(node_level9_pos61_outg), .pp(node_level9_pos61_outp));
	wire node_level10_pos2_outg;
	wire node_level10_pos2_outp;
	pos_operator node_level10_pos2(.p1(~p_in[1]), .g1(~g_in[1]), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level10_pos2_outg), .pp(node_level10_pos2_outp));
	wire node_level10_pos4_outg;
	wire node_level10_pos4_outp;
	pos_operator node_level10_pos4(.p1(~p_in[3]), .g1(~g_in[3]), .p0(~node_level2_pos3_outp), .g0(~node_level2_pos3_outg), .gp(node_level10_pos4_outg), .pp(node_level10_pos4_outp));
	wire node_level10_pos6_outg;
	wire node_level10_pos6_outp;
	pos_operator node_level10_pos6(.p1(~p_in[5]), .g1(~g_in[5]), .p0(node_level9_pos5_outp), .g0(node_level9_pos5_outg), .gp(node_level10_pos6_outg), .pp(node_level10_pos6_outp));
	wire node_level10_pos8_outg;
	wire node_level10_pos8_outp;
	pos_operator node_level10_pos8(.p1(~p_in[7]), .g1(~g_in[7]), .p0(node_level3_pos7_outp), .g0(node_level3_pos7_outg), .gp(node_level10_pos8_outg), .pp(node_level10_pos8_outp));
	wire node_level10_pos10_outg;
	wire node_level10_pos10_outp;
	pos_operator node_level10_pos10(.p1(~p_in[9]), .g1(~g_in[9]), .p0(node_level9_pos9_outp), .g0(node_level9_pos9_outg), .gp(node_level10_pos10_outg), .pp(node_level10_pos10_outp));
	wire node_level10_pos12_outg;
	wire node_level10_pos12_outp;
	pos_operator node_level10_pos12(.p1(~p_in[11]), .g1(~g_in[11]), .p0(~node_level8_pos11_outp), .g0(~node_level8_pos11_outg), .gp(node_level10_pos12_outg), .pp(node_level10_pos12_outp));
	wire node_level10_pos14_outg;
	wire node_level10_pos14_outp;
	pos_operator node_level10_pos14(.p1(~p_in[13]), .g1(~g_in[13]), .p0(node_level9_pos13_outp), .g0(node_level9_pos13_outg), .gp(node_level10_pos14_outg), .pp(node_level10_pos14_outp));
	wire node_level10_pos16_outg;
	wire node_level10_pos16_outp;
	pos_operator node_level10_pos16(.p1(~p_in[15]), .g1(~g_in[15]), .p0(~node_level4_pos15_outp), .g0(~node_level4_pos15_outg), .gp(node_level10_pos16_outg), .pp(node_level10_pos16_outp));
	wire node_level10_pos18_outg;
	wire node_level10_pos18_outp;
	pos_operator node_level10_pos18(.p1(~p_in[17]), .g1(~g_in[17]), .p0(node_level9_pos17_outp), .g0(node_level9_pos17_outg), .gp(node_level10_pos18_outg), .pp(node_level10_pos18_outp));
	wire node_level10_pos20_outg;
	wire node_level10_pos20_outp;
	pos_operator node_level10_pos20(.p1(~p_in[19]), .g1(~g_in[19]), .p0(~node_level8_pos19_outp), .g0(~node_level8_pos19_outg), .gp(node_level10_pos20_outg), .pp(node_level10_pos20_outp));
	wire node_level10_pos22_outg;
	wire node_level10_pos22_outp;
	pos_operator node_level10_pos22(.p1(~p_in[21]), .g1(~g_in[21]), .p0(node_level9_pos21_outp), .g0(node_level9_pos21_outg), .gp(node_level10_pos22_outg), .pp(node_level10_pos22_outp));
	wire node_level10_pos24_outg;
	wire node_level10_pos24_outp;
	pos_operator node_level10_pos24(.p1(~p_in[23]), .g1(~g_in[23]), .p0(node_level7_pos23_outp), .g0(node_level7_pos23_outg), .gp(node_level10_pos24_outg), .pp(node_level10_pos24_outp));
	wire node_level10_pos26_outg;
	wire node_level10_pos26_outp;
	pos_operator node_level10_pos26(.p1(~p_in[25]), .g1(~g_in[25]), .p0(node_level9_pos25_outp), .g0(node_level9_pos25_outg), .gp(node_level10_pos26_outg), .pp(node_level10_pos26_outp));
	wire node_level10_pos28_outg;
	wire node_level10_pos28_outp;
	pos_operator node_level10_pos28(.p1(~p_in[27]), .g1(~g_in[27]), .p0(~node_level8_pos27_outp), .g0(~node_level8_pos27_outg), .gp(node_level10_pos28_outg), .pp(node_level10_pos28_outp));
	wire node_level10_pos30_outg;
	wire node_level10_pos30_outp;
	pos_operator node_level10_pos30(.p1(~p_in[29]), .g1(~g_in[29]), .p0(node_level9_pos29_outp), .g0(node_level9_pos29_outg), .gp(node_level10_pos30_outg), .pp(node_level10_pos30_outp));
	wire node_level10_pos32_outg;
	wire node_level10_pos32_outp;
	pos_operator node_level10_pos32(.p1(~p_in[31]), .g1(~g_in[31]), .p0(node_level5_pos31_outp), .g0(node_level5_pos31_outg), .gp(node_level10_pos32_outg), .pp(node_level10_pos32_outp));
	wire node_level10_pos34_outg;
	wire node_level10_pos34_outp;
	pos_operator node_level10_pos34(.p1(~p_in[33]), .g1(~g_in[33]), .p0(node_level9_pos33_outp), .g0(node_level9_pos33_outg), .gp(node_level10_pos34_outg), .pp(node_level10_pos34_outp));
	wire node_level10_pos36_outg;
	wire node_level10_pos36_outp;
	pos_operator node_level10_pos36(.p1(~p_in[35]), .g1(~g_in[35]), .p0(~node_level8_pos35_outp), .g0(~node_level8_pos35_outg), .gp(node_level10_pos36_outg), .pp(node_level10_pos36_outp));
	wire node_level10_pos38_outg;
	wire node_level10_pos38_outp;
	pos_operator node_level10_pos38(.p1(~p_in[37]), .g1(~g_in[37]), .p0(node_level9_pos37_outp), .g0(node_level9_pos37_outg), .gp(node_level10_pos38_outg), .pp(node_level10_pos38_outp));
	wire node_level10_pos40_outg;
	wire node_level10_pos40_outp;
	pos_operator node_level10_pos40(.p1(~p_in[39]), .g1(~g_in[39]), .p0(node_level7_pos39_outp), .g0(node_level7_pos39_outg), .gp(node_level10_pos40_outg), .pp(node_level10_pos40_outp));
	wire node_level10_pos42_outg;
	wire node_level10_pos42_outp;
	pos_operator node_level10_pos42(.p1(~p_in[41]), .g1(~g_in[41]), .p0(node_level9_pos41_outp), .g0(node_level9_pos41_outg), .gp(node_level10_pos42_outg), .pp(node_level10_pos42_outp));
	wire node_level10_pos44_outg;
	wire node_level10_pos44_outp;
	pos_operator node_level10_pos44(.p1(~p_in[43]), .g1(~g_in[43]), .p0(~node_level8_pos43_outp), .g0(~node_level8_pos43_outg), .gp(node_level10_pos44_outg), .pp(node_level10_pos44_outp));
	wire node_level10_pos46_outg;
	wire node_level10_pos46_outp;
	pos_operator node_level10_pos46(.p1(~p_in[45]), .g1(~g_in[45]), .p0(node_level9_pos45_outp), .g0(node_level9_pos45_outg), .gp(node_level10_pos46_outg), .pp(node_level10_pos46_outp));
	wire node_level10_pos48_outg;
	wire node_level10_pos48_outp;
	pos_operator node_level10_pos48(.p1(~p_in[47]), .g1(~g_in[47]), .p0(~node_level6_pos47_outp), .g0(~node_level6_pos47_outg), .gp(node_level10_pos48_outg), .pp(node_level10_pos48_outp));
	wire node_level10_pos50_outg;
	wire node_level10_pos50_outp;
	pos_operator node_level10_pos50(.p1(~p_in[49]), .g1(~g_in[49]), .p0(node_level9_pos49_outp), .g0(node_level9_pos49_outg), .gp(node_level10_pos50_outg), .pp(node_level10_pos50_outp));
	wire node_level10_pos52_outg;
	wire node_level10_pos52_outp;
	pos_operator node_level10_pos52(.p1(~p_in[51]), .g1(~g_in[51]), .p0(~node_level8_pos51_outp), .g0(~node_level8_pos51_outg), .gp(node_level10_pos52_outg), .pp(node_level10_pos52_outp));
	wire node_level10_pos54_outg;
	wire node_level10_pos54_outp;
	pos_operator node_level10_pos54(.p1(~p_in[53]), .g1(~g_in[53]), .p0(node_level9_pos53_outp), .g0(node_level9_pos53_outg), .gp(node_level10_pos54_outg), .pp(node_level10_pos54_outp));
	wire node_level10_pos56_outg;
	wire node_level10_pos56_outp;
	pos_operator node_level10_pos56(.p1(~p_in[55]), .g1(~g_in[55]), .p0(node_level7_pos55_outp), .g0(node_level7_pos55_outg), .gp(node_level10_pos56_outg), .pp(node_level10_pos56_outp));
	wire node_level10_pos58_outg;
	wire node_level10_pos58_outp;
	pos_operator node_level10_pos58(.p1(~p_in[57]), .g1(~g_in[57]), .p0(node_level9_pos57_outp), .g0(node_level9_pos57_outg), .gp(node_level10_pos58_outg), .pp(node_level10_pos58_outp));
	wire node_level10_pos60_outg;
	wire node_level10_pos60_outp;
	pos_operator node_level10_pos60(.p1(~p_in[59]), .g1(~g_in[59]), .p0(~node_level8_pos59_outp), .g0(~node_level8_pos59_outg), .gp(node_level10_pos60_outg), .pp(node_level10_pos60_outp));
	wire node_level10_pos62_outg;
	wire node_level10_pos62_outp;
	pos_operator node_level10_pos62(.p1(~p_in[61]), .g1(~g_in[61]), .p0(node_level9_pos61_outp), .g0(node_level9_pos61_outg), .gp(node_level10_pos62_outg), .pp(node_level10_pos62_outp));


	assign s[0] = p_in[0];
	assign s[1] = p_in[1] ^ g_in[0];
	assign s[2] = p_in[2] ^ ~node_level1_pos1_outg;
	assign s[3] = p_in[3] ^ node_level10_pos2_outg;
	assign s[4] = p_in[4] ^ node_level2_pos3_outg;
	assign s[5] = p_in[5] ^ node_level10_pos4_outg;
	assign s[6] = p_in[6] ^ ~node_level9_pos5_outg;
	assign s[7] = p_in[7] ^ node_level10_pos6_outg;
	assign s[8] = p_in[8] ^ ~node_level3_pos7_outg;
	assign s[9] = p_in[9] ^ node_level10_pos8_outg;
	assign s[10] = p_in[10] ^ ~node_level9_pos9_outg;
	assign s[11] = p_in[11] ^ node_level10_pos10_outg;
	assign s[12] = p_in[12] ^ node_level8_pos11_outg;
	assign s[13] = p_in[13] ^ node_level10_pos12_outg;
	assign s[14] = p_in[14] ^ ~node_level9_pos13_outg;
	assign s[15] = p_in[15] ^ node_level10_pos14_outg;
	assign s[16] = p_in[16] ^ node_level4_pos15_outg;
	assign s[17] = p_in[17] ^ node_level10_pos16_outg;
	assign s[18] = p_in[18] ^ ~node_level9_pos17_outg;
	assign s[19] = p_in[19] ^ node_level10_pos18_outg;
	assign s[20] = p_in[20] ^ node_level8_pos19_outg;
	assign s[21] = p_in[21] ^ node_level10_pos20_outg;
	assign s[22] = p_in[22] ^ ~node_level9_pos21_outg;
	assign s[23] = p_in[23] ^ node_level10_pos22_outg;
	assign s[24] = p_in[24] ^ ~node_level7_pos23_outg;
	assign s[25] = p_in[25] ^ node_level10_pos24_outg;
	assign s[26] = p_in[26] ^ ~node_level9_pos25_outg;
	assign s[27] = p_in[27] ^ node_level10_pos26_outg;
	assign s[28] = p_in[28] ^ node_level8_pos27_outg;
	assign s[29] = p_in[29] ^ node_level10_pos28_outg;
	assign s[30] = p_in[30] ^ ~node_level9_pos29_outg;
	assign s[31] = p_in[31] ^ node_level10_pos30_outg;
	assign s[32] = p_in[32] ^ ~node_level5_pos31_outg;
	assign s[33] = p_in[33] ^ node_level10_pos32_outg;
	assign s[34] = p_in[34] ^ ~node_level9_pos33_outg;
	assign s[35] = p_in[35] ^ node_level10_pos34_outg;
	assign s[36] = p_in[36] ^ node_level8_pos35_outg;
	assign s[37] = p_in[37] ^ node_level10_pos36_outg;
	assign s[38] = p_in[38] ^ ~node_level9_pos37_outg;
	assign s[39] = p_in[39] ^ node_level10_pos38_outg;
	assign s[40] = p_in[40] ^ ~node_level7_pos39_outg;
	assign s[41] = p_in[41] ^ node_level10_pos40_outg;
	assign s[42] = p_in[42] ^ ~node_level9_pos41_outg;
	assign s[43] = p_in[43] ^ node_level10_pos42_outg;
	assign s[44] = p_in[44] ^ node_level8_pos43_outg;
	assign s[45] = p_in[45] ^ node_level10_pos44_outg;
	assign s[46] = p_in[46] ^ ~node_level9_pos45_outg;
	assign s[47] = p_in[47] ^ node_level10_pos46_outg;
	assign s[48] = p_in[48] ^ node_level6_pos47_outg;
	assign s[49] = p_in[49] ^ node_level10_pos48_outg;
	assign s[50] = p_in[50] ^ ~node_level9_pos49_outg;
	assign s[51] = p_in[51] ^ node_level10_pos50_outg;
	assign s[52] = p_in[52] ^ node_level8_pos51_outg;
	assign s[53] = p_in[53] ^ node_level10_pos52_outg;
	assign s[54] = p_in[54] ^ ~node_level9_pos53_outg;
	assign s[55] = p_in[55] ^ node_level10_pos54_outg;
	assign s[56] = p_in[56] ^ ~node_level7_pos55_outg;
	assign s[57] = p_in[57] ^ node_level10_pos56_outg;
	assign s[58] = p_in[58] ^ ~node_level9_pos57_outg;
	assign s[59] = p_in[59] ^ node_level10_pos58_outg;
	assign s[60] = p_in[60] ^ node_level8_pos59_outg;
	assign s[61] = p_in[61] ^ node_level10_pos60_outg;
	assign s[62] = p_in[62] ^ ~node_level9_pos61_outg;
	assign s[63] = p_in[63] ^ node_level10_pos62_outg;
endmodule


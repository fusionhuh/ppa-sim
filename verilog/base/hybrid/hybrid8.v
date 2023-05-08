`include "carry_operator.v"

module hybridadder8(x1, x2, s);
	input[7:0]x1;
	input[7:0]x2;
	output[7:0]s;
	wire[7:0]p_in = x1 ^ x2;
	wire[7:0]g_in = x1 & x2;
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	carry_operator node_level1_pos1(.p1(p_in[1]), .g1(g_in[1]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	carry_operator node_level1_pos3(.p1(p_in[3]), .g1(g_in[3]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level1_pos5_outg;
	wire node_level1_pos5_outp;
	carry_operator node_level1_pos5(.p1(p_in[5]), .g1(g_in[5]), .p0(p_in[4]), .g0(g_in[4]), .gp(node_level1_pos5_outg), .pp(node_level1_pos5_outp));
	wire node_level1_pos7_outg;
	wire node_level1_pos7_outp;
	carry_operator node_level1_pos7(.p1(p_in[7]), .g1(g_in[7]), .p0(p_in[6]), .g0(g_in[6]), .gp(node_level1_pos7_outg), .pp(node_level1_pos7_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	carry_operator node_level2_pos3(.p1(node_level1_pos3_outp), .g1(node_level1_pos3_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));
	wire node_level2_pos5_outg;
	wire node_level2_pos5_outp;
	carry_operator node_level2_pos5(.p1(node_level1_pos5_outp), .g1(node_level1_pos5_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level2_pos5_outg), .pp(node_level2_pos5_outp));
	wire node_level2_pos7_outg;
	wire node_level2_pos7_outp;
	carry_operator node_level2_pos7(.p1(node_level1_pos7_outp), .g1(node_level1_pos7_outg), .p0(node_level2_pos5_outp), .g0(node_level2_pos5_outg), .gp(node_level2_pos7_outg), .pp(node_level2_pos7_outp));
	wire node_level3_pos5_outg;
	wire node_level3_pos5_outp;
	carry_operator node_level3_pos5(.p1(node_level2_pos5_outp), .g1(node_level2_pos5_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level3_pos5_outg), .pp(node_level3_pos5_outp));
	wire node_level3_pos7_outg;
	wire node_level3_pos7_outp;
	carry_operator node_level3_pos7(.p1(node_level2_pos7_outp), .g1(node_level2_pos7_outg), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level3_pos7_outg), .pp(node_level3_pos7_outp));
	wire node_level4_pos2_outg;
	wire node_level4_pos2_outp;
	carry_operator node_level4_pos2(.p1(p_in[2]), .g1(g_in[2]), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level4_pos2_outg), .pp(node_level4_pos2_outp));
	wire node_level4_pos4_outg;
	wire node_level4_pos4_outp;
	carry_operator node_level4_pos4(.p1(p_in[4]), .g1(g_in[4]), .p0(node_level2_pos3_outp), .g0(node_level2_pos3_outg), .gp(node_level4_pos4_outg), .pp(node_level4_pos4_outp));
	wire node_level4_pos6_outg;
	wire node_level4_pos6_outp;
	carry_operator node_level4_pos6(.p1(p_in[6]), .g1(g_in[6]), .p0(node_level3_pos5_outp), .g0(node_level3_pos5_outg), .gp(node_level4_pos6_outg), .pp(node_level4_pos6_outp));


	assign s[0] = p_in[0];
	assign s[1] = node_level1_pos1_outg;// ^ node_level1_pos1_outp;
	assign s[2] = node_level4_pos2_outg;// ^ node_level4_pos2_outp;
	assign s[3] = node_level2_pos3_outg;// ^ node_level2_pos3_outp;
	assign s[4] = node_level4_pos4_outg;// ^ node_level4_pos4_outp;
	assign s[5] = node_level3_pos5_outg;// ^ node_level3_pos5_outp;
	assign s[6] = node_level4_pos6_outg;// ^ node_level4_pos6_outp;
	assign s[7] = node_level3_pos7_outg;// ^ node_level3_pos7_outp;
endmodule

`include "carry_operator.v"

module ksadder4(x1, x2, s);
	input[3:0]x1;
	input[3:0]x2;
	output[3:0]s;
	wire[3:0]p_in = x1 ^ x2;
	wire[3:0]g_in = x1 & x2;
	wire node_level1_pos1_outg;
	wire node_level1_pos1_outp;
	carry_operator node_level1_pos1(.p1(p_in[1]), .g1(g_in[1]), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level1_pos1_outg), .pp(node_level1_pos1_outp));
	wire node_level1_pos2_outg;
	wire node_level1_pos2_outp;
	carry_operator node_level1_pos2(.p1(p_in[2]), .g1(g_in[2]), .p0(p_in[1]), .g0(g_in[1]), .gp(node_level1_pos2_outg), .pp(node_level1_pos2_outp));
	wire node_level1_pos3_outg;
	wire node_level1_pos3_outp;
	carry_operator node_level1_pos3(.p1(p_in[3]), .g1(g_in[3]), .p0(p_in[2]), .g0(g_in[2]), .gp(node_level1_pos3_outg), .pp(node_level1_pos3_outp));
	wire node_level2_pos2_outg;
	wire node_level2_pos2_outp;
	carry_operator node_level2_pos2(.p1(node_level1_pos2_outp), .g1(node_level1_pos2_outg), .p0(p_in[0]), .g0(g_in[0]), .gp(node_level2_pos2_outg), .pp(node_level2_pos2_outp));
	wire node_level2_pos3_outg;
	wire node_level2_pos3_outp;
	carry_operator node_level2_pos3(.p1(node_level1_pos3_outp), .g1(node_level1_pos3_outg), .p0(node_level1_pos1_outp), .g0(node_level1_pos1_outg), .gp(node_level2_pos3_outg), .pp(node_level2_pos3_outp));


	assign s[0] = p_in[0];
	assign s[1] = g_in[0] ^ p_in[1];
	assign s[2] = node_level1_pos1_outg ^ p_in[2];
	assign s[3] = node_level2_pos2_outg ^ p_in[3];
endmodule

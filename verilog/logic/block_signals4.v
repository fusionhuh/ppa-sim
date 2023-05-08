`define BLOCK_SIGNALS4


module block_signals4(g_in, p_in, p_out, g_out);
	input[3:0]g_in;
	input[3:0]p_in;
	output p_out, g_out;

	assign p_out = (p_in[0] & p_in[1] & p_in[2] & p_in[3]);
	assign g_out = g_in[3] | (p_in[3] & g_in[2]) | (p_in[3] & p_in[2] & g_in[1]) | (p_in[3] & p_in[2] & p_in[1] & g_in[0]);

endmodule
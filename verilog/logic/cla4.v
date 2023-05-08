`define CLA4

module cla4(p_in, g_in, cin, cout, p_out, g_out);
	input[3:0]p_in;
	input[3:0]g_in;
	input cin;
	output[3:0]cout;
	output p_out, g_out;

	assign cout[0] = cin;
	assign cout[1] = g_in[0] | (p_in[0] & cin);
	assign cout[2] = g_in[1] | (p_in[1] & p_in[0] & cin) | (g_in[0] & p_in[1]);
	assign cout[3] = g_in[2] | (p_in[2] & p_in[1] & p_in[0] & cin) | (p_in[2] & p_in[1] & g_in[0]) | (p_in[2] & g_in[1]);
	
	assign p_out = p_in[0] & p_in[1] & p_in[2] & p_in[3];
	assign g_out = g_in[3] | (p_in[3] & g_in[2]) | (p_in[3] & p_in[2] & g_in[1]) | (p_in[3] & p_in[2] & p_in[1] & g_in[0]);

endmodule
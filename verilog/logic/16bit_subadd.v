module _16bit_subadd_{type}(x1, x2, s, cin, cout, p_out, g_out);
	input[15:0]x1;
	input[15:0]x2;
	input cin;
	wire[15:0]p_in;
	wire[15:0]g_in;
	output[15:0]s;
	output cout;

	output p_out, g_out;

	wire adder0_cin;
	wire adder0_cout;
	{type} adder0(.x1(x1[3:0]), .x2(x2[3:0]), .s(s[3:0]), .p_out(p_in[3:0]), .g_out(g_in[3:0]), .cin(adder0_cin));
	wire adder0_p_out;
	wire adder0_g_out;
	block_signals4 block0(.g_in(g_in[3:0]), .p_in(p_in[3:0]), .p_out(adder0_p_out), .g_out(adder0_g_out));

	wire adder1_cin;
	wire adder1_cout;
	{type} adder1(.x1(x1[7:4]), .x2(x2[7:4]), .s(s[7:4]), .p_out(p_in[7:4]), .g_out(g_in[7:4]), .cin(adder1_cin));
	wire adder1_p_out;
	wire adder1_g_out;
	block_signals4 block1(.g_in(g_in[7:4]), .p_in(p_in[7:4]), .p_out(adder1_p_out), .g_out(adder1_g_out));

	wire adder2_cin;
	wire adder2_cout;
	{type} adder2(.x1(x1[11:8]), .x2(x2[11:8]), .s(s[11:8]), .p_out(p_in[11:8]), .g_out(g_in[11:8]), .cin(adder2_cin));
	wire adder2_p_out;
	wire adder2_g_out;
	block_signals4 block2(.g_in(g_in[11:8]), .p_in(p_in[11:8]), .p_out(adder2_p_out), .g_out(adder2_g_out));

	wire adder3_cin;
	wire adder3_cout;
	{type} adder3(.x1(x1[15:12]), .x2(x2[15:12]), .s(s[15:12]), .p_out(p_in[15:12]), .g_out(g_in[15:12]), .cin(adder3_cin));
	wire adder3_p_out;
	wire adder3_g_out;
	block_signals4 block3(.g_in(g_in[15:12]), .p_in(p_in[15:12]), .p_out(adder3_p_out), .g_out(adder3_g_out));

	wire[3:0]cla_cout;
	cla4 cla_block(.p_in({{adder3_p_out, adder2_p_out, adder1_p_out, adder0_p_out}}), .g_in({{adder3_g_out, adder2_g_out, adder1_g_out, adder0_g_out}}), .cin(cin), .cout(cla_cout), .p_out(p_out), .g_out(g_out));
	assign adder0_cin = cla_cout[0];
	assign adder1_cin = cla_cout[1];
	assign adder2_cin = cla_cout[2];
	assign adder3_cin = cla_cout[3];
endmodule



`ifndef BK4
`include "bk/bk4.v"
`endif
`ifndef CLA4
`include "cla4.v"
`endif
`ifndef BLOCK_SIGNALS4
`include "block_signals4.v"
`endif
`ifndef _16BIT_SUBADD
`include "_16bit_subadd.v"
`endif
module bk_16_cla_4(x1, x2, s, cin, cout);
	input[15:0]x1;
	input[15:0]x2;
	input cin;
	wire[15:0]p_in;
	wire[15:0]g_in;
	output[15:0]s;
	output cout;

	_16bit_subadd adder(.x1(x1), .x2(x2), .s(s), .cin(cin), .cout(cout));
endmodule

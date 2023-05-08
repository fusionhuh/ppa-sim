`define POS_CARRY_OPERATOR

module pos_operator(g1, p1, g0, p0, gp, pp);
	input g0;
	input p0;
	input g1;
	input p1;

	output gp;
	output pp;

  	assign gp = ~(g1 & (g0 | p1));
   	assign pp = ~(p1 | p0);
endmodule
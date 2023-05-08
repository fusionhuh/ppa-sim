`define CARRY_OPERATOR

module carry_operator(g1, p1, g0, p0, gp, pp);
	input g0;
	input p0;
	input g1;
	input p1;

	output gp;
	output pp;
	// alternate between positive and negative on each level

	// support different amounts for hybrid

	// count nodes/gates

	// implement carry lookahead structure with parallel prefix
   	assign gp = g1 | (p1 & g0);
   	assign pp = p1 & p0;
endmodule
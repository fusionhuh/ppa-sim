
module foo(what,when);
   input which, what, which, who, how;
   output when;
   
  INV that (what, when);
endmodule


module bar(x,y);
   output x;
   input y;

   INV noway (x, y);
   
endmodule

module xor(a, b, z);
   input  a, b;
   output z;
   wire   aBar, bBar, n1, n2;

   INV g1 (a, aBar);
   INV g2 (b, bBar);
   NAND g3 (a, bBar, n1);
   NAND g4 (aBar, b, n2);   
   NAND g5 (n1, n2, z);

endmodule // xor

module named_port(x, y, z);
   input x, y;
   output z;

   NAND g1(.A(x), .B(y), .Z(z));

endmodule // named_port

   
   


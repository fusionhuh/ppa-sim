
    function integer max(input integer a,b);    begin        if (a > b)            max = a;        else            max = b;    end    endfunction    function integer calc_width(input integer in1, in2, out);        calc_width = 2**$clog2(max(max(in1,in2), out));    endfunction


    function integer max(input integer a,b);    begin        if (a > b)            max = a;        else            max = b;    end    endfunction    function integer calc_width(input integer in1, in2, out);        calc_width = 2**$clog2(max(max(in1,in2), out));    endfunction

// 
// Politecnico di Milano
// Code created using PandA - Version: PandA 2023.1 - Revision 04336c437a53bc96ae90b74052c455629946ec8b-main - Date 2023-11-05T19:46:38
// /tmp/.mount_bambutjLsrr/usr/bin/bambu executed with: /tmp/.mount_bambutjLsrr/usr/bin/bambu --top-fname=icrc1 substitution/hlsynthesis/src/irc.c 
// 
// Send any bug to: panda-info@polimi.it
// ************************************************************************
// The following text holds for all the components tagged with PANDA_LGPLv3.
// They are all part of the BAMBU/PANDA IP LIBRARY.
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
// 
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public
// License along with the PandA framework; see the files COPYING.LIB
// If not, see <http://www.gnu.org/licenses/>.
// ************************************************************************

`ifdef __ICARUS__
  `define _SIM_HAVE_CLOG2
`endif
`ifdef VERILATOR
  `define _SIM_HAVE_CLOG2
`endif
`ifdef MODEL_TECH
  `define _SIM_HAVE_CLOG2
`endif
`ifdef VCS
  `define _SIM_HAVE_CLOG2
`endif
`ifdef NCVERILOG
  `define _SIM_HAVE_CLOG2
`endif
`ifdef XILINX_SIMULATOR
  `define _SIM_HAVE_CLOG2
`endif
`ifdef XILINX_ISIM
  `define _SIM_HAVE_CLOG2
`endif

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>, Christian Pilato <christian.pilato@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module constant_value(out1);
  parameter BITSIZE_out1=1,
    value=1'b0;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  assign out1 = value;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module register_SE(clock,
  reset,
  in1,
  wenable,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input clock;
  input reset;
  input [BITSIZE_in1-1:0] in1;
  input wenable;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  
  reg [BITSIZE_out1-1:0] reg_out1 =0;
  assign out1 = reg_out1;
  always @(posedge clock)
    if (wenable)
      reg_out1 <= in1;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module UIdata_converter_FU(in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input [BITSIZE_in1-1:0] in1;
  // OUT
  output signed [BITSIZE_out1-1:0] out1;
  generate
  if (BITSIZE_out1 <= BITSIZE_in1)
  begin
    assign out1 = in1[BITSIZE_out1-1:0];
  end
  else
  begin
    assign out1 = {{(BITSIZE_out1-BITSIZE_in1){1'b0}},in1};
  end
  endgenerate
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module IIconvert_expr_FU(in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  // OUT
  output signed [BITSIZE_out1-1:0] out1;
  generate
  if (BITSIZE_out1 <= BITSIZE_in1)
  begin
    assign out1 = in1[BITSIZE_out1-1:0];
  end
  else
  begin
    assign out1 = {{(BITSIZE_out1-BITSIZE_in1){in1[BITSIZE_in1-1]}},in1};
  end
  endgenerate
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module IUdata_converter_FU(in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  generate
  if (BITSIZE_out1 <= BITSIZE_in1)
  begin
    assign out1 = in1[BITSIZE_out1-1:0];
  end
  else
  begin
    assign out1 = {{(BITSIZE_out1-BITSIZE_in1){in1[BITSIZE_in1-1]}},in1};
  end
  endgenerate
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2020-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module ui_extract_bit_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1;
  // IN
  input [BITSIZE_in1-1:0] in1;
  input [BITSIZE_in2-1:0] in2;
  // OUT
  output out1;
  assign out1 = (in1 >> in2)&1;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module read_cond_FU(in1,
  out1);
  parameter BITSIZE_in1=1;
  // IN
  input [BITSIZE_in1-1:0] in1;
  // OUT
  output out1;
  assign out1 = in1 != {BITSIZE_in1{1'b0}};
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module bit_xor_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  input signed [BITSIZE_in2-1:0] in2;
  // OUT
  output signed [BITSIZE_out1-1:0] out1;
  assign out1 = in1 ^ in2;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module lshift_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1,
    PRECISION=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  input [BITSIZE_in2-1:0] in2;
  // OUT
  output signed [BITSIZE_out1-1:0] out1;
  `ifndef _SIM_HAVE_CLOG2
    function integer log2;
       input integer value;
       integer temp_value;
      begin
        temp_value = value-1;
        for (log2=0; temp_value>0; log2=log2+1)
          temp_value = temp_value>>1;
      end
    endfunction
  `endif
  `ifdef _SIM_HAVE_CLOG2
    parameter arg2_bitsize = $clog2(PRECISION);
  `else
    parameter arg2_bitsize = log2(PRECISION);
  `endif
  generate
    if(BITSIZE_in2 > arg2_bitsize)
      assign out1 = in1 <<< in2[arg2_bitsize-1:0];
    else
      assign out1 = in1 <<< in2;
  endgenerate
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module ne_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  input signed [BITSIZE_in2-1:0] in2;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  assign out1 = in1 != in2;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module plus_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1,
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);
  input signed [FINAL_WIDTH-1:0] in1;
  input signed [FINAL_WIDTH-1:0] in2;
  output signed [FINAL_WIDTH-1:0] out1;
  assign out1 = in1 + in2;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module ui_cond_expr_FU(in1,
  in2,
  in3,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_in3=1,
    BITSIZE_out1=1;
  // IN
  input [BITSIZE_in1-1:0] in1;
  input [BITSIZE_in2-1:0] in2;
  input [BITSIZE_in3-1:0] in3;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  assign out1 = in1 != 0 ? in2 : in3;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module ui_plus_expr_FU(in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1,
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);
  input signed [FINAL_WIDTH-1:0] in1;
  input signed [FINAL_WIDTH-1:0] in2;
  output signed [FINAL_WIDTH-1:0] out1;
  assign out1 = in1 + in2;
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module IIdata_converter_FU(in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input signed [BITSIZE_in1-1:0] in1;
  // OUT
  output signed [BITSIZE_out1-1:0] out1;
  generate
  if (BITSIZE_out1 <= BITSIZE_in1)
  begin
    assign out1 = in1[BITSIZE_out1-1:0];
  end
  else
  begin
    assign out1 = {{(BITSIZE_out1-BITSIZE_in1){in1[BITSIZE_in1-1]}},in1};
  end
  endgenerate
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>, Christian Pilato <christian.pilato@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module MUX_GATE(sel,
  in1,
  in2,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_in2=1,
    BITSIZE_out1=1;
  // IN
  input sel;
  input [BITSIZE_in1-1:0] in1;
  input [BITSIZE_in2-1:0] in2;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  assign out1 = sel ? in1 : in2;
endmodule

// Datapath RTL description for icrc1
// This component has been derived from the input source code and so it does not fall under the copyright of PandA framework, but it follows the input source code copyright, and may be aggregated with components of the BAMBU/PANDA IP LIBRARY.
// Author(s): Component automatically generated by bambu
// License: THIS COMPONENT IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
`timescale 1ns / 1ps
module datapath_icrc1(clock,
  reset,
  in_port_crc,
  in_port_onech,
  return_port,
  selector_MUX_22_reg_0_0_0_0,
  selector_MUX_23_reg_1_0_0_0,
  wrenable_reg_0,
  wrenable_reg_1,
  OUT_CONDITION_icrc1_33778_33847);
  // IN
  input clock;
  input reset;
  input [15:0] in_port_crc;
  input [7:0] in_port_onech;
  input selector_MUX_22_reg_0_0_0_0;
  input selector_MUX_23_reg_1_0_0_0;
  input wrenable_reg_0;
  input wrenable_reg_1;
  // OUT
  output [15:0] return_port;
  output OUT_CONDITION_icrc1_33778_33847;
  // Component and signal declarations
  wire signed [15:0] out_IIconvert_expr_FU_3_i0_fu_icrc1_33778_33809;
  wire [15:0] out_IUdata_converter_FU_5_i0_fu_icrc1_33778_33812;
  wire [15:0] out_IUdata_converter_FU_9_i0_fu_icrc1_33778_33843;
  wire [31:0] out_MUX_22_reg_0_0_0_0;
  wire [15:0] out_MUX_23_reg_1_0_0_0;
  wire signed [8:0] out_UIdata_converter_FU_2_i0_fu_icrc1_33778_33807;
  wire signed [15:0] out_UIdata_converter_FU_4_i0_fu_icrc1_33778_33810;
  wire signed [15:0] out_UIdata_converter_FU_8_i0_fu_icrc1_33778_33840;
  wire signed [15:0] out_bit_xor_expr_FU_16_0_16_13_i0_fu_icrc1_33778_33842;
  wire signed [15:0] out_bit_xor_expr_FU_16_16_16_14_i0_fu_icrc1_33778_33811;
  wire out_const_0;
  wire [1:0] out_const_1;
  wire [4:0] out_const_2;
  wire [13:0] out_const_3;
  wire out_const_4;
  wire [3:0] out_const_5;
  wire signed [31:0] out_conv_out_const_0_I_1_I_32;
  wire signed [31:0] out_ii_conv_conn_obj_0_IIdata_converter_FU_ii_conv_0;
  wire signed [15:0] out_lshift_expr_FU_16_0_16_15_i0_fu_icrc1_33778_33808;
  wire out_ne_expr_FU_32_0_32_16_i0_fu_icrc1_33778_33893;
  wire signed [15:0] out_plus_expr_FU_16_0_16_17_i0_fu_icrc1_33778_33841;
  wire signed [31:0] out_plus_expr_FU_32_0_32_18_i0_fu_icrc1_33778_33846;
  wire out_read_cond_FU_11_i0_fu_icrc1_33778_33847;
  wire [31:0] out_reg_0_reg_0;
  wire [15:0] out_reg_1_reg_1;
  wire [15:0] out_ui_cond_expr_FU_16_16_16_16_19_i0_fu_icrc1_33778_33845;
  wire out_ui_extract_bit_expr_FU_10_i0_fu_icrc1_33778_33909;
  wire [15:0] out_ui_plus_expr_FU_16_0_16_20_i0_fu_icrc1_33778_33844;
  
  IIdata_converter_FU #(.BITSIZE_in1(32),
    .BITSIZE_out1(32)) IIdata_converter_FU_ii_conv_0 (.out1(out_ii_conv_conn_obj_0_IIdata_converter_FU_ii_conv_0),
    .in1(out_conv_out_const_0_I_1_I_32));
  MUX_GATE #(.BITSIZE_in1(32),
    .BITSIZE_in2(32),
    .BITSIZE_out1(32)) MUX_22_reg_0_0_0_0 (.out1(out_MUX_22_reg_0_0_0_0),
    .sel(selector_MUX_22_reg_0_0_0_0),
    .in1(out_ii_conv_conn_obj_0_IIdata_converter_FU_ii_conv_0),
    .in2(out_plus_expr_FU_32_0_32_18_i0_fu_icrc1_33778_33846));
  MUX_GATE #(.BITSIZE_in1(16),
    .BITSIZE_in2(16),
    .BITSIZE_out1(16)) MUX_23_reg_1_0_0_0 (.out1(out_MUX_23_reg_1_0_0_0),
    .sel(selector_MUX_23_reg_1_0_0_0),
    .in1(out_IUdata_converter_FU_5_i0_fu_icrc1_33778_33812),
    .in2(out_ui_cond_expr_FU_16_16_16_16_19_i0_fu_icrc1_33778_33845));
  constant_value #(.BITSIZE_out1(1),
    .value(1'b0)) const_0 (.out1(out_const_0));
  constant_value #(.BITSIZE_out1(2),
    .value(2'b01)) const_1 (.out1(out_const_1));
  constant_value #(.BITSIZE_out1(5),
    .value(5'b01000)) const_2 (.out1(out_const_2));
  constant_value #(.BITSIZE_out1(14),
    .value(14'b01000000100001)) const_3 (.out1(out_const_3));
  constant_value #(.BITSIZE_out1(1),
    .value(1'b1)) const_4 (.out1(out_const_4));
  constant_value #(.BITSIZE_out1(4),
    .value(4'b1111)) const_5 (.out1(out_const_5));
  IIdata_converter_FU #(.BITSIZE_in1(1),
    .BITSIZE_out1(32)) conv_out_const_0_I_1_I_32 (.out1(out_conv_out_const_0_I_1_I_32),
    .in1(out_const_0));
  UIdata_converter_FU #(.BITSIZE_in1(8),
    .BITSIZE_out1(9)) fu_icrc1_33778_33807 (.out1(out_UIdata_converter_FU_2_i0_fu_icrc1_33778_33807),
    .in1(in_port_onech));
  lshift_expr_FU #(.BITSIZE_in1(9),
    .BITSIZE_in2(5),
    .BITSIZE_out1(16),
    .PRECISION(32)) fu_icrc1_33778_33808 (.out1(out_lshift_expr_FU_16_0_16_15_i0_fu_icrc1_33778_33808),
    .in1(out_UIdata_converter_FU_2_i0_fu_icrc1_33778_33807),
    .in2(out_const_2));
  IIconvert_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33809 (.out1(out_IIconvert_expr_FU_3_i0_fu_icrc1_33778_33809),
    .in1(out_lshift_expr_FU_16_0_16_15_i0_fu_icrc1_33778_33808));
  UIdata_converter_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33810 (.out1(out_UIdata_converter_FU_4_i0_fu_icrc1_33778_33810),
    .in1(in_port_crc));
  bit_xor_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_in2(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33811 (.out1(out_bit_xor_expr_FU_16_16_16_14_i0_fu_icrc1_33778_33811),
    .in1(out_IIconvert_expr_FU_3_i0_fu_icrc1_33778_33809),
    .in2(out_UIdata_converter_FU_4_i0_fu_icrc1_33778_33810));
  IUdata_converter_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33812 (.out1(out_IUdata_converter_FU_5_i0_fu_icrc1_33778_33812),
    .in1(out_bit_xor_expr_FU_16_16_16_14_i0_fu_icrc1_33778_33811));
  UIdata_converter_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33840 (.out1(out_UIdata_converter_FU_8_i0_fu_icrc1_33778_33840),
    .in1(out_reg_1_reg_1));
  plus_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_in2(2),
    .BITSIZE_out1(16)) fu_icrc1_33778_33841 (.out1(out_plus_expr_FU_16_0_16_17_i0_fu_icrc1_33778_33841),
    .in1(out_UIdata_converter_FU_8_i0_fu_icrc1_33778_33840),
    .in2(out_const_1));
  bit_xor_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_in2(14),
    .BITSIZE_out1(16)) fu_icrc1_33778_33842 (.out1(out_bit_xor_expr_FU_16_0_16_13_i0_fu_icrc1_33778_33842),
    .in1(out_plus_expr_FU_16_0_16_17_i0_fu_icrc1_33778_33841),
    .in2(out_const_3));
  IUdata_converter_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33843 (.out1(out_IUdata_converter_FU_9_i0_fu_icrc1_33778_33843),
    .in1(out_bit_xor_expr_FU_16_0_16_13_i0_fu_icrc1_33778_33842));
  ui_plus_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_in2(1),
    .BITSIZE_out1(16)) fu_icrc1_33778_33844 (.out1(out_ui_plus_expr_FU_16_0_16_20_i0_fu_icrc1_33778_33844),
    .in1(out_reg_1_reg_1),
    .in2(out_const_4));
  ui_cond_expr_FU #(.BITSIZE_in1(1),
    .BITSIZE_in2(16),
    .BITSIZE_in3(16),
    .BITSIZE_out1(16)) fu_icrc1_33778_33845 (.out1(out_ui_cond_expr_FU_16_16_16_16_19_i0_fu_icrc1_33778_33845),
    .in1(out_ui_extract_bit_expr_FU_10_i0_fu_icrc1_33778_33909),
    .in2(out_IUdata_converter_FU_9_i0_fu_icrc1_33778_33843),
    .in3(out_ui_plus_expr_FU_16_0_16_20_i0_fu_icrc1_33778_33844));
  plus_expr_FU #(.BITSIZE_in1(32),
    .BITSIZE_in2(2),
    .BITSIZE_out1(32)) fu_icrc1_33778_33846 (.out1(out_plus_expr_FU_32_0_32_18_i0_fu_icrc1_33778_33846),
    .in1(out_reg_0_reg_0),
    .in2(out_const_1));
  read_cond_FU #(.BITSIZE_in1(1)) fu_icrc1_33778_33847 (.out1(out_read_cond_FU_11_i0_fu_icrc1_33778_33847),
    .in1(out_ne_expr_FU_32_0_32_16_i0_fu_icrc1_33778_33893));
  ne_expr_FU #(.BITSIZE_in1(32),
    .BITSIZE_in2(5),
    .BITSIZE_out1(1)) fu_icrc1_33778_33893 (.out1(out_ne_expr_FU_32_0_32_16_i0_fu_icrc1_33778_33893),
    .in1(out_plus_expr_FU_32_0_32_18_i0_fu_icrc1_33778_33846),
    .in2(out_const_2));
  ui_extract_bit_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_in2(4)) fu_icrc1_33778_33909 (.out1(out_ui_extract_bit_expr_FU_10_i0_fu_icrc1_33778_33909),
    .in1(out_reg_1_reg_1),
    .in2(out_const_5));
  register_SE #(.BITSIZE_in1(32),
    .BITSIZE_out1(32)) reg_0 (.out1(out_reg_0_reg_0),
    .clock(clock),
    .reset(reset),
    .in1(out_MUX_22_reg_0_0_0_0),
    .wenable(wrenable_reg_0));
  register_SE #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) reg_1 (.out1(out_reg_1_reg_1),
    .clock(clock),
    .reset(reset),
    .in1(out_MUX_23_reg_1_0_0_0),
    .wenable(wrenable_reg_1));
  // io-signal post fix
  assign return_port = out_reg_1_reg_1;
  assign OUT_CONDITION_icrc1_33778_33847 = out_read_cond_FU_11_i0_fu_icrc1_33778_33847;

endmodule

// FSM based controller description for icrc1
// This component has been derived from the input source code and so it does not fall under the copyright of PandA framework, but it follows the input source code copyright, and may be aggregated with components of the BAMBU/PANDA IP LIBRARY.
// Author(s): Component automatically generated by bambu
// License: THIS COMPONENT IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
`timescale 1ns / 1ps
module controller_icrc1(done_port,
  selector_MUX_22_reg_0_0_0_0,
  selector_MUX_23_reg_1_0_0_0,
  wrenable_reg_0,
  wrenable_reg_1,
  OUT_CONDITION_icrc1_33778_33847,
  clock,
  reset,
  start_port);
  // IN
  input OUT_CONDITION_icrc1_33778_33847;
  input clock;
  input reset;
  input start_port;
  // OUT
  output done_port;
  output selector_MUX_22_reg_0_0_0_0;
  output selector_MUX_23_reg_1_0_0_0;
  output wrenable_reg_0;
  output wrenable_reg_1;
  parameter [2:0] S_0 = 3'b001,
    S_1 = 3'b010,
    S_2 = 3'b100;
  reg [2:0] _present_state=S_0, _next_state;
  reg done_port;
  reg selector_MUX_22_reg_0_0_0_0;
  reg selector_MUX_23_reg_1_0_0_0;
  reg wrenable_reg_0;
  reg wrenable_reg_1;
  
  always @(posedge clock)
    if (reset == 1'b0) _present_state <= S_0;
    else _present_state <= _next_state;
  
  always @(*)
  begin
    done_port = 1'b0;
    selector_MUX_22_reg_0_0_0_0 = 1'b0;
    selector_MUX_23_reg_1_0_0_0 = 1'b0;
    wrenable_reg_0 = 1'b0;
    wrenable_reg_1 = 1'b0;
    case (_present_state)
      S_0 :
        if(start_port == 1'b1)
        begin
          selector_MUX_22_reg_0_0_0_0 = 1'b1;
          selector_MUX_23_reg_1_0_0_0 = 1'b1;
          wrenable_reg_0 = 1'b1;
          wrenable_reg_1 = 1'b1;
          _next_state = S_1;
        end
        else
        begin
          _next_state = S_0;
        end
      S_1 :
        begin
          wrenable_reg_0 = 1'b1;
          wrenable_reg_1 = 1'b1;
          if (OUT_CONDITION_icrc1_33778_33847 == 1'b1)
            begin
              _next_state = S_1;
            end
          else
            begin
              _next_state = S_2;
              done_port = 1'b1;
              wrenable_reg_0 = 1'b0;
            end
        end
      S_2 :
        begin
          _next_state = S_0;
        end
      default :
        begin
          _next_state = S_0;
        end
    endcase
  end
endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Marco Lattuada <marco.lattuada@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module flipflop_AR(clock,
  reset,
  in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input clock;
  input reset;
  input in1;
  // OUT
  output out1;
  
  reg reg_out1 =0;
  assign out1 = reg_out1;
  always @(posedge clock )
    if (reset == 1'b0)
      reg_out1 <= {BITSIZE_out1{1'b0}};
    else
      reg_out1 <= in1;
endmodule

// Top component for icrc1
// This component has been derived from the input source code and so it does not fall under the copyright of PandA framework, but it follows the input source code copyright, and may be aggregated with components of the BAMBU/PANDA IP LIBRARY.
// Author(s): Component automatically generated by bambu
// License: THIS COMPONENT IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
`timescale 1ns / 1ps
module _icrc1(clock,
  reset,
  start_port,
  done_port,
  crc,
  onech,
  return_port);
  // IN
  input clock;
  input reset;
  input start_port;
  input [15:0] crc;
  input [7:0] onech;
  // OUT
  output done_port;
  output [15:0] return_port;
  // Component and signal declarations
  wire OUT_CONDITION_icrc1_33778_33847;
  wire done_delayed_REG_signal_in;
  wire done_delayed_REG_signal_out;
  wire selector_MUX_22_reg_0_0_0_0;
  wire selector_MUX_23_reg_1_0_0_0;
  wire wrenable_reg_0;
  wire wrenable_reg_1;
  
  controller_icrc1 Controller_i (.done_port(done_delayed_REG_signal_in),
    .selector_MUX_22_reg_0_0_0_0(selector_MUX_22_reg_0_0_0_0),
    .selector_MUX_23_reg_1_0_0_0(selector_MUX_23_reg_1_0_0_0),
    .wrenable_reg_0(wrenable_reg_0),
    .wrenable_reg_1(wrenable_reg_1),
    .OUT_CONDITION_icrc1_33778_33847(OUT_CONDITION_icrc1_33778_33847),
    .clock(clock),
    .reset(reset),
    .start_port(start_port));
  datapath_icrc1 Datapath_i (.return_port(return_port),
    .OUT_CONDITION_icrc1_33778_33847(OUT_CONDITION_icrc1_33778_33847),
    .clock(clock),
    .reset(reset),
    .in_port_crc(crc),
    .in_port_onech(onech),
    .selector_MUX_22_reg_0_0_0_0(selector_MUX_22_reg_0_0_0_0),
    .selector_MUX_23_reg_1_0_0_0(selector_MUX_23_reg_1_0_0_0),
    .wrenable_reg_0(wrenable_reg_0),
    .wrenable_reg_1(wrenable_reg_1));
  flipflop_AR #(.BITSIZE_in1(1),
    .BITSIZE_out1(1)) done_delayed_REG (.out1(done_delayed_REG_signal_out),
    .clock(clock),
    .reset(reset),
    .in1(done_delayed_REG_signal_in));
  // io-signal post fix
  assign done_port = done_delayed_REG_signal_out;

endmodule

// This component is part of the BAMBU/PANDA IP LIBRARY
// Copyright (C) 2004-2023 Politecnico di Milano
// Author(s): Fabrizio Ferrandi <fabrizio.ferrandi@polimi.it>
// License: PANDA_LGPLv3
`timescale 1ns / 1ps
module ui_view_convert_expr_FU(in1,
  out1);
  parameter BITSIZE_in1=1,
    BITSIZE_out1=1;
  // IN
  input [BITSIZE_in1-1:0] in1;
  // OUT
  output [BITSIZE_out1-1:0] out1;
  assign out1 = in1;
endmodule

// Minimal interface for function: icrc1
// This component has been derived from the input source code and so it does not fall under the copyright of PandA framework, but it follows the input source code copyright, and may be aggregated with components of the BAMBU/PANDA IP LIBRARY.
// Author(s): Component automatically generated by bambu
// License: THIS COMPONENT IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
`timescale 1ns / 1ps
module icrc1(clock,
  reset,
  start_port,
  crc,
  onech,
  done_port,
  return_port);
  // IN
  input clock;
  input reset;
  input start_port;
  input [15:0] crc;
  input [7:0] onech;
  // OUT
  output done_port;
  output [15:0] return_port;
  // Component and signal declarations
  wire [15:0] out_return_port_ui_view_convert_expr_FU;
  
  _icrc1 _icrc1_i0 (.done_port(done_port),
    .return_port(out_return_port_ui_view_convert_expr_FU),
    .clock(clock),
    .reset(reset),
    .start_port(start_port),
    .crc(crc),
    .onech(onech));
  ui_view_convert_expr_FU #(.BITSIZE_in1(16),
    .BITSIZE_out1(16)) return_port_ui_view_convert_expr_FU (.out1(return_port),
    .in1(out_return_port_ui_view_convert_expr_FU));

endmodule



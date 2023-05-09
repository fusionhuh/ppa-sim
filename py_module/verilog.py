import graph
from pathlib import Path

# {type,hybrid-levels}.width.{basic,ripple-block,cla-block,skip-block,select-block}
class adder:
    def __init__(self, description: str):
        assert description.count(".") == 2
        [adder_type, width, structure] = tuple(description.split("."))

        # 1) fill width information
        assert width.isdigit()
        self.width: int = int(width)

        # 2) fill adder type information
        type_info = adder_type.split("-")
        self.base_type: str = type_info[0]
        assert self.base_type in ["bk", "ks", "hybrid", "serial", "skl"]
        if len(type_info) == 2:
            assert self.base_type == "hybrid"
            assert type_info[1].isdigit()
            self.hybrid_levels: int = int(type_info[1])

        # 3) fill adder structure information
        structure_info = structure.split("-")
        self.structure: str = structure_info[0]
        assert self.structure in ["basic", "rc", "cla", "cskip", "cselect"]
        if self.structure == "basic":
            assert len(structure_info) == 1
            self.block_size: int = self.width
            self.block_count: int = 1

        else:
            assert len(structure_info) == 2
            if self.structure == "cla":
                assert int(structure_info[1]) == 4
                assert self.width == 16 or self.width == 64
            self.block_size: int = int(structure_info[1])
            self.block_count: int = self.width//self.block_size

        # 4) generate graph
        gen_function_name = "generate_{type}_graph".format(type=self.base_type)
        if self.base_type == "hybrid":
            self.graph: list = graph.get_globals()[gen_function_name](self.block_size, self.hybrid_levels)
        else:
            self.graph: list = graph.get_globals()[gen_function_name](self.block_size)
        graph.test_graph_completeness(self.block_size, self.graph)
        self.depth = len(self.graph)
        self.node_count = graph.get_node_count(self.graph)
        self.__calculate_gate_counts()

        # 5) update gate counts if structured adder
        if self.structure != "basic":
            self.node_count *= self.block_count
            self.nand_count *= self.block_count
            self.and_count *= self.block_count
            self.nor_count *= self.block_count
            self.or_count *= self.block_count
            self.not_count *= self.block_count
            self.transistor_count *= self.block_count

        self.verilog_base_name = "{type}{width}".format(type=self.base_type, width=self.block_size)
        if self.base_type == "hybrid":
            self.verilog_base_name += "_" + str(self.hybrid_levels)

        # 6) update verilog files (including dependencies) according to project file structure
        file = Path("verilog/base/{type}/{name}.v".format(type=self.base_type, name=self.verilog_base_name))
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(generate_basic_adder(self))      

        if self.structure != "basic":
            self.verilog_structured_name = "{type}_{width}_{structure}_{block_size}".format(type=self.base_type, width=self.width, structure=self.structure, block_size=self.block_size)   
            file = Path("verilog/structured/{structure}/{name}.v".format(structure=self.structure, name=self.verilog_structured_name))
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(generate_structured_adder(self))

    def __calculate_gate_counts(self):
        self.and_count: int = 0
        self.nand_count: int = 0
        self.or_count: int = 0
        self.nor_count: int = 0
        self.not_count: int = 0
        self.transistor_count: int = 0

        for i in range(1, self.depth):
            row: dict = self.graph[i]
            operator_list: list = [node for node in row.values() if node.is_operator]
            num_operators: int = len(operator_list)
            self.nand_count += num_operators
            self.nor_count += num_operators
            if i % 2 == 1: # negative layer
                self.and_count += num_operators
            else: # positive layer
                self.or_count += num_operators
            
            for o in operator_list:    
                pred_up: graph.node = o.pred_up
                pred_right: graph.node = o.pred_right
                if (o.level - pred_up.level) % 2 != 1:
                    self.not_count += 2
                if (o.level - pred_right.level) % 2 != 1:
                    self.not_count += 2

        sum_node_list = [graph.get_lowest_node(i, self.graph) for i in range(1, self.block_size)]
        negative_nodes = [node for node in sum_node_list if node.level % 2 == 1]
        self.not_count += len(negative_nodes)

        self.transistor_count = 6*self.or_count + 6*self.and_count + 4*self.nor_count + 4*self.nand_count + 2*self.not_count


def generate_adder_info_block(a: adder) -> str:
    info_block = "// number of levels: {levels}\n// number of nodes: {nodes}\n".format(levels=a.depth, nodes=a.node_count)
    info_block += "// NAND count: {nand_count}, AND count: {and_count}\n".format(nand_count=a.nand_count, and_count=a.and_count)
    info_block += "// NOR count: {nor_count}, OR count: {or_count}\n".format(nor_count=a.nor_count, or_count=a.or_count)
    info_block += "// NOT count: {not_count}, Transistor count: {transistor_count}\n".format(not_count=a.not_count, transistor_count=a.transistor_count)
    return info_block

def generate_port_declare_block(width: int, group_signals: bool = True) -> str:
    declare_block = "\tinput[{len}:0]x1;\n".format(len=width-1)
    declare_block += "\tinput[{len}:0]x2;\n".format(len=width-1)
    declare_block += "\tinput cin;\n"
    declare_block += "\twire[{len}:0]p_in;\n".format(len=width-1)
    declare_block += "\twire[{len}:0]g_in;\n".format(len=width-1)
    declare_block += "\toutput[{len}:0]s;\n".format(len=width-1)
    if group_signals:
        declare_block += "\toutput cout, g_out, p_out;\n\n"
    else:
        declare_block += "\toutput cout;\n\n"
    return declare_block 

def generate_module_declaration(module_name: str, group_signals: bool = True):
    if group_signals:
        return "module {module_name}(x1, x2, s, cin, cout, p_out, g_out);\n".format(module_name=module_name)
    else:
        return f"module {module_name}(x1, x2, s, cin, cout);\n"


def generate_structured_adder(a: adder):
    def generate_rc_adder():
        include_block = "`include \"{name}.v\"\n".format(name=a.verilog_base_name)
        module_definition: str = include_block
        module_definition += generate_adder_info_block(a)
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        for i in range(0, a.block_count):
            block_declaration = "\twire block{num}_cout;\n".format(num=i)
            bit_slice_range = "[{a}:{b}]".format(a=a.block_size*i + a.block_size-1, b=a.block_size*i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            cin = ".cin(cin)" if i == 0 else ".cin(block{num}_cout)".format(num=i-1)
            cout = ".cout(cout)" if i == a.block_count-1 else ".cout(block{num}_cout)".format(num=i)
            block_declaration += "\t{base_name} block{num}({x1x2s}, {cin}, {cout});\n".format(base_name=a.verilog_base_name, num=i, x1x2s=x1x2s, cin=cin, cout=cout)
            module_definition += block_declaration
        module_definition += "endmodule\n"
        return module_definition

    def generate_cskip_adder():
        include_block = "`include \"{name}.v\"\n".format(name=a.verilog_base_name)
        module_definition: str = include_block
        module_definition += generate_adder_info_block(a)
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        module_definition += "\twire[{width}:0]p = x1 ^ x2;\n\n".format(width=a.width-1)   
        for i in range(0, a.block_count):
            block_cout = "block{num}_cout".format(num=i)
            real_cout = "block{num}_real_cout".format(num=i)
            group_p = "block{num}_group_p".format(num=i)
            block_cin: str
            if i == 0:
                block_cin = "cin"
            else:
                block_cin = "block{num}_real_cout".format(num=i-1)

            bit_slice_range = "[{a}:{b}]".format(a=a.block_size*i + a.block_size-1, b=a.block_size*i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            block_declaration = "\t{base_name} block{num}({x1x2s}, .cin({cin}), .cout({cout}));\n".format(base_name=a.verilog_base_name, num=i, x1x2s=x1x2s, cin=block_cin, cout=block_cout)
            p_and_declaration = "\tand gate{num}({group_p}, p{bit_slice_range});\n".format(num=i, group_p=group_p, bit_slice_range=bit_slice_range)
            mux_statement = "\tassign {real_cout} = {group_p} ? {cin} : {block_cout};\n\n".format(real_cout=real_cout, group_p=group_p, cin=block_cin, block_cout=block_cout)

            module_definition += "\twire {block_cout};\n".format(block_cout=block_cout)
            module_definition += block_declaration
            module_definition += "\twire {real_cout};\n".format(real_cout=real_cout)
            module_definition += "\twire {group_p};\n".format(group_p=group_p)
            module_definition += p_and_declaration
            module_definition += mux_statement
            if i == a.block_count - 1:
                module_definition += "\tassign cout = {real_cout};\n".format(real_cout=real_cout)

        module_definition += "endmodule\n"
        return module_definition

    def generate_cla_adder():
        # theoretical steps for two-level, 16-bit adder block design:
        # 1) create 16-bit adder module with four 4-bit adder blocks each
        # 2) if desired adder is 16 bits, instantiate module and stop here
        # 3) if desired adder is 64 bits, instantiate 4 and chain together with 4 bit cla
        include_block = "`ifndef {up_name}\n`include \"{type}/{name}.v\"\n`endif\n".format(type=a.base_type, up_name=a.verilog_base_name.upper(), name=a.verilog_base_name)
        include_block += "`ifndef {up_name}\n`include \"{name}.v\"\n`endif\n".format(up_name="cla4".upper(), name="cla4")
        include_block += "`ifndef {up_name}\n`include \"{name}.v\"\n`endif\n".format(up_name="block_signals4".upper(), name="block_signals4")
        subadder_name = "_16bit_subadd"
        include_block += "`ifndef {up_name}\n`include \"{name}.v\"\n`endif\n".format(up_name=subadder_name.upper(), name=subadder_name)
        """
        subadder_definition: str = "module {name}(x1, x2, s, cin, cout, p_out, g_out);\n".format(name=subadder_name)
        subadder_definition += generate_port_declare_block(16)
        subadder_definition += "\toutput p_out, g_out;\n\n"
        if a.base_type == "serial":
            subadder_definition += "\tassign p_in = x1 ^ x2;\n"
            subadder_definition += "\tassign g_in = x1 & x2;\n"
        for i in range(0, 4):
            bit_slice_range = "[{a}:{b}]".format(a=4*i + 4-1, b=4*i)
            subadder_definition += "\twire adder{num}_cin;\n\twire adder{num}_cout;\n".format(num=i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            pg = ".p_out(p_in{bit_slice_range}), .g_out(g_in{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            cin = ".cin(adder{num}_cin)".format(num=i)
            if a.base_type != "serial":
                subadder_definition += "\t{type} adder{num}({x1x2s}, {pg}, {cin});\n".format(type=a.verilog_base_name, num=i, x1x2s=x1x2s, pg=pg, cin=cin)
            else:
                subadder_definition += "\t{type} adder{num}({x1x2s}, {cin});\n".format(type=a.verilog_base_name, num=i, x1x2s=x1x2s, cin=cin)
            group_pout = "adder{num}_p_out".format(num=i)
            group_gout = "adder{num}_g_out".format(num=i)
            subadder_definition += "\twire {pout};\n".format(pout=group_pout)
            subadder_definition += "\twire {gout};\n".format(gout=group_gout)
            pg = ".g_in(g_in{bit_slice_range}), .p_in(p_in{bit_slice_range}), .p_out({group_pout}), .g_out({group_gout})".format(bit_slice_range=bit_slice_range, group_gout=group_gout, group_pout=group_pout)
            subadder_definition += "\tblock_signals4 block{num}({pg});\n\n".format(num=i, pg=pg)
        subadder_definition += "\twire[3:0]cla_cout;\n"
        cla_p: str = "{adder3_p_out, adder2_p_out, adder1_p_out, adder0_p_out}"
        cla_g: str = "{adder3_g_out, adder2_g_out, adder1_g_out, adder0_g_out}"
        cla_cin: str = "cin"
        subadder_definition += "\tcla4 cla_block(.p_in({p}), .g_in({g}), .cin({cin}), .cout(cla_cout), .p_out(p_out), .g_out(g_out));\n".format(p=cla_p, g=cla_g, cin=cla_cin)
        for i in range(0, 4):
            subadder_definition += "\tassign adder{num}_cin = cla_cout[{num}];\n".format(num=i)
        subadder_definition += "endmodule\n"
        """
        module_definition: str = include_block
        #module_definition += "\n" + subadder_definition + "\n\n"
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        if a.width == 16:
            module_definition += "\t{subadder_name} adder(.x1(x1), .x2(x2), .s(s), .cin(cin), .cout(cout));\n".format(subadder_name=subadder_name)
            module_definition += "endmodule\n"
        else:
            # process:
            # 1) declare each of the four 16-bit adders with wire connections from
            # g/p_out and cin
            # 2) wire them up to 4-bit cla generator after 
            for i in range(0, 4):
                cin = f"adder{i}_cin"
                g_out = f"adder{i}_g_out"
                p_out = f"adder{i}_p_out"
                module_definition += f"\twire {cin};\n"
                module_definition += f"\twire {g_out};\n"
                module_definition += f"\twire {p_out};\n"
                bit_range = f"[{16*i + 15}:{16*i}]"
                module_definition += f"\t{subadder_name} adder{i}(.x1(x1{bit_range}), .x2(x2{bit_range}), .s(s{bit_range}), .cin({cin}), .p_out({p_out}), .g_out({g_out}));\n\n"
            module_definition += "\twire[3:0]cla_cout;\n"
            cla_p: str = "{adder3_p_out, adder2_p_out, adder1_p_out, adder0_p_out}"
            cla_g: str = "{adder3_g_out, adder2_g_out, adder1_g_out, adder0_g_out}"
            cla_cin: str = "cin"
            module_definition += "\tcla4 cla_block(.p_in({p}), .g_in({g}), .cin({cin}), .cout(cla_cout), .p_out(p_out), .g_out(g_out));\n".format(p=cla_p, g=cla_g, cin=cla_cin)
            for i in range(0, 4):
                module_definition += f"\tassign adder{i}_cin = cla_cout[{i}];\n"
            module_definition += "endmodule\n"
        return module_definition

    def generate_cselect_adder():
        pass

    func_name = "generate_{structure}_adder".format(structure=a.structure)
    text = locals()[func_name]()
    return text

def generate_basic_adder(a: adder):
    def invert(wire: str) -> str:
        return "~" + wire

    def generate_input_ports(pred: graph.node, curr: graph.node) -> tuple: # returns [p, g]
        g: str
        p: str

        if pred.level == 0: 
            p = "p_in[{bit_pos}]".format(bit_pos=pred.bit_pos)
            g = "g_in[{bit_pos}]".format(bit_pos=pred.bit_pos)
            if (curr.level - pred.level) % 2 == 0:
                g = invert(g)
                p = invert(p)
        else:
            p = "node_level{level}_pos{bit_pos}_outp".format(level=pred.level, bit_pos=pred.bit_pos)
            g = "node_level{level}_pos{bit_pos}_outg".format(level=pred.level, bit_pos=pred.bit_pos)
            if (curr.level - pred.level) % 2 == 0:
                g = invert(g)
                p = invert(p)

        return [p, g]

    include_block: str = """`ifndef CARRY_OPERATOR\n`include \"carry_operator.v\"\n`endif\n`ifndef NEG_CARRY_OPERATOR\n`include \"neg_operator.v\"\n`endif\n`ifndef POS_CARRY_OPERATOR\n`include \"pos_operator.v\"\n`endif\n"""
    include_block += "`define {name}\n".format(name=a.verilog_base_name.upper())

    info_block = generate_adder_info_block(a)

    module_definition: str = ""
    module_name: str
    if a.base_type == "hybrid":
        module_name = "{adder_type}{bit_width}_{hybrid_levels}".format(adder_type=a.base_type, bit_width=a.block_size, hybrid_levels=a.hybrid_levels)
    else:
        module_name = "{adder_type}{bit_width}".format(adder_type=a.base_type, bit_width=a.block_size)
    module_definition += generate_module_declaration(a.verilog_base_name)
    module_definition += generate_port_declare_block(a.block_size, False)
    module_definition += "\toutput[{len}:0]p_out;\n\toutput[{len}:0]g_out;\n".format(len=a.block_size-1)
    module_definition += "\tassign p_in = x1 ^ x2;\n\tassign p_out = p_in;\n"
    module_definition += "\tassign g_in[{len}:1] = x1[{len}:1] & x2[{len}:1];\n".format(len=a.block_size-1)
    module_definition += "\tassign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);\n"
    module_definition += "\tassign g_out = g_in;\n"
    for level in range(1, a.depth):
        row = a.graph[level]
        for bit_pos, curr in row.items():
            if curr.is_operator == False or curr.level != level: continue

            pred_up = curr.pred_up
            pred_right = curr.pred_right

            up_connection: str
            right_connection: str

            output_declaration = "\twire node_level{level}_pos{bit_pos}_outg;\n".format(level=curr.level, bit_pos=curr.bit_pos)
            output_declaration += "\twire node_level{level}_pos{bit_pos}_outp;\n".format(level=curr.level, bit_pos=curr.bit_pos)

            module_definition += output_declaration

            [p1, g1] = generate_input_ports(pred_up, curr)
            up_connection: str = ".p1({p1}), .g1({g1})".format(p1=p1, g1=g1)

            [p0, g0] = generate_input_ports(pred_right, curr)
            right_connection: str = ".p0({p0}), .g0({g0})".format(p0=p0, g0=g0)

            output_connection = ".gp(node_level{level}_pos{bit_pos}_outg), .pp(node_level{level}_pos{bit_pos}_outp)".format(level=curr.level, bit_pos=curr.bit_pos)

            operator_type: str = "neg_operator" if level % 2 == 1 else "pos_operator"

            operator_declaration = "\t{type} node_level{level}_pos{bit_pos}".format(type=operator_type, level=level, bit_pos=bit_pos)
            operator_declaration = operator_declaration + "({up}, {right}, {output})".format(up=up_connection, right=right_connection, output=output_connection)

            operator_declaration += ";\n"
            module_definition += operator_declaration
    
    module_definition += "\n\n\tassign s[0] = p_in[0] ^ cin;\n"

    for bit_pos in range(1, a.block_size):
        cur_level = a.depth-1
        sum: str = "p_in[{index}]".format(index=bit_pos)
        carry_node: graph.node = graph.get_lowest_node(bit_pos-1, a.graph)
        carry: str
        if carry_node.is_operator == False:
            carry = "g_in[{index}]".format(index=bit_pos-1)
        else:
            carry = "node_level{level}_pos{pos}_outg".format(level=carry_node.level, pos=carry_node.bit_pos)
        
        if carry_node.level > 0 and carry_node.level % 2 == 1:
            carry = invert(carry)

        output_connection = "\tassign s[{bit_pos}] = {sum} ^ {carry};\n".format(bit_pos=bit_pos, sum=sum, carry=carry)
        module_definition += output_connection

    module_definition += "\tassign cout = (x1[{len}] & x2[{len}]) | (~s[{len}] & (x1[{len}] | x2[{len}]));\n".format(len=a.block_size-1)
    
    module_definition += "endmodule\n"

    text = include_block + info_block + module_definition
    return text
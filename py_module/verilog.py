import graph
from pathlib import Path
import math
import os


BASE_ADDER_DESIGNS = ["bk", "ks", "hybrid", "serial", "skl"]
SPECIAL_BASE_ADDERS = ["hybrid"]
STRUCTURED_ADDER_DESIGNS = ["basic", "rc", "cla", "cskip", "cselect"]

test_cases: list = [{"x1" : 10, "x2" : 20, "cin" : 1}, {"x1" : 1, "x2" : -1, "cin" : 0}]

# {type,hybrid-levels}.width.{basic,ripple-block,cla-block,skip-block,select-block}
class adder:
    def __init__(self, description: str, test: bool = False):
        assert description.count(".") == 2
        [adder_type, width, structure] = tuple(description.split("."))

        # 1) fill width information
        assert width.isdigit()
        self.width: int = int(width)

        # 2) fill adder type information
        type_info = adder_type.split("-")
        self.base_type: str = type_info[0]
        assert self.base_type in BASE_ADDER_DESIGNS
        if len(type_info) == 2:
            assert self.base_type == "hybrid"
            assert type_info[1].isdigit()
            self.hybrid_levels: int = int(type_info[1])

        # 3) fill adder structure information
        structure_info = structure.split("-")
        self.structure: str = structure_info[0]
        assert self.structure in STRUCTURED_ADDER_DESIGNS
        if self.structure == "basic":
            assert len(structure_info) == 1
            self.block_size: int = self.width
            self.block_count: int = 1
        else:
            assert len(structure_info) == 2
            self.block_size: int = int(structure_info[1])
            self.block_count: int = self.width//self.block_size
            if self.structure == "cla":
                assert self.block_size == 4
                assert self.width == 16 or self.width == 64
            if self.structure == "cselect":
                assert self.block_count == 2 or self.block_count == 4

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

        # 6) test + update basic adder

        # lazily assume desired adder is just base type, could probably refactor to be cleaner later
        self.verilog_file_path = f"verilog/base/{self.base_type}/{self.verilog_base_name}.v"
        self.verilog_text = generate_basic_adder(self)
        file = Path("verilog/base/{type}/{name}.v".format(type=self.base_type, name=self.verilog_base_name))
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(self.verilog_text)   
        if test:
            # uglyyyyyyy asf
            old_structure = self.structure
            self.structure = "basic"
            test_adder(self, test_cases)
            self.structure = old_structure

        # 7) dependencies, filename, and structured adder testing
        dependency_list: list = ["pos_operator.v", "neg_operator.v", "carry_operator.v"]
        if self.structure != "basic":
            if self.structure == "cla":
                dependency_list.append("cla4.v")
                dependency_list.append("block_signals4.v")
            self.dependencies: list = ["verilog/logic/" + file for file in dependency_list]
            self.verilog_structured_name = f"{self.base_type}_{self.width}_{self.structure}_{self.block_size}"
            self.verilog_file_path = f"verilog/structured/{self.structure}/{self.verilog_structured_name}.v"
            self.dependencies.append(f"verilog/base/{self.base_type}/{self.verilog_base_name}.v")
            self.dependencies.append(self.verilog_file_path)
            file = Path(self.verilog_file_path)
            file.parent.mkdir(parents=True, exist_ok=True)
            self.verilog_text = generate_structured_adder(self)
            file.write_text(self.verilog_text)

            if test:
                test_adder(self, test_cases)
        else:
            self.dependencies: list = ["verilog/logic/" + file for file in dependency_list]
            self.dependencies.append(self.verilog_file_path)
            # no need to test because we already tested before




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


def generate_base_adder_declaration(a: adder, name: str, ports: dict) -> str:
    port_list: list = [f".{pair[0]}({pair[1]})" for pair in ports.items()]
    port_list = ", ".join(port_list)
    return f"\t{a.verilog_base_name} {name}({port_list});\n"
        
def generate_include_block(dependencies: list) -> str:
    text: str = ""
    for dep in dependencies:
        text += "`ifndef {macro}\n`include \"{file}\"\n`endif\n".format(macro=dep.upper(), file=dep+".v")
    return text

def generate_wires(wires: list) -> str:
    text: str = ""
    for wire in wires:
        if isinstance(wire, tuple):
            width = wire[1]
            text += f"\twire[{width-1}:0] {wire[0]};\n"
        else:
            text += f"\twire {wire};\n"
    return text

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
        module_definition: str = generate_include_block([a.verilog_base_name])
        module_definition += generate_adder_info_block(a)
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        for i in range(0, a.block_count):
            block_cout = f"block{i}_cout"
            module_definition += generate_wires([block_cout])
            bit_slice_range = "[{a}:{b}]".format(a=a.block_size*i + a.block_size-1, b=a.block_size*i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            cin = ".cin(cin)" if i == 0 else ".cin(block{num}_cout)".format(num=i-1)
            cout = ".cout(cout)" if i == a.block_count-1 else ".cout(block{num}_cout)".format(num=i)
            block_declaration = "\t{base_name} block{num}({x1x2s}, {cin}, {cout});\n".format(base_name=a.verilog_base_name, num=i, x1x2s=x1x2s, cin=cin, cout=cout)
            module_definition += block_declaration
        module_definition += "endmodule\n"
        return module_definition

    def generate_cskip_adder():
        module_definition: str = generate_include_block([a.verilog_base_name])
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
        subadder_name = "_16bit_subadd"
        include_block = generate_include_block([a.verilog_base_name, "cla4", "block_signals4"])

        module_definition: str = include_block
        subadder_file = open("verilog/logic/" + subadder_name + ".v", "r")
        subadder_text = subadder_file.read()
        subadder_text = subadder_text.format(type=a.verilog_base_name)
        module_definition += subadder_text
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        subadder_name += f"_{a.verilog_base_name}"
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
                module_definition += generate_wires([cin, g_out, p_out])
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
        # process:
        # 1) assign a positional index to each adder block
        # 2) place two adders every block except on first block
        # 3) place two muxes on the 2nd level every 2 block except on the first placement
        # 4) place two muxes on the 3rd level every 4 blocks, except on the first placement
        module_definition: str = generate_include_block([a.verilog_base_name])
        module_definition += generate_module_declaration(a.verilog_structured_name, False)
        module_definition += generate_port_declare_block(a.width, False)
        lowest_depth: int = int(math.log(a.block_count, 2) + 1)

        sum_wires: list = []
        for i in range(0, a.block_count):
            bit_range = [(i+1) * a.block_size - 1, i*a.block_size]
            bit_range_str = f"[{bit_range[0]}:{bit_range[1]}]"
            ports: dict = {
                "x1" : "x1" + bit_range_str,
                "x2" : "x2" + bit_range_str,
                "s"  : "s" + bit_range_str,
                "cin" : "cin",
                "cout" : "<fill>"
            }
            if i == 0:
                adder_name = "component_level0_pos0_cin0"
                module_definition += generate_wires([adder_name + "_cout"])
                ports["cout"] = adder_name + "_cout"
                module_definition += generate_base_adder_declaration(a, adder_name, ports)
            else:
                for cin in ["0", "1"]:
                    adder_name = f"component_level0_pos{i}_cin{cin}"
                    adder_cout = adder_name + "_cout"
                    adder_out = adder_name + "_out"
                    module_definition += generate_wires([adder_cout, (adder_out, a.block_size)])
                    ports["cin"] = "1'b" + cin
                    ports["cout"] = adder_cout
                    ports["s"] = adder_out
                    module_definition += generate_base_adder_declaration(a, adder_name, ports)

            for k in [2**j for j in range(1, lowest_depth+1)]:
                if (i+1) % k == 0 and i != 0:
                    mux_span = k//2
                    # if not first mux, make two muxes to connect to both adders with
                    # cin = 0/1
                    # for mux '0' in, seem to connect from lowest component associated with cin 0,
                    # i.e. adder with cin 0 or mux that takes in selection bit from adder with cin 0
                    mux_in0: list = []
                    mux_in1: list = []
                    # ^ list of strings representing components- a:b:c, where a is the level, b is the pos,
                    # and c is the cin
                    step_sequence = []
                    step_sequence.append(1)
                    for l in range(0, mux_span-1):
                        step_sequence.append(2**l)
                    pos = i
                    level: int = int(math.log(k, 2))
                    curr_level = level-1
                    while pos > i - mux_span:
                        assert curr_level >= 0
                        # do our thing...
                        component0: tuple = [curr_level, pos, 0]
                        component1: tuple = [curr_level, pos, 1]
                        mux_in0.append(component0)
                        mux_in1.append(component1)
                        curr_level -= 1
                        pos -= step_sequence.pop()
                    mux_concat_list0 = [f"component_level{component[0]}_pos{component[1]}_cin{component[2]}_out" for component in mux_in0]
                    mux_concat_list1 = [f"component_level{component[0]}_pos{component[1]}_cin{component[2]}_out" for component in mux_in1]

                    if i+1 == a.block_count and k == 2:
                        mux_concat_list0.insert(0, f"component_level0_pos{i}_cin0_cout")
                        mux_concat_list1.insert(0, f"component_level0_pos{i}_cin1_cout")

                    mux_in0 = "{{{list}}}".format(list=", ".join(mux_concat_list0))
                    mux_in1 = "{{{list}}}".format(list=", ".join(mux_concat_list1))
                    mux0_name = f"component_level{level}_pos{i}_cin0"
                    mux0_control = f"component_level{level-1}_pos{i-mux_span}_cin0_cout" # mux will always take in select bit from first mux on prev level
                    mux0_out = mux0_name + "_out"
                    width = mux_span * a.block_size if i + 1 != a.block_count else mux_span * a.block_size + 1
                    module_definition += generate_wires([(mux0_out, width)])
                    mux0_statement = f"\tassign {mux0_out} = {mux0_control} ? {mux_in1} : {mux_in0};\n"
                    module_definition += mux0_statement + "\n"
                    if i+1 > k:
                        mux1_name = f"component_level{level}_pos{i}_cin1"
                        mux1_control = f"component_level{level-1}_pos{i-mux_span}_cin1_cout"
                        mux1_out = mux1_name + "_out"
                        module_definition += generate_wires([mux1_out, width])
                        mux1_statement = f"\tassign {mux1_name} = {mux1_control} ? {mux_in1} : {mux_in0};\n"
                        module_definition += mux1_statement + "\n"
                    elif i+1 == k:
                        sum_wires.insert(0, mux0_out)
                    module_definition += "\n\n"
        module_definition += generate_wires([("sum", a.width+1 - a.block_size)])
        module_definition += "\tassign sum = {{{sum_wires}}};\n".format(sum_wires=", ".join(sum_wires))
        module_definition += f"\tassign cout = sum[{a.width}];\n"
        module_definition += f"\tassign s[{a.width-1}:{a.block_size}] = sum[{a.width-1-a.block_size}:{0}];\n"
        module_definition += "endmodule\n"
        return module_definition
                    
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


def test_adder(a: adder, test_cases: list):
    text = a.verilog_text
    if compile_verilog(text) == False:
        print("Generated code could not compile correctly, exiting...")
        exit()
    

    assert len(test_cases) > 0
    tb_template = open("verilog/testbench_template.txt", "r")
    tb_template_text = tb_template.read()
    tb_template.close()

    adder_name: str = a.verilog_base_name if a.structure == "basic" else a.verilog_structured_name


    test_cases_text: str = ""
    count = 1
    for test in test_cases:
        assert isinstance(test, dict)
        x1 = test["x1"]
        x2 = test["x2"]
        cin = test["cin"]
        assert cin == 0 or cin == 1
        expected_s = x1 + x2 + cin
        # assuming no overflow currently

        test_cases_text += f"\t\t// test case {count}\n"
        test_cases_text += f"\t\tx1 = {x1};\n"
        test_cases_text += f"\t\tx2 = {x2};\n"
        test_cases_text += f"\t\tcin = {cin};\n"
        test_cases_text += "\t\t#100;\n\n\n"
        test_cases_text += f"\t\tif (s != {expected_s}) $finish;\n"

        count += 1
    tb_text = tb_template_text.format(dependency=a.verilog_file_path.replace("verilog/structured/", ""), width=a.width, adder=adder_name, tests=test_cases_text)


    if compile_verilog(tb_text) == False:
        print("Testbench could not compile correctly, exiting...")
        exit()

    tb = open("verilog/tb.v", "w+")
    tb.write(tb_text)
    tb.close()

    os.system("make run_test")
    os.system("make compile_test_clean > /dev/null")

def compile_verilog(text: str) -> bool:
    test = open("verilog/test.v", "w+")
    test.write(text)
    test.close()
    result = os.system("make compile_test > /dev/null")
    return result == 0

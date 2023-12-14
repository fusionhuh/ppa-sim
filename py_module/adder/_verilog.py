import sys
from ._graph import node, get_lowest_node
import math
import os
import re

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

def generate_adder_info_block(adder_info: dict) -> str:
    info_block = "// number of levels: {levels}\n// number of nodes: {nodes}\n".format(levels=adder_info["depth"], nodes=adder_info["node_count"])
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


def generate_structured_adder(adder_info: dict):
    verilog_base_name: str = adder_info["verilog_base_name"]
    verilog_structured_name: str = adder_info["verilog_structured_name"]
    width: int = adder_info["width"]
    block_count: int = adder_info["block_count"]
    block_size: int = adder_info["block_size"]
    structure: str = adder_info["structure"]

    def generate_rc_adder():
        module_definition: str = generate_include_block([verilog_base_name])
        module_definition += generate_adder_info_block(adder_info)
        module_definition += generate_module_declaration(verilog_structured_name, False)
        module_definition += generate_port_declare_block(width, False)
        for i in range(0, block_count):
            block_cout = f"block{i}_cout"
            module_definition += generate_wires([block_cout])
            bit_slice_range = "[{a}:{b}]".format(a=block_size*i + block_size-1, b=block_size*i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            cin = ".cin(cin)" if i == 0 else ".cin(block{num}_cout)".format(num=i-1)
            cout = ".cout(cout)" if i == block_count-1 else ".cout(block{num}_cout)".format(num=i)
            block_declaration = "\t{base_name} block{num}({x1x2s}, {cin}, {cout});\n".format(base_name=verilog_base_name, num=i, x1x2s=x1x2s, cin=cin, cout=cout)
            module_definition += block_declaration
        module_definition += "endmodule\n"
        return module_definition

    def generate_cskip_adder():
        module_definition: str = generate_include_block([verilog_base_name])
        module_definition += generate_adder_info_block(adder_info)
        module_definition += generate_module_declaration(verilog_structured_name, False)
        module_definition += generate_port_declare_block(width, False)
        module_definition += "\twire[{width}:0]p = x1 ^ x2;\n\n".format(width=width-1)   
        for i in range(0, block_count):
            block_cout = "block{num}_cout".format(num=i)
            real_cout = "block{num}_real_cout".format(num=i)
            group_p = "block{num}_group_p".format(num=i)
            block_cin: str
            if i == 0:
                block_cin = "cin"
            else:
                block_cin = "block{num}_real_cout".format(num=i-1)

            bit_slice_range = "[{a}:{b}]".format(a=block_size*i + block_size-1, b=block_size*i)
            x1x2s = ".x1(x1{bit_slice_range}), .x2(x2{bit_slice_range}), .s(s{bit_slice_range})".format(bit_slice_range=bit_slice_range)
            block_declaration = "\t{base_name} block{num}({x1x2s}, .cin({cin}), .cout({cout}));\n".format(base_name=verilog_base_name, num=i, x1x2s=x1x2s, cin=block_cin, cout=block_cout)
            p_and_declaration = "\tand gate{num}({group_p}, p{bit_slice_range});\n".format(num=i, group_p=group_p, bit_slice_range=bit_slice_range)
            mux_statement = "\tassign {real_cout} = {group_p} ? {cin} : {block_cout};\n\n".format(real_cout=real_cout, group_p=group_p, cin=block_cin, block_cout=block_cout)
            
            module_definition += "\twire {block_cout};\n".format(block_cout=block_cout)
            module_definition += block_declaration
            module_definition += "\twire {real_cout};\n".format(real_cout=real_cout)
            module_definition += "\twire {group_p};\n".format(group_p=group_p)
            module_definition += p_and_declaration
            module_definition += mux_statement
            if i == block_count - 1:
                module_definition += "\tassign cout = {real_cout};\n".format(real_cout=real_cout)

        module_definition += "endmodule\n"
        return module_definition

    def generate_cla_adder():
        # theoretical steps for two-level, 16-bit adder block design:
        # 1) create 16-bit adder module with four 4-bit adder blocks each
        # 2) if desired adder is 16 bits, instantiate module and stop here
        # 3) if desired adder is 64 bits, instantiate 4 and chain together with 4 bit cla
        subadder_name = "_16bit_subadd"
        include_block = generate_include_block([verilog_base_name, "cla4", "block_signals4"])

        module_definition: str = include_block
        subadder_file = open("verilog/logic/16bit_subadd.v", "r")
        subadder_text = subadder_file.read()
        subadder_text = subadder_text.format(type=verilog_base_name)
        module_definition += subadder_text
        module_definition += generate_module_declaration(verilog_structured_name, False)
        module_definition += generate_port_declare_block(width, False)
        subadder_name += f"_{verilog_base_name}"
        if width == 16:
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


    # produces random wire declarations
    def generate_cselect_adder():
        # process:
        # 1) assign a positional index to each adder block
        # 2) place two adders every block except on first block
        # 3) place two muxes on the 2nd level every 2 block except on the first placement
        # 4) place two muxes on the 3rd level every 4 blocks, except on the first placement
        def generate_base_adder_declaration(name: str, ports: dict) -> str:
            port_list: list = [f".{pair[0]}({pair[1]})" for pair in ports.items()]
            port_list = ", ".join(port_list)
            return f"\t{verilog_base_name} {name}({port_list});\n"

        module_definition: str = generate_include_block([verilog_base_name])
        module_definition += generate_module_declaration(verilog_structured_name, False)
        module_definition += generate_port_declare_block(width, False)
        lowest_depth: int = int(math.log(block_count, 2) + 1)

        sum_wires: list = []
        for i in range(0, block_count):
            bit_range = [(i+1) * block_size - 1, i*block_size]
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
                module_definition += generate_base_adder_declaration(adder_name, ports)
            else:
                for cin in ["0", "1"]:
                    adder_name = f"component_level0_pos{i}_cin{cin}"
                    adder_cout = adder_name + "_cout"
                    adder_out = adder_name + "_out"
                    module_definition += generate_wires([adder_cout, (adder_out, block_size)])
                    ports["cin"] = "1'b" + cin
                    ports["cout"] = adder_cout
                    ports["s"] = adder_out
                    module_definition += generate_base_adder_declaration(adder_name, ports)

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

                    if i+1 == block_count and k == 2:
                        mux_concat_list0.insert(0, f"component_level0_pos{i}_cin0_cout")
                        mux_concat_list1.insert(0, f"component_level0_pos{i}_cin1_cout")

                    mux_in0 = "{{{list}}}".format(list=", ".join(mux_concat_list0))
                    mux_in1 = "{{{list}}}".format(list=", ".join(mux_concat_list1))
                    mux0_name = f"component_level{level}_pos{i}_cin0"
                    mux0_control = f"component_level{level-1}_pos{i-mux_span}_cin0_cout" # mux will always take in select bit from first mux on prev level
                    mux0_out = mux0_name + "_out"
                    temp_width = mux_span * block_size if i + 1 != block_count else mux_span * block_size + 1
                    module_definition += generate_wires([(mux0_out, temp_width)])
                    mux0_statement = f"\tassign {mux0_out} = {mux0_control} ? {mux_in1} : {mux_in0};\n"
                    module_definition += mux0_statement + "\n"
                    if i+1 > k:
                        mux1_name = f"component_level{level}_pos{i}_cin1"
                        mux1_control = f"component_level{level-1}_pos{i-mux_span}_cin1_cout"
                        mux1_out = mux1_name + "_out"
                        module_definition += generate_wires([mux1_out, temp_width])
                        mux1_statement = f"\tassign {mux1_name} = {mux1_control} ? {mux_in1} : {mux_in0};\n"
                        module_definition += mux1_statement + "\n"
                    elif i+1 == k:
                        sum_wires.insert(0, mux0_out)
                    module_definition += "\n\n"
        module_definition += generate_wires([("sum", temp_width+1 - block_size)])
        module_definition += "\tassign sum = {{{sum_wires}}};\n".format(sum_wires=", ".join(sum_wires))
        module_definition += f"\tassign cout = sum[{temp_width}];\n"
        module_definition += f"\tassign s[{temp_width-1}:{block_size}] = sum[{temp_width-1-block_size}:{0}];\n"
        module_definition += "endmodule\n"
        return module_definition
                    
    func_name = "generate_{structure}_adder".format(structure=structure)
    text = locals()[func_name]()
    return text

def generate_basic_adder(adder_info: dict):
    verilog_base_name: str = adder_info["verilog_base_name"]
    block_size: int = adder_info["block_size"]
    base_type: str = adder_info["base_type"]
    hybrid_levels = None
    depth: int = adder_info["depth"]
    ppa_graph = adder_info["graph"]

    def invert(wire: str) -> str:
        return "~" + wire

    def generate_input_ports(pred: node, curr: node) -> tuple: # returns [p, g]
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
    include_block += "`define {name}\n".format(name=verilog_base_name.upper())

    info_block = generate_adder_info_block(adder_info)

    module_definition: str = ""
    module_name: str
    if base_type == "hybrid":
        hybrid_levels = adder_info["hybrid_levels"]
        module_name = "{adder_type}{bit_width}_{hybrid_levels}".format(adder_type=base_type, bit_width=block_size, hybrid_levels=hybrid_levels)
    else:
        module_name = "{adder_type}{bit_width}".format(adder_type=base_type, bit_width=block_size)
    module_definition += generate_module_declaration(verilog_base_name)
    module_definition += generate_port_declare_block(block_size, False)
    module_definition += "\toutput[{len}:0]p_out;\n\toutput[{len}:0]g_out;\n".format(len=block_size-1)
    module_definition += "\tassign p_in = x1 ^ x2;\n\tassign p_out = p_in;\n"
    module_definition += "\tassign g_in[{len}:1] = x1[{len}:1] & x2[{len}:1];\n".format(len=block_size-1)
    module_definition += "\tassign g_in[0] = (x1[0] & x2[0]) | (p_in[0] & cin);\n"
    module_definition += "\tassign g_out = g_in;\n"
    for level in range(1, depth):
        row = ppa_graph[level]
        for bit_pos, curr in row.items():
            if curr.is_operator == False or curr.level != level: continue

            pred_up = curr.pred_up
            pred_right = curr.pred_right

            up_connection: str
            right_connection: str

            output_declaration = "\t(* keep *) wire node_level{level}_pos{bit_pos}_outg;\n".format(level=curr.level, bit_pos=curr.bit_pos)
            output_declaration += "\t(* keep *) wire node_level{level}_pos{bit_pos}_outp;\n".format(level=curr.level, bit_pos=curr.bit_pos)

            module_definition += output_declaration

            [p1, g1] = generate_input_ports(pred_up, curr)
            up_connection: str = ".p1({p1}), .g1({g1})".format(p1=p1, g1=g1)

            [p0, g0] = generate_input_ports(pred_right, curr)
            right_connection: str = ".p0({p0}), .g0({g0})".format(p0=p0, g0=g0)

            output_connection = ".gp(node_level{level}_pos{bit_pos}_outg), .pp(node_level{level}_pos{bit_pos}_outp)".format(level=curr.level, bit_pos=curr.bit_pos)

            operator_type: str = "neg_operator" if level % 2 == 1 else "pos_operator"

            operator_declaration = "(* keep *) {type} node_level{level}_pos{bit_pos}".format(type=operator_type, level=level, bit_pos=bit_pos)
            operator_declaration = operator_declaration + "({up}, {right}, {output})".format(up=up_connection, right=right_connection, output=output_connection)

            operator_declaration += ";\n"
            module_definition += operator_declaration
    
    module_definition += "\n\n\tassign s[0] = p_in[0] ^ cin;\n"

    for bit_pos in range(1, block_size):
        cur_level = depth-1
        sum: str = "p_in[{index}]".format(index=bit_pos)
        carry_node: ppa_graph.node = get_lowest_node(bit_pos-1, ppa_graph)
        carry: str
        if carry_node.is_operator == False:
            carry = "g_in[{index}]".format(index=bit_pos-1)
        else:
            carry = "node_level{level}_pos{pos}_outg".format(level=carry_node.level, pos=carry_node.bit_pos)
        
        if carry_node.level > 0 and carry_node.level % 2 == 1:
            carry = invert(carry)

        output_connection = "\tassign s[{bit_pos}] = {sum} ^ {carry};\n".format(bit_pos=bit_pos, sum=sum, carry=carry)
        module_definition += output_connection

    module_definition += "\tassign cout = (x1[{len}] & x2[{len}]) | (~s[{len}] & (x1[{len}] | x2[{len}]));\n".format(len=block_size-1)
    
    module_definition += "endmodule\n"

    text = include_block + info_block + module_definition
    return text

def compile_verilog(text: str) -> bool:
    test = open("test.v", "w+")
    test.write(text)
    test.close()
    result = os.system("make compile_test > /dev/null")
    os.system("make compile_test_clean > /dev/null")
    return result == 0

def get_module_declaration_info(line: str):
    info = re.findall("^\\s*(\\S+)\\s+(\\S+?)\\s*\((.+)\)\\s*;", line)
    assert len(info) > 0
    gate_type = info[0][0]
    mod_name = info[0][1]
    ports = info[0][2].replace(" ", "")
    ports = re.findall("\.(\\w+)\\s*\(\\s*(.+?)\\s*\)", ports)
    ports_dict: dict = {}
    for i in range(0, len(ports)):
        ports_dict[ports[i][0]] = ports[i][1]

    result: dict = {"type" : gate_type, "name" : mod_name, "ports" : ports_dict }
    return result

def create_module_declaration(info: dict): 
    pairs = list(info["ports"].items())
    assert len(pairs) > 0
    port_list_str: str = ""
    for i in range(0, len(pairs)-1):
        port_list_str += f".{pairs[i][0]}({pairs[i][1]}), "
    port_list_str += f".{pairs[-1][0]}({pairs[-1][1]})"

    return f" {info['type']} {info['name']}({port_list_str});"

def find_gate_boundaries(text: str) -> tuple:
    lines = text.split("\n")
    i = 2
    while "input" in lines[i] or "wire" in lines[i] or "output" in lines[i]:
        i+=1
    gate_start = i
    while lines[i] != "endmodule":
        i+=1
    gate_end = i
    return (gate_start, gate_end)

def convert_cases_to_text(cases: list, ind=-1, clear=False):
    ind = "" if ind == -1 else int(ind)
    text: str = ""
    for i in range(0, len(cases)):
        case = cases[i]
        if clear == True:
            text += f'\t\t$display("MODULE{ind}_CASE{i+1}_CLEAR");\n'
            text += f"\t\ta{ind}=0;\n\t\tb{ind}=0;\n\t\tcin{ind}=0;\n\t\t#1;\n"
        text += f'\t\t$display("MODULE{ind}_CASE{i+1}");\n'
        text += f'\t\ta{ind}={case["a"]};\n'
        text += f'\t\tb{ind}={case["b"]};\n'
        text += f'\t\tcin{ind}={case["cin"]};\n'
        text += "\t\t#1;\n"
        text += f'\t\t$display("MODULE{ind}_CASE{i+1}_END");\n'
    return text

def get_module_declaration_info(line: str):
    info = re.findall("^\\s*(\\S+)\\s+(\\S+?)\\s*\((.+)\)\\s*;", line)
    assert len(info) > 0
    gate_type = info[0][0]
    mod_name = info[0][1]
    ports = info[0][2].replace(" ", "")
    ports = re.findall("\.(\\w+)\\s*\(\\s*(.+?)\\s*\)", ports)
    ports_dict: dict = {}
    for i in range(0, len(ports)):
        ports_dict[ports[i][0]] = ports[i][1]

    result: dict = {"type" : gate_type, "name" : mod_name, "ports" : ports_dict }
    return result



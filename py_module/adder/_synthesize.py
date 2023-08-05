from ._file import *
from ._verilog import *

def synthesize(self) -> None:
    def clean_text(text: str) -> str:
        def fix_bad_net_names() -> None:
            net_list: list = []
            for i in range(net_start, net_end):
                expr = "\\w+\\s+(\\S+)\\s*;" if "[" not in lines[i] else "\\w+\\s+\[.+\]\\s+(\\S+)\\s*;"
                name = re.findall(expr, lines[i])
                assert len(name) == 1
                name = name[0]
                if "." in name:
                    net_list.append(name)
            for net in net_list:
                num_lines = len(lines)
                for i in range(0, num_lines):
                    fixed_net = net.replace(".", "_")
                    lines[i] = lines[i].replace(net, fixed_net)

        def standardize_gates():
            type_list: set = set()
            for i in range(gate_start, gate_end):
                info = get_module_declaration_info(lines[i])
                # standardize name
                info["type"] = (info["type"].replace("_", "")).upper()
                info["type"] = info["type"].replace("NOT", "INV")
                new_out_pin = "ZN" if info["type"] != "MUX" and info["type"] != "XOR" else "Z"
                info["ports"][new_out_pin] = info["ports"].pop("Y", None)
                
                second_port: str = "B"
                if "X" not in info["type"] and info["type"] != "MUX" and info["type"] != "INV": # very shaky condition
                    info["ports"]["A1"] = info["ports"].pop("A", None)
                    info["ports"]["A2"] = info["ports"].pop("B", None)
                    second_port = "A2" 

                if "INV" not in info["type"]:
                    info["type"] += "2"
                    lines[i] = create_module_declaration(info)
                    continue
                if info["type"] == "INV":
                    lines[i] = create_module_declaration(info)
                    continue
                base_type = info["type"].replace("INV", "")
                info["type"] = base_type + "2"
                # create new inverter to invert wire B
                wire_b = info["ports"][second_port]
                safe_wire_b = wire_b.replace("[", "_").replace("]", "_")  # remove any []
                wire_b_inverted = safe_wire_b + "_inv"

                inv_info = {"type" : "INV", "name" : safe_wire_b+"_inverter", "ports" : {"A" : wire_b, "ZN" : wire_b_inverted}}

                lines[net_start] += f" wire {wire_b_inverted};\n"
                new_line = create_module_declaration(inv_info)
                info["ports"][second_port] = wire_b_inverted
                new_line += create_module_declaration(info)
                lines[i] = new_line

        def resolve_assigns() -> list:
            statement_list: list = []

            for i in range(assign_start, assign_end):
                sides = re.findall("^\\s*assign\\s+(.+)\\s*=\\s*(.+)\\s*;", lines[i])
                left = sides[0][0].replace(" ", "")
                right = sides[0][1].replace(" ", "")

                def separate_net_list(src: str) -> list:
                    if "{" not in src:
                        return [src]
                    src = src.replace("{", "")
                    src = src.replace("}", "")
                    result: list = src.split(",")
                    return result

                temp_left_nets: list = separate_net_list(left)
                temp_right_nets: list = separate_net_list(right)

                def expand_temp_nets(nets: list) -> list:
                    expanded_nets: list = []
                    for i in range(0, len(nets)):
                        if ":" in nets[i]:
                            info = re.findall(",*\\s*(\\S+)\\s*\[(\\d+):(\\d+)\]", nets[i])
                            name = info[0][0]
                            low_bit = int(info[0][2])
                            high_bit = int(info[0][1])
                            for j in range(low_bit, high_bit+1):
                                expanded_nets.append(f"{name}[{j}]")
                        else:
                            expanded_nets.append(nets[i])
                    return expanded_nets

                left_nets = expand_temp_nets(temp_left_nets)
                right_nets = expand_temp_nets(temp_right_nets)

                assert len(right_nets) == len(left_nets)

                if len(left_nets) != len(right_nets):
                    exit()
                for j in range(0, len(right_nets)):
                    old_net = right_nets[j]
                    new_net = left_nets[j]

                    for k in range(net_start, net_end):
                        if old_net in lines[k]:
                            lines[k] = ""
                    for k in range(gate_start, gate_end):
                        lines[k] = lines[k].replace(old_net, new_net)
                lines[i] = "" # delete assign statement
        
        text = fix_hanging_newlines(text)
        text = fix_illegal_chars(text)
        lines = text.split("\n")
        num_lines = len(lines)
        mod_start, mod_end = 0, 0
        net_start, net_end = 0, 0
        gate_start, gate_end = 0, 0
        assign_start, assign_end = 0, 0
        curr = 0
        while curr < num_lines:
            if "module " in lines[curr]:
                mod_start = curr
                curr = curr+1
                break
            curr = curr+1
        net_start = curr
        while curr < num_lines:
            curr_line = lines[curr]
            is_wire = "input " in curr_line or "wire " in curr_line or "output " in curr_line
            if not is_wire:
                net_end = curr 
                break     
            curr = curr+1
        gate_start = curr
        while curr < num_lines:
            if "assign" in lines[curr]:
                gate_end = curr
                break
            curr = curr + 1
        assign_start = curr
        while curr < num_lines:
            if "endmodule" in lines[curr]:
                assign_end = curr
            curr = curr+1
        mod_end = curr+1

        # replace invalid wire names
        fix_bad_net_names()
        # resolve assigns
        resolve_assigns()
        # standardize gate types
        standardize_gates()

        text = fix_hanging_newlines("\n".join(lines))

        return text

    def fix_illegal_chars(text: str) -> str:
        text = text.replace("\\", "_")
        text = text.replace("$", "_")
        return text

    def fix_hanging_newlines(text: str) -> str:
        lines = text.split(";")
        length = len(lines)
        for i in range(0, length):
            if lines[i].isspace():
                lines[i] = ""
            lines[i] = lines[i].replace("\n", "")
            lines[i] = "\n" + lines[i]
        new_text = ";".join(lines)
        mod_start = new_text.find("module")
        new_text = new_text[mod_start:len(new_text)]
        new_text = re.sub(r"[^\S\r\n]+", " ", new_text)
        return new_text

    script_template_text = read_text("synthesis/script_template.txt")
    script_text = script_template_text.format(dependencies=" ".join(self._dependencies + [self._verilog_file_path]), design_name=self.adder_name, top_module=self._verilog_file_path, top_module_dir=self._verilog_folder_path)
    write_text("synthesis/script.tcl", script_text)
    if os.system("sh synthesis/synthesis_setup.sh") != 0:
        print("Error during synthesis, exiting...")
        exit()
        
    # process and clean up synthesized file
    syn_text = read_text(self._syn_file_path)
    cleaned_text = clean_text(syn_text)
    write_text(self._syn_file_path, cleaned_text)
    self.synthesized_text = cleaned_text
from ._file import *
from ._verilog import *
import re

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
    
        def expand_operators():
            for i in range(assign_start, assign_end):
                op_declare = lines[i]
                info = get_module_declaration_info(op_declare)
                info["name"] = info["name"].replace(".", "")
                new_line: str = ""
                if info["type"] == "pos_operator":
                    new_line += f" OAI21 {info['name']}_oai(.A({info['ports']['g1']}),.B1({info['ports']['g0']}),.B2({info['ports']['p1']}),.ZN({info['ports']['gp']}));\n"
                    new_line += f" NOR2 {info['name']}_nor(.A1({info['ports']['p1']}),.A2({info['ports']['p0']}),.ZN({info['ports']['pp']}));\n"                
                elif info["type"] == "neg_operator":
                    new_line += f" AOI21 {info['name']}_aoi(.A({info['ports']['g1']}),.B1({info['ports']['p1']}),.B2({info['ports']['g0']}),.ZN({info['ports']['gp']}));\n"
                    new_line += f" NAND2 {info['name']}_nand(.A1({info['ports']['p1']}),.A2({info['ports']['p0']}),.ZN({info['ports']['pp']}));\n"  
                else:
                    print("synthesize.expand_operators(): Could not recognize operator type (error)")
                    exit()
                lines[i] = new_line

        text = fix_hanging_newlines(text)
        text = fix_illegal_chars(text)
        lines = text.split("\n")
        num_lines = len(lines)
        net_start, net_end = 0, 0
        gate_start, gate_end = 0, 0
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
            if "pos_operator" in lines[curr] or "neg_operator" in lines[curr]:
                gate_end = curr
                break
            curr = curr + 1
        assign_start = curr
        while curr < num_lines:
            if "endmodule" in lines[curr]:
                assign_end = curr
            curr = curr+1
        mod_end = curr+1
        op_start = assign_start
        op_end = assign_end

        fix_bad_net_names()
        expand_operators()
        text = fix_hanging_newlines("\n".join(lines))
        text = re.sub("_X\\d{1}", "", text)
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
        print("synthesize.synthesize(): Could not synthesize design (error)")
        exit()

    def fix_gate_counts():
        os.system(f'echo "read_verilog {self._syn_file_path}; tee -o synthesis/{self._verilog_folder_path}/{self.adder_name}_stats.json stat -json;" | yosys')
        
    # process and clean up synthesized file
    syn_text = read_text(self._syn_file_path)
    cleaned_text = clean_text(syn_text)
    write_text(self._syn_file_path, cleaned_text)
    fix_gate_counts()
    self.synthesized_text = cleaned_text
    #if (os.system("make clean_script") != 0):
    #    print("synthesize.synthesize(): Could not clean script file (Makefile error)")
    #    exit()
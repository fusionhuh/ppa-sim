import re
import math
from ._file import *

important_regex_str = r"(plus_expr_FU|ui_plus_expr_FU) #\([\S\s]+?\)\)[\s\n]+?([\S\s]+?\([\s\S\n]+?\));"

def replace_addition(self, text):
    pass

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

def print_module_parameters(text: str):
    modules = get_module_text(text)
    for module in modules:
        parameters = get_module_parameters(module)

def update_plus_modules(text: str):
    regex_str = r"(module (plus_expr_FU|ui_plus_expr_FU)[\S\s\n]+?;)([\S\s\n]+?)endmodule"

    function = "\n\
    function integer max(input integer a,b);\n\
    begin\n\
        if (a > b)\n\
            max = a;\n\
        else\n\
            max = b;\n\
    end\n\
    endfunction\n\
\n\
    function integer calc_width(input integer in1, in2, out);\n\
        calc_width = 2**$clog2(max(max(in1,in2), out));\n\
    endfunction\n"

    signed_new = f"\n\
  parameter BITSIZE_in1=1,\n\
    BITSIZE_in2=1,\n\
    BITSIZE_out1=1,\n\
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);\n\
{function}\
  input signed [BITSIZE_out1-1:0] in1;\n\
  input signed [BITSIZE_out1-1:0] in2;\n\
  wire signed [BITSIZE_out1-1:0] internal_sum;\n\
  output signed [BITSIZE_out1-1:0] out1;\n\
  assign internal_sum = in1+in2;\n\
  assign out1 = internal_sum;\n"
    
    unsigned_new = f"\n\
  parameter BITSIZE_in1=1,\n\
    BITSIZE_in2=1,\n\
    BITSIZE_out1=1,\n\
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);\n\
{function}\
  input [BITSIZE_out1-1:0] in1;\n\
  input [BITSIZE_out1-1:0] in2;\n\
  wire [BITSIZE_out1-1:0] internal_sum;\n\
  output [BITSIZE_out1-1:0] out1;\n\
  assign internal_sum = in1+in2;\n\
  assign out1 = internal_sum;\n"
    def replace(matchobj):
        type = matchobj.group(2)
        if type == "plus_expr_FU":
            full = matchobj.group(1) + signed_new + "endmodule"
            return full
        elif type == "ui_plus_expr_FU":
            full = matchobj.group(1) + unsigned_new + "endmodule"
            return full

    text = re.sub(regex_str, replace, text)
    return text

def update_signed_instances(text):
    info = get_addition_info(text, gate_level=False)
    curr = 0
    for instance in info:
        if instance["type"] != "plus_expr_FU": continue
        ports = instance["ports"]
        new_in1 = f"in1_replacement{curr}"
        new_in2 = f"in2_replacement{curr}"
        in1_declaration = f"  wire signed [{instance['new_width']-1}:0] {new_in1};\n  assign {new_in1} = $signed({ports['in1']});\n"
        in2_declaration = f"  wire signed [{instance['new_width']-1}:0] {new_in2};\n  assign {new_in2} = $signed({ports['in2']});\n"
        new_text = in1_declaration + in2_declaration + instance["full_text"].replace(ports['in1'], new_in1).replace(ports['in2'], new_in2) # kind of jank, may not work
        print(new_text)
        text = text.replace(instance["full_text"], new_text)
        curr+=1
    return text


def get_addition_info(text, gate_level: bool = True):
    instances = None
    if gate_level == True:
        text = fix_hanging_newlines(text)
        instances = re.findall(r"(([\S]+?) #\(([\S\s]+?\))\s+\) ([\S]+?) \(([\S\s]+?\))\s*\);)", text)
    else:
        instances = re.findall(r"(^  (\S+?) #\(([\S\s\n]+?\))\) (\S+?) \(([\S\s\n]+?\))\));", text, flags=re.MULTILINE)
        print(instances)

    info: list = []

    for instance in instances:
        full_text, mod_type, params_str, name, ports_str = instance
        if mod_type != "ui_plus_expr_FU" and mod_type != "plus_expr_FU": continue
        extract_info_regex = r"\.([\S]+?)\(([\S]+?\s*)\)"
        ports = dict(re.findall(extract_info_regex, ports_str.replace(" ", "").replace("\n","")))
        params = dict(re.findall(extract_info_regex, params_str.replace(" ", "").replace("\n","")))
        for key, val in params.items():
            params[key] = val.split("sd")[1] if gate_level == True else val
        new_info: dict = dict()
        new_info["ports"] = ports
        new_info["type"] = mod_type
        new_info["name"] = name
        new_info["parameters"] = params
        new_info["full_text"] = full_text
        param_nums = list(map(int, params.values()))
        new_info["old_width"] = int(params["BITSIZE_out1"])
        new_info["new_width"] = new_info["old_width"]
        info.append(new_info)

    return info

def update_signed_modules(text, addition_info):
    for instance in addition_info:
        type = instance["type"]
        if type != "plus_expr_FU": continue
        ports = instance["ports"]
        print(ports["in2"])


def get_module_text(text: str):
    modules: list = re.findall("module[\\S\\s\\n]+?;([\\S\\n\\s]+?)endmodule", text)
    assert len(modules) > 0
    return modules

def get_module_parameters(text: str):
    param_blocks: list = re.findall(r"parameter[\s]{1}([\S\s\n]+?);", text)
    parameters: dict = {}
    for i, block in enumerate(param_blocks):
        block = block.replace(" ", "").replace("\n", "")
        statements = block.split(",")
        for statement in statements:
            lhs, rhs = statement.split("=")
            parameters[lhs] = rhs
    return parameters

def get_addition_information(line, parameters, text) -> dict:
    net_names = re.findall(r"(\S+?)\s\+\s(\S+?);", line)
    if net_names == []: return None

    lines = text.split('\n')

    line = line.replace(" ", "").split("+")

    for i, line in enumerate(lines):
        pass

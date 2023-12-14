import re
import math

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

    new = f"\n\
  parameter BITSIZE_in1=1,\n\
    BITSIZE_in2=1,\n\
    BITSIZE_out1=1,\n\
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);\n\
{function}\
  input signed [FINAL_WIDTH-1:0] in1;\n\
  input signed [FINAL_WIDTH-1:0] in2;\n\
  output signed [FINAL_WIDTH-1:0] out1;\n\
  assign out1 = in1 + in2;\n"
    text = re.sub(regex_str, f"\\1{new}endmodule", text)
    return text

def get_addition_info(text):
    text = fix_hanging_newlines(text)
    instances = re.findall(r"(([\S]+?) #\(([\S\s]+?\))\s+\) ([\S]+?) \(([\S\s]+?\))\s*\);)", text)
   
    info: list = []

    for instance in instances:
        full_text, mod_type, params_str, name, ports_str = instance
        if mod_type != "ui_plus_expr_FU" and mod_type != "plus_expr_FU": continue
        extract_info_regex = r"\.([\S]+?)\(([\S]+?\s*)\)"
        ports = dict(re.findall(extract_info_regex, ports_str.replace(" ", "").replace("\n","")))
        params = dict(re.findall(extract_info_regex, params_str.replace(" ", "").replace("\n","")))
        for key, val in params.items():
            params[key] = val.split("sd")[1]
        new_info: dict = dict()
        new_info["ports"] = ports
        new_info["type"] = mod_type
        new_info["name"] = name
        new_info["parameters"] = params
        new_info["full_text"] = full_text
        param_nums = list(map(int, params.values()))
        new_info["old_width"] = params["BITSIZE_out1"]
        new_info["new_width"] = int(2**math.ceil(math.log2(max(param_nums))))
        info.append(new_info)

    return info

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

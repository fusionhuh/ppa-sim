import re
import math

important_regex_str = r"(plus_expr_FU|ui_plus_expr_FU) #\([\S\s]+?\)\)[\s\n]+?([\S\s]+?\([\s\S\n]+?\));"


def replace_addition(self, text):
    pass

def print_module_parameters(text: str):
    modules = get_module_text(text)
    for module in modules:
        parameters = get_module_parameters(module)
        print(parameters)

def update_plus_modules(text: str):
    regex_str = r"(module (plus_expr_FU|ui_plus_expr_FU)[\S\s\n]+?;)([\S\s\n]+?)endmodule"

    new = "\n\
  parameter BITSIZE_in1=1,\n\
    BITSIZE_in2=1,\n\
    BITSIZE_out1=1,\n\
    FINAL_WIDTH = calc_width(BITSIZE_in1, BITSIZE_in2, BITSIZE_out1);\n\
  input signed [FINAL_WIDTH-1:0] in1;\n\
  input signed [FINAL_WIDTH-1:0] in2;\n\
  output signed [FINAL_WIDTH-1:0] out1;\n\
  assign out1 = in1 + in2;\n"
    text = re.sub(regex_str, f"\\1{new}endmodule", text)
    return text

def inject_function(text: str):
    function = "\n\
    function integer max(input integer a,b);\
    begin\
        if (a > b)\
            max = a;\
        else\
            max = b;\
    end\
    endfunction\
\
    function integer calc_width(input integer in1, in2, out);\
        calc_width = 2**$clog2(max(max(in1,in2), out));\
    endfunction\n"
    
    lines = text.split("\n")
    lines = [function] + lines
    return "\n".join(lines)

def get_addition_info(text: str):
    instances = get_plus_instances(text)

    return [get_plus_instance_info(instance) for instance in instances]

        

def get_plus_instance_info(instance):
    full_text, mod_type, parameters, mod_name, ports_str = instance

    ports_regex_str = r"\.([\S]+?)[\s\n]*?\(([\S\s]+?)\)(,[\n\s]*?|[\n\s]*?$)"
    info: dict = dict()
    ports = dict([tup[0:2] for tup in re.findall(ports_regex_str, ports_str)])
    info["ports"] = ports
    info["type"] = mod_type
    info["name"] = mod_name

    parameters_regex_str = r"\.(\S+?)\(\d+'[a-zA-Z]+(\d+)\)"
    parameters = parameters.replace(" ", "").replace("\n", "")
    parameters = dict(re.findall(parameters_regex_str, parameters))
    info["parameters"] = parameters
    param_nums = list(map(int, parameters.values()))
    info["new_width"] = int(2**math.ceil(math.log2(max(param_nums))))
    return info

def get_plus_instances(text: str):
    regex_str = r"((plus_expr_FU|ui_plus_expr_FU) #\(([\S\s\n]+?\)[\s\n]*?)\)[\s\n]+?([\S\s\n]+?) \(([\S\s\n]+?)\);)"
    return re.findall(regex_str, text)

def replace_modules(text: str):
    old = "\
  parameter BITSIZE_in1=1,\n\
    BITSIZE_in2=1,\n\
    BITSIZE_out1=1;\n\
  // IN\n\
  input signed [BITSIZE_in1-1:0] in1;\n\
  input signed [BITSIZE_in2-1:0] in2;\n\
  // OUT\n\
  output signed [BITSIZE_out1-1:0] out1;\n\
  assign out1 = in1 + in2;"


    # to verify understanding
    old_count = text.count(old)
    new_text = text.replace(old, new)

    new_old_count = text.replace(old, new)
    assert new_old_count == 0

    return text.replace(old, new)

def get_module_text(text: str):
    print(text)
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

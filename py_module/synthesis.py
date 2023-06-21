import sys
import verilog
import os

def generate_synthesis_script(a: verilog.adder):
    script_template = open("synthesis/script_template.txt", "r")
    script_template_text = script_template.read()
    dependencies: list = ["../" + path for path in a.dependencies]
    syn_file_path: str = a.dependencies[-1].replace("verilog/", "")
    adder_name = a.verilog_base_name if a.structure == "basic" else a.verilog_structured_name
    syn_file_path = syn_file_path.replace(adder_name+".v", "")
    script_text = script_template_text.format(dependencies=" ".join(dependencies), adder_name=adder_name, syn_file_path=syn_file_path)
    script = open("synthesis/script.tcl", "w+")
    script.write(script_text)
    script.close()

def execute_synthesis_script():
    os.chdir("./synthesis")
    os.system("sh setup_genus.sh")

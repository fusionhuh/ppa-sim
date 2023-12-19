from .command import run_command
from hlsynthesizer._file import *
from file_structure import *
import re


def generate_submodule_import_text(submodules: list):
    submodule_text = ""
    for submodule in submodules:
        submodule_text += f"read_verilog {submodule};\n"
    return submodule_text

# returns worst case delay from report_checks
def run_worst_case_delay_script(top_level_file: str, design_name: str, submodules: list = [], sdf_output_path: str = "temp.sdf", script_path:str ="temp.tcl") -> float:
    path = HLS_STA_SCRIPT_PATH
    script_text = read_text(path)
    submodule_text = generate_submodule_import_text(submodules)
    script_text = script_text.format(
        verilog_file = top_level_file,
        submodule_text=submodule_text,
        design_name=design_name,
        sdf_file_out=sdf_output_path
    )
    write_text(script_path, script_text)
    report_path = "report_out.txt"
    run_command(f"sta {script_path}", redirect=report_path)
    report_out_text = read_text(report_path)
    run_command(f"rm {report_path}")
    worst_case_delay = re.findall("^\s+(0\.\d+)\s+data arrival time", report_out_text, flags=re.MULTILINE)
    print(worst_case_delay)


# returns connected_dffs as dict mapping sum bit to list of connected DFFs
def run_connected_dffs_script(top_level_file: str, design_name: str, instance_name: str, submodules: list = [], thread_id: int = 0) -> tuple:
    path = HLS_CONNECTED_DFFS_SCRIPT_PATH
    script_text = read_text(path)
    submodule_text = generate_submodule_import_text(submodules)
    script_text = script_text.replace(r"\\DESIGN_FILE", top_level_file)
    script_text = script_text.replace(r"\\ADDER_READS", submodule_text)
    script_text = script_text.replace(r"\\DESIGN_NAME", design_name)
    script_text = script_text.replace(r"\\ADDER_INST_NAME", instance_name)
    script_path = HLS_WORKING_DIR + f"/connected_dffs{thread_id}.tcl"
    output_path = HLS_WORKING_DIR + f"/connected_dffs_out{thread_id}.txt"
    write_text(script_path, script_text)

    run_command(f"sta {script_path}", redirect=output_path)

    connected_dffs: dict = dict()

    lines = read_text(output_path).split("\n")
    normalized_instance_name = instance_name.replace("\\", "")

    num_connected_dffs = 0
    curr_sum_bit = None
    for i, line in enumerate(lines):
        split_line = line.split(":")
        if len(split_line) != 2: continue
        tag, value = split_line
        if tag not in ["NUM_CONNECTIONS", "PORT", "NET", "DEST_PIN"]: continue
        if tag == "NUM_CONNECTIONS": num_connections = int(value)
        elif tag == "PORT":
            split_value = value.rsplit("/", 1)
            if len(split_value) != 2: continue
            reference, name = split_value
            # not sure if we actually need to do anything here? I think we can
            # sufficiently verify the net if we just look at the net name
        elif tag == "NET":
            split_value = value.rsplit("/", 1)
            if len(split_value) != 2: continue
            reference, name = split_value
            if reference == normalized_instance_name and name[0:2] == "s[":
                if curr_sum_bit != None:
                    raise Exception("Found duplicate sum bit for one DFF connection")
                curr_sum_bit = int(name.replace("s[", "")[0:-1])
        elif tag == "DEST_PIN":
            dff_instance = value.rsplit("/", 1)[0]
            if curr_sum_bit == None:
                raise Exception("No sum bit found for current DFF connection")
            if curr_sum_bit not in connected_dffs.keys(): 
                connected_dffs[curr_sum_bit] = []
            connected_dffs[curr_sum_bit] += [dff_instance]
            num_connected_dffs += 1
            curr_sum_bit = None   
    connected_dffs["NUM_CONNECTIONS"] = num_connected_dffs
    return connected_dffs

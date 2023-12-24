from .command import *
from file_structure import *
from hlsynthesizer._file import *

def _run_hls_syn_script(in_script_path: str, top_level_file: str, design_name: str, clock_time: float = 100.0, syn_output_path: str = "temp.v", script_path: str = "temp.tcl"):
    script_text = read_text(in_script_path)
    script_text = script_text.format(
        in_path=top_level_file,
        design_name=design_name,
        clock_time=clock_time,
        out_path=syn_output_path
    )
    write_text(script_path, script_text)
    run_command(f"yosys -c {script_path}", touch_list=[syn_output_path])

def run_hls_template_syn_script(top_level_file: str, design_name: str, clock_time: float = 100.0, syn_output_path: str = "temp.v", script_path: str = "temp.tcl"):
    _run_hls_syn_script(HLS_SYN_SCRIPT_PATH, top_level_file, design_name, clock_time, syn_output_path, script_path)

def run_hls_generic_syn_script(top_level_file: str, design_name: str, clock_time: float = 100.0, syn_output_path: str = "temp.v", script_path: str = "temp.tcl"):
    _run_hls_syn_script(HLS_SECOND_SYN_SCRIPT_PATH, top_level_file, design_name, clock_time, syn_output_path, script_path)

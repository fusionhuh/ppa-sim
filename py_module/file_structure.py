LIB_PATH: str = "hardware/NangateOpenCellLibrary_typical.lib"
NANGATE_LIB_FILE: str = "NangateOpenCellLibrary_typical_conditional.v"

SUPPORTED_TYPES: list = ["bk", "ks", "hybrid", "serial", "skl"]
SUPPORTED_STRUCTURES: list = ["basic", "rc", "cla", "cskip", "cselect"]
VERI_DIR = "verilog"
VERI_BASE_DIR = "base"
VERI_STRUCTURED_DIR = "structured"
VERI_LOGIC_DIR = "logic"

SYN_DIR = "synthesis"
SYN_VERILOG_DIR = f"verilog"
SYN_SCRIPT_TEMPLATE_PATH = f"{SYN_DIR}/script_template.txt"
SYN_SCRIPT_PATH = f"{SYN_DIR}/script.tcl"

OPT_DIR = "optimization"
OPT_VERILOG_DIR = f"verilog"
OPT_SDF_DIR = f"sdf"
OPT_DATA_DIR = f"size_data"
OPT_SCRIPT_TEMPLATE_PATH = f"{OPT_DIR}/script_template.txt"
OPT_SCRIPT_PATH = f"{OPT_DIR}/script.tcl"
OPT_REPORT_PATH = "report_out"

SIM_DIR = "simulation"
SIM_TESTBENCH_TEMPLATE_PATH = f"{SIM_DIR}/testbench_template.txt"
SIM_TESTBENCH_PATH = f"{SIM_DIR}/tb.v"
SIM_OUTPUT_PATH = f"{SIM_DIR}/tb_out"

PIN_OPERANDS_FILENAME = "extracted_operands.txt"
PIN_OPERANDS_PATH = f"simulation/pintool/{PIN_OPERANDS_FILENAME}"

PIN_CONTEXT_FILENAME = "context.txt"
PIN_CONTEXT_PATH = f"simulation/pintool/{PIN_CONTEXT_FILENAME}"

SIM_BIN_DIR = "simulation/bin/"

HLS_DIR = "substitution"
HLS_OUTPUT_DIR = f"{HLS_DIR}/hlsynthesis/out"
HLS_SYN_SCRIPT_PATH = f"{HLS_DIR}/hlsynthesis/syn_script_template.tcl"
HLS_STA_SCRIPT_PATH = f"{HLS_DIR}/hlsynthesis/sta_script_template.tcl"

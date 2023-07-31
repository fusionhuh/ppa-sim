import sys
from pathlib import Path
from verilog import generate_basic_adder, generate_structured_adder, compile_verilog, get_module_declaration_info, create_module_declaration
import verilog
import re
import graph
import os
from GateSize import cktopt
import json
from file_help import write_text, create_file_parents, read_text, file_exists

LIB_PATH: str = "synthesis/NangateOpenCellLibrary_typical.lib"
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
SYN_LIB_PATH = f"{SYN_DIR}/NangateOpenCellLibrary_typical.lib"

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

class adder:
    def __init__(self, description: str):
        assert description.count(".") == 2
        [adder_type, width, structure] = tuple(description.split("."))

        # fill adder type and size information
        assert width.isdigit()
        self.width: int = int(width)
        type_info = adder_type.split("-")
        self.base_type: str = type_info[0]
        assert self.base_type in SUPPORTED_TYPES
        if len(type_info) == 2:
            assert self.base_type == "hybrid"
            assert type_info[1].isdigit()
            self.hybrid_levels: int = int(type_info[1])

        # fill adder structure information
        structure_info = structure.split("-")
        self.structure: str = structure_info[0]
        assert self.structure in SUPPORTED_STRUCTURES
        if self.structure == "basic":
            assert len(structure_info) == 1
            self.block_size: int = self.width
            self.block_count: int = 1
        else:
            assert len(structure_info) == 2
            self.block_size: int = int(structure_info[1])
            self.block_count: int = self.width//self.block_size
            if self.structure == "cla":
                assert self.block_size == 4
                assert self.width == 16 or self.width == 64
            if self.structure == "cselect":
                assert self.block_count == 2 or self.block_count == 4

        # generate adder name
        self.verilog_base_name = "{type}{width}".format(type=self.base_type, width=self.block_size)
        if self.base_type == "hybrid":
            self.verilog_base_name += "_" + str(self.hybrid_levels)
        if self.structure != "basic":
            self.verilog_structured_name = f"{self.verilog_base_name}_{self.width}_{self.structure}"
            #self.verilog_structured_name = "{type}_{width}_{structure}_{block_size}".format(type=self.base_type, width=self.width, structure=self.structure, block_size=self.block_size)   
        self.adder_name = self.verilog_base_name if self.structure == "basic" else self.verilog_structured_name

        # generate important file/folder paths for each process (verification/verilog, synthesis, optimization, etc)
        subdir = f"{VERI_BASE_DIR}/{self.base_type}" if self.structure == "basic" else f"{VERI_STRUCTURED_DIR}/{self.structure}"

        # verilog
        self._verilog_folder_path = f"verilog/{subdir}"
        self._verilog_file_path = f"{self._verilog_folder_path}/{self.adder_name}.v"

        # synthesis
        prefix = f"{VERI_DIR}/{VERI_LOGIC_DIR}"
        dependency_list = [f"{prefix}/pos_operator.v", f"{prefix}/neg_operator.v", f"{prefix}/carry_operator.v"]
        if self.structure != "basic":
            if self.structure == "cla":
                dependency_list.extend([f"{prefix}/cla4.v", f"{prefix}/block_signals4.v"])
            base_file_path = f"{VERI_DIR}/{VERI_BASE_DIR}/{self.base_type}/{self.verilog_base_name}.v"
            dependency_list.append(base_file_path)
        self._dependencies = dependency_list

        self._syn_folder_path = f"{SYN_DIR}/{SYN_VERILOG_DIR}/{subdir}"
        self._syn_file_path = f"{self._syn_folder_path}/{self.adder_name}.v"
        self._syn_area_file_path = f"{self._syn_folder_path}/{self.adder_name}_area"
        self._syn_stats_file_path = f"{self._syn_folder_path}/{self.adder_name}_stats.json"

        # optimization
        self._opt_data_folder_path = f"{OPT_DIR}/{OPT_DATA_DIR}/{subdir}"
        self._opt_data_file_path = f"{self._opt_data_folder_path}/{self.adder_name}_sizes.json"
        self._opt_verilog_folder_path = f"{OPT_DIR}/{OPT_VERILOG_DIR}/{subdir}"
        self._opt_verilog_template_path = f"{self._opt_verilog_folder_path}/{self.adder_name}_template"
        self._opt_sdf_folder_path = f"{OPT_DIR}/{OPT_SDF_DIR}/{subdir}"
        self._opt_sdf_template_path = f"{self._opt_sdf_folder_path}/{self.adder_name}_template"
        self._opt_sdf_data_path = f"{self._opt_sdf_folder_path}/{self.adder_name}_data.json"

        # simulation
#        self._sim_tb_template = "simulation/testbench_template.txt"
#        self._sim_tb_file_path = "simulation/tb.v"

    def get_verbose_name(self) -> str:
        name: str
        width = f"{self.width}-bit"
        base_descriptor: str
        if self.base_type == "ks":
            base_descriptor = "Kogge-Stone"
        elif self.base_type == "bk":
            base_descriptor = "Brent-Kung"
        elif self.base_type == "skl":
            base_descriptor = "Sklansky"
        elif self.base_type == "hybrid":
            base_descriptor = "Hybrid"
        elif self.base_type == "serial":
            base_descriptor = "Serial"

        if self.structure != "basic":
            structure_descriptor: str = ""
            if self.structure == "rc":
                structure_descriptor = "Ripple-Carry"
            elif self.structure == "cskip":
                structure_descriptor = "Carry-Skip"
            elif self.structure == "cselect":
                structure_descriptor = "Carry-Select"
            elif self.structure == "cla":
                structure_descriptor = "Carry-Lookahead"
            end = f"with {self.block_size}-bit {base_descriptor} blocks"
            return f"{width} {structure_descriptor} {end}"
        else:
            return f"{width} {base_descriptor}"
        
    def get_real_cell_counts(self, areas: list) -> list:
        cell_list: list = []
        for area in areas:
            cell_list.append(int(area * (self._get_synthesized_cell_count()+1)))
        return cell_list

    # Creates high-level verilog description of circuit
    # Writes description to verilog/
    # First phase in modeling process
    def generate_verilog(self) -> None:
        gen_function_name = "generate_{type}_graph".format(type=self.base_type)
        if self.base_type == "hybrid":
            self.graph: list = graph.get_globals()[gen_function_name](self.block_size, self.hybrid_levels)
        else:
            self.graph: list = graph.get_globals()[gen_function_name](self.block_size)
        graph.test_graph_completeness(self.block_size, self.graph)
        self.depth = len(self.graph)
        self.node_count = graph.get_node_count(self.graph)

        # create adder info if nonexistent
        if not hasattr(self, "adder_info"):
            self.adder_info = {}
            for var in self.__dict__.keys():
                val = getattr(self, var)
                if var[0] == "_": var = var[1:]
                self.adder_info[var] = val

        # update verilog files (including dependencies) according to project file structure
        base_verilog_path = f"verilog/base/{self.base_type}/{self.verilog_base_name}.v"
        base_verilog_text = generate_basic_adder(self.adder_info)
        write_text(base_verilog_path, base_verilog_text)

        # now generate structured verilog if applicable
        if self.structure == "basic":
            self.verilog_text = base_verilog_text
            return 

        structured_verilog_path = f"verilog/structured/{self.structure}/{self.verilog_structured_name}.v"
        structured_verilog_text = generate_structured_adder(self.adder_info)
        write_text(structured_verilog_path, structured_verilog_text)
        self.verilog_text = structured_verilog_text

    def get_adder_info(self):
        return self.adder_info

    # Runs test cases on the high-level verilog from first phase
    def test_high_verilog(self, cases: list) -> bool:
        return self._test_verilog(self.verilog_text, cases)
    
    # Runs test cases on synthesized verilog
    def test_synth_verilog(self, cases: list) -> bool:
        return self._test_verilog(self.synthesized_text, cases)

    def _test_verilog(self, text: str, cases: list) -> bool:
        if compile_verilog(text) == False:
            print("Generated code could not compile correctly, exiting...")
            exit()

        assert len(cases) > 0
        tb_template_text = read_text("verilog/testbench_template.txt")

        test_cases_text: str = ""
        count = 1
        for test in cases:
            assert isinstance(test, dict)
            x1 = test["x1"]
            x2 = test["x2"]
            cin = test["cin"]
            assert cin == 0 or cin == 1
            expected_s = x1 + x2 + cin
            # assuming no overflow currently

            test_cases_text += f"\t\t// test case {count}\n"
            test_cases_text += f"\t\tx1 = {x1};\n"
            test_cases_text += f"\t\tx2 = {x2};\n"
            test_cases_text += f"\t\tcin = {cin};\n"
            test_cases_text += "\t\t#100;\n\n\n"
            test_cases_text += f"\t\tif (s != {expected_s}) $finish;\n"

            count += 1
        tb_text = tb_template_text.format(dependency=self.verilog_file_path.replace("verilog/structured/", ""), width=self.width, adder=self.adder_name, tests=test_cases_text)

        if compile_verilog(tb_text) == False:
            print("Testbench could not compile correctly, exiting...")
            exit()

        write_text("verilog/tb.v", tb_text)

        os.system("make run_test")

    # Synthesizes the high-level verilog that represents this adder
    # Writes result to synthesis/verilog
    # Second phase in modeling process
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
                        lines[i] = verilog.create_module_declaration(info)
                        continue
                    if info["type"] == "INV":
                        lines[i] = verilog.create_module_declaration(info)
                        continue
                    base_type = info["type"].replace("INV", "")
                    info["type"] = base_type + "2"
                    # create new inverter to invert wire B
                    wire_b = info["ports"][second_port]
                    safe_wire_b = wire_b.replace("[", "_").replace("]", "_")  # remove any []
                    wire_b_inverted = safe_wire_b + "_inv"

                    inv_info = {"type" : "INV", "name" : safe_wire_b+"_inverter", "ports" : {"A" : wire_b, "ZN" : wire_b_inverted}}

                    lines[net_start] += f" wire {wire_b_inverted};\n"
                    new_line = verilog.create_module_declaration(inv_info)
                    info["ports"][second_port] = wire_b_inverted
                    new_line += verilog.create_module_declaration(info)
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

    def _create_sized_file_path(self, area: int) -> str:
        return f"{self._opt_verilog_folder_path}/{self.adder_name}_MAX_AREA_{area}.v"

    # Returns the number of modules in synthesized verilog file
    def _get_synthesized_cell_count(self) -> int:
        if hasattr(self, "_syn_cell_count"):
            return self._syn_cell_count
        area_file = open(self._syn_stats_file_path)
        data = json.load(area_file)
        compound_cell_count: int = 0
        if "$_ORNOT_" in data["design"]["num_cells_by_type"].keys():
            compound_cell_count += data["design"]["num_cells_by_type"]["$_ORNOT_"]
        if "$_ANDNOT_" in data["design"]["num_cells_by_type"].keys():
            compound_cell_count += data["design"]["num_cells_by_type"]["$_ANDNOT_"]
        self._syn_cell_count = data["design"]["num_cells"] + compound_cell_count
        return self._syn_cell_count

    def optimize(self, areas_list: list):
        def parse_lib_file() -> dict:
            size_dict: dict = {}
            lib_text = read_text(LIB_PATH)
            cells = re.findall("cell\\s+\((.+?)\)", lib_text)
            for cell in cells:
                components = cell.split("_")
                gate_type = components[0]
                drive = int(components[1].replace("X", ""))
                if gate_type not in size_dict.keys():
                    size_dict[gate_type] = []
                if drive not in size_dict[gate_type]:
                    size_dict[gate_type].append(drive)
            return size_dict
        
        def get_optimization_results(area: int) -> dict:
            data_file_path = Path(self._opt_data_file_path)
            if data_file_path.is_file(): # file exists, could be cached
                json_data: dict
                with open(self._opt_data_file_path, "r") as fp:
                    json_data = json.load(fp)                    
                if str(area) in json_data.keys():
                    return json_data[str(area)]
                else:
                    results = cktopt.optimize(self._syn_file_path, [area])
                    json_data[area] = results
                    with open(self._opt_data_file_path, "w") as fp:
                        json.dump(json_data, fp)     
                    return results
            else: # file doesn't exist, results definitely are not cached
                data_file_path.parent.mkdir(parents=True, exist_ok=True)
                new_json_data: dict = {}
                results = cktopt.optimize(self._syn_file_path, [area])
                new_json_data[area] = results
                with open(self._opt_data_file_path, "w") as fp:
                    json.dump(new_json_data, fp)
                return results

        def map_opt_size(sizes: list, size: float) -> str:
            end = len(sizes)-1
            while end >= 0:
                if size >= sizes[end]:
                    return str(sizes[end])
                end-=1
            return "-1"

        def size_synthesized_file(results: dict, area: int) -> str:
            lib_dict = parse_lib_file()
            syn_text = read_text(self._syn_file_path)
            syn_text = syn_text.replace(f"module {self.adder_name}", f"module {self.adder_name}"+f"_{area}")
            lines = syn_text.split("\n")
            gate_start, gate_end = verilog.find_gate_boundaries(syn_text)
            for i in range(gate_start, gate_end):
                info = get_module_declaration_info(lines[i])
                gate_type = info["type"].split("_")[0]
                size = results[info["name"]]
                size = map_opt_size(lib_dict[gate_type], size)
                info["type"] += f"_X{size}"
                lines[i] = create_module_declaration(info)
            syn_text = "\n".join(lines)
            return syn_text
        
        def create_script(verilog_path: str, area: int) -> None:
            sdf_file_path = self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"
            create_file_parents(sdf_file_path)
            template_text = read_text(OPT_SCRIPT_TEMPLATE_PATH)
            script_text = template_text.format(verilog_file=verilog_path, design_name=self.adder_name+f"_{area}", sdf_file=sdf_file_path)
            write_text(OPT_SCRIPT_PATH, script_text)

        def strip_sdf_file(area: int):
            template_exists = file_exists(self._opt_sdf_template_path)
            sdf_file_path = self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"
            if not file_exists(sdf_file_path):
                print("ERROR: Tried stripping sdf file when it doesn't exist")
                exit()
            sdf_text = read_text(sdf_file_path)
            design = f'{self.adder_name}_{area}'
            print(design)
            sdf_text = sdf_text.replace(design, "design")
            data: dict = {}
            data["celltypes"] = []
            #data["instances"] = []
            data["drives"] = []
            data["delays"] = {}
            sdf_lines = sdf_text.split("\n")
            curr_line = 0
            while "INTERCONNECT" not in sdf_lines[curr_line]:
                curr_line += 1
            while "INTERCONNECT" in sdf_lines[curr_line]:
                curr_line += 1
            celltype: str
            instance: str
            instance_num: int = -1
            delay_num: int = 0
            num_lines = len(sdf_lines)

            while curr_line < num_lines:
                if "CELLTYPE" in sdf_lines[curr_line]:
                    delay_num=0
                    instance_num += 1
                    celltype = re.findall('\(CELLTYPE "(.+?)"\)', sdf_lines[curr_line])[0]
                    base_type = celltype.split("_")[0]
                    new_celltype = base_type + f"_DRIVE_{instance_num}"
                    data["celltypes"].append(base_type)
                    data["drives"].append(celltype.split("_X")[1])
                    
                    if not template_exists:
                        sdf_lines[curr_line] = sdf_lines[curr_line].replace(celltype, new_celltype)
                    curr_line += 1
                    instance = re.findall('\(INSTANCE (.+?)\)', sdf_lines[curr_line])[0]
                    #data["instances"].append(instance)

                    #if not template_exists:
                    #    sdf_lines[curr_line] = sdf_lines[curr_line].replace(instance, f"{{INSTANCE_{instance_num}}}")
                if "IOPATH" in sdf_lines[curr_line]:
                    matches = re.findall(r"\(IOPATH.+?\((.+?)\) \((.+?)\)", sdf_lines[curr_line])
                    if not template_exists:
                        sdf_lines[curr_line] = sdf_lines[curr_line].replace(matches[0][0], f"INSTANCE_{instance_num}_DELAY_{delay_num}")
                        sdf_lines[curr_line] = sdf_lines[curr_line].replace(matches[0][1], f"INSTANCE_{instance_num}_DELAY_{delay_num+1}")
                    if instance_num not in data["delays"].keys():
                        data["delays"][instance_num] = []
                    data["delays"][instance_num] += [matches[0][0], matches[0][1]]
                    delay_num += 2
                curr_line += 1 
            data["num_instances"] = instance_num+1
            if not template_exists:
                write_text(self._opt_sdf_template_path, "\n".join(sdf_lines))
            if not file_exists(self._opt_sdf_data_path):
                create_file_parents(self._opt_sdf_data_path)
                root: dict = {}
                root[area] = data
                with open(self._opt_sdf_data_path, "w") as fp:
                    json.dump(root, fp)
            else:
                json_data: dict = {}
                with open(self._opt_sdf_data_path, "r") as fp:
                    json_data = json.load(fp)
                json_data[area] = data
                with open(self._opt_sdf_data_path, "w") as fp:
                    json.dump(json_data, fp)

        def get_sdf_path(area: int):
            return self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"

        def get_verilog_path(area: int):
            return self._opt_verilog_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.v"

        def construct_sdf_file(area: int):
            path = get_sdf_path(area)
            sdf_text = read_text(self._opt_sdf_template_path)
            design = f"{self.adder_name}_{area}"
            sdf_text = sdf_text.replace("design", design)
            data: dict
            with open(self._opt_sdf_data_path, "r") as fp:
                data = json.load(fp)[f"{area}"]
            drives = data["drives"]
            delays = data["delays"]
            num_instances = data["num_instances"]
            for i in range(0, num_instances):
                curr_drive_key = f"DRIVE_{i}"
                sdf_text = sdf_text.replace(curr_drive_key, f"X{drives[i]}", 1)
                instance_delays = delays[f"{i}"]
                for j in range(0, len(instance_delays)):
                    delay_key = f"INSTANCE_{i}_DELAY_{j}"
                    delay = instance_delays[j]
                    sdf_text = sdf_text.replace(delay_key, delay)
            write_text(get_sdf_path(area), sdf_text)

        def fix_sdf_file(area: int):
            sdf_file_path = self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"
            sdf_file_text = read_text(sdf_file_path)
            def replace(match):
                match = re.findall("\((\\S+)::(\\S+)\)", match.group())
                num1 = float(match[0][0])
                num2 = float(match[0][1])
                return f"({num1}:{(num1+num1)/2}:{num2})"
            sdf_file_text = re.sub("\((\\S+?)\:\:(\\S+?)\)", replace, sdf_file_text)
            write_text(sdf_file_path, sdf_file_text)

        for i in range(0, len(areas_list)):
            min_area = int((self._get_synthesized_cell_count()+1)*areas_list[i])
            result = get_optimization_results(min_area)
            sizes_only: dict = result[0]
            sizes_only.pop("delay")
            sizes_only.pop("maxArea")
            sized_file_text: str = size_synthesized_file(sizes_only, min_area)
            sized_file_path = get_verilog_path(min_area)
            write_text(sized_file_path, sized_file_text)
            create_script(sized_file_path, min_area)
            if os.system(f"sta {OPT_SCRIPT_PATH}") != 0:
                print("Error during sdf generation, exiting...")
                exit()
            fix_sdf_file(min_area)
            original_sdf_text = read_text(get_sdf_path(min_area))
            strip_sdf_file(min_area)
            construct_sdf_file(min_area)
            new_sdf_text = read_text(get_sdf_path(min_area))
            os.remove(get_sdf_path(min_area))

            report_text = read_text(OPT_REPORT_PATH)
            delay = float(re.findall("(\\S+?)\\s+data arrival time", report_text)[0])
            opt_data: dict
            with open(self._opt_data_file_path, "r") as fp:
                opt_data = json.load(fp)
            opt_data[f"{min_area}"][0]["worst"] = delay
            with open(self._opt_data_file_path, "w") as fp:
                json.dump(opt_data, fp)

    def simulate(self, areas: list, cases: list) -> float:
        #if case["a"] + case["b"] + case["cin"] >= 2**self.width:
        #    print("WARNING: Overflow detected")
        def format_testbench(areas: list):
            includes_text: str = ""
            wires_text: str = ""
            modules_text: str = ""
            cases_text: str = ""
            for i in range(0, len(areas)):
                area = areas[i]
                includes_text += f"`include \"{self._create_sized_file_path(area)}\"\n"

                wires_text += f"\treg [`WIDTH-1:0]a{i};\n"
                wires_text += f"\treg [`WIDTH-1:0]b{i};\n"
                wires_text += f"\twire [`WIDTH-1:0]s{i};\n"
                wires_text += f"\treg cin{i};\n"
                wires_text += f"\twire cout{i};\n"

                modules_text += f"\t{self.adder_name}_{areas[i]} test{i}(.x1(a{i}), .x2(b{i}), .s(s{i}), .cin(cin{i}), .cout(cout{i}));\n"

                sdf_path = self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"
                cases_text += f'\t\t$sdf_annotate("{sdf_path}", tb.test{i});\n'
                cases_text += f'\t\t$monitor($realtime,,"a: %d, b: %d, s: %d", a{i}, b{i}, s{i}, cout{i});\n'
                cases_text += convert_cases_to_text(cases,i)

            #cases_text = convert_cases_to_text(cases)
            tb_template_text = read_text(SIM_TESTBENCH_TEMPLATE_PATH)
            tb_text = tb_template_text.format(includes=includes_text, wire_declares=wires_text, module_declares=modules_text, cases=cases_text, width=self.width)
            write_text(SIM_TESTBENCH_PATH, tb_text)
            if verilog.compile_verilog(tb_text) == False:
                print("TESTBENCH ERROR")
                exit()

        def run_testbench():
            if os.system("cvc64 +exe -pipe simulation/tb.v") != 0:
                print("TESTBENCH ERROR")
                exit()

            os.system(f"./cvcsim > {SIM_OUTPUT_PATH}")
            os.system("rm ./cvcsim")

        def retrieve_timing_results(cases) -> list:
            num_cases = len(cases)
            out_text = read_text(SIM_OUTPUT_PATH)
            out_lines = out_text.split("\n")
            line_index = 0
            timing_results: list = []
            num_lines = len(out_lines)
            for i in range(0, len(areas)):
                timing_results.append([])
                for j in range(1, num_cases+1):
                    section_start: str = f"MODULE{i}_CASE{j}"
                    section_end: str = section_start+"_END"
                    while out_lines[line_index] != section_start:
                        line_index+=1
                    line_index+=1
                    start_time = float(re.findall("^(\\S+)\\s", out_lines[line_index])[0])
                    while out_lines[line_index] != section_end:
                        line_index+=1
                    line_index-=1
                    end_time = float(re.findall("^(\\S+)\\s", out_lines[line_index])[0])
                    timing_results[i].append(end_time-start_time)
            return timing_results
 
        def get_testbench_output() -> float:
            out_text = read_text(SIM_OUTPUT_PATH)
            out_lines = out_text.split("\n")
            last_time_line = out_lines[-3]
            time = float(re.findall("^(\\S+)\\s", last_time_line)[0])
            return time

        real_areas = [int(area * (self._get_synthesized_cell_count()+1)) for area in areas]
        format_testbench(real_areas)
        run_testbench()
        return retrieve_timing_results(cases)

    def get_worst_case_delays(self, areas: list) -> list:
        delay_list: list = []
        data: dict
        with open(self._opt_data_file_path, "r") as fp:
            data = json.load(fp)
        for i in range(0, len(areas)):
            real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
            delay_list.append(data[f"{real_area}"][0]["worst"])
        return delay_list
    
    def get_optimizer_delays(self, areas: list) -> list:
        delay_list: list = []
        data: dict
        with open(self._opt_data_file_path, "r") as fp:
            data = json.load(fp)
        for i in range(0, len(areas)):
            real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
            delay_list.append(data[f"{real_area}"][0]["delay"])
        return delay_list

def convert_cases_to_text(cases: list, ind=-1):
    ind = "" if ind == -1 else int(ind)
    text: str = ""
    for i in range(0, len(cases)):
        case = cases[i]
        print(case)
        text += f'\t\t$display("MODULE{ind}_CASE{i+1}_CLEAR");\n'
        text += f"\t\ta{ind}=0;\n\t\tb{ind}=0;\n\t\tcin{ind}=0;\n\t\t#1;\n"
        text += f'\t\t$display("MODULE{ind}_CASE{i+1}");\n'
        text += f'\t\ta{ind}={case["a"]};\n'
        text += f'\t\tb{ind}={case["b"]};\n'
        text += f'\t\tcin{ind}={case["cin"]};\n'
        text += "\t\t#1;\n"
        text += f'\t\t$display("MODULE{ind}_CASE{i+1}_END");\n'

    return text
import sys
from pathlib import Path
from verilog import generate_basic_adder, generate_structured_adder, compile_verilog
import re
import graph
import os
sys.path.append("GateSize/")
import cktopt

class adder:
    def __init__(self, description: str):
        assert description.count(".") == 2
        [adder_type, width, structure] = tuple(description.split("."))

        # fill adder type and size information
        assert width.isdigit()
        self.width: int = int(width)
        type_info = adder_type.split("-")
        self.base_type: str = type_info[0]
        assert self.base_type in ["bk", "ks", "hybrid", "serial", "skl"]
        if len(type_info) == 2:
            assert self.base_type == "hybrid"
            assert type_info[1].isdigit()
            self.hybrid_levels: int = int(type_info[1])

        # fill adder structure information
        structure_info = structure.split("-")
        self.structure: str = structure_info[0]
        assert self.structure in ["basic", "rc", "cla", "cskip", "cselect"]
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
            self.verilog_structured_name = "{type}_{width}_{structure}_{block_size}".format(type=self.base_type, width=self.width, structure=self.structure, block_size=self.block_size)   
        self.adder_name = self.verilog_base_name if self.structure == "basic" else self.verilog_structured_name

        # generate important file/folder paths for each process (verification/verilog, synthesis, optimization, etc)
        subdir = f"base/{self.base_type}" if self.structure == "basic" else f"structured/{self.structure}"

        # verilog
        self._verilog_folder_path = f"verilog/{subdir}"
        self._verilog_file_path = f"{self._verilog_folder_path}/{self.adder_name}.v"

        # synthesis
        dependency_list = ["verilog/logic/pos_operator.v", "verilog/logic/neg_operator.v", "verilog/logic/carry_operator.v"]
        if self.structure != "basic":
            if self.structure == "cla":
                dependency_list.extend(["verilog/logic/cla4.v", "verilog/logic/block_signals4.v"])
            base_file_path = f"verilog/base/{self.base_type}/{self.base_type}{self.block_size}.v"
            dependency_list.append(base_file_path)
        self._dependencies = dependency_list

        self._syn_folder_path = f"synthesis/verilog/{subdir}"
        self._syn_file_path = f"{self._syn_folder_path}/{self.adder_name}.v"
        self._syn_area_file_path = f"{self._syn_folder_path}/{self.adder_name}_area"

        # optimization
        self._opt_data_folder_path = f"optimization/{subdir}"
        self._opt_data_file_path = f"{self._opt_data_folder_path}/{self.adder_name}_sizes.json"

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
        file = Path("verilog/base/{type}/{name}.v".format(type=self.base_type, name=self.verilog_base_name))
        file.parent.mkdir(parents=True, exist_ok=True)
        base_verilog_text = generate_basic_adder(self.adder_info)
        file.write_text(base_verilog_text)

        # now generate structured verilog if applicable
        if self.structure == "basic":
            self.verilog_text = base_verilog_text
            return 

        file = Path(f"verilog/structured/{self.structure}/{self.verilog_structured_name}.v")
        file.parent.mkdir(parents=True, exist_ok=True)
        structured_verilog_test = generate_structured_adder(self.adder_info)
        self.verilog_text = structured_verilog_test
        file.write_text(self.verilog_text)

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
        tb_template = open("verilog/testbench_template.txt", "r")
        tb_template_text = tb_template.read()
        tb_template.close()

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

        tb = open("verilog/tb.v", "w+")
        tb.write(tb_text)
        tb.close()

        os.system("make run_test")

    # Synthesizes the high-level verilog that represents this adder
    # Writes result to synthesis/verilog
    # Second phase in modeling process
    def synthesize(self) -> None:
        def generate_techmaps() -> str:
            text: str = ""
            for dependency in self._dependencies:
                text += f"techmap -map {dependency}\n"
            return text

        def fix_illegal_chars(text: str) -> str:
            text = text.replace("\\", "_")
            text = text.replace("$", "_")
            return text

        def rename_modules(text: str) -> str:
            rename_table = {
                
            }
            lines = text.split("\n")
            mod_start = 0
            mod_end = 0
            for i in range(0, len(lines)):
                if mod_start == 0 and "module" in lines[i]:
                    mod_start = i
                if mod_end == 0 and "endmodule" in lines[i]:
                    mod_end = i

        def fix_hanging_newlines(text: str) -> str:
            lines = text.split(";")
            length = len(lines)
            for i in range(0, length):
                lines[i] = lines[i].replace("\n", "")
                lines[i] = "\n" + lines[i]
            new_text = ";".join(lines)
            mod_start = new_text.find("module")
            new_text = new_text[mod_start:len(new_text)]
            new_text = re.sub(r"[^\S\r\n]+", " ", new_text)
            return new_text

        script_template = open("synthesis/script_template.txt", "r")
        script_template_text = script_template.read()
        techmaps = generate_techmaps()
        script_text = script_template_text.format(dependencies=" ".join(self._dependencies + [self._verilog_file_path]), design_name=self.adder_name, top_module=self._verilog_file_path, top_module_dir=self._verilog_folder_path)
        script = open("synthesis/script.tcl", "w+")
        script.write(script_text)
        script.close()
        os.system("sh synthesis/synthesis_setup.sh")
        # process and clean up synthesized code
        file = open(self._syn_file_path, "r")
        text = file.read()
        text = fix_hanging_newlines(text)
        text = fix_illegal_chars(text)
        file.close()
        file = open(self._syn_file_path, "w")
        file.write(text)
        self.synthesized_text = text

    # Returns the number of modules in synthesized verilog file
    def get_synthesized_cell_count(self) -> int:
        if hasattr(self, "_syn_cell_count"):
            return self._syn_cell_count
        area_file = open(self._syn_area_file_path, "r")
        text = area_file.read()
        lines = text.split("\n")
        last_line = lines[-2]
        regex = "\\w+\\s+(\\d+)\\s+\\d+\.\\d+"
        cell_count = int(re.findall(regex, last_line)[0])
        return cell_count

    # Calculates the worst case delay of adder circuit (according to synthesized
    # representation)
    def calculate_worst_case_delay(self, area_list):
        result = cktopt.optimize(self._syn_file_path, area_list)
        def fun(x):
            return x["delay"]
        return list(map(fun, result))

    def calculate_real_delay(self, a: int, b: int, cin: int):
        pass
import json
from ._file_structure import *
from ._verilog import *
from ._file import *

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
            includes_text += f"`include \"{self._get_sized_file_path(area)}\"\n"

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
        if compile_verilog(tb_text) == False:
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

    for area in areas:
        cell_area = int(area*(self._get_synthesized_cell_count()+1))
        self._construct_sdf_file(cell_area)

    real_areas = [int(area * (self._get_synthesized_cell_count()+1)) for area in areas]
    format_testbench(real_areas)
    run_testbench()
    for area in areas:
        cell_area = int(area*(self._get_synthesized_cell_count()+1))
        os.remove(self._get_sdf_path(cell_area))
    return retrieve_timing_results(cases)

def get_worst_case_delays(self, areas: list) -> list:
    delay_list: list = []
    data: dict
    with open(self._opt_data_file_path, "r") as fp:
        data = json.load(fp)
    for i in range(0, len(areas)):
        real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
        delay_list.append(data[f"{areas[i]}"][0]["worst"])
    return delay_list

def get_optimizer_delays(self, areas: list) -> list:
    delay_list: list = []
    data: dict
    with open(self._opt_data_file_path, "r") as fp:
        data = json.load(fp)
    for i in range(0, len(areas)):
        real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
        delay_list.append(data[f"{areas[i]}"][0]["delay"])
    return delay_list
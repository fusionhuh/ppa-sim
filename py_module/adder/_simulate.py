import json
from file_structure import *
from ._verilog import *
from ._file import *
import threading
import math
from multiprocessing.pool import ThreadPool

SIM_CHUNK_SIZE = 1000

def simulate(self, areas: list, cases: list, clear=False, target="individual", skip_accidentals=True) -> float:
    def format_testbench(areas: list, cases: list, thread_num: int = 0):
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
            cases_text += f'\t\t$monitor($realtime,,"a: %d, b: %d, cin: %d, s: %d, cout: %d", a{i}, b{i}, cin{i}, s{i}, cout{i});\n'
            cases_text += convert_cases_to_text(cases,i,clear=clear)

        tb_template_text = read_text(SIM_TESTBENCH_TEMPLATE_PATH)
        tb_text = tb_template_text.format(includes=includes_text, wire_declares=wires_text, module_declares=modules_text, cases=cases_text, width=self.width)
        write_text(SIM_TESTBENCH_PATH+str(thread_num), tb_text)
        #if compile_verilog(tb_text) == False:
        #    print("simulate.format_testbench(): Testbench could not compile (error)")
        #    exit()
        
    def run_testbench(thread_num: int = 0):
        if os.system(f"cvc64 +2state +interp +suppress_warns+3106+679+ +-pipe simulation/tb.v{thread_num} > {SIM_OUTPUT_PATH}{thread_num}") != 0:
            print("simulate.run_testbench(): Could not run testbench (error)")
            exit()

    def retrieve_timing_results(cases, thread_num: int = 0) -> list:
        num_cases = len(cases)
        out_text = read_text(SIM_OUTPUT_PATH+str(thread_num))
        out_lines = out_text.split("\n")
        line_index = 0
        timing_results: list = []
        num_lines = len(out_lines)
        for i in range(0, len(areas)):
            timing_results.append([None]*num_cases)
            for j in range(1, num_cases+1):
                section_start: str = f"MODULE{i}_CASE{j}"
                section_end: str = section_start+"_END"
                while out_lines[line_index] != section_start:
                    line_index+=1
                line_index+=1
                start_time = re.findall("^(\\S+)\\s", out_lines[line_index])
                if start_time == []: # likely 0 delay resulting from identical input
                    timing_results[i][j-1] = 0
                    continue
                start_time = float(start_time[0])
                while out_lines[line_index] != section_end:
                    line_index+=1
                line_index-=1
                end_time = float(re.findall("^(\\S+)\\s", out_lines[line_index])[0])
                timing_results[i][j-1] = end_time-start_time
            if skip_accidentals:
                new_results = [timing_results[i][j] for j in range(0, num_cases) if j % 2 == 1]
                timing_results[i] = new_results
        if target=="individual":
            return timing_results
        else:
            return [sum(result_list) for result_list in timing_results]

    def get_testbench_output() -> float:
        out_text = read_text(SIM_OUTPUT_PATH)
        out_lines = out_text.split("\n")
        last_time_line = out_lines[-3]
        time = float(re.findall("^(\\S+)\\s", last_time_line)[0])
        return time

    for area_scale in areas:
        real_area = int(self.get_min_area()*area_scale+1)
        self._construct_sdf_file(real_area)
    real_areas = [int(area_scale*self.get_min_area()+1) for area_scale in areas]

    old_cases = cases
    num_cases = len(old_cases)
    results = None

    iter_amount = SIM_CHUNK_SIZE
    curr = 0

    def sim_helper(cases, thread_num) -> list:
        results = None
        nonlocal real_areas
        format_testbench(real_areas, cases, thread_num)
        run_testbench(thread_num)
        if results == None:
            results = retrieve_timing_results(cases, thread_num)
        else:
            curr_results = retrieve_timing_results(cases, thread_num)
            for i in range(0, len(results)):
                results[i] += curr_results[i]
        return results

    while curr < num_cases:
        available_threads = min(12, math.ceil((num_cases - curr)/SIM_CHUNK_SIZE)) # replace min threads with constant

        pool = ThreadPool(available_threads)
        thread_list = [None] * available_threads

        for thread_num in range(0, available_threads):
            print(curr)
            if (curr + iter_amount > num_cases): iter_amount = num_cases - curr
            cases = old_cases[curr:(curr+iter_amount)]
            thread_list[thread_num] = pool.apply_async(sim_helper, (cases,thread_num))
            #sim_helper(cases, thread_num)
            curr+=iter_amount
        pool.close()
        pool.join()
        for thread_num in range(0, available_threads):  
            thread_results = thread_list[thread_num].get()
            if results == None:
                results = thread_results
            else:
                for i in range(0, len(results)):
                    results[i] += thread_results[i]

    for area_scale in areas:
        real_area = int(self.get_min_area()*area_scale+1)
        os.remove(self._get_sdf_path(real_area))
    print(len(results[0]))
    return results

def get_worst_case_delays(self, areas: list) -> list:
    delay_list: list = []
    data: dict
    with open(self._opt_data_file_path, "r") as fp:
        data = json.load(fp)
    for i in range(0, len(areas)):
        real_area = int(self.get_min_area()*areas[i]+1)
        delay_list.append(data[f"{areas[i]}"][0]["worst"])
    return delay_list

def get_optimizer_delays(self, areas: list) -> list:
    delay_list: list = []
    data: dict
    with open(self._opt_data_file_path, "r") as fp:
        data = json.load(fp)
    for i in range(0, len(areas)):
        real_area = int(self.get_min_area()*areas[i]+1)
        delay_list.append(data[f"{areas[i]}"][0]["delay"])
    return delay_list
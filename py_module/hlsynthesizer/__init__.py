from ._file import *
from file_structure import *
from ._verilog import *
from adder._verilog import *
import random
from adder import Adder
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt
import json
from tool_utils import sta
from tool_utils import vsyn
from tool_utils import vsim
from tool_utils import hls

SIM_CLOCK_TIME = 20
REAL_CLOCK_TIME = 3
NUM_THREADS = 12
VOLTAGE = 1.1
STANDARD_VOLTAGE = 1.1
ERROR_WINDOW_SIZE = 10
MIN_VOLTAGE = 0.5
MAX_VOLTAGE = 5
ERROR_THRESHOLD = 0.05

# replacement function args format: (curr_voltage, average window error rate)
# returns next voltage

def limd(curr_voltage: float, window_error: float, threshold: float, min_voltage: float) -> float:
    if window_error > threshold:
        curr_voltage += 0.05
    else:
        curr_voltage -= 0.01
        curr_voltage = max(curr_voltage, min_voltage)
    return curr_voltage

# PLEASE FIX THIS!
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

class HLSynthesizer(object):
    def __init__(self):
        self.num_adders = 0
        self.addition_info = []
        self.substitution_path = None
        self.substituted_adder_paths: set = set()
        self.generic_design_path = None # synthesized with no adder substitutions
        self.cache_path = None
        self.design_name: str
        self.no_substitution: bool = False
        self.connected_dffs_path = None

    def read_file(self, path: str, top_fname: str, xml_tb=None, override_cache = False):
        xml_tb_filepath = HLS_WORKING_DIR + "/tb.xml"

        self.yosys_out_path = f"{HLS_OUTPUT_DIR}/{top_fname}_yosys.v"
        self.substitution_path = f"{HLS_OUTPUT_DIR}/{top_fname}_substituted.v"
        self.cache_path = HLS_CACHE_DIR+f"/{top_fname}"
        self.connected_dffs_path = self.cache_path + "/connected_dffs.json"
        self.bambu_out_path = f"{HLS_OUTPUT_DIR}/{top_fname}.v"
        self.design_name = top_fname

        if not file_exists(self.bambu_out_path) or override_cache == True:
            hls.synthesize_file(
                file=path,
                top_fname=top_fname,
                clock_time=SIM_CLOCK_TIME,
                output_path=self.bambu_out_path,
                tb_path=HLS_TB_FORMAT_PATH.format(design=self.design_name),
                xml_tb=None
            )

    def get_worst_case_delay(self):
        top_level_file = self.generic_design_path if self.no_substitution == True else self.substitution_path
        return sta.run_worst_case_delay_script(
            top_level_file=top_level_file,
            design_name=self.design_name,
            submodules=self.adder_dependencies,
            sdf_output_path=HLS_WORKING_SDF_PATH,
            script_path=HLS_WORKING_DIR+"/sta.tcl"
        )

    def print_adder_info(self):
        print(f"There are {self.num_adders} adders in this design.")
        for i, adder_info in enumerate(self.addition_info):
            print(f"Adder num {i}:")
            print(f"  name: {adder_info['name']}")
            print(f"  width: {adder_info['new_width']}")
 
    def simulate(self) -> dict:
        print("here in simulate")
        return vsim.simulate_hls_tb(
            tb_file=HLS_TB_FORMAT_PATH.format(design=self.design_name),
            design_file=self.substitution_path,
            submodules=self.adder_dependencies,
            design_name=self.design_name,
            clock_time=SIM_CLOCK_TIME
        )

    def check_error_rate(self, update_func, window_size, clock_time):
        curr_voltage = STANDARD_VOLTAGE
        timing_results: dict = self.simulate()
        num_cycles = timing_results["NUM_CYCLES"]
        timing_results = timing_results["dff"]
        num_dffs = len(list(timing_results.keys()))
        error_results = [0.0] * num_cycles # maps each cycle to the instantaneous error rate at that cycle
        average_error_results = [0.0]*num_cycles # maps each cycle to the window average error at that cycle
        voltage_results = [0] * num_cycles # maps each cycle to the current voltage
        window_total_error = 0.0
        window_average = 0.0
        for cycle in range(0,num_cycles):
            num_violations = 0
            for dff, cycle_to_delay in timing_results.items():
                setup_time = 0.0 if cycle not in cycle_to_delay.keys() else cycle_to_delay[cycle][0]
                scaled_time = setup_time*(STANDARD_VOLTAGE/curr_voltage)
                if scaled_time > clock_time: # may need to apply some scaling here
                    num_violations += 1
            voltage_results[cycle] = curr_voltage
            curr_voltage = update_func(curr_voltage, window_average)

            cycle_error_rate = num_violations/num_dffs
            error_results[cycle] = cycle_error_rate

            window_total_error += cycle_error_rate

            if cycle+1 > window_size:
                window_total_error -= error_results[cycle-window_size] # should never produce a negative result
                window_average = window_total_error/window_size
            else:
                window_average = window_total_error/(cycle+1)

            average_error_results[cycle] = window_average

        return (average_error_results, error_results, voltage_results, num_cycles)                    

    def analyze_limd(self, window_size, min_voltage, threshold, clock_time):
        print("here finally")
        average_error, error, voltage, num_cycles = self.check_error_rate(lambda curr_voltage, window_average: limd(curr_voltage, window_average, threshold, min_voltage), window_size, clock_time)
        print(voltage)
        fig, ax1 = plt.subplots()
        ax1.plot(range(0, num_cycles),average_error, color='red')
        ax2 = ax1.twinx()
        ax2.plot(range(0, num_cycles), voltage, color='green')
        fig.tight_layout()
        plt.show()
                
# data analysis portion, may want to split into new function
    def analyze_and_replace_adders(self, index: int, priority="area", allow_errors="False"):
        adder = self.addition_info[index]
        # step 1: classify current 

        ordered_name_list = [self.addition_info[i]["name"] for i in range(0, len(self.addition_info))]

        connected_dffs: dict = json.loads(read_text(self.connected_dffs_path))
        print(connected_dffs)
        exit()

        for i, name in enumerate(ordered_name_list):
            print(f"Adder {i}: ")
            mean_delay: float = 0.0
            max_delay: float = 0.0
            nonactive_cycles: int = 0
            active_cycles: int = 0
            for j in range(0, num_cycles):
                if j not in adder_results[name].keys():
                    nonactive_cycles+=1
                    continue
                pair = adder_results[name][j]
                delay = pair[1] - pair[0]
                if delay <= 0.0:
                    nonactive_cycles+=1
                    continue

                active_cycles+=1
                max_delay = max(max_delay, delay)
                mean_delay += delay
            
            mean_delay = round(mean_delay/active_cycles,4) if active_cycles != 0 else 0.0
            max_delay = round(max_delay, 4)
            instance_name = self.addition_info[i]['name']

            print(f"  instance name: {instance_name}")
            print(f"  width: {self.addition_info[i]['new_width']}")
            print(f"  output bits used: {self.addition_info[i]['old_width']}/{self.addition_info[i]['new_width']}" )
            print(f"  cycles active: {active_cycles} ({round(100*active_cycles/num_cycles,2)}% of total)")
            print(f"  mean (across only active cycles): {mean_delay}")
            print(f"  max: {max_delay}")
            print(f"  num connected DFFs: {num_connections}")
            connected_dffs = dict(sorted(connected_dffs.items()))
            for sum_bit, dff_list in connected_dffs.items():
                worst_setup = 0
                for dff in dff_list:
                    if dff not in dff_results.keys(): continue
                    timing_data = dff_results[dff]
                    for cycle, pair in timing_data.items():
                        if pair[0] > worst_setup: worst_setup = pair[0]

                print(f"    s[{sum_bit}] worst_setup -> {worst_setup}")

    def get_num_adders(self):
        return self.num_adders

    def substitute_adders(self, adder_types: list, areas: list, override_cache:bool=False):
        print("here in substitute")
        if adder_types == None:
            self.no_substitution = True
            self.get_worst_case_delay()
            return

        self.no_substitution = False
        text = read_text(self.substitution_template_path)
        self.adder_dependencies = set()
        total_index = 0      
        for i, curr_add_expr in enumerate(self.addition_info):
            curr = i
            width = curr_add_expr["new_width"]

            curr_adder: Adder = Adder(f"{adder_types[i]}.{width}.basic")
            if not curr_adder.is_generated():
                curr_adder.generate_verilog()
            if not curr_adder.is_synthesized():
                curr_adder.synthesize()
            if not curr_adder.is_optimized([areas[i]]): curr_adder.optimize([areas[i]])

            self.adder_dependencies.add(curr_adder.get_optimized_verilog_path(areas[i]))

            old_ports = curr_add_expr["ports"]
            new_adder_declaration = ""

            mod_type = curr_add_expr["type"]
            cin = "1'b1" if mod_type == "ui_minus_expr_FU" or mod_type == "minus_expr_FU" else "1'b0"

            new_ports = {"x1" : old_ports['in1']+" ", "x2" : old_ports['in2']+" ", "s" : old_ports['out1']+" ", "cin":cin, "cout" : "cout_placeholder"}
            old_adder_declaration = curr_add_expr["full_text"]

            new_ports["cout"] = f"cout_placeholder_{total_index}"
            new_adder_declaration += f"wire {new_ports['cout']} ;\n {curr_adder.create_module_declaration(curr_add_expr['name'], new_ports, area=areas[i])}\n"
            text = text.replace(old_adder_declaration, new_adder_declaration)
            total_index += 1
        text = re.sub(r"(\\\S+?)\[", r"\1 [", text)
        text = re.sub(r"(\\\S+?)\,", r"\1 ,", text)
        text = re.sub(r"(\\\S+?)\}", r"\1 }", text)

        write_text(self.substitution_path, text)
        self.get_worst_case_delay()


    def synthesize_design(self, override_cache=False):
        print("HERE")
        def retrieve_connected_dffs(adder_name: str, thread_id = 0)->tuple: # returns (connected_dffs: dict (sum_bit -> dff_instance), num_connections: int) 
            return sta.run_connected_dffs_script(
                top_level_file=self.substitution_path,
                design_name=self.design_name,
                instance_name=adder_name,
                submodules=self.adder_dependencies,
                thread_id=thread_id
            )

        exists_in_cache: bool = False
        cache_dir = HLS_CACHE_DIR + f"/{self.design_name}"
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)

        self.substitution_template_path = cache_dir + f"/{self.design_name}_template.v"
        if not file_exists(self.substitution_template_path):
            os.system(f"touch {self.substitution_template_path}")
        else:
            exists_in_cache = True

        if override_cache == True or exists_in_cache == False:
            vsyn.run_hls_template_syn_script(
                top_level_file=self.bambu_out_path,
                design_name=self.design_name,
                clock_time=REAL_CLOCK_TIME,
                syn_output_path=self.substitution_template_path,
                script_path=HLS_WORKING_DIR+"/syn_template.tcl"
            )
            vsyn.run_hls_generic_syn_script(
                top_level_file=self.bambu_out_path,
                design_name=self.design_name,
                clock_time=REAL_CLOCK_TIME,
                syn_output_path=self.generic_design_path,
                script_path=HLS_WORKING_DIR+"/syn_generic.tcl"
            )

            write_text(self.substitution_template_path, fix_hanging_newlines(read_text(self.substitution_template_path)))

            self.addition_info = get_addition_info(read_text(self.substitution_template_path))
            self.num_adders = len(self.addition_info)

            # performing initial substitution and connected dff retrieval
            initial_types = ["serial"]*self.num_adders
            initial_areas = [1]*self.num_adders

            self.substitute_adders(initial_types, initial_areas)
            curr_adder = 0
            connected_dffs = dict()
            while curr_adder != self.num_adders:
                available_threads = min(NUM_THREADS, self.num_adders-curr_adder)

                pool = ThreadPool(available_threads)
                thread_list = [None]*available_threads

                start_reference = curr_adder
                for thread_num in range(0, available_threads):
                    name = self.addition_info[curr_adder]["name"]
                    thread_list[thread_num] = pool.apply_async(retrieve_connected_dffs, (name, thread_num))
                    curr_adder+=1

                pool.close()
                pool.join()
                for thread_num in range(0, available_threads):
                    result = thread_list[thread_num].get()
                    name = self.addition_info[start_reference+thread_num]["name"]
                    connected_dffs[name] = result
            write_text(self.connected_dffs_path, json.dumps(connected_dffs))

        self.addition_info = get_addition_info(read_text(self.substitution_template_path))
        self.num_adders = len(self.addition_info)

        self.substitute_adders(["serial"]*self.num_adders, [1]*self.num_adders)



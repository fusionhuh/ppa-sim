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
from tool_utils.multithreading import *
import numpy
from numpy import arange
from numpy.fft import fft, ifft
import numpy as np

SIM_CLOCK_TIME = 20
REAL_CLOCK_TIME = 3
NUM_THREADS = 12
VOLTAGE = 1.1
STANDARD_VOLTAGE = 1.1
ERROR_WINDOW_SIZE = 10
MIN_VOLTAGE = 0.3
THRESHOLD_VOLTAGE = 0.5
ALPHA=1.3
MAX_VOLTAGE = 5
ERROR_THRESHOLD = 0.05

# replacement function args format: (curr_voltage, average window error rate)
# returns next voltage

class DynamicSimState(object):
    def __init__(self):
        self.integral_error = 0
        self.instantaneous_error = 0
        self.window_error = 0
        self.curr_voltage = 0

class DynamicSimResults(object):
    def __init__(self, num_cycles: int):
        self.cycle_error = [0] * num_cycles
        self.cycle_voltage = [0] * num_cycles
        self.cycle_scaled_worst_case_delay = [0] * num_cycles
        self.cycle_unscaled_worst_case_delay = [0] * num_cycles
        self.cycle_speedup = [0] * num_cycles
        self.num_cycles = num_cycles

        self.mean_voltage = None
        self.voltage_stdev = None
        self.mean_error = None
        self.error_stdev = None

    def filter_empty_cycles(self):
        new_num_cycles = 0
        new_cycle_error = []
        new_cycle_voltage = []
        new_cycle_scaled_worst_case_delay = []
        new_cycle_unscaled_worst_case_delay = []
        new_cycle_speedup = []

        for i in range(0, self.num_cycles):
            if self.cycle_unscaled_worst_case_delay[i] != 0:
                new_num_cycles += 1
                new_cycle_error.append(self.cycle_error[i])
                new_cycle_voltage.append(self.cycle_voltage[i])
                new_cycle_scaled_worst_case_delay.append(self.cycle_scaled_worst_case_delay[i])
                new_cycle_unscaled_worst_case_delay.append(self.cycle_unscaled_worst_case_delay[i])
                new_cycle_speedup.append(self.cycle_speedup[i])
        self.num_cycles = new_num_cycles
        self.cycle_error = new_cycle_error
        self.cycle_voltage = new_cycle_voltage
        self.cycle_scaled_worst_case_delay = new_cycle_scaled_worst_case_delay
        self.cycle_unscaled_worst_case_delay = new_cycle_unscaled_worst_case_delay

    def calculate_stats(self):
        self.mean_voltage = np.mean(self.cycle_voltage)
        self.voltage_stdev = np.std(self.cycle_voltage)
        self.mean_error = np.mean(self.cycle_error)
        self.error_stdev = np.std(self.cycle_error)
        

def calculate_speedup(voltage: float):
    ratio = (STANDARD_VOLTAGE*((voltage - THRESHOLD_VOLTAGE)**ALPHA))/(voltage*((STANDARD_VOLTAGE - THRESHOLD_VOLTAGE)**ALPHA))
    if ratio == 0: ratio = 0.0001
    if isinstance(ratio, complex): return 0.0001
    return ratio


def limd(curr_voltage: float, window_error: float, threshold: float, min_voltage: float) -> float:
    if window_error > threshold:
        curr_voltage *= 1.1
    else:
        curr_voltage -= 0.05
        curr_voltage = max(curr_voltage, min_voltage)
    return curr_voltage

def pi(sim_state: DynamicSimState, Kc, T1):
    next = STANDARD_VOLTAGE + Kc*sim_state.instantaneous_error + (Kc/T1)*sim_state.integral_error
    return min(max(MIN_VOLTAGE, next), STANDARD_VOLTAGE)

def constant_v(curr_voltage: float, window_error: float):
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
        self.connected_dffs = dict()
        self.dff_to_adder = dict()
        self.worst_case_delay = None

        self.working_results = None # temp variable, remove later

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
                xml_tb=xml_tb
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
 
    def simulate(self, init_clock_time, thread_id = 0) -> dict:
        print(init_clock_time)
        return vsim.simulate_hls_tb(
            template_tb_file=HLS_TB_FORMAT_PATH.format(design=self.design_name),
            design_file=self.substitution_path,
            submodules=self.adder_dependencies,
            design_name=self.design_name,
            clock_time=init_clock_time,
            thread_id=thread_id
        )

    def dynamic_sim(self, sim_results: vsim.SimResults, update_func, window_size, clock_time, target_error, skip_zeros: bool = True):
        curr_voltage = STANDARD_VOLTAGE

        num_cycles = sim_results.num_cycles
        timing_results: vsim.TimeResults = sim_results.dff_results
        num_dffs = timing_results.num_objects()
        error_results = [0.0] * num_cycles # maps each cycle to the instantaneous error rate at that cycle
        average_error_results = [0.0]*num_cycles # maps each cycle to the window average error at that cycle
        voltage_results = [0] * num_cycles # maps each cycle to the current voltage
        window_total_error = 0.0
        window_average = 0.0
        violated_dffs: set = set()
        speedups = []

        results: DynamicSimResults = DynamicSimResults(num_cycles)
        sim_state: DynamicSimState = DynamicSimState()
        for cycle in range(0,num_cycles):
            num_violations = 0
            dff_to_delay = timing_results.get_cycle_delays(cycle)
            speedup = calculate_speedup(curr_voltage)
            results.cycle_speedup[cycle] = speedup
            for dff, delay_pair in dff_to_delay.items():
                setup_time = delay_pair[0]
                results.cycle_unscaled_worst_case_delay[cycle] = max(results.cycle_unscaled_worst_case_delay[cycle], setup_time)
                scaled_time = 0
                if setup_time != 0:
                    scaled_time = setup_time/speedup
                    results.cycle_scaled_worst_case_delay[cycle] = max(results.cycle_scaled_worst_case_delay[cycle], scaled_time)
                if scaled_time > clock_time: # may need to apply some scaling here
                    num_violations += 1
                    violated_dffs.add(dff)

            
            voltage_results[cycle] = curr_voltage
            results.cycle_voltage[cycle] = curr_voltage
            
            cycle_error_rate = num_violations/num_dffs - target_error
            error_results[cycle] = cycle_error_rate

            results.cycle_error[cycle] = cycle_error_rate

            window_total_error += cycle_error_rate

            if skip_zeros == True and results.cycle_unscaled_worst_case_delay[cycle] == 0:
                continue

            sim_state.instantaneous_error = cycle_error_rate
            sim_state.integral_error += cycle_error_rate

            curr_voltage = update_func(sim_state)

            if cycle+1 > window_size:
                window_total_error -= error_results[cycle-window_size] # should never produce a negative result
                window_average = window_total_error/window_size
            else:
                window_average = window_total_error/(cycle+1)

            average_error_results[cycle] = window_average

        if skip_zeros: results.filter_empty_cycles()

        results.calculate_stats()

        return results                    


    def analyze_update_func(self, update_func, window_size, clock_time, target_error, skip_zeros: bool = True):
        sim_results = self.simulate(math.ceil(clock_time), 0)
        dsr: DynamicSimResults = self.dynamic_sim(sim_results, update_func, window_size, clock_time, target_error, skip_zeros)
        fig, ax1 = plt.subplots()
        ax1.plot(range(0, dsr.num_cycles),dsr.cycle_voltage, color='red')
        ax1.set(ylabel="Voltage")
        ax2 = ax1.twinx()
        ax2.plot(range(0, dsr.num_cycles), dsr.cycle_error, color='green')
        ax2.set(ylabel="Error rate")
        fig.tight_layout()
        plt.title(self.design_name)
        plt.show()

    def analyze_delays(self, update_func, window_size, clock_time, target_error, skip_zeros: bool = True):
        sim_results = self.simulate(math.ceil(clock_time)*2, 0)
        dsr: DynamicSimResults = self.dynamic_sim(sim_results, update_func, window_size, clock_time, target_error, skip_zeros)
        fig, ax1 = plt.subplots()
        ax1.plot(range(0, dsr.num_cycles),dsr.cycle_unscaled_worst_case_delay, color='red')
        #ax1.set(ylabel="Unscaled worst case cycle delay")
        #ax2 = ax1.twinx()
        ax1.plot(range(0, dsr.num_cycles), [self.worst_case_delay]*dsr.num_cycles, color='green')
        #ax2.set(ylabel="Clock time")
        #fig.tight_layout()
        plt.title(self.design_name)
        plt.show() 

    def analyze_limd(self, window_size, min_voltage, threshold, clock_time):

        critical_errors, average_error, error, voltage, num_cycles = self.dynamic_sim(self.working_results, lambda curr_voltage, window_average: limd(curr_voltage, window_average, threshold, min_voltage), window_size, clock_time)
        

    def analyze_pi(self, Kc, T1, target_error):
        #if self.working_results == None:
        #    self.working_results = sim_results = self.simulate(math.ceil(self.worst_case_delay*2), 0)
        update_func = lambda x: pi(x, Kc, T1)
        self.analyze_delays(update_func, 10, self.worst_case_delay, target_error)

    def analyze_bla(self, Kc, T1, target_error):
        update_func = lambda x: pi(x, Kc, T1)
        self.analyze_delays(update_func, 10, self.worst_case_delay, target_error)

    def determine_critical_values(self):
        min_time = self.worst_case_delay/(STANDARD_VOLTAGE/1.0)
        cycle_times = arange(min_time, self.worst_case_delay, 0.1)
        results = perform_sync_tasks(function=self.simulate, 
                                     inputs=cycle_times, 
                                     dynamic_arg_index=0,
                                     args=(None,))
        critical_time, critical_results = None, None
        supercritical_time, supercritical_results = None, None

        for i, time in enumerate(cycle_times):
            sim_results: vsim.SimResults = results[i]
            if sim_results.completed == False: continue
            invalid_result = False
            for case in sim_results.case_results:
                if case[0] == False:
                    invalid_result = True
            if invalid_result == True: continue
            
            critical_time = time
            critical_results = results[i]
            if i > 1 and results[i-1].completed == True: 
                supercritical_time = cycle_times[i-1]
                supercritical_results = results[i-1]
            break

        print(supercritical_time)
        print(critical_time)

        self._determine_worst_case_cycle_delays(critical_results)

        return

        # need to update this part of the code to reflect SimResults implementation
        violated_dffs, average_error, error, voltage, num_cycles = self.dynamic_sim(critical_results[0], constant_v, 10, round(supercritical_time,2))
        fig, ax1 = plt.subplots()
        ax1.plot(range(0, num_cycles),average_error, color='red')
        ax2 = ax1.twinx()
        ax2.plot(range(0, num_cycles), voltage, color='green')
        fig.tight_layout()
        plt.show()    

        print(violated_dffs)
        implicated_adders: dict = dict()
        adderless_dffs: set = set()
        for dff in violated_dffs:
            if dff in self.dff_to_adder.keys():
                adders = self.dff_to_adder[dff]
                for adder_bit_pair in adders:
                    adder = adder_bit_pair[0]
                    if adder not in implicated_adders.keys(): implicated_adders[adder] = 1
                    else: implicated_adders[adder]+=1
            else:
                adderless_dffs.add(dff)

        print(implicated_adders)
        print(adderless_dffs)

        exit()

        # if no "supercritical" cases, skip this phase of analysis

        supercritical_case_results = supercritical_results[1]
        failed_cases = [i for i in range(0, len(case_results)) if supercritical_case_results[i][0] == False]




        for i, time in enumerate(cycle_times):
            result = results[i]
            attached_adders: set = set()   
            num_adderless_dffs = 0 
            unique_dffs: set = set()
            dff_to_num_violations: dict = dict()
            for dff, time in result[0]['violations']:
                unique_dffs.add(dff)
                if dff not in dff_to_num_violations.keys():
                    dff_to_num_violations[dff] = 1
                else:
                    dff_to_num_violations[dff] += 1

                if dff not in self.dff_to_adder.keys():
                    num_adderless_dffs += 1
                else:
                    adders = self.dff_to_adder[dff]
                    for adder in adders: attached_adders.add(adder)

    def _determine_worst_case_cycle_delays(self, results: vsim.SimResults):
        num_cycles = results.num_cycles
        cycle_to_delay = [None]*num_cycles
        real_cycle_delays = []
        dff_results: vsim.TimeResults = results.dff_results
        for i in range(40, num_cycles):
            cycle_results: dict = map(lambda x: x[0], dff_results.get_cycle_delays(i).values())
            worst = max(list(cycle_results))
            cycle_to_delay[i] = worst
            if worst == 0: # naive way of handling empty cycles, may need to change later
                continue
            real_cycle_delays += [worst]



        sr = 20000
        ts = 1.0/sr

        X = fft(real_cycle_delays)
        N = len(X)
        n = np.arange(N)
        T = N/sr
        freq = n/T

        enumerated_X = enumerate(X)
        print(list(enumerated_X))




        bound = 20
        for i in range(bound, len(X)):
            X[i] = 0

        plt.stem(freq, np.abs(X))
        plt.show()


        fig, ax = plt.subplots()
        ax.plot(range(0, len(real_cycle_delays)), real_cycle_delays)
        #ax.plot(range(0, len(real_cycle_delays)), ifft(X), 'r')
        plt.show()



# data analysis portion, may want to split into new function
    def analyze_and_replace_adders(self, index: int, priority="area", allow_errors="False"):
        adder = self.addition_info[index]
        # step 1: classify current 

        ordered_name_list = [self.addition_info[i]["name"] for i in range(0, len(self.addition_info))]

        connected_dffs: dict = json.loads(read_text(self.connected_dffs_path))
        print(connected_dffs)
        critical_errors, average_error, error, voltage, num_cycles = self.dynamic_sim(lambda curr_voltage, window_average: constant_v(MIN_VOLTAGE, 1), window_size, clock_time)        
        

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
        if adder_types == None:
            self.no_substitution = True
            self.worst_case_delay = self.get_worst_case_delay()
            return

        self.no_substitution = False
        text = read_text(self.substitution_template_path)
        self.adder_dependencies = set()
        total_index = 0      
        for i, curr_add_expr in enumerate(self.addition_info):
            curr = i
            width = curr_add_expr["new_width"]
            if width < 4: width = 4

            curr_adder: Adder = Adder(f"{adder_types[i]}.{width}.basic")
            if not curr_adder.is_generated():
                curr_adder.generate_verilog()
            if not curr_adder.is_synthesized():
                curr_adder.synthesize()
            if not curr_adder.is_optimized([areas[i]]): 
                curr_adder.optimize([areas[i]])

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
        self.worst_case_delay = self.get_worst_case_delay()


    def synthesize_design(self, override_cache=False):
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
            #vsyn.run_hls_generic_syn_script(
            #    top_level_file=self.bambu_out_path,
            #    design_name=self.design_name,
            #    clock_time=REAL_CLOCK_TIME,
            #    syn_output_path=self.generic_design_path,
            #    script_path=HLS_WORKING_DIR+"/syn_generic.tcl"
            #)

            write_text(self.substitution_template_path, fix_hanging_newlines(read_text(self.substitution_template_path)))

            self.addition_info = get_addition_info(read_text(self.substitution_template_path))
            self.num_adders = len(self.addition_info)

            # performing initial substitution and connected dff retrieval
            initial_types = ["serial"]*self.num_adders
            initial_areas = [1]*self.num_adders

            self.substitute_adders(initial_types, initial_areas)
            curr_adder = 0

            connected_dffs = dict()

            inputs = [adder["name"] for adder in self.addition_info]

            results = perform_sync_tasks(retrieve_connected_dffs, inputs, 0, (None,))
            
            for i, name in enumerate(inputs):
                self.connected_dffs[name] = results[i]


            '''
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
            '''
            print(json.dumps(self.connected_dffs))
            write_text(self.connected_dffs_path, json.dumps(self.connected_dffs))


        self.addition_info = get_addition_info(read_text(self.substitution_template_path))
        self.num_adders = len(self.addition_info)

        self.adder_to_dffs = json.loads(read_text(self.connected_dffs_path))
        for adder, bit_to_list in self.adder_to_dffs.items():
            for key, dff_list in bit_to_list.items():
                if key == "NUM_CONNECTIONS": continue
                for dff in dff_list:
                    if dff in self.dff_to_adder.keys():
                        self.dff_to_adder[dff] += [(adder, key)]
                    else:
                        self.dff_to_adder[dff] = [(adder, key)]

        self.addition_info = get_addition_info(read_text(self.substitution_template_path))

        self.num_adders = len(self.addition_info)

        self.substitute_adders(["serial"]*self.num_adders, [1]*self.num_adders)



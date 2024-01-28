from .command import *
from file_structure import *
from hlsynthesizer._file import *
import time
import threading
import os
import datetime
import pexpect
import re

lock: threading.Lock = threading.Lock()

_monitoring_code_str = r'''
    reg [63:0] stored_x1 = 0;
    reg [63:0] stored_x2 = 0;
    reg stored_cin = 0;
    reg stored_cout = 0;
    reg [63:0] stored_s = 0;

    always@(*) begin
        if (x1 !== stored_x1) begin
            stored_x1<=x1;
            $display($realtime,,"%m \\\\EVENT:ADDER_INPUT_CHANGE");
        end
        else if (x2 !== stored_x2) begin
            stored_x2<=x2;
            $display($realtime,,"%m \\\\EVENT:ADDER_INPUT_CHANGE");
        end
        else if (cin !== stored_cin) begin
            stored_cin<=cin;
            $display($realtime,,"%m \\\\EVENT:ADDER_INPUT_CHANGE");
        end

        if (s !== stored_s) begin
            stored_s <= s;
            $display($realtime,,"%m \\\\EVENT:ADDER_OUTPUT_CHANGE");
        end
        else if (cout != stored_cout) begin
            stored_cout <= cout;
            $display($realtime,,"%m \\\\EVENT:ADDER_OUTPUT_CHANGE");
        end  
    end
endmodule
'''

class TimeResults(object):
    def __init__(self):
        self.obj_cycle_to_delay: dict = dict()
        self.cycle_obj_to_delay: dict = dict()

    def get_object_cycle_delay(self, object: str, cycle: int) -> tuple:
        return self.obj_cycle_to_delay[object][cycle]

    # return dict maps cycle to tuple of (input change time, output change time) for that particular object
    def get_object_delays(self, object: str) -> dict:
        return self.obj_cycle_to_delay[object]

    # return dict maps object name to tuple of (input change time, output change time) for that particular cycle
    def get_cycle_delays(self, cycle: int) -> dict:
        if cycle not in self.cycle_obj_to_delay.keys():
            return {0:[0,0]}
        return self.cycle_obj_to_delay[cycle]

    def update_entry(self, object: str, cycle: int, type: str, time: float):
        assert type == "INPUT_CHANGE" or type == "OUTPUT_CHANGE"
        if object not in self.obj_cycle_to_delay.keys(): 
            self.obj_cycle_to_delay[object] = dict()
        if cycle not in self.obj_cycle_to_delay[object].keys():
            self.obj_cycle_to_delay[object][cycle] = [0, 0]
        index = 1 if type == "OUTPUT_CHANGE" else 0
        self.obj_cycle_to_delay[object][cycle][index] = max(self.obj_cycle_to_delay[object][cycle][index], time)

        if cycle not in self.cycle_obj_to_delay.keys(): 
            self.cycle_obj_to_delay[cycle] = dict()
        if object not in self.cycle_obj_to_delay[cycle].keys():
            self.cycle_obj_to_delay[cycle][object] = [0,0]
        self.cycle_obj_to_delay[cycle][object][index] = max(self.cycle_obj_to_delay[cycle][object][index], time)

    def num_objects(self) -> int:
        return len(list(self.obj_cycle_to_delay.keys()))

class SimResults(object):
    def __init__(self, dff_results, adder_results, num_cycles):
        self.completed = False
        self.case_results = None
        self.dff_results: TimeResults = dff_results
        self.adder_results: TimeResults = adder_results
        self.num_cycles = num_cycles
        self.violations=None


def simulate_hls_tb(template_tb_file: str, design_file: str, submodules: list, design_name: str, clock_time: float, thread_id: int=0):
    timing_results_path = HLS_WORKING_DIR + f"/time_results{thread_id}.txt"
    num_cycles = 0
    sim_failed = False
    working_tb_path = HLS_WORKING_DIR + f"/tb{thread_id}.v"
    tb_summary_path = HLS_WORKING_DIR + f"/results{thread_id}.txt"

    rounded_clock_time = round(clock_time,1)
    text = read_text(template_tb_file).replace(r"\\CLOCK_TIME", str(rounded_clock_time)).replace(r"\\THREAD_ID", str(thread_id))
    text = text.replace("`define HALF_CLOCK_PERIOD 10.0", f"`define HALF_CLOCK_PERIOD {rounded_clock_time/2}")

    write_text(working_tb_path, text)

    def enable_port_monitoring():
        for dep in submodules:
            text = read_text(dep)
            text = text.replace("endmodule", _monitoring_code_str)
            write_text(dep, text)

    def disable_port_monitoring():
        for dep in submodules:
            text = read_text(dep)
            text = text.replace(_monitoring_code_str, "endmodule")
            write_text(dep, text)

    def extract_timing_results():
        nonlocal num_cycles
        text = read_text(timing_results_path)
        lines = text.split("\n")
        results_dict: dict = dict() # maps (adder|dff) -> mod name -> clock cycle -> (start time, end time)
        dff_results: TimeResults = TimeResults()
        adder_results: TimeResults = TimeResults()
        results_dict["violations"] = list()
        found_start = False
        timing_violation_pattern = r"\*\*[\S\s]+?WARN\*\*[\S\s]+?timing violation in (\S+?) [\S\s\n]+? setup[\S\s]+?:(\d+?) ps"
        i = 0
        while i < len(lines):
            line = lines[i]
            if r"\\EVENT" not in line:
                if i < len(lines)-1:
                    if line[0:2] != "**": 
                        i+=1
                        continue
                    match = re.findall(timing_violation_pattern, line+f"\n{lines[i+1]}", flags=re.MULTILINE)
                    if len(match) == 0:
                        i+=1
                        continue
                    dff_name = match[0][0].rsplit(".", 1)[1]
                    time = float(match[0][1])/1000
                    results_dict["violations"].append((dff_name, time))
                    i+=2
                    continue
                i+=1
                continue
            line = line.replace("  ", " ")

            event_time, mod_name, event_type = line.split(" ")
            event_type = event_type.replace(r"\\EVENT:", "")
            event_time = float(event_time)
            clock_cycle = int(event_time/clock_time)
            num_cycles = max(clock_cycle+1, num_cycles)
            mod_name = mod_name.replace(f"{design_name}_tb_top.DUT.{design_name}.", "")

            mod_type = "adder" if "ADDER" in event_type else "dff"
            #if mod_name not in results_dict[mod_type].keys():
            #    results_dict[mod_type][mod_name] = dict()

            #if clock_cycle not in results_dict[mod_type][mod_name].keys():
            #    results_dict[mod_type][mod_name][clock_cycle] = [0, 0]
            
            change_type = event_type.split("_", 1)[1]
            adjusted_time = event_time - (clock_time * clock_cycle)

            if event_type == "ADDER_INPUT_CHANGE":
                adder_results.update_entry(mod_name, clock_cycle, change_type, adjusted_time)
            else:
                dff_results.update_entry(mod_name, clock_cycle, change_type, adjusted_time)
            '''
            prev_pair = results_dict[mod_type][mod_name][clock_cycle]
            results_dict[mod_type].update_entry()
            if "INPUT_CHANGE" in event_type:
                results_dict[mod_type][mod_name][clock_cycle][0] = max(adjusted_time, prev_pair[0])
            elif "OUTPUT_CHANGE" in event_type: 
                results_dict[mod_type][mod_name][clock_cycle][1] = max(adjusted_time, prev_pair[1])
            '''
            i+=1
        results_dict["NUM_CYCLES"] = num_cycles
        sim_results = SimResults(dff_results, adder_results, num_cycles)
        return sim_results

    mod_list_str = ""
    for mod in submodules:
        mod_list_str += f"{mod} "
    command_str = f"cvc64 +interp {working_tb_path} {design_file} {mod_list_str} substitution/hardware/NangateOpenCellLibrary_typical_conditional.v"
    #enable_port_monitoring()
    latest_modify_time = None
    output_started = False
    simulation_halted = False
    proc: pexpect.spawn = run_command(command_str, redirect=timing_results_path, touch_list=[timing_results_path], as_subprocess=True)
    init_modify_time = os.path.getmtime(timing_results_path)

    while True:
        if output_started == True:
            status = proc.isalive()
            time.sleep(3)
            if latest_modify_time == os.path.getmtime(timing_results_path):
                if status == False:
                    break
                proc.sendintr()
                time.sleep(0.1) # bad approach
                proc.send("$finish;")
                simulation_halted = True
                print(f"HALTED HERE IN THREAD {thread_id}")
                time.sleep(0.1)
                proc.close()
                while proc.signalstatus == None and proc.exitstatus == None:
                    print("Stalling here")
                    exit()
                print(proc.exitstatus, proc.signalstatus)
            else:
                latest_modify_time = os.path.getmtime(timing_results_path)
        else:
            time.sleep(0.1)
            text = read_text(timing_results_path)
            lines = text.split("\n")
            for i in range(len(lines)-1, 0, -1):
                if r"\\EVENT" in lines[i]:
                    output_started = True
                    latest_modify_time = os.path.getmtime(timing_results_path)
                    break

    #disable_port_monitoring()
    sim_results: SimResults = extract_timing_results()
    case_results_lines = read_text(tb_summary_path).split("\n")
    case_results: list = []
    if not simulation_halted:
        for i, line in enumerate(case_results_lines):
            print(line)
            if line == "": continue
            case_results += [(bool(line[0] == "1"), int(line[1:]))]

    sim_results.completed = not simulation_halted
    sim_results.case_results = case_results

    return sim_results


    


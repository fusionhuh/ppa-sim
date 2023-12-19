from .command import run_command
from file_structure import *
from hlsynthesizer._file import *

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



def simulate_hls_tb(tb_file: str, design_file: str, submodules: list, design_name: str, clock_time: float):
    timing_results_path = HLS_WORKING_DIR + "/time_results.txt"
    num_cycles = 0
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
        results_dict["dff"] = dict()
        results_dict["adder"] = dict()
        found_start = False
        for i, line in enumerate(lines):
            if r"\\EVENT" not in line: continue
            line = line.replace("  ", " ")

            event_time, mod_name, event_type = line.split(" ")
            event_type = event_type.replace(r"\\EVENT:", "")
            event_time = float(event_time)
            clock_cycle = int(event_time/clock_time)
            num_cycles = max(clock_cycle+1, num_cycles)
            mod_name = mod_name.replace(f"{design_name}_tb_top.DUT.{design_name}.", "")

            mod_type = "adder" if "ADDER" in event_type else "dff"
            if mod_name not in results_dict[mod_type].keys():
                results_dict[mod_type][mod_name] = dict()

            if clock_cycle not in results_dict[mod_type][mod_name].keys():
                results_dict[mod_type][mod_name][clock_cycle] = [0, 0]
            
            prev_pair = results_dict[mod_type][mod_name][clock_cycle]
            adjusted_time = event_time - (clock_time * clock_cycle)

            if "INPUT_CHANGE" in event_type:
                results_dict[mod_type][mod_name][clock_cycle][0] = max(adjusted_time, prev_pair[0])
            elif "OUTPUT_CHANGE" in event_type: 
                results_dict[mod_type][mod_name][clock_cycle][1] = max(adjusted_time, prev_pair[1])
            else:
                raise Exception("Invalid event type detected")
        results_dict["NUM_CYCLES"] = num_cycles
        return results_dict

    mod_list_str = ""
    for mod in submodules:
        mod_list_str += f"{mod} "
    command_str = f"cvc64 +interp +notimingchecks {tb_file} {design_file} {mod_list_str} substitution/hardware/NangateOpenCellLibrary_typical_conditional.v"
    enable_port_monitoring()
    run_command(command_str, timing_results_path, fail_func=disable_port_monitoring)
    disable_port_monitoring()
    results = extract_timing_results()
    assert len(results) > 0
    return results



    


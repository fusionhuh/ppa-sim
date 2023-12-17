from ._file import *
from file_structure import *
from ._verilog import *
from adder._verilog import *
import random
from adder import Adder
from multiprocessing.pool import ThreadPool
import json

CLOCK_TIME = 10
NUM_THREADS = 12

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
        self.source_text = None
        self.num_adders = 0
        self.addition_lines = []
        self.addition_info = []
        self.out_path = None
        self.substitution_path = None
        self.substituted_adder_paths: set = set()
        self.substituted_adder_sdf_files: set = set()
        self.generic_design_path = None # synthesized with no adder substitutions
        self.cache_path = None
        self.design_name: str
        self.dependencies: str = ""
        self.no_substitution: bool = False
        self.blackbox_list: set = set()
        self.connected_dffs_path = None

    def read_file(self, path: str, top_fname: str, xml_tb=None, override_cache = False):
        xml_tb_filepath = HLS_WORKING_DIR + "/tb.xml"

        def fix_bambu_files():
            #os.system("rm array_ref_*.mem") need to devise a way for getting rid of these files without messing up synthesis
            os.system("rm a.out")
            os.system(f"rm simulate_{self.design_name}.sh")
            os.system("rm bambu_results_*.xml")
            os.system(f"rm ./synthesize_Synthesis_{filename}.sh")
            os.system(f"mv {out_filename} {self.bambu_out_path}")
            os.system(f"mv HLS_output/simulation/testbench_{self.design_name}.v {HLS_TB_FORMAT_PATH.format(design=self.design_name)}")
            os.system(f"mv HLS_output/simulation/values.txt {self.cache_path}/values.txt")
            os.system("rm -rf HLS_output/")
            os.system("rm results.txt")
            os.system("touch array.mem")

        def fix_bambu_tb():
            tb_path = HLS_TB_FORMAT_PATH.format(design=self.design_name)
            text = read_text(tb_path)
            new_text = f'''
  initial
  begin
    $sdf_annotate("{HLS_WORKING_SDF_PATH}", {self.design_name});
'''



            text = text.replace("  initial\n  begin\n", new_text, 1)
            text = text.replace(f"{os.getcwd()}/HLS_output//simulation/values.txt", self.cache_path+"/values.txt")
            write_text(tb_path, text)

        def generate_tb_xml(path: str): # currently only set up for dfadd, needs to be adjusted to support arbitrary modules
            base_text = '''
<?xml version="1.0"?>
<function>
{cases}
</function>
'''
            cases_text: str = ""
            for i in range(0, 5):
                cases_text += f'  <testbench x1="{random.randint(0, 1000000000)}" x2="{random.randint(0,1000000000)}"/>\n'

            final_text = base_text.format(cases=cases_text)
            write_text(path, final_text)

        assert file_exists(path)

        self.design_name = top_fname
        self.cache_path = HLS_CURR_CACHE_FORMAT_DIR.format(design=self.design_name)

        if not os.path.exists(self.cache_path):
            os.system(f"mkdir {self.cache_path}")

        filename = top_fname
        out_filename = filename + ".v"
        self.bambu_out_path = f"{HLS_OUTPUT_DIR}/{out_filename}"
        

        if xml_tb == None:
            generate_tb_xml(xml_tb_filepath)
        elif xml_tb == "bambu-default":
            xml_tb_filepath = "test.xml" # bambu default path
        else:
            xml_tb_filepath = xml_tb

        if not file_exists(self.bambu_out_path) or override_cache == True:
            if os.system(f"bambu {path} --generate-tb=\"{xml_tb_filepath}\" --top-fname={top_fname} --simulate --simulator=ICARUS") != 0:
                raise Exception("Bambu couldn't compile provided file")
            fix_bambu_files()
            fix_bambu_tb()
            bambu_out_text = read_text(self.bambu_out_path)
            bambu_out_text = update_plus_modules(bambu_out_text)
            bambu_out_text = convert_minus_modules(bambu_out_text)
            bambu_out_text = update_signed_instances(bambu_out_text)
            write_text(self.bambu_out_path, bambu_out_text)

        self.yosys_out_path = f"{HLS_OUTPUT_DIR}/{top_fname}_yosys.v"
        self.substitution_path = f"{HLS_OUTPUT_DIR}/{top_fname}_substituted.v"
        self.connected_dffs_path = self.cache_path + "/connected_dffs.json"

    def get_worst_case_delay(self):
        submodule_text: str = ""
        script_text: str = ""
        if self.no_substitution == True:
            script_text = read_text(HLS_STA_SCRIPT_PATH).format(
                verilog_file=self.generic_design_path,
                design_name=self.design_name,
                submodule_text="",
                sdf_file_out=HLS_WORKING_SDF_PATH)
        else:
            for path in self.adder_dependencies:
                submodule_text += f"read_verilog {path}\n"
            script_text = read_text(HLS_STA_SCRIPT_PATH).format(
                verilog_file = self.substitution_path,
                design_name = self.design_name,
                submodule_text = submodule_text,
                sdf_file_out = HLS_WORKING_SDF_PATH)
        os.system("touch temp.tcl")
        write_text("temp.tcl", script_text)
        os.system("sta temp.tcl")

        if not file_exists(f"{HLS_WORKING_DIR}/sta.tcl"):
            os.system(f"touch {HLS_WORKING_DIR}/sta.tcl")

        os.system(f"mv temp.tcl {HLS_WORKING_DIR}/sta.tcl")

    def print_adder_info(self):
        print(f"There are {self.num_adders} adders in this design.")
        for i, adder_info in enumerate(self.addition_info):
            print(f"Adder num {i}:")
            print(f"  name: {adder_info['name']}")
            print(f"  width: {adder_info['new_width']}")
 
    def simulate(self):
        num_cycles = 0
        timing_results_path = HLS_WORKING_DIR + "/time_results.txt"
        monitoring_code_str = r'''
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
        def enable_port_monitoring():
            for dep in self.adder_dependencies:
                text = read_text(dep)
                text = text.replace("endmodule", monitoring_code_str)
                write_text(dep, text)

        def disable_port_monitoring():
            for dep in self.adder_dependencies:
                text = read_text(dep)
                text = text.replace(monitoring_code_str, "endmodule")
                write_text(dep, text)

        def retrieve_connected_dffs(adder_name: str)->tuple: # returns (connected_dffs: dict (sum_bit -> dff_instance), num_connections: int) 
            text = read_text(HLS_CONNECTED_DFFS_SCRIPT_PATH)
            adder_text = ""
            for adder_path in self.adder_dependencies:
                adder_text += f"read_verilog {adder_path};\n"
            script_text = text.replace(r"\\ADDER_INST_NAME", adder_name).replace(r"\\ADDER_READS", adder_text).replace(r"\\DESIGN_FILE", self.substitution_path).replace(r"\\DESIGN_NAME", self.design_name)
            script_path = HLS_WORKING_DIR+"/connected_dffs.tcl"
            script_output_path = HLS_WORKING_DIR+"/connected_dffs_out.txt"
            write_text(script_path, script_text)
            if os.system(f"sta {script_path} > {script_output_path}") != 0:
                raise Exception("Could not run connected DFFs script")
            
            connected_dffs: dict = dict() # maps sum bit to corresponding connected dff
            text = read_text(script_output_path)
            lines = text.split("\n")
            
            num_connected_dffs = 0
            curr_sum_bit = None
            normalized_instance_name = adder_name.replace("\\", "")
            for i, line in enumerate(lines):
                split_line = line.split(":")
                if len(split_line) != 2: continue
                tag, value = split_line
                if tag not in ["NUM_CONNECTIONS", "PORT", "NET", "DEST_PIN"]: continue
                if tag == "NUM_CONNECTIONS": num_connections = int(value)
                elif tag == "PORT":
                    split_value = value.rsplit("/", 1)
                    if len(split_value) != 2: continue
                    reference, name = split_value
                    # not sure if we actually need to do anything here? I think we can
                    # sufficiently verify the net if we just look at the net name
                elif tag == "NET":
                    split_value = value.rsplit("/", 1)
                    if len(split_value) != 2: continue
                    reference, name = split_value
                    if reference == normalized_instance_name and name[0:2] == "s[":
                        #test_name = name.replace("s[", "")[0:-1]
                        if curr_sum_bit != None:
                            raise Exception("Found duplicate sum bit for one DFF connection")
                        curr_sum_bit = int(name.replace("s[", "")[0:-1])
                elif tag == "DEST_PIN":
                    dff_instance = value.rsplit("/", 1)[0]
                    if curr_sum_bit == None:
                        raise Exception("No sum bit found for current DFF connection")
                    if curr_sum_bit not in connected_dffs.keys(): 
                        connected_dffs[curr_sum_bit] = []
                    connected_dffs[curr_sum_bit] += [dff_instance]
                    num_connected_dffs += 1
                    curr_sum_bit = None   
            print(connected_dffs)
            return (connected_dffs, num_connected_dffs)                 

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
                clock_cycle = int(event_time/CLOCK_TIME)
                num_cycles = max(clock_cycle+1, num_cycles)
                mod_name = mod_name.replace(f"{self.design_name}_tb_top.DUT.{self.design_name}.", "")

                mod_type = "adder" if "ADDER" in event_type else "dff"
                if mod_name not in results_dict[mod_type].keys():
                    results_dict[mod_type][mod_name] = dict()

                if clock_cycle not in results_dict[mod_type][mod_name].keys():
                    results_dict[mod_type][mod_name][clock_cycle] = [0, 0]
                
                prev_pair = results_dict[mod_type][mod_name][clock_cycle]
                adjusted_time = event_time - (CLOCK_TIME * clock_cycle)

                if "INPUT_CHANGE" in event_type:
                    results_dict[mod_type][mod_name][clock_cycle][0] = max(adjusted_time, prev_pair[0])
                elif "OUTPUT_CHANGE" in event_type: 
                    results_dict[mod_type][mod_name][clock_cycle][1] = max(adjusted_time, prev_pair[1])
                else:
                    raise Exception("Invalid event type detected")
            return results_dict

        dependencies_str: str = ""
        for dep in self.adder_dependencies: dependencies_str += f"{dep} "

        enable_port_monitoring()

        tb_path = HLS_TB_FORMAT_PATH.format(design=self.design_name)

        sim_command = f"cvc64 +notimingchecks +interp {tb_path} {self.substitution_path} {dependencies_str} {HLS_HARDWARE_VERILOG_PATH} > {timing_results_path}"
        print(sim_command)
        if os.system(sim_command) != 0:
            disable_port_monitoring()
            raise Exception("Testbench could not compile for simulation.")
        disable_port_monitoring()

        results = extract_timing_results()
        adder_results = results["adder"]
        dff_results = results["dff"]

# data analysis portion, may want to split into new function


        ordered_name_list = [self.addition_info[i]["name"] for i in range(0, len(self.addition_info))]

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
            connected_dffs, num_connections = retrieve_connected_dffs(instance_name)

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
        def retrieve_connected_dffs(adder_name: list, thread_id = 0)->tuple: # returns (connected_dffs: dict (sum_bit -> dff_instance), num_connections: int) 
            adder_text = ""
            for adder_path in self.adder_dependencies:
                adder_text += f"read_verilog {adder_path};\n"

            text = read_text(HLS_CONNECTED_DFFS_SCRIPT_PATH)
            script_text = text.replace(r"\\ADDER_INST_NAME", adder_name).replace(r"\\ADDER_READS", adder_text).replace(r"\\DESIGN_FILE", self.substitution_path).replace(r"\\DESIGN_NAME", self.design_name)
            script_path = HLS_WORKING_DIR+f"/connected_dffs{thread_id}.tcl"
            script_output_path = HLS_WORKING_DIR+f"/connected_dffs_out{thread_id}.txt"
            write_text(script_path, script_text)
            if os.system(f"sta {script_path} > {script_output_path}") != 0:
                raise Exception("Could not run connected DFFs script")
            
            connected_dffs: dict = dict() # maps sum bit to corresponding connected dff
            text = read_text(script_output_path)
            lines = text.split("\n")
            
            num_connected_dffs = 0
            curr_sum_bit = None
            normalized_instance_name = adder_name.replace("\\", "")
            for i, line in enumerate(lines):
                split_line = line.split(":")
                if len(split_line) != 2: continue
                tag, value = split_line
                if tag not in ["NUM_CONNECTIONS", "PORT", "NET", "DEST_PIN"]: continue
                if tag == "NUM_CONNECTIONS": num_connections = int(value)
                elif tag == "PORT":
                    split_value = value.rsplit("/", 1)
                    if len(split_value) != 2: continue
                    reference, name = split_value
                    # not sure if we actually need to do anything here? I think we can
                    # sufficiently verify the net if we just look at the net name
                elif tag == "NET":
                    split_value = value.rsplit("/", 1)
                    if len(split_value) != 2: continue
                    reference, name = split_value
                    if reference == normalized_instance_name and name[0:2] == "s[":
                        #test_name = name.replace("s[", "")[0:-1]
                        if curr_sum_bit != None:
                            raise Exception("Found duplicate sum bit for one DFF connection")
                        curr_sum_bit = int(name.replace("s[", "")[0:-1])
                elif tag == "DEST_PIN":
                    dff_instance = value.rsplit("/", 1)[0]
                    if curr_sum_bit == None:
                        raise Exception("No sum bit found for current DFF connection")
                    if curr_sum_bit not in connected_dffs.keys(): 
                        connected_dffs[curr_sum_bit] = []
                    connected_dffs[curr_sum_bit] += [dff_instance]
                    num_connected_dffs += 1
                    curr_sum_bit = None   
            connected_dffs["NUM_CONNECTIONS"] = num_connected_dffs
            return connected_dffs

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
            script_text = read_text(HLS_SYN_SCRIPT_PATH).format(in_path=self.bambu_out_path,
                                                                       design_name=self.design_name,
                                                                       out_path=self.substitution_template_path)
            if not file_exists(f"{HLS_WORKING_DIR}/syn.tcl"):
                os.system(f"mkdir {HLS_WORKING_DIR}")
                os.system(f"touch {HLS_WORKING_DIR}/syn.tcl")   
            write_text(f"{HLS_WORKING_DIR}/syn.tcl", script_text)
            if os.system(f"yosys -c {HLS_WORKING_DIR}/syn.tcl") != 0:
                raise Exception("Yosys could not successfully synthesize the file")

            # start second process to synthesize un-blackboxed version
            
            self.generic_design_path = cache_dir + f"/{self.design_name}_generic.v"
            script_text = read_text(HLS_SECOND_SYN_SCRIPT_PATH).format(in_path=self.bambu_out_path,
                                                                        design_name=self.design_name,
                                                                        out_path=self.generic_design_path)
            if not file_exists(f"{HLS_WORKING_DIR}/syn_second.tcl"):
                os.system(f"mkdir {HLS_WORKING_DIR}")
                os.system(f"touch {HLS_WORKING_DIR}/syn_second.tcl")   
            write_text(f"{HLS_WORKING_DIR}/syn_second.tcl", script_text) 
            #if os.system(f"yosys -c {HLS_WORKING_DIR}/syn_second.tcl") != 0:
            #    raise Exception("Yosys could not successfully synthesize the file")

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





from ._file import *
from file_structure import *
from ._verilog import *

class HLSynthesizer(object):
    def __init__(self):
        self.source_text = None
        self.num_adders = 0
        self.addition_lines = []
        self.addition_information = []
        self.out_path = None
        self.design_name: str




    def synthesize_file(self, path: str, top_fname: str, override_cache = False):
        assert file_exists(path)
        
        self.design_name = top_fname
        
        filename = top_fname
        out_filename = filename + ".v"
        self.bambu_out_path = f"{HLS_OUTPUT_DIR}/{out_filename}"
        
        if not file_exists(self.bambu_out_path) or override_cache == True:
            os.system(f"bambu {path} --top-fname={top_fname}")
            os.system(f"rm -rf ./HLS_output")
            os.system(f"rm ./synthesize_Synthesis_{filename}.sh")
            os.system(f"mv {out_filename} {self.bambu_out_path}")

        bambu_out_text = read_text(self.bambu_out_path)

        adder_type_format_str = "{type}"
        adder_name_format_str = "{name}{num}"

        bambu_out_text = inject_function(bambu_out_text)
        bambu_out_text = update_plus_modules(bambu_out_text)

        write_text(self.bambu_out_path, bambu_out_text)
        self.yosys_out_path = f"{HLS_OUTPUT_DIR}/{top_fname}_yosys.v"

        if not file_exists(self.yosys_out_path) or override_cache == True:
            os.system(f"rm {self.yosys_out_path}")
            os.system(f"touch {self.yosys_out_path}")

            script_text = read_text(HLS_SYN_SCRIPT_PATH).format(
                in_path=self.bambu_out_path, 
                out_path=self.yosys_out_path,
                design_name=self.design_name)
            os.system("touch temp.tcl")
            write_text("temp.tcl", script_text)

            os.system(f"yosys -c temp.tcl")
            os.system("rm temp.tcl")

        yosys_out_text = read_text(self.yosys_out_path)

        #info = get_addition_info(yosys_out_text)
        #self.num_adders = len(info)
        
    def get_worst_case_delay(self):
        script_text = read_text(HLS_STA_SCRIPT_PATH).format(
            verilog_file = self.yosys_out_path,
            design_name = self.design_name,
            sdf_file = "temp.sdf")
        os.system("touch temp.tcl")
        write_text("temp.tcl", script_text)
        os.system("sta temp.tcl")
        os.system("rm temp.tcl")

        # PLEASE DONT REUSE CODE LIKE THIS AHHHHHH
        def fix_sdf_file():
            sdf_file_text = read_text("temp.sdf")
            def replace(match):
                match = re.findall("\((\\S+)::(\\S+)\)", match.group())
                num1 = float(match[0][0])
                num2 = float(match[0][1])
                return f"({num1}:{(num1+num1)/2}:{num2})"
            sdf_file_text = re.sub("\((\\S+?)\:\:(\\S+?)\)", replace, sdf_file_text)
            write_text("temp.sdf", sdf_file_text)

        fix_sdf_file()




    def get_num_adders(self):
        return self.num_adders

    def substitute_adders(self, adder_list: list, area_list: list):
        if len(adder_list) * len(area_list) != self.num_adders:
            raise Exception(f"HLSynthesizer.init.substitute_adders (error): Number of provided adders does ({len(adder_list)*len(area_list)}) not match number of required adders ({self.num_adders} required).")
        

        text = read_text(self.out_path)
        pair_list = []
        for i, adder in enumerate(adder_list):
            for j, area in enumerate(area_list):
                pair_list += [(adder, area)]

        pair_index = 0
        lines = text.split("\n")
        for i in self.addition_lines:
            adder, area = pair_list[pair_index]
            lines[i] = lines[i].format(type=adder.get_module_name_with_area(area), name="adder", num=pair_index)
            pair_index += 1

        text = "\n".join(lines)
        write_text(self.out_path, text)




import json
from ._file import *
from ._verilog import *
from file_structure import *
from .GateSize import cktopt

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
    
    def get_optimization_results(area) -> dict:
        data_file_path = Path(self._opt_data_file_path)
        if data_file_path.is_file(): # file exists, could be cached
            json_data: dict
            with open(self._opt_data_file_path, "r") as fp:
                json_data = json.load(fp)                    
            if str(area) in json_data.keys():
                return json_data[str(area)]
            else:
                results = cktopt.optimize(self._syn_file_path, [area])
                json_data[f"{area}"] = results
                with open(self._opt_data_file_path, "w") as fp:
                    json.dump(json_data, fp)     
                return results
        else: # file doesn't exist, results definitely are not cached
            data_file_path.parent.mkdir(parents=True, exist_ok=True)
            new_json_data: dict = {}
            results = cktopt.optimize(self._syn_file_path, [area])
            new_json_data[f"{area}"] = results
            with open(self._opt_data_file_path, "w") as fp:
                json.dump(new_json_data, fp)
            return results

    def map_opt_size(sizes: list, size: float) -> str:
        size = round(size)
        nearest_power: int = 2**int(math.log(size, 2))
        end = len(sizes)-1
        while end >= 0:
            if nearest_power >= sizes[end]:
                return str(sizes[end])
            end-=1
        return "1"

    def size_synthesized_file(results: dict, area: int) -> str:
        lib_dict = parse_lib_file()
        syn_text = read_text(self._syn_file_path)
        syn_text = syn_text.replace(f"module {self.adder_name}", f"module {self.adder_name}"+f"_{area}")
        lines = syn_text.split("\n")
        gate_start, gate_end = find_gate_boundaries(syn_text)
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
            print("optimize.strip_sdf_file(): Tried stripping sdf file when it doesn't exist (error)")
            exit()
        sdf_text = read_text(sdf_file_path)
        design = f'{self.adder_name}_{area}'
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

    def get_verilog_path(area: int):
        return self._opt_verilog_folder_path + f"/{self.get_filename_with_area(area)}"

    def fix_sdf_file(area: int):
        sdf_file_path = self._opt_sdf_folder_path + f"/{self.get_filename_with_area(area, extension='.sdf')}"
        sdf_file_text = read_text(sdf_file_path)
        def replace(match):
            match = re.findall("\((\\S+)::(\\S+)\)", match.group())
            num1 = float(match[0][0])
            num2 = float(match[0][1])
            return f"({num1}:{(num1+num1)/2}:{num2})"
        sdf_file_text = re.sub("\((\\S+?)\:\:(\\S+?)\)", replace, sdf_file_text)
        write_text(sdf_file_path, sdf_file_text)

    areas_list = self._get_unoptimized_areas(areas_list)

    for i in range(0, len(areas_list)):
        min_area = int(self.get_min_area()*areas_list[i]+1)
        result = get_optimization_results(areas_list[i])
        sizes_only: dict = result[0]
        sizes_only.pop("delay")
        sizes_only.pop("maxArea")
        sized_file_text: str = size_synthesized_file(sizes_only, min_area)
        sized_file_path = get_verilog_path(min_area)
        write_text(sized_file_path, sized_file_text)
        create_script(sized_file_path, min_area)
        if os.system(f"sta {OPT_SCRIPT_PATH}") != 0:
            print("optimize.optimize(): Could not generate sdf file (error)")
            exit()
        fix_sdf_file(min_area)
        original_sdf_text = read_text(self._get_sdf_path(min_area))
        strip_sdf_file(min_area)
        self._construct_sdf_file(min_area)
        new_sdf_text = read_text(self._get_sdf_path(min_area))
        os.remove(self._get_sdf_path(min_area))

        report_text = read_text(OPT_REPORT_PATH)
        delay = float(re.findall("(\\S+?)\\s+data arrival time", report_text)[0])
        opt_data: dict
        with open(self._opt_data_file_path, "r") as fp:
            opt_data = json.load(fp)
        opt_data[f"{areas_list[i]}"][0]["worst"] = delay
        with open(self._opt_data_file_path, "w") as fp:
            json.dump(opt_data, fp)
    if (os.system("make clean_script") != 0):
        print("optimize.optimize(): Could not clean script file (Makefile error)")
        exit()
from file_structure import *
from ._file import *
import liberty
import json

class Adder(object):
    def __init__(self, description: str):
        assert description.count(".") == 2
        [adder_type, width, structure] = tuple(description.split("."))

        # fill adder type and size information
        assert width.isdigit()
        self.width: int = int(width)
        type_info = adder_type.split("-")
        self.base_type: str = type_info[0]
        assert self.base_type in SUPPORTED_TYPES
        if len(type_info) == 2:
            assert self.base_type == "hybrid"
            assert type_info[1].isdigit()
            self.hybrid_levels: int = int(type_info[1])

        # fill adder structure information
        structure_info = structure.split("-")
        self.structure: str = structure_info[0]
        assert self.structure in SUPPORTED_STRUCTURES
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
            self.verilog_structured_name = f"{self.verilog_base_name}_{self.width}_{self.structure}"
            #self.verilog_structured_name = "{type}_{width}_{structure}_{block_size}".format(type=self.base_type, width=self.width, structure=self.structure, block_size=self.block_size)
        self.adder_name = self.verilog_base_name if self.structure == "basic" else self.verilog_structured_name

        # generate important file/folder paths for each process (verification/verilog, synthesis, optimization, etc)
        subdir = f"{VERI_BASE_DIR}/{self.base_type}" if self.structure == "basic" else f"{VERI_STRUCTURED_DIR}/{self.structure}"

        # verilog
        self._verilog_folder_path = f"verilog/{subdir}"
        self._verilog_file_path = f"{self._verilog_folder_path}/{self.adder_name}.v"

        # synthesis
        prefix = f"{VERI_DIR}/{VERI_LOGIC_DIR}"
        dependency_list = [f"{prefix}/pos_operator.v", f"{prefix}/neg_operator.v", f"{prefix}/carry_operator.v"]
        if self.structure != "basic":
            if self.structure == "cla":
                dependency_list.extend([f"{prefix}/cla4.v", f"{prefix}/block_signals4.v"])
            base_file_path = f"{VERI_DIR}/{VERI_BASE_DIR}/{self.base_type}/{self.verilog_base_name}.v"
            dependency_list.append(base_file_path)
        self._dependencies = dependency_list

        self._syn_folder_path = f"{SYN_DIR}/{SYN_VERILOG_DIR}/{subdir}"
        self._syn_file_path = f"{self._syn_folder_path}/{self.adder_name}.v"
        self._syn_area_file_path = f"{self._syn_folder_path}/{self.adder_name}_area"
        self._syn_stats_file_path = f"{self._syn_folder_path}/{self.adder_name}_stats.json"

        # optimization
        self._opt_data_folder_path = f"{OPT_DIR}/{OPT_DATA_DIR}/{subdir}"
        self._opt_data_file_path = f"{self._opt_data_folder_path}/{self.adder_name}_sizes.json"
        self._opt_verilog_folder_path = f"{OPT_DIR}/{OPT_VERILOG_DIR}/{subdir}"
        self._opt_verilog_template_path = f"{self._opt_verilog_folder_path}/{self.adder_name}_template"
        self._opt_sdf_folder_path = f"{OPT_DIR}/{OPT_SDF_DIR}/{subdir}"
        self._opt_sdf_template_path = f"{self._opt_sdf_folder_path}/{self.adder_name}_template"
        self._opt_sdf_data_path = f"{self._opt_sdf_folder_path}/{self.adder_name}_data.json"






# ------------------------- PRIVATE -----------------------------

    def _get_sized_file_path(self, area: int) -> str:
        return f"{self._opt_verilog_folder_path}/{self.adder_name}_MAX_AREA_{area}.v"

    def _get_sdf_path(self, area: int):
        area = int(area)
        return self._opt_sdf_folder_path + f"/{self.adder_name}_MAX_AREA_{area}.sdf"

    def _construct_sdf_file(self, area: int):
        area = int(area)
        path = self._get_sdf_path(area)
        sdf_text = read_text(self._opt_sdf_template_path)
        design = f"{self.adder_name}_{area}"
        sdf_text = sdf_text.replace("design", design)
        data: dict
        with open(self._opt_sdf_data_path, "r") as fp:
            data = json.load(fp)[f"{area}"]
        drives = data["drives"]
        delays = data["delays"]
        num_instances = data["num_instances"]
        for i in range(0, num_instances):
            curr_drive_key = f"DRIVE_{i}"
            sdf_text = sdf_text.replace(curr_drive_key, f"X{drives[i]}", 1)
            instance_delays = delays[f"{i}"]
            for j in range(0, len(instance_delays)):
                delay_key = f"INSTANCE_{i}_DELAY_{j}"
                delay = instance_delays[j]
                sdf_text = sdf_text.replace(delay_key, delay)
        write_text(self._get_sdf_path(area), sdf_text)

    def _get_synthesized_cell_count(self) -> int:
        if hasattr(self, "_syn_cell_count"):
            return self._syn_cell_count
        area_file = open(self._syn_stats_file_path)
        data = json.load(area_file)["modules"][f"\\{self.adder_name}"]
        compound_cell_count: int = 0
        if "$_ORNOT_" in data["num_cells_by_type"].keys():
            compound_cell_count += data["design"]["num_cells_by_type"]["$_ORNOT_"]
        if "$_ANDNOT_" in data["num_cells_by_type"].keys():
            compound_cell_count += data["num_cells_by_type"]["$_ANDNOT_"]
        self._syn_cell_count = data["num_cells"] + compound_cell_count
        return self._syn_cell_count

    def _get_unoptimized_areas(self, areas: list) -> list:
        if not file_exists(self._opt_data_file_path):
            return areas
        unoptimized_areas: list = []
        data: dict
        with open(self._opt_data_file_path, "r") as fp:
            data = json.load(fp)
        optimized_areas = data.keys()
        for area in areas:
            if f"{area}" not in optimized_areas:
                unoptimized_areas.append(area)
        return unoptimized_areas

# ---------------------------- PUBLIC -----------------------------------------

    def get_worst_case_delays(self, areas: list) -> list:
        delay_list: list = []
        data: dict
        with open(self._opt_data_file_path, "r") as fp:
            data = json.load(fp)
        for i in range(0, len(areas)):
            real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
            delay_list.append(data[f"{areas[i]}"][0]["worst"])
        return delay_list


    def get_min_area(self) -> float:
        if not self.is_synthesized:
            print("Error: Can only get minimum area on a synthesized design")
            exit()
        if hasattr(self, "min_area"):
            return self.min_area
        lib_info = liberty.get_gate_info()
        design_info: dict
        with open(self._syn_stats_file_path, "r") as fp:
            design_info = json.load(fp)["modules"][f"\\{self.adder_name}"]["num_cells_by_type"]
        total_area = 0
        for gate, count in design_info.items():
            total_area += lib_info[gate]["area"]*count
        self.min_area = total_area
        return self.min_area

    def get_optimizer_delays(self, areas: list) -> list:
        delay_list: list = []
        data: dict
        with open(self._opt_data_file_path, "r") as fp:
            data = json.load(fp)
        for i in range(0, len(areas)):
            real_area = int((self._get_synthesized_cell_count()+1)*areas[i])
            delay_list.append(data[f"{areas[i]}"][0]["delay"])
        return delay_list

    def get_real_cell_counts(self, areas: list) -> list:
        cell_list: list = []
        for area in areas:
            cell_list.append(int(area * (self._get_synthesized_cell_count()+1)))
        return cell_list

    def is_generated(self):
        return file_exists(self._verilog_file_path)

    def is_synthesized(self):
        return file_exists(self._syn_file_path)

    def is_optimized(self, areas):
        return (len(self._get_unoptimized_areas(areas)) == 0)

    def get_design_status(self, areas: list):
        generated: bool = file_exists(self._verilog_file_path)
        synthesized: bool = file_exists(self._syn_file_path)
        optimized: bool = (len(self._get_unoptimized_areas(areas)) == 0)
        return {"optimized" : optimized, "synthesized" : synthesized, "generated" : generated}

    def get_verbose_name(self) -> str:
        name: str
        width = f"{self.width}-bit"
        base_descriptor: str
        if self.base_type == "ks":
            base_descriptor = "Kogge-Stone"
        elif self.base_type == "bk":
            base_descriptor = "Brent-Kung"
        elif self.base_type == "skl":
            base_descriptor = "Sklansky"
        elif self.base_type == "hybrid":
            base_descriptor = "Hybrid"
        elif self.base_type == "serial":
            base_descriptor = "Serial"

        hybrid_levels: str
        if self.base_type != "hybrid":
            hybrid_levels = ""
        else:
            if self.hybrid_levels == 1:
                hybrid_levels = " (1 level)"
            else:
                hybrid_levels = f" ({self.hybrid_levels} levels)"

        if self.structure != "basic":
            structure_descriptor: str = ""
            if self.structure == "rc":
                structure_descriptor = "Ripple-Carry"
            elif self.structure == "cskip":
                structure_descriptor = "Carry-Skip"
            elif self.structure == "cselect":
                structure_descriptor = "Carry-Select"
            elif self.structure == "cla":
                structure_descriptor = "Carry-Lookahead"
            end = f"with {self.block_size}-bit {base_descriptor} blocks"
            return f"{width} {structure_descriptor} {end}{hybrid_levels}"
        else:
            return f"{width} {base_descriptor}{hybrid_levels}"

    from ._generate import generate_verilog
    from ._synthesize import synthesize
    from ._optimize import optimize
    from ._simulate import simulate
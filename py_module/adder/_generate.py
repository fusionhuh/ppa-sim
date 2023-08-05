from ._file import *
from ._graph import *
from ._verilog import *

def generate_verilog(self) -> None:
    gen_function_name = "generate_{type}_graph".format(type=self.base_type)
    if self.base_type == "hybrid":
        self.graph: list = generate_graph(gen_function_name, self.block_size, self.hybrid_levels)
    else:
        self.graph: list = generate_graph(gen_function_name, self.block_size)
    test_graph_completeness(self.block_size, self.graph)
    self.depth = len(self.graph)
    self.node_count = get_node_count(self.graph)

    # create adder info if nonexistent
    if not hasattr(self, "adder_info"):
        self.adder_info = {}
        for var in self.__dict__.keys():
            val = getattr(self, var)
            if var[0] == "_": var = var[1:]
            self.adder_info[var] = val

    # update verilog files (including dependencies) according to project file structure
    base_verilog_path = f"verilog/base/{self.base_type}/{self.verilog_base_name}.v"
    base_verilog_text = generate_basic_adder(self.adder_info)
    write_text(base_verilog_path, base_verilog_text)

    # now generate structured verilog if applicable
    if self.structure == "basic":
        self.verilog_text = base_verilog_text
        return 

    structured_verilog_path = f"verilog/structured/{self.structure}/{self.verilog_structured_name}.v"
    structured_verilog_text = generate_structured_adder(self.adder_info)
    write_text(structured_verilog_path, structured_verilog_text)
    self.verilog_text = structured_verilog_text
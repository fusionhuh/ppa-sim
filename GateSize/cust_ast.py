


class ModuleDef:
    def __init__(self, name, ports, env):
        self.name = name
        self.ports = ports
        self.env = env

class ModuleInst:
    def __init__(self, type, name, ports):
        self.name = name
        self.type = type
        self.ports = ports

class NetDef:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


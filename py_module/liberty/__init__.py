import json

GateLib = {
    "INV" : [("A", "in"), ("ZN", "out")],
    "NAND2" : [("A1", "in"), ("A2", "in"), ("ZN", "out")],
    "NOR2" : [("A1", "in"), ("A2", "in"), ("ZN", "out")],
    "XNOR2" : [("A", "in"), ("B", "in"), ("ZN", "out")],
    "AND2" : [("A1", "in"), ("A2", "in"), ("ZN", "out")],
    "OR2" : [("A1", "in"), ("A2", "in"), ("ZN", "out")],
    "XOR2" : [("A", "in"), ("B", "in"), ("Z", "out")],
    "MUX2" : [("A", "in"), ("B", "in"), ("S", "in"), ("Z", "out")],
    "AOI21" : [("B1", "in"), ("B2", "in"), ("A", "in"), ("ZN", "out")],
    "OAI21" : [("B1", "in"), ("B2", "in"), ("A", "in"), ("ZN", "out")],
    "AOI211" : [("A", "in"), ("B", "in"), ("C1", "in"), ("C2", "in"), ("ZN", "out")],
    "OAI211" : [("A", "in"), ("B", "in"), ("C1", "in"), ("C2", "in"), ("ZN", "out")],
    "NOR3" : [("A1", "in"), ("A2", "in"), ("A3", "in"), ("ZN", "out")],
    "NOR4" : [("A1", "in"), ("A2", "in"), ("A3", "in"), ("ZN", "out"), ("A4", "in")],
    "OR3" : [("A1", "in"), ("A2", "in"), ("A3", "in"), ("ZN", "out")],
    "AND3" : [("A1", "in"), ("A2", "in"), ("A3", "in"), ("ZN", "out")],
    "NAND3" : [("A1", "in"), ("A2", "in"), ("A3", "in"), ("ZN", "out")],
    "OAI22" : [("A1", "in"), ("A2", "in"), ("B1", "in"), ("B2", "in"), ("ZN", "out")],
    "AOI22" : [("A1", "in"), ("A2", "in"), ("B1", "in"), ("B2", "in"), ("ZN", "out")],
    "AOI221" : [("B1", "in"), ("B2", "in"), ("C1", "in"), ("C2", "in"), ("A", "out"), ("ZN", "out")],
    "OAI221" : [("B1", "in"), ("B2", "in"), ("C1", "in"), ("C2", "in"), ("A", "out"), ("ZN", "out")],
}

GateInfo = {
    "INV" : {"cap" : 0.01, "area" : 0.532, "port_caps" : {"A" : 1.7002}, "min" : 1.0, "max" : 16.0, "resistance" : 0.39},
    "NAND2" : {"cap" : 1.664, "area" : 0.798, "port_caps" : {"A1" : 1.599, "A2" : 1.6642}, "min" : 1.0, "max" : 4.0, "resistance" : 0.459},
    "AND2" : {"cap" : 0.9746, "area" : 1.064, "port_caps" : {"A1" : 0.9181, "A2" : 0.9746}, "min" : 1.0, "max" : 4.0, "resistance" : 0.333},
    "NOR2" : {"cap" : 1.7145, "area" : 0.798, "port_caps" : {"A1" : 1.7145, "A2" : 1.6513}, "min" : 1.0, "max" : 4.0, "resistance" : 0.347},
    "OR2" : {"cap" : 0.9468, "area" : 1.064, "port_caps" : {"A1" : 0.9468, "A2" : 0.9419}, "min" : 1.0, "max" : 4.0, "resistance" : 0.342},
    "XNOR2" : {"cap" : 2.5736, "area" : 2.66, "port_caps" : {"A" : 2.2328, "B" : 2.5736}, "min" : 1.0, "max" : 2.0, "resistance" : 1.415},
    "XOR2" : {"cap" : 2.4115, "area" : 2.394, "port_caps" : {"A" : 2.2321, "B" : 2.4115}, "min" : 1.0, "max" : 2.0, "resistance" : 0.352},
    "MUX2" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A" : 0.9464, "B" : 0.9448, "S" : 1.9199}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AOI21" : {"cap" : 1.9199, "area" : 1.064, "port_caps" : {"B1" : 1.647, "B2" : 1.677, "A" : 1.6264, "ZN" : 1.9199}, "min" : 1.0, "max" : 4.0, "resistance" : 0.348},
    "OAI21" : {"cap" : 1.9199, "area" : 1.064, "port_caps" : {"B1" : 1.6621, "B2" : 1.5719, "A" : 1.6707, "ZN" : 1.9199}, "min" : 1.0, "max" : 4.0, "resistance" : 0.348},
    "AOI211" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"C1" : 0.9464, "C2" : 0.9448, "A" : 0.9464, "B" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "OAI211" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"C1" : 0.9464, "C2" : 0.9448, "A" : 0.9464, "B" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "NOR3" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "A3" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "OR3" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "A3" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AND3" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "A3" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "NAND3" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "A3" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AOI211" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"C1" : 0.9464, "C2" : 0.9448, "A" : 0.9464, "B" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "OAI22" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "B1" : 0.9464, "B2" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AOI22" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "B1" : 0.9464, "B2" : 1.9199, "ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "OAI221" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"B1" : 0.9464, "B2" : 0.9448, "C1" : 0.9464, "C2" : 1.9199, "ZN" : 1.0, "A" : 0.5}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AOI221" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"B1" : 0.9464, "B2" : 0.9448, "C1" : 0.9464, "C2" : 1.9199, "ZN" : 1.0, "A" : 0.5}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "NOR4" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A1" : 0.9464, "A2" : 0.9448, "A3" : 1.9199, "A4":1.0,"ZN" : 1.0}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
}

def get_gate_lib():
    return GateLib

def get_gate_info():
    return GateInfo
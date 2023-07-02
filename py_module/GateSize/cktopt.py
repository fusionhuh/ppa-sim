#!/usr/bin/python
# Circuit Optimizer

import sys
import veriparse
import cust_ast
import nets
import argparse
import re

# Gate Library
GateLib = {
    "INV" : [("A", "in"), ("Y", "out")],
    "NAND2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "NOR2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "XNOR2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "AND2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "OR2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "XOR2" : [("A", "in"), ("B", "in"), ("Y", "out")],
    "MUX2" : [("A", "in"), ("B", "in"), ("S", "in"), ("Y", "out")]
}

def fill_gate_lib(text: str) -> str:
    module_declare_expr = "(\\S+)\\s+\\S+\\s+\((.*?)\);"
    port_list_expr = "\.(\\w+)\\s*\(\\s*\\w+\\s*\)"
    module_declares = re.findall(module_declare_expr, text)
    module_declares.pop(0)
    for declaration in module_declares:
        if declaration[0] in GateLib.keys():
            continue
        port_list = declaration[1]
        port_names = re.findall(port_list_expr, port_list)
        port_function_list = []
        for port in port_names:
            function: str
            if "A" in port or "B" in port:
                function = "in"
            elif "Z" in port or "CO" in port or "S" in port or "Y" in port:
                function = "out"
            else:
                function = "in"
            port_function_list.append((port, function))
        GateLib[declaration[0]] = port_function_list
    print(GateLib)

def fix_bus_references(text: str) -> str:
    lines = text.split("\n")
    line_num = 0
    while "module" not in lines[line_num]:
        line_num += 1
    file_length = len(lines)
    identifiers = ["wire", "input", "output"]
    bus_index_expr = "(\\w+)\\s*\[(\\d+)\]"
    net_declare_expr = "(\\w+)\\s+\[(\\d+):0\]\\s+(\\S+)\\s*;"
    while line_num < file_length:
        curr_line = lines[line_num]
        print(curr_line)
        if any([x in curr_line for x in identifiers]) and "[" in curr_line:
            declaration = re.findall(net_declare_expr, curr_line)
            assert len(declaration) == 1
            net_type = declaration[0][0]
            width = int(declaration[0][1]) + 1
            name_list = declaration[0][2].split(", ")
            new_line = f" {net_type} "
            for name in name_list:
                for i in range(0, width):
                    new_wire = f"{name}_{i}, "
                    new_line += new_wire
            for i in range(0, 2): new_line = new_line.rstrip(new_line[-1])
            new_line += ";\n"
            lines[line_num] = new_line
        elif "[" in curr_line:
            def replace(matchobj):
                name = matchobj.group(1)
                index = matchobj.group(2)
                return f"{name}_{index}"
            lines[line_num] = re.sub(bus_index_expr, replace, lines[line_num])
        line_num += 1
    return "\n".join(lines)

# Read Verilog file and return selected module
def readVerilog(fname, target):
    verilog_src = open(fname)
    text = verilog_src.read()
    text = fix_bus_references(text)
    #fill_gate_lib(text)
    mods = veriparse.parser.parse(text)
    if target:
        match = [m for m in mods if m.name == args.target]
        result = match[0]
    else:
        result = mods[-1]
    return result

def optimizeMod(target, maxAreaList):
    # All this ast stuff should be factored

    # Better to do this iteratively and check for duplicates???
    netList = [n for n in target.env if isinstance(n, cust_ast.NetDef)]
    netMap = {n.name : nets.Net(n.name, n.type) for n in netList}

    gateList = [g for g in target.env if isinstance(g, cust_ast.ModuleInst)]
    gateMap = {}
    for modInst in gateList:
        if modInst.name in gateList:
            print('Duplicate name', modInst.name)
            raise

        libObj = GateLib[modInst.type]
        ins = {}
        outs = {}


        def addPort(pname, type, net):
            if type == 'in':
                ins[pname] = net
            elif type == 'out':
                outs[pname] = net
            else:
                print('Badness...un resolved port type')
                raise

        if isinstance(modInst.ports[0], tuple):
            # uses named ports
            pMap = {k:v for k,v in libObj}
            for p,n in modInst.ports:
                addPort(p, pMap[p], netMap[n])
        else:
            # uses ordered ports
            for netName,desc in zip(modInst.ports, libObj):
                addPort(desc[0], desc[1], netMap[netName])

        gate = nets.Gate(modInst.name, modInst.type, ins, outs)
        gateMap[modInst.name] = gate
        #print(gate.name, gate.ins, gate.outs)

    # Think seriously about test cases

    primeIns,primeOuts = nets.findPrimeInsOuts(netMap.values())

    # Do we want to have some semantic check that makes sure that declared ins/outs match with ones found by analysis?
    # Maybe give a warning at minimum

    # Should redo this so that matrix does not need to be completely rebuilt each time
    result = []
    for maxArea in maxAreaList:
        F,G,K, gateToVar = nets.buildMatrix(gateMap.values(), netMap.values(), primeIns, primeOuts, maxArea)
        solution = nets.optimizeMatrix(F, G, K)
        # result.append(solution)

        # redo this so that each iteration produces a hash with area (effective and max) and all gate sizes
        # construct list of these

        resultHash = {'delay' : solution[0], 'maxArea' : maxArea}
        varHash = {g.name : solution[gateToVar[g]] for g in gateToVar.keys()}
        resultHash.update(varHash)
        result.append(resultHash)

    return result

def calculate_delay(a):
    # load cell count from timing file
    # generate a list of some amount of numbers that are (cell_count+1)*n
    # provide that list as area_list argument to optimize
    # read through delay results
    pass

def optimize(file_path: str, area_list: int) -> int:
    result = optimizeHelper(fname=file_path, target=None, areaList=area_list)
    print(result)
    return result

def optimizeHelper(fname: str, target, areaList: list):
    targetMod = readVerilog(fname, target)
    maxAreaList = map(float, areaList)
    result = optimizeMod(targetMod, maxAreaList)
    return result


#if __name__ == "__main__":
#    argParser = argparse.ArgumentParser()
#    argParser.add_argument('-t', '--target', action='store', default=None)
#    argParser.add_argument('fname')

    # Allow a list of areas...sort them and then loop through
#    argParser.add_argument('areaList', nargs='+')
#    args = argParser.parse_args(sys.argv[1:])

#    print("THIS IS TARGET")
#    print(args.target)

    # Check arguments
#    targetMod = readVerilog(args.fname, args.target)
#    maxAreaList = map(float,args.areaList)
    

#    result = optimizeMod(targetMod, maxAreaList)

    # What should output be? Delay and sizes? Only useful if we get a columnar output
    # Use json!!!

#    print(result)


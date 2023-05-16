#!/usr/bin/python
# Circuit Optimizer

import sys
import veriparse
import cust_ast
import nets
import argparse

# Gate Library
GateLib = {
    'INV' : [('A', 'in'), ('Z', 'out')],
    'NAND' : [('A', 'in'), ('B', 'in'), ('Z', 'out')],
    'NOR' : [('A', 'in'), ('B', 'in'), ('Z', 'out')]
}

def get_bus_width(line: str) -> int:
    bracket1 = line.index("[")
    bracket2 = line.index("]")
    temp = line[bracket1 + 1 : bracket2]
    width = int(temp.split(":")[0]) + 1
    return width

def fix_bus_references(text: str) -> str:
    lines = text.split("\n")
    line_num = 0
    while "module" not in lines[line_num]:
        line_num += 1
    file_length = len(lines)
    identifiers = ["wire", "input", "output"]
    while line_num < file_length:
        curr_line = lines[line_num]
        if any([x in curr_line for x in identifiers]) and "[" in curr_line:
            net_type: str
            for x in identifiers: 
                if x in curr_line: net_type = x
            width = get_bus_width(curr_line)
            net_list = curr_line.split(" ")
            net_list = net_list[4 : len(net_list)]
            net_list = [item[0:len(item)-1] for item in net_list]
            new_line = f"  {net_type} "
            for wire in net_list:
                for i in range(0, width):
                    new_wire = f"{wire}_{i}, "
                    new_line += new_wire
            for i in range(0, 2): new_line = new_line.rstrip(new_line[-1])
            new_line += ";\n"
            lines[line_num] = new_line
        elif "[" in curr_line:
            
            port_list = curr_line.split(".")
            if port_list[0].find(")") == -1:
                port_list.pop(0)
            problematic_port_list: list = []
            print(port_list)
            for i in range(0, len(port_list)):
                print(port_list[i])
                curr_port = port_list[i]
                paren1 = curr_port.find("(")
                paren2 = curr_port.find(")")
                port_list[i] = curr_port[paren1 + 1: paren2]
                if "[" in port_list[i]:
                    problematic_port_list.append(port_list[i])
            if port_list[-1] == "": port_list.pop()
            for port in problematic_port_list:
                bracket1 = port.find("[")
                bracket2 = port.find("]")
                port_name = port[0: bracket1]
                bus_index: int = int(port[bracket1 + 1: bracket2])
                new_name = f"{port_name}_{bus_index}"
                curr_line = curr_line.replace(port, new_name)
            lines[line_num] = curr_line
        line_num += 1
    return "\n".join(lines)

# Read Verilog file and return selected module
def readVerilog(fname, target):
    verilog_src = open(fname)
    text = verilog_src.read()
    text = fix_bus_references(text)
    print(text)
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
        print(gate.name, gate.ins, gate.outs)

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


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-t', '--target', action='store', default=None)
    argParser.add_argument('fname')

    # Allow a list of areas...sort them and then loop through
    argParser.add_argument('areaList', nargs='+')
    args = argParser.parse_args(sys.argv[1:])

    # Check arguments
    targetMod = readVerilog(args.fname, args.target)
    maxAreaList = map(float,args.areaList)
    

    result = optimizeMod(targetMod, maxAreaList)

    # What should output be? Delay and sizes? Only useful if we get a columnar output
    # Use json!!!

    print(result)


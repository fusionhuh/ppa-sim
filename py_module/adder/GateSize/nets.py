
import random
import numpy as np
from cvxopt import matrix, log, exp, solvers



GateInfo = {
    "INV" : {"cap" : 0.01, "area" : 0.532, "port_caps" : {"A" : 1.7002}, "min" : 1.0, "max" : 16.0, "resistance" : 0.39},
    "NAND2" : {"cap" : 1.664, "area" : 0.798, "port_caps" : {"A1" : 1.599, "A2" : 1.6642}, "min" : 1.0, "max" : 4.0, "resistance" : 0.459},
    "AND2" : {"cap" : 0.9746, "area" : 1.064, "port_caps" : {"A1" : 0.9181, "A2" : 0.9746}, "min" : 1.0, "max" : 4.0, "resistance" : 0.333},
    "NOR2" : {"cap" : 1.7145, "area" : 0.798, "port_caps" : {"A1" : 1.7145, "A2" : 1.6513}, "min" : 1.0, "max" : 4.0, "resistance" : 0.347},
    "OR2" : {"cap" : 0.9468, "area" : 1.064, "port_caps" : {"A1" : 0.9468, "A2" : 0.9419}, "min" : 1.0, "max" : 4.0, "resistance" : 0.342},
    "XNOR2" : {"cap" : 2.5736, "area" : 2.66, "port_caps" : {"A" : 2.2328, "B" : 2.5736}, "min" : 1.0, "max" : 2.0, "resistance" : 1.415},
    "XOR2" : {"cap" : 2.4115, "area" : 2.394, "port_caps" : {"A" : 2.2321, "B" : 2.4115}, "min" : 1.0, "max" : 2.0, "resistance" : 0.352},
    "MUX2" : {"cap" : 1.9199, "area" : 1.862, "port_caps" : {"A" : 0.9464, "B" : 0.9448, "S" : 1.9199}, "min" : 1.0, "max" : 2.0, "resistance" : 0.348},
    "AOI21" : {"cap" : 1.9199, "area" : 1.064, "port_caps" : {"B1" : 1.6621, "B2" : 1.5719, "A" : 1.6707, "ZN" : 1.9199}, "min" : 1.0, "max" : 4.0, "resistance" : 0.348},
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



class PortRef:
    def __init__(self, gate, portname):
        self.gate = gate
        self.portname = portname

class Net:
    def __init__(self, name, type=None):
        self.name = name
        self.ports = []
        self.type = type
    def addPort(self, gate, portname):
        self.ports.append(PortRef(gate, portname))

class Gate:
    def __init__(self, name: str, type: str, ins, outs):
        self.name = name
        self.min = GateInfo[type]["min"]
        self.max = GateInfo[type]["max"]
        self.ins = ins
        self.outs = outs
        self.in_caps = GateInfo[type]["port_caps"]
        self.area = GateInfo[type]["area"]
        self.int_cap = 0.5
        self.resistance =  0.5/self.area
        for portname,net in self.ins.items():
            net.addPort(self, portname)
        for portname,net in self.outs.items():
            net.addPort(self, portname)
    def isDriver(self,name):
        return name in self.outs
    def isLoad(self,name):
        return name in self.ins
    def getInputCap(self, portname):
        return self.in_caps[portname]
    def getIntrCap(self, portname):
        return self.int_cap
    def getResist(self,portname):
        return self.resistance
    def getMin(self):
        return self.min
    def getMax(self):
        return self.max
    def getAreaScaleFactor(self):
       return self.area

RinDefault = 1.0

class PNom:
    def __init__(self, const, *factors):
        self.const = const
        self.vars = list(factors[0::2])
        self.powers = list(factors[1::2])
    def __mul__(self, pnom):
        vars = self.vars + pnom.vars
        powers = self.powers + pnom.powers
        z = zip(vars, powers)
        factors = [elem for tupl in z for elem in tupl]
        return PNom(self.const * pnom.const, *factors)
    def __str__(self):
        return "PNom(%f, %s %s)" % (self.const, str(self.vars), str(self.powers))
    __repr__ = __str__


def addConstraint(Fmat, Gvect, Kdim, posyTerms, constraint):
    nterms = len(posyTerms)
    Kdim = np.append(Kdim, [nterms])
    nvars,nconstr = Fmat.shape
    Fmat = np.append(Fmat, np.zeros((nvars,nterms)), axis=1)
    for i,p in enumerate(reversed(posyTerms),nconstr):
        Gvect = np.append(Gvect, [float(p.const) / constraint])
        for v,e in zip(p.vars, p.powers):
            Fmat[v][i] += e
    return Fmat, Gvect, Kdim


def buildMatrix(gatelist, netlist, pins, pouts, maxArea):
    # matrix variable 0 = max of all outputs...needs single row (first) for optimization
    F = np.zeros((1 + len(gatelist) + len(netlist), 1))
    F[0] = 1
    G = np.array([1])
    K = np.array([1])

    tconst = 0.69
    # build gatemap gate -> matrix variable index
    gateMap = {}
    for i,g in enumerate(gatelist,1):
        gateMap[g] = i
    
    # build netmap net -> matrix variable index (for max function)
    netMap = {}
    for i,n in enumerate(netlist,1+len(gatelist)):
        netMap[n] = i


    # Need better story for inputs and outputs
    #  For primary outpus, there must be a load (fixed value which becomes part of the constant)
    #  For primary inputs, there will be a driver (fixed value which becomes part of the constant -- look at Horowitz paper)


    # build delays
    for n in netlist:
        ToutVar = netMap[n]
        DivTout = PNom(1, ToutVar, -1)

        #print n, n.name, ToutVar

        drivers = filter(lambda x: x.gate.isDriver(x.portname), n.ports)
        loads = filter(lambda x: x.gate.isLoad(x.portname), n.ports)

        CapTerms = []

        # should check for primary output...
        # compute all loads associated with this net
        for ld in loads:
            Cscale = ld.gate.getInputCap(ld.portname)
            Cvar = gateMap[ld.gate]
            CapTerms.append(PNom(Cscale, Cvar, 0.9))

        if not drivers:
            # this must be a prime input
            Rin = PNom(tconst * RinDefault)
            RCTerms = [c * Rin for c in CapTerms]
            delay = [DivTout * rc for rc in RCTerms]
            F, G, K = addConstraint(F, G, K, delay, 1)
            #print n.name, delay
            continue
        
        # for each driver of this net
        for drv in drivers:
            Rscale = drv.gate.getResist(drv.portname)
            Rvar = gateMap[drv.gate]
            Cintr = drv.gate.getIntrCap(drv.portname)

            Rdrv = PNom(tconst * Rscale, Rvar, -0.9)
            RCintr = PNom(tconst * Rscale * Cintr, Rvar, -1)

            RCTerms = [c * Rdrv for c in CapTerms]

            # for each input to driver compute delay constraint
            #  Tin + (tconst * Rscale * Cintr) * Rvar^-1  + Sum over all inputs (tconst * Rscale * Rvar^-1) * Rvar^-1 * Cscale * Cvar <= Tout

            # should check for primary input...

            # and divide this by Tout
            #  so the Tin will be specific to each instancen of the loop below
            #  but all the loads are reused
            for inp in drv.gate.ins.values():
                TinVar = netMap[inp]
                Tin = PNom(1, TinVar, 1)

                # Create constraint for this path
                #print n.name, drv.gate.name, inp.name
                terms = [Tin, RCintr] + RCTerms 
                delay = [DivTout * t for t in terms]
                
                F, G, K = addConstraint(F, G, K, delay, 1)
                #print n.name, delay
                #print F

    # add gate size constraints
    for gate,gateVar in gateMap.items():
        minSize = gate.getMin()
        maxSize = gate.getMax()
        F, G, K = addConstraint(F, G, K, [PNom(1,gateVar,1)], maxSize)
        F, G, K = addConstraint(F, G, K, [PNom(1,gateVar,-1)], 1.0/minSize)

    # add gate area constratints
    areaConstraints = [PNom(gate.getAreaScaleFactor(), gateVar, 0.6) for gate,gateVar in gateMap.items()]
    F, G, K = addConstraint(F, G, K, areaConstraints, maxArea)

    # add final delay
    # find primary outputs and bound them by the first variable (max delay)
    # print "pouts = ", [x.name for x in pouts]
    for net in pouts:
        F, G, K = addConstraint(F, G, K, [PNom(1, 0, -1, netMap[net], 1)], 1)

    print (F)
    print (G)
    print (K)

    return F,G,K, gateMap

if __name__ == "__main__":
    Ain = Net('Ain')
    Bin = Net('Bin')
    Cin = Net('Cin')

    n1 = Net('n1')
    n2 = Net('n2')
    Zout = Net('Zout')
    Wout = Net('Wout')

    AND1 = Gate('AND1', ins = {'a' : Ain, 'b' : Bin}, outs = {'z' : n1})
    OR1 = Gate('OR1', ins = {'a' : n1, 'b' : Cin}, outs = {'z': Zout})
    NOT1 = Gate('NOT1', ins = {'a' : Cin}, outs = {'z' : n2})
    AND2 = Gate('AND2', ins = {'a' : Zout, 'b' : n2}, outs = {'z' : Wout})

    # Should eventually use a topsort to find all of these (or port list)
    PrimeIns = [Ain, Bin, Cin]
    PrimeOuts = [Zout, Wout]

    totalArea = 4

    gatelist = [AND1, OR1, NOT1, AND2]
    netlist = [Ain, Bin, Cin, n1, n2, Zout, Wout]
    
    F,G,K = buildMatrix(gatelist, netlist, PrimeIns, PrimeOuts, totalArea)
    
    Glog = log(matrix(G))
    
    result = exp( solvers.gp(K.tolist(), matrix(F.transpose()), Glog)['x'] )
    print(result)

# Gate lookup
# Real constants

def optimizeMatrix(F, G, K):
    Glog = log(matrix(G))
    
    # need to check for errors and eliminate verbose output (or basically all output except possibly warnings/errors)
    result = exp( solvers.gp(K.tolist(), matrix(F.transpose()), Glog)['x'] )


    return result


def findPrimeInsOuts(netlist):
    ins = []
    outs = []

    for n in netlist:
        # Could probably rewrite this with any/all...
        incoming = [pref for pref in n.ports if n in pref.gate.outs.values()]
        outgoing = [pref for pref in n.ports if n in pref.gate.ins.values()]

        if not incoming:
            ins.append(n)
        if not outgoing:
            outs.append(n)
    return ins, outs




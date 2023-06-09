

#
import numpy as np
from cvxopt import matrix, log, exp, solvers


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



# dont subclass: pass type and either ordered params or keywords...
class Gate:
    def __init__(self, name, type, ins, outs):
        self.name = name
        self.ins = ins
        self.outs = outs
        for portname,net in self.ins.items():
            net.addPort(self, portname)
        for portname,net in self.outs.items():
            net.addPort(self, portname)
    def isDriver(self,name):
        return name in self.outs
    def isLoad(self,name):
        return name in self.ins
    def getInputCap(self, portname):
        return 1.0
    def getIntrCap(self, portname):
        return 1.0
    def getResist(self,portname):
        return 1.0
    def getMin(self):
        return 1.0
    def getMax(self):
        return 16.0
    def getAreaScaleFactor(self):
        return 1.0

RinDefault = 1

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
            CapTerms.append(PNom(Cscale, Cvar, 1))

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

            Rdrv = PNom(tconst * Rscale, Rvar, -1)
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
    areaConstraints = [PNom(gate.getAreaScaleFactor(), gateVar, 1) for gate,gateVar in gateMap.items()]
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




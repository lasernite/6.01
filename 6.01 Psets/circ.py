from le import solveEquations

equationList = [[(1,'e1'),(-1,'e0'),(-15, None)], \
                [(1,'e1'), (-1,'e2'),(-3, 'i2')], \
                [(1,'e2'),(-1,'e0'),(-2, 'i3')],\
                [(1,'i4'),(10,None)],[(1,'i1'),(1,'i2')], \
                [(1,'i3'),(1,'i4'),(-1,'i2')], \
                [(1,'e0')]]

class OnePort:
    def __init__(self, e1, e2, i):
        self.e1 = e1
        self.e2 = e2
        self.i = i

class VSrc(OnePort):
    def __init__(self, v0, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1,e1),(-1,e2),(-v0,None)]

class ISrc(OnePort):
    def __init__(self, i0, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1,i),(-i0,None)]

class Resistor(OnePort):
    def __init__(self, r, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1,e1),(-1,e2),(-r,i)]

class VoltageSensor(OnePort):
    def __init__(self, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1,i)]
    
class VCVS(OnePort):
    def __init__(self, sensor, e1, e2, i, K=1000000):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(-K,sensor.e1),(K,sensor.e2),(1,e1),(-1,e2)]

class Thevenin(OnePort):
    def __init__(self, v, r, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1,e1),(-1,e2),(-v,None),(-r,i)]

def OpAmp(ea1, ea2, Ia, eb1, eb2, Ib, K=1000000):
    return [VoltageSensor(ea1,ea2,Ia),VCVS(VoltageSensor(ea1,ea2,Ia),eb1,eb2,Ib,K)]

def theveninEquivalent(components, nPlus, nMinus, current):
    circuit = solveCircuit(components, nMinus)
    vth = circuit[nPlus] - circuit[nMinus]
    components_sc = components + [Resistor(0,nPlus,nMinus,current)]
    circuit_sc = solveCircuit(components_sc, nMinus)
    isc = circuit_sc[current]
    rth = vth/isc
    return Thevenin(vth,rth,nPlus,nMinus,current)

#SOLVING CIRCUITS

def flatten_list(l):
    out = []
    for i in l:
        if type(i) == list:
            out.extend(flatten_list(i))
        else:
            out.append(i)
    return out

def solveCircuit(componentList, GND):
    # flatten_list is necessary for lists that contain two-ports,
    # which will be introduced in exercises over the nex few weeks.
    # It has no effect on lists that contain just one-ports.
    # Do not remove the following line.
    componentList = flatten_list(componentList)
    equations = []
    for oneport_instance in componentList:
        equations.append(oneport_instance.equation)

    nodes = []
    for oneport_instance in componentList:
        nodes.append(oneport_instance.e1)
        nodes.append(oneport_instance.e2)

    nodes = list(set(nodes))
    nodes.remove(GND)

    parts = []
    for node in nodes:
        for oneport_instance in componentList:
            if node == oneport_instance.e1:
                parts.append((1,oneport_instance.i))
            elif node == oneport_instance.e2:
                parts.append((-1,oneport_instance.i))
        equations.append(parts)
        parts = []
        
    ground = [(1,GND)]
    equations.append(ground)
    return solveEquations(equations,verbose=False)


def test1():
    v1 = VSrc(15,'e1','e0','i1')
    r1 = Resistor(3, 'e1','e2','i2')
    r2 = Resistor(2, 'e2', 'e0', 'i3')
    i1 = ISrc(-10, 'e2','e0','i4')
    ans = solveCircuit([v1,r1,r2,i1],'e0')
    return ans


'''vSource = VSrc(vi,'v+','gnd','iVolt')
r1 = Resistor(r, 'gnd','v+','i1')
r2 = Resistor(r, 'v+','v-','i2')
r3 = Resistor(r, 'v-','e1','i3')
r4 = Resistor(r, 'v-','gnd','i4')
r5 = Resistor(r, 'gnd','e1','i5')
r6 = Resistor(r, 'v+', 'e1', 'i6')

circuitComponents = [vSource,r1,r2,r3,r4,r5,r6]
'''
a1 = 1.00
a2 = 0.23
a3 = 0.81

r1 = Resistor(4000.0 * (1.0-a1), 'v1','vr1','i1')
r2 = Resistor(4000.0 * (1.0-a2), 'v2','vr2','i2')
r3 = Resistor(4000.0 * (1.0-a3), 'v3','vr3','i3')
r4 = Resistor(460.0, 'vr1','V','i4')
r5 = Resistor(460.0, 'vr2','V','i5')
r6 = Resistor(460.0, 'vr3', 'V', 'i6')
r7 = Resistor(0,'V','gnd','IIIIII')

v1 = VSrc(0.013,'v1','gnd','iv1')
v2 = VSrc(0.067,'v2','gnd','iv2')
v3 = VSrc(0.042,'v3','gnd','iv3')

# print solveCircuit([r1,r2,r3,r4,r5,r6,r7,v1,v2,v3], 'gnd')

# PSet 7 Solving (Two OpAmps)

r1 = 51000000.0
r2 = 1900.0
r3 = 190000.0
ipmt = 540.0 * 10**-12

ipmt = ISrc(-540.0 * 10**-12, 'gnd', 'e1', 'i1' )
r1 = Resistor(51000000.0, 'e1','transamp_out','i2')
r2 = Resistor(1900.0, 'transamp_out','e2','i3')
r3 = Resistor(190000.0, 'e2','v_out','i4')
opamp1 = OpAmp('gnd', 'e1', 'ia','transamp_out', 'gnd', 'ib', K=1000000)
opamp2 = OpAmp('gnd', 'e2', 'ia2', 'v_out', 'gnd', 'ib2', K=1000000)

circuitComponents = [ipmt, r1, r2, r3, opamp1, opamp2]

# a = solveCircuit(circuitComponents, 'gnd')




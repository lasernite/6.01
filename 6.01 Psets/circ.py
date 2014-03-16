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
    '''
kcl = {}
    for oneport_instance in componentList:
        kcl[oneport_instance.i] = [oneport_instance.e1, oneport_instance.e2]

    kcl_equations = []
    print kcl
    for i in kcl:
        for i2 in kcl:
            if i == i2:
                pass
            else:
                if kcl[i][0] == kcl[i2][0]:
                    kcl_equations.append([(1,i),(1,i2)])
                elif kcl[i][0] == kcl[i2][1]:
                    kcl_equations.append([(1,i),(-1,i2)])
                elif kcl[i][1] == kcl[i2][0]:
                    kcl_equations.append([(-1,i),(1,i2)])
                elif kcl[i][1] == kcl[i2][1]:
                    kcl_equations.append([(-1,i),(-1,i2)])
                else:
                    pass

    for eq in kcl_equations:
        if eq[0][0] + eq[1][0] < 0:
            kcl_equations.remove(eq)
    
                  
    equations += kcl_equations
    '''
    ground = [(1,GND)]
    equations.append(ground)
    return solveEquations(equations,verbose=True)


def test1():
    v1 = VSrc(15,'e1','e0','i1')
    r1 = Resistor(3, 'e1','e2','i2')
    r2 = Resistor(2, 'e2', 'e0', 'i3')
    i1 = ISrc(-10, 'e2','e0','i4')
    ans = solveCircuit([v1,r1,r2,i1],'e0')
    return ans

vSource = VSrc(vi,'v+','gnd','iVolt')
r1 = Resistor(r, 'gnd','v+','i1')
r2 = Resistor(r, 'v+','v-','i2')
r3 = Resistor(r, 'v-','e1','i3')
r4 = Resistor(r, 'v-','gnd','i4')
r5 = Resistor(r, 'gnd','e1','i5')
r6 = Resistor(r, 'v+', 'e1', 'i6')

circuitComponents = [vSource,r1,r2,r3,r4,r5,r6]

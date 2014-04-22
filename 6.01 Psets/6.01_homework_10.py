from pset9 import *

# Cabbage, Goat, Wolf

def check_switch(farm,i):
    if farm[i] == 'L':
        farm[i] = 'R'
    elif farm[i] == 'R':
        farm[i] = 'L'
    return farm

def FGWCSuccessors(state):
    successors = []
    legal = [('L','L','L','L'),('L','R','L','L'),('L','L','R','R'), \
             ('L','L','R','L'),('L','L','L','R'),('R','R','L','L'), \
             ('R','R','R','L'),('R','R','R','R'),('R','R','L','R'), \
             ('R','L','R','R')]
    farm = list(state)
    farm = tuple(check_switch(farm,0))
    if farm in legal:
        successors.append(farm)

    for i in range(1,4):
        new = list(farm)
        new = tuple(check_switch(new,i))
        if new in legal:
            successors.append(new)
            
    return successors
    
def goalTest(s):
    return s == ('R','R','R','R')

def test():
    ans = FGWCSuccessors(('L','L','L','L'))
    return ans

def test2():
    ans = FGWCSuccessors(('R','R','L','L'))
    return ans

def test3():
    ans = (goalTest(('L','L','L','L')), goalTest(('R','R','R','R')))
    return ans

def test4():
    ans = search(FGWCSuccessors, ('L','L','L','L'), goalTest)
    return ans


# Elevator Madness = Ab und Aufzug

def goal(state):
    return state[1] == (1,1,2)

from pset9 import *

def check_switch(farm,i):
    if farm[i] == 'L':
        farm[i] = 'R'
    elif farm[i] == 'R':
        farm[i] = 'L'
    return farm

def FGWCSuccessors(state):
    farm = list(state)
    farm = check_switch(farm,0)
    alls = []
    if farm[1] == farm[2] or farm[1] == farm[3]:
            new = tuple(check_switch(farm,1))
            alls.append(new)
    else:
        farm = tuple(farm)
        alls.append(farm)
    return alls

def goalTest(s):
    return s == ['R','R','R','R']

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

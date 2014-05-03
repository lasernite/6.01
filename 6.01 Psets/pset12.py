import lib601.dist as dist
from lib601.dist import *

def turtlefood(initd, depth):
    h = initd[0]
    l = initd[1]
    g = initd[2]
    def nextH(h,l,g):
        return h*0.5 + l*0.3
    def nextG(h,l,g):
        return h*0.3 + g*0.7 + l*0.2
    def nextL(h,l,g):
        return h*0.2 + l*0.5 + g*0.3
    prob = [h,l,g]
    for d in range(depth):
        H = nextH(prob[0], prob[1], prob[2])
        G = nextG(prob[0], prob[1], prob[2])
        L = nextL(prob[0], prob[1], prob[2])
        prob = [H,L,G]
    return prob

# Returns solution to Long-term Behavior
# print turtlefood([1.0/3, 1.0/3, 1.0/3], 100)   

class MarkovChain:
    def __init__(self, startDistribution, transitionDistribution):
        self.startDistribution = startDistribution
        self.transitionDistribution = transitionDistribution  

def stateSequenceProb(mc, seq):
    current_d = mc.startDistribution
    prob = 1.0
    for state in range(len(seq)):
        prob *= current_d.prob(seq[state])
        current_d = mc.transitionDistribution(seq[state])
    return prob

def occupationDist(mc, T):
    current_d = mc.startDistribution
    for time in range(T):
        inter = {}
        total = 0
        for state in current_d.support():
            nextd = mc.transitionDistribution(state)
            for dstate in nextd.support():
                if dstate in inter:
                    inter[dstate] += nextd.prob(dstate)*current_d.prob(state)
                else:
                    inter[dstate] = nextd.prob(dstate)*current_d.prob(state)
        current_d = dist.DDist(inter)
    return current_d

''' # Easier way utilizing dist.totalProbability function and recursion

def occupationDist(mc, T):
    if T == 0:
        return mc.startDistribution
    else:
        return dist.totalProbability(occupationDist(mc, T-1),
                                     mc.transitionDistribution)
'''

def test1():
    startDist = uniformDist(range(5))
    transitionDist = lambda s: mixture(uniformDist(range(s-1,s+2)), deltaDist(s-2), 0.299341)
    ans = stateSequenceProb(MarkovChain(startDist, transitionDist), [4, 2, 3, 3])
    return ans

def test2():
    startDist = uniformDist(range(5))
    transitionDist = lambda s: mixture(uniformDist(range(s-1,s+2)), deltaDist(s-2), 0.975986)
    ans = stateSequenceProb(MarkovChain(startDist, transitionDist), [4, 4, 5, 3, 1, -1])
    return ans

def test4():
    startDist = uniformDist(range(5))
    transitionDist = lambda s: mixture(uniformDist(range(s-1,s+2)), deltaDist(s-2), 0.812699)
    ans = occupationDist(MarkovChain(startDist, transitionDist), 5).d
    return ans

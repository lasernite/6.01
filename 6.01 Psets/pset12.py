import lib601.dist as dist
from lib601.dist import *
from lib601.hmm import *
from math import *
import lib601.util as util
from lib601.util import *


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

kittens3 = {0:0.125, 1:0.375, 2:0.375, 3:0.125}
kittens4 = {0:0.0625, 1:0.25, 2:0.375, 3:0.25, 4:0.0625}
kittens5 = {0:0.03125, 1:0.15625, 2:0.3125, 3:0.3125, 4:0.15625, 5:0.03125}
# Kitten dist with uniform dist:
unikitten = {}

for key in kittens5:
    unikitten[key] = kittens5[key] * 1.0/3
for key in kittens4:
    unikitten[key] += kittens4[key] * 1.0/3
for key in kittens3:
    unikitten[key] += kittens3[key] * 1.0/3

expected = 0
for key in unikitten:
    expected += unikitten[key]*key

# New kitten dist expectation
newkitten = {}

for key in kittens5:
    newkitten[key] = kittens5[key] * 0.43859649
for key in kittens4:
    newkitten[key] += kittens4[key] * 0.56140351

newexpected = 0

newexpected = 0
for key in newkitten:
    newexpected += newkitten[key]*key


# State Estimator

initialDist = dist.DDist({'c':0.1,'d':0.7,'e':0.2})
def obsModel(s):
    if s == 'c':
        return dist.DDist({'good':0.9,'bad':0.1})
    else:
        return dist.DDist({'good':0.2,'bad':0.8})

def nextChar(s):
    # return next bigger character (in alpha order)
    return chr(ord(s)+1)    
def prevChar(s):
    # return next smaller character (in alpha order)
    return chr(ord(s)-1)    

def transModel(s):
    if s == 'a':
        return dist.deltaDist('a')
    elif s == 'z':
        return dist.deltaDist('z')
    else:
        return dist.DDist({s:0.5, nextChar(s):0.25, prevChar(s):0.25})

letterC = HMM(initialDist, transModel, obsModel)

class StateEstimator:
    def __init__(self, hmm):
        self.hmm = hmm
        self.belief = self.hmm.startDistribution
    def transition(self):
        transmix = dist.makeJointDistribution(self.belief, self.hmm.transitionDistribution)
        self.belief = transmix.project(lambda (a,b): b)
    def observe(self, obs):
        self.belief = dist.bayesRule(self.belief, self.hmm.observationDistribution, obs)



def test1a():
    se = StateEstimator(letterC)
    se.observe('bad')
    se.observe('bad')
    ans = se.belief.d
    return ans

def test2a():
    se = StateEstimator(letterC)
    se.transition()
    se.transition()
    ans = se.belief.d
    return ans

def test3a():
    se = StateEstimator(letterC)
    se.transition()
    se.observe('good')
    se.transition()
    se.observe('bad')
    ans = se.belief.d
    return ans


def sonarHit(distance, sonarPose, robotPose):
    # Sonar hit distance from robot
    dr = distance + sqrt(sonarPose.x**2 + sonarPose.y**2)
    # Wall distance from robot coordinates
    wrx = cos(robotPose.theta + sonarPose.theta) * dr
    wry = sin(robotPose.theta + sonarPose.theta) * dr
    print util.Pose(wrx, wry, robotPose.theta + sonarPose.theta)
    # Global coordinates
    gx = robotPose.x + wrx
    gy = robotPose.y + wry
    print util.Pose(gx, gy, robotPose.theta + sonarPose.theta)
    # Slighty off? ~3%
    return util.Point(gx, gy)

def sonarHit(distance, sonarPose, robotPose):
    globalsensor = robotPose.transformPose(sonarPose)
    # Now set wall hit by continuing in direction of sonar for distance d
    wallhit = globalsensor.transformPose(util.Pose(distance,0,0))
    return wallhit.point()
    
def testsonar():
    ans = sonarHit(0.5, util.Pose(0.15, 0, math.pi/10), util.Pose(1, 0.5, math.pi/4)).xyTuple()
    return ans

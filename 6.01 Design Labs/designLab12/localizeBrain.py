from lib601.plotWindow import PlotWindow
from soar.io import io
import beliefGraph
reload(beliefGraph)
import lib601.idealReadings as idealReadings
import lib601.hmm as hmm
import lib601.dist as dist
import lib601.sonarDist as sonarDist
import os,os.path
import math
import lib601.util as util
import models
reload(models)

####################################################################
###
### Preliminaries -- do not change the following code
###
####################################################################

labPath = os.getcwd()
WORLD_FILE = os.path.join(labPath,'baseWorld.py')
FORWARD_VELOCITY = 0.5


# Where the robot will be in the world
(xMin, xMax) = (0.5, 7.7)
robotY = y = 1.0

# Distance and Gain for Wall Following
desiredRight = 0.5
Kp,Ka = (10.0,2.0)

# Maximum "good" sonar reading
sonarMax = 1.5

#method to discretize values into boxes of size gridSize
def discretize(value, gridSize, maxBin=float('inf'), valueMin = 0):
    return min(int((value - valueMin)/gridSize), maxBin)

#method to clip x to be within lo and hi limits, inclusive
def clip(x, lo, hi):
    return max(lo, min(x, hi))

####################################################################
###
###          Probabilistic Models -- you may change this code
###
####################################################################

import lib601.dist as dist

# Number of discrete locations and discrete observations
numStates = 100 
numObservations = 30


def naiveObsModel(s):
    return dist.deltaDist(ideal[s])

def uniformObsModel(s):
    return dist.uniformDist(range(numObservations))

def obsModel(s):
    pass # your code here


def naiveTransModel(s):
    return dist.deltaDist(clip(s+1, 0, numStates-1))

transModel = models.makeTransModel(FORWARD_VELOCITY, xMax, xMin, numStates)

def confidentLocation(belief):
    return (-1,False) #your code here

uniformInitDist = dist.squareDist(0, numStates)
spikedInitDist = dist.deltaDist(24)

INIT_DIST_TO_USE = uniformInitDist
OBS_MODEL_TO_USE = naiveObsModel
TRANS_MODEL_TO_USE = naiveTransModel

######################################################################
###
###          Brain Methods -- do not change the following code
###
######################################################################

# Robot's Ideal Readings
ideal = idealReadings.computeIdealReadings(WORLD_FILE, xMin, xMax, robotY, numStates, numObservations)

def getParkingSpot(ideal):
    avg = sum(ideal)/float(len(ideal))
    i = len(ideal)-1
    while i>0 and ideal[i]>avg:
        i -= 1
    j = i
    while j>0 and ideal[j]<avg:
        j -= 1
    i = j
    while i>0 and ideal[i]>avg:
        i -= 1
    return (i+1+j)/2


def setup():
    global ideal, confident,parkingSpot,targetTheta,targetX

    parkingSpot = getParkingSpot(ideal)
    targetX = None
    targetTheta = math.pi/2
    confident = False
    
    if not (hasattr(robot,'g') and robot.g.winfo_exists()):
        robot.g = beliefGraph.Grapher(ideal)
        robot.nS = numStates
    if robot.nS != numStates:
        robot.g.destroy()
        robot.g = beliefGraph.Grapher(ideal)
        robot.nS = numStates
    robot.hmm = hmm.HMM(INIT_DIST_TO_USE,
                        TRANS_MODEL_TO_USE,
                        OBS_MODEL_TO_USE)
    robot.estimator = robot.hmm.makeStateEstimator()
    robot.g.updateDist()
    robot.g.updateBeliefGraph([robot.estimator.belief.prob(s) \
                               for s in xrange(numStates)])
    robot.probMeasures = []
    robot.data = []

def brainStart():
    pass

def step():
    global confident, targetX, targetTheta
    sonars = io.getSonars()
    pose = io.getPosition(True)
    (px, py, ptheta) = pose

    if confident:
        ptheta = util.fixAnglePlusMinusPi(ptheta)
        if px>targetX+.05 and abs(ptheta)<math.pi/4:
            io.Action(fvel=-0.2,rvel=0).execute() #drive backwards if necessary
        elif px<targetX and abs(ptheta)<math.pi/4:
            io.Action(fvel=0.2,rvel=0).execute()  #drive to desired x location
        elif ptheta<targetTheta-.05:
            io.Action(fvel=0,rvel=0.2).execute()  #rotate
        elif sonars[3]>.3:
            io.Action(fvel=0.2,rvel=0).execute()  #drive into spot
        else:
            io.Action(fvel=0,rvel=0).execute()  #congratulate yourself (or call insuran
        return

    
    # Quality metric.  Important to do this before we update the belief state, because
    # it is always a prediction
    parkingSpaceSize = .75
    robotWidth = 0.3
    margin = (parkingSpaceSize - robotWidth) / 2
    # Robot is about .3 meters wide.  Parking place is .75
    trueX = io.getPosition(True)[0]
    robot.probMeasures.append(estimateQualityMeasure(robot.estimator.belief,
                                                     xMin, xMax, numStates, margin,
                                                     trueX))
    trueS = discretize(trueX, (xMax - xMin)/numStates, valueMin = xMin)
    n = len(robot.probMeasures)
    
    if n == 80:
        brainStop()
    
    # current discretized sonar reading
    left = discretize(sonars[0], sonarMax/numObservations, numObservations-1)
    robot.data.append((trueS, ideal[trueS], left))
    # obsProb
    obsProb = sum([robot.estimator.belief.prob(s) * OBS_MODEL_TO_USE(s).prob(left) \
                   for s in xrange(numStates)])

    # GRAPHICS
    if robot.g is not None:
        # redraw ideal distances (compensating for tk bug on macs)
        # draw robot's true state
        if trueS < numStates:
            robot.g.updateDist()
            robot.g.updateTrueRobot(trueS)
        # update observation model graph
        robot.g.updateObsLabel(left)
        robot.g.updateObsGraph([OBS_MODEL_TO_USE(s).prob(left) \
                                for s in xrange(numStates)])

    robot.estimator.update(left)
    (location, confident) = confidentLocation(robot.estimator.belief)

    if confident:
        targetX = (parkingSpot-location)*(xMax-xMin)/float(numStates) + px
        print 'I am at x =',location,': proceeding to parking space'

    # GRAPHICS
    if robot.g is not None:
        # update world drawing
        # update belief graph
        robot.g.updateBeliefGraph([robot.estimator.belief.prob(s) \
                                   for s in xrange(numStates)])

    # DL6 Angle Controller
    (distanceRight, theta) = sonarDist.getDistanceRightAndAngle(sonars)
    if not theta:
       theta = 0
    e = desiredRight-distanceRight
    ROTATIONAL_VELOCITY = Kp*e - Ka*theta
    io.setForward(FORWARD_VELOCITY)
    io.setRotational(ROTATIONAL_VELOCITY)

def brainStop():
    p = PlotWindow()
    p.plot(robot.probMeasures)
    p.axes[0].set_ylim([0.0,1.0])

def shutdown():
    pass

def estimateQualityMeasure(belief, xMin, xMax, numStates, delta, trueX):
    minGood = max(trueX - delta, xMin)
    maxGood = min(trueX + delta, xMax)
    stateSize = (xMax - xMin) / numStates
    minGoodDiscrete = max(0, discretize(minGood, stateSize, valueMin = xMin))
    maxGoodDiscrete = min(numStates-1,
                          discretize(maxGood, stateSize, valueMin = xMin)) + 1

    minGoodReconstituted = minGoodDiscrete * stateSize + xMin
    maxGoodReconstituted = maxGoodDiscrete * stateSize + xMin

    fracLowBinInRange = 1 - ((minGood - minGoodReconstituted) / stateSize)
    fracHighBinInRange = 1 - ((maxGoodReconstituted - maxGood) / stateSize)

    total =  sum(belief.prob(s) for s in range(minGoodDiscrete+1, maxGoodDiscrete))
    lowP = belief.prob(minGoodDiscrete) * fracLowBinInRange
    highP = belief.prob(maxGoodDiscrete) * fracHighBinInRange
    return total + lowP + highP


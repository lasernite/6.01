#
# soar
# io.py - object-oriented interface to the robot
#

# This io file makes use of the "official" soar interface 
# (sonarDistances, etc), and it is still ugly, since it relies on having
# a handle on the brain environment, but it is arguably neater than
# the io.py file.  However it seems to introduce some kind of lag that 
# makes the really complicated labs with localization stuff work poorly

import soar.util
from soar.util import *

robotRadius = 0.2

def configure_io(namespace):
    # need to use global 'cause we don't want to accidentally overwrite
    # the brain environ by setting it to None when io.py is imported
    global io_environ
    io_environ = namespace

class SensorInput():
    global io_environ
    """
    Represents one set of sensor readings from the robot, incluing
    sonars, odometry, and readings from the analogInputs
    """
    def __init__(self, cheat=False):
        self.sonars = io_environ['sonarDistances']()
        if cheat:
            p = io_environ['cheatPose']()
        else:
            p = io_environ['pose']()
        self.odometry = valueListToPose(p)
        self.analogInputs = io_environ['analogInputs']()
    def __str__(self):
        return 'Sonar: ' + util.prettyString(self.sonars) + \
               "; Odo: " + util.prettyString(self.odometry) +\
               "; Analog: " + util.prettyString(self.analogInputs)

referenceVoltage = 5.0
class Action:
    """
    One set of commands to send to the robot
    """
    def __init__(self, fvel = 0.0, rvel = 0.0, 
                 voltage = referenceVoltage,
                 discreteStepLength = None):
        """
        @param fvel: signed number indicating forward velocity in m/s
        @param rvel: signed number indicating rotational velocity in
        rad/sec (?)  positive is left, negative is right
        @param voltage: voltage to send to analog input port of
        control board;  should be between 0 and 10v ??
        @param discreteStepLength: if C{None}, then the robot
        continues driving at the last commanded velocity until a new
        action command is received;  if set to a positive value, the
        robot will drive at the last commanded velocity until
        C{discreteStepLength} seconds have passed, and then stop.
        Setting the step length to, e.g., 0.1, is useful when the
        brain is doing so much computation that the robot drives too
        far between steps.
        """
        self.fvel = fvel
        self.rvel = rvel
        self.voltage = voltage
        self.discreteStepLength = discreteStepLength

    def execute(self):
        if self.discreteStepLength:
            io_environ['discreteMotorOutput'](self.fvel, self.rvel,
                                              self.discreteStepLength)
        else:
            io_environ['motorOutput'](self.fvel, self.rvel)
        io_environ['analogOutput'](self.voltage)

    def __str__(self):
        return 'Act: ' + \
               util.prettyString([self.fvel, self.rvel, self.voltage])

def registerUserFunction(type, f):
    io_environ['registerUserFunction'](type, f)

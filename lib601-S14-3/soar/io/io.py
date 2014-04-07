"""
Interaction with soar

@undocumented: SensorInput, Action, robotRadius, FVEL, RVEL, VOLT, referenceVoltage, configure_io, setDiscreteStepLength, enableTeleportation, registerUserFunction, done, oscilloscope, addScopeProbeFunction, clearScope
"""

import soar.util as util
from soar.util import *

robotRadius = 0.2

def configure_io(namespace):
    global soarwideDiscreteStepLength
    soarwideDiscreteStepLength = None

def setDiscreteStepLength(stepLength=None):
    global soarwideDiscreteStepLength
    soarwideDiscreteStepLength = stepLength

def enableTeleportation(prob, pose):
    app.soar.output.enableTeleportation(prob, pose)

class SensorInput:
    """
    Represents one set of sensor readings from the robot, incluing
    sonars, odometry, and readings from the analogInputs
    """
    def __init__(self, cheat = False):
        """
        @param cheat: If C{True}, then get odometry readings in
        absolute coordinate frame of simulated world.  Otherwise,
        odometry frame is defined by robot's initial pose when powered on
        or simulated world is reset.  Should never be set to C{True} on
        the real robot.
        """
#        self.sonars = app.soar.output.oldsonars.get()[:]
        self.sonars = app.soar.output.storedsonars.get()[:]
        """List of 8 sonar readings, in meters."""
        if cheat == True:
            self.odometry = \
                util.valueListToPose(app.soar.output.abspose.get())
            """Instance of util.Pose, representing robot's pose in the global frame if C{cheat = True} and the odometry frame if C{cheat = False}."""
        else:
            self.odometry = \
                util.valueListToPose(app.soar.output.odpose.get())
        self.analogInputs = app.soar.output.analogInputs.get()
        """List of 4 analog input values."""

    def __str__(self):
        return 'Sonar: ' + util.prettyString(self.sonars) + \
               "; Odo: " + util.prettyString(self.odometry) +\
               "; Analog: " + util.prettyString(self.analogInputs)

FVEL = 0
RVEL = 0
VOLT = 0

def setForward(v):
    """
    Set the robot's forward velocity (in meters per second).  Negative values
    cause the robot to move backward.  The robot's maximum translational
    velocity is 0.5 m/s.
    
    @param v: The desired velocity, in meters/second
    """
    global FVEL
    FVEL = v
    Action(FVEL,RVEL,VOLT).execute()

def setRotational(v):
    """
    Set the robot's rotational velocity (in radians per second).  Positive
    values turn the robot anticlockwise; negative values turn the robot
    clockwise.  The robot's maximum rotational velocity is 0.5 rad/s.
    
    @param v: The desired velocity, in radians/second
    """
    global RVEL
    RVEL = v
    Action(FVEL,RVEL,VOLT).execute()

def setVoltage(v):
    """
    Set the robot's analog output voltage.  The robot can output a voltage in
    the range [0V,10V].
    
    @param v: The desired voltage, in Volts
    """
    global VOLT
    VOLT = v
    Action(FVEL,RVEL,VOLT).execute()

def stopAll():
    """
    Set the robot's velocities and analog out voltage to 0.
    """
    global FVEL, RVEL, VOLT
    FVEL = RVEL = VOLT = 0.0
    Action(FVEL,RVEL,VOLT).execute()

def getSonars():
    """
    @return: a list of the 8 current sonar readings, with index 0 representing
    the left-most sonar and index 7 representing the right-most sonar.
    """
    return SensorInput().sonars

def getPosition(cheat=False):
    """
    @return: a tuple representing the robot's position, with elements (x,y,t),
    with x being the robot's x position in meters, y being the robot's y
    position in meters, and t being the robot's angle in radians.  If C{cheat}
    is C{True} (only in simulator), return the robot's absolute position in the
    world.  Otherwise, return the robot's position relative to its start point
    (last world reload).
    """
    return SensorInput(cheat=cheat).odometry.xytTuple()

def getAnalogInputs():
    """
    @return: a list containing the current analog input readings (in Volts),
    with index 0 representing analog input 1 (pin 1) and index 3 representing
    analog input 4 (pin 7)
    """
    return SensorInput().analogInputs

referenceVoltage = 5.0
class Action:
    """
    One set of commands to send to the robot
    """
    def __init__(self, fvel = 0.0, rvel = 0.0, 
                 voltage = referenceVoltage):
        """
        @param fvel: signed number indicating forward velocity in m/s
        @param rvel: signed number indicating rotational velocity in
        rad/sec;  positive is left, negative is right
        @param voltage: voltage to send to analog input port of
        control board;  should be between 0 and 10v ??
        """
        self.fvel = fvel
        self.rvel = rvel
        self.voltage = voltage
        # ignore the input argument for the actions, and just use the
        # global variable set via the function above
        self.discreteStepLength = soarwideDiscreteStepLength

    def execute(self):
        global FVEL,RVEL,VOLT
        FVEL,RVEL,VOLT = (self.fvel, self.rvel, self.voltage)
        if self.discreteStepLength:
            app.soar.output.discreteMotorOutput(self.fvel, self.rvel,
                                                self.discreteStepLength)
        else:
            app.soar.output.motorOutput(self.fvel, self.rvel)
        app.soar.output.analogOutput(self.voltage)

    def __str__(self):
        return 'Act: ' + \
               util.prettyString([self.fvel, self.rvel, self.voltage])

def registerUserFunction(type, f):
    app.soar.registerUserFunction(type, f)

def done(donep = True):
    if donep:
        app.soar.stopall()

def sonarMonitor(on=True):
    if on:
        app.soar.openSonarMonitor()
    else:
        app.soar.closeSonarMonitor()
            
def oscilloscope(on=True):
    if on:
        app.soar.openOscillo()
    else:
        app.soar.closeOscillo()
            
def addScopeProbeFunction(name, func):
    app.soar.openOscillo()
    app.soar.addScopeProbeFunction(name, func)

def clearScope():
    app.soar.clearScope()
    
#def beep(beepFreq = 440, beepDuration = 0.5):
#    app.soar.output.cmdSay(beepFreq, beepDuration)

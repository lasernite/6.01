from soar.io import io
######################################################################
###
###          Brain methods
###
######################################################################


def setup():
    pass

def brainStart():
    pass

def step():
    vNeck,vLeft,vRight,_ = io.getAnalogInputs()
    print 'Neck:',vNeck,'Left:',vLeft,'Right:',vRight
    pass #Your code here
    io.setForward(0)
    io.setRotational(0)

def brainStop():
    pass

def shutdown():
    pass

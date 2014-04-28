
dimensions(10,10)

def d(dt):
  return (0, 0, dt*0.3)

def makeSpinner(x,y,l,dth):
  def d(dt):
    return(0, 0, dt*dth)
  movingObstacle(((x+l/2,y),(x-l/2,y)), (x,y), d)


makeSpinner(2,2,2,0.4)
makeSpinner(2,8,2,0.4)
makeSpinner(8,8,2,0.4)
makeSpinner(8,2,2,0.4)



from math import sin, cos


class oscillator(object):
  def __init__(self, k):
    self.t = 0
    self.k = k

  def step(self, dt):
    self.t += dt
    return (-dt*self.k*sin(self.k*self.t),dt*self.k*cos(self.k*self.t),dt*self.k)

movingObstacle([(5,5),(6,5),(6,6),(5,6),(5,5)], (5.5,5.5), oscillator(0.1).step)

############################soar/outputs/simulator.py############################
# soar3.0
#  / outputs/simulator.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
from time import time, sleep
from Tkinter import *
from math import sin, cos, acos, tan, atan2, sqrt, pi
from random import gauss, uniform, random
from threading import Lock 
import os

import form.main
from form.parallel import Stepper, SharedVar
from form.common import parseFile, clip, CancelGUIAction, skip

debug = skip


SONAR_INFO=[(-0.134, 0.08, pi/2), (-0.118, 0.122, 5*pi/18), (-0.077, 0.156, pi/6), (-0.0266, 0.174, pi/18), (0.0266, 0.174, -pi/18), (0.077, 0.156, -pi/6), (0.118, 0.122, -5*pi/18), (0.134, 0.08, -pi/2)] #entries need to be (x,y,th), x,y are the cartesian coordinate locations of the sonars in meters, and th is the orientation of it with respect to the nose of the robot (CCW is positive)

TELEPORT_PROB = 0
DRAW_SONARS=True #broken right now #draw sonars or not
DRAG_UPDATES_ROBOT_ODOMETRY=False #When the robot is dragged around the simulator, is it's internal odometry updated or not
MAX_SIM_WIDTH=510 #max width of simulator canvas
MAX_SIM_HEIGHT=510 #max height of simulator canvas
SONAR_VARIANCE = lambda mean: 0.0017*(mean**3) #an unaccurate approximation of the variance of sonar readings based on distance.. It's better than a single value for variance though, since it is definitely dependent on distance
MAX_SONAR_DIST=5 #mean of maximum time sonar waits before saying "I waited enough time, it's this far or farther", value for sonarcycle=40ms
#MAX_SONAR_DIST=2.465 #value for sonarcycle=12ms
MAX_EFFECTIVE_SONAR_DIST = 1.5 # most robots don't get good readings longer than this
MAX_TRANS=0.5 #maximum forward/backward velocity of the robot
MAX_ROT=0.5 #maximum rotational velocity of the robot
SONAR_GOT_RESPONSE_COLOR="grey" #color for when the sonar doesn't have to wait until MAX_SONAR_DIST
SONAR_NO_RESPONSE_COLOR="red" #color for when it does
ROBOT_POINTS = [(-0.1905, 0.09525), (-0.0889, 0.180975), (0.0, 0.200025), (0.0889, 0.180975), (0.1905, 0.09525), (0.1905, -0.0635), (0.1651, -0.0635), (0.1651, -0.1651), (0.0889, -0.23495), (-0.0889, -0.23495), (-0.1651, -0.1651), (-0.1651, -0.0635), (-0.1905, -0.0635)]
DRAG_ROT_SPEED = -pi/100 #ratio controlling speed the robot rotates when you right-click to drag
ROBOT_RADIUS = max(map(lambda (x,y): ((x)**2+(y)**2)**(0.5), ROBOT_POINTS))
SIMULATOR_FPS = 10#12

# parameters to make the response of the simulator more like the robot
CAP_ACC=False
# on robot, TransAccTop=2000, TransAcc=300 mm/s/s
TRANS_ACC=0.3/float(SIMULATOR_FPS) # translational acceleration m/s/tick
# on robot, RotAccTop=300, RotAcc=100 deg/s/s
ROT_ACC=(100.0*pi/180.0)/float(SIMULATOR_FPS) # rot. acceleration rad/s/tick

def sq(x):
  return x*x
def norm(vec):
  div = sqrt(float(sum(map(sq, vec))))
  return tuple(map(lambda x: x/div, vec))
def dot(veca, vecb):
  return sum([veca[i]*vecb[i] for i in range(len(veca))])
def vec(line):
  return (line[1][0]-line[0][0], line[1][1]-line[0][1])
def angle(linea, lineb):
  return acos(dot(norm(vec(linea)), norm(vec(lineb))))

#simple approximation for whether sonar should return or not based on angle
def sonarangleok(angle):
  return 1
  #angle*=180/pi
  #bubble wrap?	return 1-sq(sq(angle/90.0)) > uniform(0, 1)
  #if angle < 30: return 1-(angle**6)/(2*(30.**6)) > uniform(0,1)
  #else: return ((angle-90)**6)/(2*(60.**6)) > uniform(0,1)

def intersectionhelper(((xa, ya),(xb,yb)),((xc,yc),(xd,yd))):
  try:
    s = ((xb-xa)*(ya-yc)+(yb-ya)*(xc-xa))/((xb-xa)*(yd-yc)-(yb-ya)*(xd-xc)) 
    t = ((xc-xa)+(xd-xc)*s)/(xb-xa)
    if s <= 1 and s >=0 and t <= 1 and t >= 0:
      fromt = (xa+(xb-xa)*t,ya+(yb-ya)*t)
      froms = (xc+(xd-xc)*s,yc+(yd-yc)*s)
      if abs(fromt[0]-froms[0])<0.001 and abs(fromt[1]-froms[1])<0.001:
        return fromt
      return False 
  except ZeroDivisionError:
    return False

#returns the point of intersection between two line segments, or False if there is no intersection
def intersection(linea, lineb):
  first = intersectionhelper(linea, lineb)
  if first:
    return first
  else:
    return intersectionhelper(lineb, linea)

#Don't change unless the laws of math change:
CIRCLE_SCALE_FACTOR = 2**(0.5)

class Obstacle(object):
  # dr(dt) --> (dx, dy, th)
  def __init__(self, (vertices, r, dr)):
    self.d = dr
    self.x, self.y = r
    self.th = 0
    self.vertices = []
    for v in vertices:
      self.vertices.append((v[0]-r[0], v[1]-r[1]))

  def __hash__(self):
    return (hash(self.x) + hash(self.y)) % 2**32
            
  def current_walls(self):
    walls = []
    ix,iy = self.vertices[0]
    for v in self.vertices[1:]:
      fx, fy = v
      ir = ((ix)**2+(iy)**2)**(0.5)
      fr = ((fx)**2+(fy)**2)**(0.5)
      ith = atan2(iy, ix)+self.th
      fth = atan2(fy, fx)+self.th
      walls.append(((self.x+ir*cos(ith), self.y+ir*sin(ith)),
                    (self.x+fr*cos(fth), self.y+fr*sin(fth))))
      ix, iy = fx, fy
    return walls

  def step(self,dt):
    delta = self.d(dt)
    self.x+=delta[0]
    self.y+=delta[1]
    self.th+=delta[2]

  def coords(self):
    return self.x, self.y, self.th
 
class Simulator(object):
  #DON'T change the dimensions on the fly, just make a new world 
  class World(object):
    def wall(self, start, end):
      self.walls.append((start,end))

    def movingObstacle(self, vertices, com, d):
      self.moving_obstacles.append((vertices, com, d))

    def dimensions(self, width, height):
      self.width = width
      self.height = height
      # borders to make collision detection/sonars easier:
      self.wall((0,0),(0,self.height))
      self.wall((0,0),(self.width,0))
      self.wall((self.width,self.height),(0,self.height))
      self.wall((self.width,self.height),(self.width,0))
	
    def initialRobotLocation(self, x, y, theta=0):
      self.init = x,y,theta
      self.initset = True 
    
    def __init__(self, worldfile):
      self.walls = []
      self.moving_obstacles = []
      self.initset = False
      envin = {}
      envin["dimensions"] = self.dimensions
      envin["wall"] = self.wall
      envin["initialRobotLoc"] = self.initialRobotLocation
      envin["initialRobotLocation"] = self.initialRobotLocation
      envin["movingObstacle"] = self.movingObstacle
      parseFile(worldfile, envin)
      if not self.initset:
        self.init = self.width/2.0, self.height/2.0, 0.0

  def __init__(self, worldfile, geom=None):
    if len(worldfile) == 0:
      raise CancelGUIAction
    self.worldfile = worldfile
    self.world = self.World(self.worldfile)
    self.win = Toplevel(form.main.tk)
    self.win.wm_title("Simulator")
    self.win.protocol("WM_DELETE_WINDOW", skip)
    # only pay attention to the position part, since the size is determined
    # by the world file
    self.geom = None
    if geom:
      self.geom = geom[geom.find('+'):]
      self.win.geometry(self.geom)
    debug("world loaded", 2)	
    self.initGlobals()
    debug("simulator globals initialized", 2)	
    self.setters = {"motorOutput":self.motorOutput, 
                    "discreteMotorOutput":self.discreteMotorOutput,
                    "analogOutput":self.analogOutput,
                    "setMaxEffectiveSonarDistance":self.setMaxEffectiveSonarDistance,
                    "enableAccelerationCap":self.enableAccelerationCap,
                    "setMaxVelocities":self.setMaxVelocities}
    self.getters = {"sonarDistances":self.reportSonars,
                    "pose":self.odpose.get, "stalled":self.stalled.get,
                    "analogInputs":self.analogInputs.get}
    debug("module data set up", 2)
    #self.resetbutton = Button(self.win, text="Reset", command=lambda: self.initGlobals(True))
    #self.resetbutton.pack(side="top")
    self.initCanvas()
    debug("drawing area initialized", 2)	
    self.drawWorld()
    self.drawRobot()
    debug("updating sonars...", 2)	
    self.updateSonars() 
    self.updateSonars() 
    debug("...updated!", 2)	
    app.soar.addFlowTriplet((self.startmoving, self.onestep, self.stopmoving))
    debug("finished settup up simulator", 2)	
 
  # Gets called by the Start button
  def startmoving(self):
    self.stopmoving()
    self.currentthread = Stepper(self.onestep, SIMULATOR_FPS)
    self.currentthread.start()
    
  # Gets called by the Stop button
  def stopmoving(self):
    self.motorOutput(0,0)
    try:
      self.currentthread.stop()
    except AttributeError:
      pass
	
  #Clean up before closing`
  def destroy(self):
    # tell the app what the current window geometry is so that we can 
    # restore it the next time soar is run
    app.soar.simulator_geom = self.win.geometry()
    app.soar.removeFlowTriplet((self.startmoving, self.onestep, self.stopmoving))
    self.stopmoving()
    self.win.destroy()

  def initGlobals(self, reset=False):
    self.storedsonars = SharedVar(8*[5.])
    self.oldsonars = SharedVar(8*[5.])
    self.v = SharedVar(0.0)
    self.w = SharedVar(0.0)
    self.abspose = SharedVar((self.world.init[0], self.world.init[1], 
                              self.world.init[2]))
    self.odpose = SharedVar((0.0, 0.0, 0.0))
    self.analogInputs = SharedVar((0.0, 0.0, 0.0, 0.0))
    if not reset:
      self.obstacles = []
      if self.world.width > self.world.height:
        self.simheight = MAX_SIM_WIDTH*self.world.height/self.world.width
        self.simwidth = MAX_SIM_WIDTH
      else:
        self.simwidth = MAX_SIM_HEIGHT*self.world.width/self.world.height
        self.simheight = MAX_SIM_HEIGHT
      self.pxmax = float(self.world.width)
      self.pxmin = 0.0
      self.pymax = float(self.world.height)
      self.pymin = 0.0
      self.cxmax = float(self.simwidth-5)
      self.cxmin = 5.0
      self.cymax = 5.0
      self.cymin = float(self.simheight-5)
      self.pxtocx = (self.cxmax-self.cxmin)/(self.pxmax-self.pxmin)
      self.pytocy = (self.cymax-self.cymin)/(self.pymax-self.pymin)    
      self.cxtopx = (self.pxmax-self.pxmin)/(self.cxmax-self.cxmin)    
      self.cytopy = (self.pymax-self.pymin)/(self.cymax-self.cymin) 
      self.pxcxconstant = self.cxmin-self.pxmin*self.pxtocx
      self.pycyoffset = self.cymin-self.pymin*self.pytocy
      self.cxpxoffset = self.pxmin-self.cxmin*self.cxtopx
      self.cypyoffset = self.pymin-self.cymin*self.cytopy
    else:
      self.drawRobot()
      self.updateSonars()
      self.updateSonars()
    self.inrobot = False
    self.stalled = SharedVar(False)

  # Get the drawable space ready
  def initCanvas(self):
    self.canvas = Canvas(self.win, width = self.simwidth, height = self.simheight, background = "white")
    self.canvas.bind("<Button-1>", self.left_click_down)
    self.canvas.bind("<B1-Motion>", self.left_click_moved)
    self.canvas.bind("<ButtonRelease-1>", self.left_click_up)

    #Thanks for making the right-button different on Macs, but not Linux.
    #Thanks for making os.uname not exist on windows... ugh!
    try:
      if os.uname()[0] == 'Darwin': 
        self.canvas.bind("<Button-2>", self.right_click_down)
        self.canvas.bind("<B2-Motion>", self.right_click_moved)
        self.canvas.bind("<ButtonRelease-2>", self.right_click_up)
      else:
        self.canvas.bind("<Button-3>", self.right_click_down)
        self.canvas.bind("<B3-Motion>", self.right_click_moved)
        self.canvas.bind("<ButtonRelease-3>", self.right_click_up)
    except AttributeError:
      self.canvas.bind("<Button-3>", self.right_click_down)
      self.canvas.bind("<B3-Motion>", self.right_click_moved)
      self.canvas.bind("<ButtonRelease-3>", self.right_click_up)
    self.canvas.pack(side = "top")
    self.odometrytext = StringVar()
    self.odometrylabel = Label(self.win, textvariable=self.odometrytext)
    self.odometrylabel.pack(side = "top")    

  # The next two functions are inverses of each other

  # A mapping from the space the robot lives in to the space that is displayed onto the computer screen 
  def PtoC(self, (px, py)):
    cx = px*self.pxtocx+self.pxcxconstant
    cy = py*self.pytocy+self.cymin-self.pymin*self.pytocy
    return (cx, cy)

  # A mapping from the space that is displayed onto the computer screen to the space the robot lives in 
  def CtoP(self, (cx, cy)):
    px = cx*self.cxtopx+self.pxmin-self.cxmin*self.cxtopx
    py = cy*self.cytopy+self.pymin-self.cymin*self.cytopy
    return (px, py)

  # Draw the world when a world is loaded
  def drawWorld(self):
    self.canvas.create_rectangle(0,0,5,self.simheight-5, 
                                 fill = "grey", outline="grey")
    self.canvas.create_rectangle(0,self.simheight-5,self.simwidth-5,
                                 self.simheight, fill="grey", outline="grey")
    self.canvas.create_rectangle(5,0,self.simwidth,5, fill="grey",
                                 outline="grey")
    self.canvas.create_rectangle(self.simwidth-5, 5, self.simwidth, 
                                 self.simheight, fill = "grey", outline="grey")
    self.lines = []
    for wall in self.world.walls:
      start, end = wall
      icx, icy = self.PtoC(start)
      fcx, fcy = self.PtoC(end)
      self.lines.append(self.canvas.create_line(icx, icy, fcx, fcy, fill = "black", width = 2))
    for obstacle in self.world.moving_obstacles:
      obstacle = Obstacle(obstacle)
      self.obstacles.append(obstacle)
    self.drawObstacles(0)

  def drawObstacles(self, dt):
    newlines = []
    for obstacle in self.obstacles:
      obstacle.step(dt)
      for wall in obstacle.current_walls():
        newlines.append(map(self.PtoC, wall))
    def tk_update_obstacles():
      for item in self.canvas.find_withtag("obstacle"):
        self.canvas.delete(item)
      for line in newlines:
        apply(self.canvas.create_line, line[0]+line[1], {'fill':'brown', 'width':2, 'tags':'obstacle'})
    form.main.tk_enqueue(tk_update_obstacles)

  def map_robot_point(self, robot_point):
    absx, absy, absth = self.abspose.get()
    cx, cy = self.PtoC((absx, absy))
    x,y = robot_point
    r = (x**2+y**2)**(0.5)
    th = atan2(x,y)+absth
    return (cx+self.pxtocx*r*cos(th), cy+self.pytocy*r*sin(th))
         
  # Draw the Pioneer robot at its current position
  def drawRobot(self):
    points = map(self.map_robot_point, ROBOT_POINTS)
    def tk_update_robot():
      for item in self.canvas.find_withtag("robot"):
        self.canvas.delete(item)
      if self.stalled.get():
        colorstr = "red"
      else:
        colorstr = "black"
      self.canvas.create_polygon( \
          points[0][0], points[0][1],  \
          points[1][0], points[1][1],  \
          points[2][0], points[2][1],  \
          points[3][0], points[3][1],  \
          points[4][0], points[4][1],  \
          points[5][0], points[5][1],  \
          points[6][0], points[6][1],  \
          points[7][0], points[7][1],  \
          points[8][0], points[8][1],  \
          points[9][0], points[9][1],  \
          points[10][0], points[10][1],\
          points[11][0], points[11][1],\
          points[12][0], points[12][1],\
          tags="robot", fill=colorstr)
      self.canvas.tag_raise("robot")
    form.main.tk_enqueue(tk_update_robot)
    #if os.name == "posix": form.main.tk_enqueue(self.canvas.update_idletasks)
    absx, absy, absth = self.abspose.get()
    sonarlines = []
    for entry in SONAR_INFO:
      r = (entry[0]**2+entry[1]**2)**(0.5)
      th = atan2(entry[1], entry[0]) + absth - pi/2
      xa, ya = (absx+r*cos(th), absy+r*sin(th))
      xb, yb = xa+MAX_SONAR_DIST*cos(absth+entry[2]), ya+MAX_SONAR_DIST*sin(absth+entry[2])
      sonarlines.append(((xa, ya),(xb,yb)))
    self.fullsonarlines = sonarlines

  def reportSonars(self):
    return self.oldsonars.get()

  def setMaxEffectiveSonarDistance(self, d):
    global MAX_EFFECTIVE_SONAR_DIST
    MAX_EFFECTIVE_SONAR_DIST = d

  def enableAccelerationCap(self, enable):
    global CAP_ACC
    CAP_ACC = enable

  def setMaxVelocities(self, maxTransVel, maxRotVel):
    global MAX_TRANS, MAX_ROT
    MAX_TRANS = maxTransVel
    MAX_ROT = maxRotVel

  def enableTeleportation(self, perStepProbability, poseDist):
    global TELEPORT_PROB, TELEPORT_DIST
    TELEPORT_PROB = perStepProbability
    TELEPORT_DIST = poseDist
    print 'Enabling teleportation with probability', TELEPORT_PROB

  # Set translational and rotational velocities
  def motorOutput(self, v, w):
    if TELEPORT_PROB > 0:
      if random() < TELEPORT_PROB:
        newPose = TELEPORT_DIST.draw()
        print 'Teleporting to', newPose
        self.abspose.set(newPose)
    if CAP_ACC:
      (oldTrans, oldRot) = (self.v.get(), self.w.get())
      transDiff = clip(v-oldTrans,-TRANS_ACC, TRANS_ACC)
      rotDiff = clip(w-oldRot,-ROT_ACC,ROT_ACC)
      self.v.set(clip(oldTrans+transDiff, -MAX_TRANS, MAX_TRANS))
      self.w.set(clip(oldRot+rotDiff, -MAX_ROT, MAX_ROT))
    else:
      self.v.set(clip(v, -MAX_TRANS, MAX_TRANS))
      self.w.set(clip(w, -MAX_ROT, MAX_ROT))
  
  def analogOutput(self, val):
    pass

  # Support for accurate prediction of motion even when the brain is slow
  def discreteMotorOutput(self, v, w, dt):
    self.motorOutput(v,w)
    self.onestep(dt)
    self.motorOutput(0,0)

  def cmdSay(self, freq, dur):
    pass

  # Calculate new sonar values
  def updateSonars(self):
    sonars = []
    sonars_to_draw = []
    for sonar in self.fullsonarlines:
      mindist = MAX_SONAR_DIST
      lastint = False
      anglegood = False
      walls = []
      walls+= self.world.walls 
      for obstacle in self.obstacles:
        walls+=obstacle.current_walls()
      for wall in walls:
        i = intersection(sonar, wall)
        if i:
          ix, iy = i
          sx, sy = sonar[0]
          dist = ((ix-sx)**2+(iy-sy)**2)**(0.5) 
          if dist < mindist:
            anglegood = sonarangleok(abs(pi/2-angle(sonar, wall)))
            mindist = dist
            lastint = i
      if DRAW_SONARS:
        icx, icy = self.PtoC(sonar[0])
        if lastint: 
          fcx, fcy = self.PtoC(lastint)
        else:	
          fcx, fcy = self.PtoC(sonar[1])
        icx, icy, fcx, fcy = int(icx), int(icy), int(fcx), int(fcy)
        if anglegood and mindist < MAX_EFFECTIVE_SONAR_DIST:
          sonars_to_draw.append((icx, icy, fcx, fcy, SONAR_GOT_RESPONSE_COLOR))
        else:
          sonars_to_draw.append((icx, icy, fcx, fcy, SONAR_NO_RESPONSE_COLOR))

      if anglegood and mindist < MAX_EFFECTIVE_SONAR_DIST:
        val = gauss(mindist, SONAR_VARIANCE(mindist))
        sonars.append(val)
      else:
        val = MAX_SONAR_DIST
        sonars.append(val)

    if DRAW_SONARS:
      def tk_update_sonars():
        for item in self.canvas.find_withtag("sonarlines"):
          self.canvas.delete(item)
        for sonar_to_draw in sonars_to_draw:
          icx, icy, fcx, fcy, sonar_color = sonar_to_draw
          self.canvas.create_line(icx, icy, fcx, fcy, fill = sonar_color, tag = "sonarlines")
      form.main.tk_enqueue(tk_update_sonars)
    self.oldsonars.set(self.storedsonars.get())
    self.storedsonars.set(sonars)

  # First part of dealing with collisions cleanishly
  def cache(self):
    try: 
      self.lastlastpos = self.lastpos 
    except AttributeError:
      pass
    self.lastpos = self.odpose.get()+self.abspose.get()

  # Second part of dealing with collisions cleanishly
  def uncache(self):
    odx, ody, odth, absx, absy, absth = self.lastpos
    self.odpose.set((odx, ody, odth))
    self.abspose.set((absx, absy, absth))
    try:
      if self.collision():
        odx, ody, odth, absx, absy, absth = self.lastlastpos
        self.odpose.set((odx, ody, odth))
        self.abspose.set((absx, absy, absth))
    except AttributeError:
      pass

  # One step of the whole running simulation
  def onestep(self, dt):
    self.cache()
    self.move(dt)
    self.stalled.set(False)
    if self.collision():
      self.uncache()
      self.stalled.set(True)
    self.drawObstacles(dt)
    self.drawRobot()
    self.updateSonars() 

  def perp(self, ((x0, y0),(x1, y1))):
    x,y = self.abspose.get()[:2]
    try:
      a = tan(-(x1-x0)/(y1-y0))
    except ZeroDivisionError:
      a = pi/2
    dx = ROBOT_RADIUS*cos(a)
    dy = ROBOT_RADIUS*sin(a)
    return ((x-dx,y-dy),(x+dx,y+dy))

  def collision(self):
    for wall in self.world.walls:
      if intersection(wall, self.perp(wall)):
        return True
    return False
  
  # Move the robot properly based on how time passed
  def move(self, dt):
    v = self.v.get()
    w = self.w.get()
    odx, ody, odth = self.odpose.get()
    absx, absy, absth = self.abspose.get()
    thstep=dt*w
    try:
      #integrate the path
      absxstep=v*(sin(absth+thstep)-sin(absth))/w
      odxstep=v*(sin(odth+thstep)-sin(odth))/w
      absystep=v*(cos(absth)-cos(absth+thstep))/w
      odystep=v*(cos(odth)-cos(odth+thstep))/w
    except ZeroDivisionError:
      #deal with a zero case that I dropped deriving the above expression
      absxstep = dt*cos(absth+thstep/2)*v	
      odxstep = dt*cos(odth+thstep/2)*v	
      absystep = dt*sin(absth+thstep/2)*v	
      odystep = dt*sin(odth+thstep/2)*v	
    absx+=absxstep
    absy+=absystep 
    absth+=thstep
    absth%=2*pi
    odx+=odxstep
    ody+=odystep
    odth+=thstep
    odth%=2*pi
    form.main.tk_enqueue(lambda: self.odometrytext.set("POSE - X: " + `odx`[:7] + ", Y: " + `ody`[:7] + ", TH: " + `odth`[:7]))
    self.odpose.set((odx, ody, odth))
    self.abspose.set((absx, absy, absth))

  # Respond to a left click down
  def left_click_down(self, event):
    for item in self.canvas.find_withtag("robot"):
      xn, yn, xx, yx = self.canvas.bbox(item)
      if event.x <= xx and event.x >= xn and event.y <= yx and event.y >= yn:
        self.inrobot = True
        break  

  # Respond to a left click drag
  def left_click_moved(self, event):
    if self.inrobot:
      x, y = self.CtoP((event.x,event.y))
      self.abspose.set((x, y, self.abspose.get()[2]))
      if DRAG_UPDATES_ROBOT_ODOMETRY: 
        self.odpose.set((x, y, self.odpose.get()[2]))
      self.drawRobot()
      self.updateSonars()

  # Respond to releasing left mouse button
  def left_click_up(self, event):
    self.left_click_moved(event)
    self.inrobot = False

  # Respond to a right click down
  def right_click_down(self, event):
    for item in self.canvas.find_withtag("robot"):
      xn, yn, xx, yx = self.canvas.bbox(item)
      if event.x <= xx and event.x >= xn and event.y <= yx and event.y >= yn: 
        self.inrobot = True
        self.lasteventx, self.lasteventy = event.x, event.y 

  # Respond to releasing right mouse button
  def right_click_up(self, event):
    self.inrobot = False

  # Respond to a right click drag
  def right_click_moved(self, event):
    if self.inrobot:
      dx, dy = event.x-self.lasteventx, event.y-self.lasteventy
      absx, absy, absth = self.abspose.get()
      self.abspose.set((absx, absy, absth+(dy+dx)*DRAG_ROT_SPEED))
      if DRAG_UPDATES_ROBOT_ODOMETRY: 
        odx, ody, odth = self.odpose.get()
        self.odpose.set((odx, ody, odth+(dy+dx)*DRAG_ROT_SPEED))
      self.drawRobot()
      self.updateSonars()
      self.lasteventx, self.lasteventy = event.x, event.y 


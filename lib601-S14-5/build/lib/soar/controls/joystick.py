############################soar/controls/joystick.py############################
# soar3.0
#  / controls/joystick.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
from Tkinter import *

from form.common import skip

#!NOTE
# Original inspiration for this from Pyrobot project: http://pyrobotics.org/

dim = (10, 10, 210, 210)
center = ((dim[2] + dim[0])/2, (dim[3] + dim[1])/2)
radius = ((dim[2] - dim[0])/2)**2
def inside(x,y):
  return (center[0]-x)**2+(center[1]-y)**2 < radius 
def transrot(x,y):
  return ((center[1]-y)/float(center[1]-dim[1]), (center[0]-x)/float(center[0]-dim[0]))	

class Joystick(object):
  def __init__(self):
    self.v = 0
    self.w = 0
    self.parent = app.soar
    self.win = app.mainframe.addFrame('Joystick')
    self.canvas = Canvas(self.win, width=220, height=220, bg = "white")
    self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
    self.canvas.bind("<Button-1>", self.respond)
    self.canvas.bind("<B1-Motion>", self.respond)
    self.canvas.pack(side=TOP)
    self.canvas.create_oval(dim, fill = 'white')
    self.canvas.create_oval(105, 105, 115, 115, fill='black')
    self.setup = skip
    self.resetmo = False

  def step(self, dt):
    self.parent.namespace["motorOutput"](self.v,self.w)

  def clear(self):
    for item in self.canvas.find_withtag("line"):
      self.canvas.delete(item)
  
  def canvas_clicked_up(self, event):
    self.v, self.w = 0,0
    self.clear()

  def respond(self, event):
    self.clear()  
    if inside(event.x, event.y):
      self.v, self.w = transrot(event.x, event.y)
      self.canvas.create_line(110, 110, 110, event.y, fill = "red", width = 2, arrow = LAST, tags = "line")
      self.canvas.create_line(110, 110, event.x, 110, fill = "blue", width = 2, arrow = LAST, tags = "line")

  def destroy(self):
    app.mainframe.removeFrame('Joystick')

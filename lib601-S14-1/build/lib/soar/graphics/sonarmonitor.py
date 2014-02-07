import Tkinter
import form.main
import math
import soar.util as util
from soar.util import Pose

sonarPoses = [util.Pose(0.08, 0.134, math.pi/2),
              util.Pose(0.122, 0.118, 5*math.pi/18),
              util.Pose(0.156, 0.077, math.pi/6),
              util.Pose(0.174, 0.0266, math.pi/18),
              util.Pose(0.174, -0.0266, -math.pi/18),
              util.Pose(0.156, -0.077, -math.pi/6),
              util.Pose(0.122, -0.118, -5*math.pi/18),
              util.Pose(0.08, -0.134, -math.pi/2)]
"""Positions and orientations of sonar sensors with respect to the
              center of the robot.""" 


class SonarMonitor():
    def __init__(self, robotPoints, geom=None):
        self.windowHeight = 220
        self.windowWidth = 350
        self.robotScale = 100
        self.robotPos = (self.windowWidth/2.0, self.windowHeight*5.0/6.0)
        def mapPoints((x,y)):
            return (x*self.robotScale + self.robotPos[0],
                    -y*self.robotScale + self.robotPos[1])
        self.points = map(mapPoints, robotPoints)
#        self.robotPose = Pose(self.windowWidth/2.0, self.windowWidth/2.0,
#                              math.pi)
        self.robotPose = Pose(0.0, 0.0, -math.pi/2.0)
        self.maxReading = 1.5
        self.window = None
        # just pay attention to the position part (not the size, since
        # the canvas is a fixed size)
        self.geom = None
        if geom:
            self.geom = geom[geom.find('+'):]

    def isOn(self):
        return self.window is not None

    def openWindow(self):
        # already open, don't open again
        if self.window:
            return
        self.window = Tkinter.Toplevel()
        self.window.wm_title("Sonar Monitor")
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
        if self.geom:
            self.window.geometry(self.geom)
        self.canvas = Tkinter.Canvas(self.window,
                                     width = self.windowWidth,
                                     height = self.windowHeight, 
                                     background="white")
        self.canvas.pack()
        self.makeCanvasObjects()

    def closeWindow(self):
        if self.window:
            app.soar.sonarmon_geom = self.window.geometry()
            self.geom = self.window.geometry()
            self.window.destroy()
            self.window = None

    def reopenWindow(self):
        if self.window:
            self.geom = self.window.geometry()
            self.closeWindow()
        self.openWindow()
        if self.geom:
            self.window.geometry(self.geom)

    def makeCanvasObjects(self):
        points = self.points
        self.robotPoly = self.canvas.create_polygon( \
            points[0][0], points[0][1],
            points[1][0], points[1][1],
            points[2][0], points[2][1],
            points[3][0], points[3][1],
            points[4][0], points[4][1],
            points[5][0], points[5][1],
            points[6][0], points[6][1],
            points[7][0], points[7][1],
            points[8][0], points[8][1],
            points[9][0], points[9][1],
            points[10][0], points[10][1],
            points[11][0], points[11][1],
            points[12][0], points[12][1],
            tags="robot", fill="black")
        self.lines = []
        for sp in sonarPoses:
            self.lines.append(self.canvas.create_line(sp.x+self.robotPos[0],
                                                      sp.y+self.robotPos[1],
                                                      sp.x+self.robotPos[0],
                                                      sp.y+self.robotPos[1],
                                                      width = 3,
                                                      fill = "black",
                                                      tag = "sonarlines"))

    def raiseRobot(self):
        if self.window:
            self.canvas.tag_raise("robot")

    def update(self, sonarReadings):
        if not self.window:
            return
        items_to_move = []
        items_to_color = []
        for i in range(len(sonarReadings)):
            reading = sonarReadings[i]
            color = "black" if reading < self.maxReading else "red"
            reading = min(sonarReadings[i], self.maxReading)
            sonarPose = sonarPoses[i]
            hit = self.sonarHit(reading, sonarPose, self.robotPose)
            items_to_color.append((self.lines[i], color))
            items_to_move.append((self.lines[i],
                                  sonarPose.x+self.robotPos[0],
                                  sonarPose.y+self.robotPos[1],
                                  -self.robotScale*hit.x+self.robotPos[0],
                                  self.robotScale*hit.y+self.robotPos[1]))
        def move_items():
            for (item, color) in items_to_color:
                self.canvas.itemconfig(item, fill=color)
            for (item, x0, y0, x1, y1) in items_to_move:
                self.canvas.coords(item, x0, y0, x1, y1)
            self.canvas.tag_raise("robot")
        form.main.tk_enqueue(move_items)
            
    def sonarHit(self, distance, sonarPose, robotPose):
        """
        @param distance: distance along ray that the sonar hit something
        @param sonarPose: C{util.Pose} of the sonar on the robot
        @param robotPose: C{util.Pose} of the robot in the global frame
        @return: C{util.Point} representing position of the sonar hit in the
        global frame.  
        """
        return robotPose.transformPoint(sonarPose.transformPoint(\
                util.Point(distance,0)))

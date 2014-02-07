import Tkinter
import form.main
from soar.io import io
import sys
from scopeConfig import ScopeConfigWindow

class Probe():
    def __init__(self, name, func, functext, numelems, samplesPerElem, initVal):
        self.name = name
        self.func = func
        self.functext = functext
        self.resize(numelems, samplesPerElem, initVal)
        # keep track of min and max for auto scaling
        self.minv, self.maxv = initVal, None

    def extremes(self):
        if self.maxv:
            return self.minv, self.maxv
        else:
            return self.minv, self.minv

    def step(self, inp):
        sample = self.func(inp)
        self.elemSum += sample
        self.elemSamples += 1
        if self.elemSamples == self.samplesPerElem:
            elemVal = self.elemSum/self.elemSamples
            self.data[self.bufidx] = elemVal
            self.bufidx = (self.bufidx+1)%(len(self.data))
            self.elemSum, self.elemSamples = 0,0
            self.minv = elemVal if self.minv==None else min(self.minv, elemVal)
            self.maxv = elemVal if self.maxv==None else max(self.maxv, elemVal)

    def resize(self, numelems, samplesPerElem, initVal=0):
        self.elemSum = 0
        self.elemSamples = 0
        self.samplesPerElem = samplesPerElem
        self.data = [initVal]*numelems
        self.bufidx = 0

    def dataPt(self, idx):
        return self.data[self.bufidx-idx-1]

class Oscilloscope():
    def __init__(self, geom=None):
        self.window = None
        self.configWindow = None
        self.canvasInited = False
        # add more lines by adding colors
        self.colors = ["blue", "green", "red", "cyan", "magenta"]
        self.probes = []
        self.numActiveProbes = 0
        # range for the data (xaxis always starts at zero)
        self.maxNumelems = 60
        self.setTimeAxis(100)
        self.yrange = (None, None)
        self.opts = {'Title':'Untitled',
                     'X Label':'Cycles Past (Sample Period='+
                     str(self.samplesPerElem)+')',
                     'Y Label':'Value',
                     'X Scale':self.xrange,
                     'Y Scale':'auto'}
        self.ymin, self.ymax = None, None
        self.ybounds = None, None
        self.ptRadius = 2
        self.legend = True
        # just pay attention to the position part, since the canvas is a 
        # fixed size
        self.geom = None
        if geom:
            self.geom = geom[geom.find('+'):]

    def openWindow(self):
        # already open; don't open again
        if self.window:
            return
        self.window = Tkinter.Toplevel()
        self.window.wm_title("Soar Oscilloscope")
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
        if self.geom:
            self.window.geometry(self.geom)
        self.canvWidth, self.canvHeight = 600, 400
        self.canvas = Tkinter.Canvas(self.window,
                                     width = self.canvWidth, 
                                     height = self.canvHeight,
                                     background = "white")
        self.canvas.pack()
        self.button = Tkinter.Button(self.window, 
                                     text="Configure Oscilloscope",
                                     command = self.configure)
        self.button.pack()
        self.makeCanvasObjects()
        self.canvas.wait_visibility()
        self.setStaticObjects()

    def configure(self):
        if self.configWindow:
            self.configWindow.closeWindow()
        self.configWindow = ScopeConfigWindow(self)

    def doneConfiguring(self):
        self.configWindow = None
        self.setStaticObjects()
        
    def deleteScalingCanvasObjects(self):
        def deleteTask():
            for i in range(self.lines):
                for j in range(self.lines[i]):
                    self.canvas.delete(self.lines[i][j])
                for j in range(self.points[i]):
                    self.canvas.delete(self.points[i][j])
        form.main.tk_enqueue(deleteTask)

    def makeCanvasObjects(self):
        if not self.window:
            return
        if self.canvasInited:
            self.deleteScalingCanvasObjects()
        # number of text objects doesn't change with rescale
        else:
            self.canvasInited = True
            # clear rect comes first so everything else shows up
            #self.clearRect = self.canvas.create_rectangle(0,0,
            #                                              self.canvWidth,
            #                                              self.canvHeight,
            #                                              fill="white")
            # outline rect needs to come first (don't draw over pts)
            self.outlineRect = self.canvas.create_rectangle(0,0,1,1,
                                                            fill="white")
            self.xminText = self.canvas.create_text(0, 0, text="")
            self.xmaxText = self.canvas.create_text(0, 0, text="")
            self.yminText = self.canvas.create_text(0, 0, text="")
            self.ymaxText = self.canvas.create_text(0, 0, text="")
            self.yLabelText = self.canvas.create_text(0, 0, text="")
            self.xLabelText = self.canvas.create_text(0, 0, text="")
            self.titleText = self.canvas.create_text(0, 0, text="")
            if self.legend:
                self.legendLines = []
                self.legendText = []
                self.legendPoints = []
                for color in self.colors:
                    l = self.canvas.create_line(-2, -1, -1, -1,
                                                 fill=color, smooth=1, width=3)
                    self.legendLines.append(l)
                    t = self.canvas.create_text(0, 0, text="")
                    self.legendText.append(t)
                    p = self.canvas.create_oval(-2, -2, -1, -1,
                                                 fill=color, outline=color)
                    self.legendPoints.append(p)

        self.lines = []
        self.points = []
        rad = self.ptRadius
        # make all the objects off the canvas
        x0,y0 = -2, -1
        x1,y1 = -1, -1
        for i in range(len(self.colors)):
            color = self.colors[i]
            self.lines.append([])
            self.points.append([])
            for j in range(self.numelems):
                if j < self.numelems-1:
                    l = self.canvas.create_line(x0,y0,x1,y1, fill=color,
                                                smooth=1, width=3)
                    self.lines[i].append(l)
                p = self.canvas.create_oval(x1-rad, y1-rad, x1+rad, x1+rad,
                                            fill=color, outline=color)
                self.points[i].append(p)

    def setCanvasText(self, item, x, y, **opts):
        self.canvas.coords(item, x, y)
        self.canvas.itemconfig(item, opts)

    def closeWindow(self):
        if self.window:
            self.geom = self.window.geometry()
            app.soar.scope_geom = self.geom
            self.window.destroy()
            self.window = None
        if self.configWindow:
            self.configWindow.closeWindow()
            self.configWindow = None

    def setTimeAxis(self, desiredRange=None):
        if not desiredRange:
            desiredRange = self.opts['X Scale']
        if desiredRange < 1:
            return
        self.numelems = desiredRange + 1
        self.samplesPerElem = 1
        while self.numelems > self.maxNumelems:
            self.samplesPerElem += 1
            self.numelems = int((desiredRange+1)/self.samplesPerElem)
        # TODO: put appropriate label on graph
        self.xrange = desiredRange
        for p in self.probes:
            if p:
                p.resize(self.numelems, self.samplesPerElem)
        self.makeCanvasObjects()
        self.setStaticObjects()

    def clearProbes(self):
        self.probes = []
        self.ymin, self.ymax = None, None

    def makeFunc(self, func, i=None):
        if func.func_code.co_argcount == 0:
            if i is not None: return lambda inp: func()[i]
            else: return lambda inp: func()
        elif func.func_code.co_argcount == 1:
            if i is not None: return lambda inp: func(inp)[i]
            else: return lambda inp: func(inp)
        else:
            sys.stderr.write("Dynamic plot function takes too many arguments")
            return lambda inp: 0.0

    def addProbeFunction(self, names, func, functext=None, initVal=0):
        numavail = len(self.colors) - len(self.probes)
        if numavail == 0:
            sys.stderr.write("All available probes are in use.  Signal will not be plotted")
            return
        if type(names) == list or type(names) == tuple:
            numprobes = min(numavail, len(names))
            if numprobes < len(names):
                sys.stderr.write("Not enough available probes for all signals.  Only "+str(numprobes)+" signals will be plotted.")
            for i in range(numprobes):
                text = functext if functext else str(func)
                text = text+"["+str(i)+"]"
                self.addProbe(names[i], self.makeFunc(func, i), text, initVal)
        else:
            self.addProbe(names, self.makeFunc(func), 
                          functext if functext else str(func), initVal)
        self.setStaticObjects()

    def addProbe(self, name, functext, initVal=0):
        func = lambda: eval(functext)
        self.addProbeFunction(name, func, functext, initVal)

    def setProbeText(self, probeidx, name, functext):
        func = lambda: eval(functext)
        self.setProbe(probeidx, name, func, functext)

    def addProbe(self, name, func, functext, initVal=0):
        self.probes.append(Probe(name, func, functext, self.numelems,
                                 self.samplesPerElem, initVal))
        self.setStaticObjects()
                                      
    def setExtremes(self, (minv, maxv)):
        self.ymin = minv if self.ymin==None else min(self.ymin, minv)
        self.ymax = maxv if self.ymax==None else max(self.ymax, maxv)

    def getDimensions(self):
        c_width, c_height = self.canvWidth, self.canvHeight
        # don't call these functions of the canvas directly, because
        # on redhat, it causes a collision with the jobs on the tk_queue
        #c_height = self.canvas.winfo_height()
        #c_width = self.canvas.winfo_width()
        x_lgd = 100 if self.legend else 0
        x_gapl, x_gapr, y_gap = 40, 10+x_lgd, 20
        x_size, y_size = c_width-x_gapr-x_gapl, c_height-2*y_gap
        return (c_height, c_width, x_lgd, x_gapl, x_gapr, y_gap,
                x_size, y_size)

    def setStaticObjects(self):
        if not self.window:
            return
        dims = self.getDimensions()
        (c_height, c_width, x_lgd, x_gapl, x_gapr, y_gap,
         x_size, y_size) = dims
        text_funcs = []
        items_to_move = []
        ## clear the canvas without deleting the objects
        #self.canvas.coords(self.clearRect, 0, 0, c_width, c_height)
        ## box for graph
        items_to_move.append((self.outlineRect, x_gapl, y_gap,
                              c_width-x_gapr, c_height-y_gap))
        # y scale labels (only static if we're not auto-scaling
        if self.opts['Y Scale'] != 'auto':
            smin, smax = self.opts['Y Scale']
            def f():
                self.setCanvasText(self.yminText, x_gapl/2, c_height-y_gap, 
                                   text=round(smin,3))
                self.setCanvasText(self.ymaxText, x_gapl/2, y_gap, 
                                   text=round(smax,3))
            text_funcs.append(f)
        def f():
            # x scale labels
            self.setCanvasText(self.xminText, x_gapl, c_height-y_gap/2, 
                               text=self.xrange)
            self.setCanvasText(self.xmaxText, c_width-x_gapr, c_height-y_gap/2, 
                               text="0")
            # axes labels
            self.setCanvasText(self.yLabelText, x_gapl/2, c_height/2, 
                               text=self.opts['Y Label'], width=40)
            self.setCanvasText(self.xLabelText, (c_width-x_gapr)/2, 
                               c_height-y_gap/2, text=self.opts['X Label'])
            # graph title
            self.setCanvasText(self.titleText, (c_width-x_gapr)/2, 10, 
                               text=self.opts['Title'])
        text_funcs.append(f)
        if self.legend:
            y_lgd = 2*y_gap
            lgd_line_width = 11
            rad = self.ptRadius
            for i in range(len(self.probes)):
                p = self.probes[i]
                if not p: continue
                color = self.colors[i]
                x,y = c_width-x_lgd+lgd_line_width/2-1, y_lgd
                items_to_move.append((self.legendLines[i],
                                      c_width-x_lgd, y_lgd,
                                      c_width-x_lgd+lgd_line_width, y_lgd))
                items_to_move.append((self.legendPoints[i],
                                      x-rad, y-rad, x+rad, y+rad))
                labelHeight = y_lgd
                def f():
                    self.setCanvasText(self.legendText[i],
                                       c_width-x_lgd+lgd_line_width+2, 
                                       labelHeight, text=p.name,
                                       #width=x_lgd-lgd_line_width,
                                       anchor='w')
                text_funcs.append(f)
                y_lgd += 20
        def doCanvasTasks():
            for f in text_funcs:
                f()
            for (item, x0, y0, x1, y1) in items_to_move:
                self.canvas.coords(item, x0, y0, x1, y1)
        form.main.tk_enqueue(doCanvasTasks)


    def step(self):
        # we *could* store the data anyway, but I'm inclined to think that's
        # a waste of resources.
        if not self.window:
            return
        # also, if we have no probes, don't plot anything
        if len(self.probes) == 0:
            return
        inp = io.SensorInput()
        for p in self.probes:
            if p:
                p.step(inp)
                self.setExtremes(p.extremes())
        self.draw()

    def draw(self):
        dims = self.getDimensions()
        (c_height, c_width, x_lgd, x_gapl, x_gapr, y_gap,
         x_size, y_size) = dims
        text_funcs = []
        items_to_move = []

        if self.opts['Y Scale'] == 'auto':
            smin, smax = self.ymin, self.ymax
            oldmin, oldmax = self.ybounds
            if oldmin != smin or oldmax != smax:
                def f():
                    # update the labels in case they've changed (not very smart)
                    self.setCanvasText(self.yminText, x_gapl/2, c_height-y_gap, 
                                       text=round(smin,3))
                    self.setCanvasText(self.ymaxText, x_gapl/2, y_gap, 
                                       text=round(smax,3))
                text_funcs.append(f)
            self.ybounds = (smin, smax)
        else:
            smin, smax = self.opts['Y Scale']
        srange = smax-smin
        if srange == 0.0:
            srange = 0.1

        y_height = float(y_size) / float(srange)
        x_width = float(x_size)/ float(self.numelems-1)

        rad = self.ptRadius
        for i in range(len(self.probes)):
            p = self.probes[i]
            if not p: continue
            x0, y0 = None, None
            color = self.colors[i]
            for x in range(self.numelems):
                y = p.dataPt(x)
                x1 = (self.numelems-1-x) * x_width + x_gapl
                y1 = c_height - y_gap - ((y-smin) * y_height)
                if x0:
                    items_to_move.append((self.lines[i][x-1],
                                          x0, y0, x1, y1))
                items_to_move.append((self.points[i][x], 
                                      x1-rad, y1-rad, x1+rad, y1+rad))
                x0 = x1
                y0 = y1
        def doCanvasTasks():
            for f in text_funcs:
                f()
            for (item, x0, y0, x1, y1) in items_to_move:
                self.canvas.coords(item, x0, y0, x1, y1)
        form.main.tk_enqueue(doCanvasTasks)
        


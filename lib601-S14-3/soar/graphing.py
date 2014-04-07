################################soar/graphing.py#################################
# soar3.0
#  / graphing.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
import Tkinter
from types import NoneType
import os
import platform
from form.common import clip
import form.main
import form.widgets as widgets
import sys
################################################################################

#SPECIAL VALUES
GARBAGE = "foo"

#valid graphing modes
CONTINUOUS = 0 #connect the points, approximating a simple curve
DISCRETE_TIME = 1 #discrete time mode, with the lines and ovals
SLOPE_FIELD = 2 #graph little slope lines accross the visible canvas
SCALAR_FIELD = 3 #graph a colormap representing a scalar field accross the visible canvas
CONTINUOUS_SET = 7
#other graphing objects
LABELS = 4
AXES = 5
RK = 6
RK4_COLOR = "purple"

#other GraphCanvas constants
DEFAULT_STEP = -1
DOTTED_LINE_SPACING = 6
DEFAULT_SLOPE_SPACING = 12
X_LABEL_WIDTH = 35
Y_LABEL_HEIGHT = 12
if os.name == 'nt':
    LABEL_FONT = ("Courier New", 6)
elif os.name == 'posix':
    LABEL_FONT = ("Courier New", 10)

#Color constants
ALL = -1
DEFAULT_COLORMAPS =  [
lambda w, g: Color(w, ["red", "yellow", "green", "cyan", "blue", "purple", "red"], g), #rainbow
lambda w, g: Color(w, ["white", "black"], g), #whiteblack
lambda w, g: Color(w, ["blue", "red"], g) #bluered
]

#return a number in a string  (guaranteed max length of 4 + length of appropriate power of 10) 
#representation of its value in scientific notation
def scinot(num):
    string=`num`
    power = 0
    i = 0
    j = string[i]
    str = ''
    while not j =='.' and i < len(string):
        j = string[i]
        str+=j
        power+=1
        i+=1
    i-=1
    if i < 5:
        str = string[:5]
    if i >= 5 and power > 0:
        str= string[:4] + 'e' + `power`
    return str

#call apply() on every possible composition of one element from each list
def argFor(vec, apply, current = []):
    if len(vec) == 0:
        apply(current)
    else:
        for i in vec[0]:
            next = current + [i]
            argFor(vec[1:], apply, next)

class GraphingWindow(Tkinter.Toplevel):
        
    def __init__(self, width, height, xmin, xmax, ymin, ymax, title):
        Tkinter.Toplevel.__init__(self, form.main.tk)
	self.wm_title(title)
        # Can't call this self.title, that overwrites something important
        self.window_title = title
        self.choice = Tkinter.IntVar(0)
        self.initToolbarTop()
	self.canvas = GraphCanvas(self, width, height, xmin, xmax, ymin, ymax)
	self.canvas.bind("<ButtonRelease-1>", self.updateBoxes)
        self.canvas.pack()
        self.updateBoxes()
        self.close = self.destroy

    def helpIdle(self):
	self.protocol("WM_DELETE_WINDOW", form.main.tk.quit)
        form.main.tk.mainloop()
        form.main.tk_recycle()
	GraphingWindow.__init__(self,self.canvas.width, self.canvas.height, self.canvas.xmin, self.canvas.xmax, self.canvas.ymin, self.canvas.ymax, self.window_title)

    def graphContinuous(self, f, color="black"):
	self.canvas.graphFunc(f, CONTINUOUS, color)
    def graphContinuousSet(self, xset, yset, color="black"):
	self.canvas.graphFunc((xset, yset), CONTINUOUS_SET, color)
    def graphDiscrete(self, f, color="black"):
	self.canvas.graphFunc(f, DISCRETE_TIME, color)
    def graphSlopefield(self, f, color="black"):
	self.canvas.graphFunc(f, SLOPE_FIELD, color)
    def graphScalarfield(self, f):
	self.canvas.graphFunc(f, SCALAR_FIELD, "foo")     

    def clear(self):
   	self.canvas.functions = []
	self.canvas.draw()    

    def postscript(self, filename):
        self.canvas.update()
	self.canvas.postscript(file = filename)

    def saveByExtension(self, filename, ext):
        self.postscript(filename+".ps")
        if ext is not ".ps":
            try:
                import Image
                print "reading from:", filename+".ps"
                print "writing to:", filename+ext
                im = Image.open(filename+".ps")
                im.save(filename+ext)
#                os.system("rm "+filename+".ps")
            except:
                sys.stderr.write("Python Imaging Library not installed.  "+
                                 "Trying convert ...\n")
                ret = os.system("convert "+filename+".ps "+filename+ext)
                if ret == 0:
                    sys.stdout.write("Done writing file "+filename+ext)
#                    os.system("rm "+filename+".ps")
                else:
                    sys.stderr.write("Error using convert to convert "+
                                     "from postscript: "+filename+".ps")

    def pdf(self, filename):
	self.postscript(filename+".ps")
	ret = os.system("ps2pdf "+filename+".ps "+filename+".pdf")
	converted = (ret == 0)
	if not converted:
	    ret = os.system("convert "+filename+".ps "+filename+".pdf")
	    converted = (ret == 0)
	if converted:
	    sys.stdout.write("Done writing file "+filename+".pdf\n")
	    os.system("rm "+filename+".ps")
	else:
	    sys.stderr.write("Error converting file from postscript: "+
			     filename+".ps")

    def save(self):
	filename = widgets.asksaveasfilename(title = "Choose a Filename...",
					     initialdir = self.ps_dir_default)
	if (len(filename) > 0):
	    self.ps_dir_default = filename[0:filename.rfind("/")]
	    dotidx = filename.rfind(".")
	    slashidx = filename.rfind("/")
	    if (dotidx>slashidx):
		filename = filename[0:dotidx]
                self.pdf(filename)
#                self.saveByExtension(filename[0:dotidx], 
#                                     filename[dotidx:len(filename)])


    def updateBoxes(self, event = None):
        if not event == None:
            self.canvas.canvas_left_clicked_up(event)
        self.xmintext.set(`self.canvas.xmin`)
        self.xmaxtext.set(`self.canvas.xmax`)
        self.ymintext.set(`self.canvas.ymin`)
        self.ymaxtext.set(`self.canvas.ymax`)
        
    def initToolbarTop(self):
	self.topframe = Tkinter.Frame(self)
	frame = self.topframe
        self.xmintext = Tkinter.StringVar()
        self.xmaxtext = Tkinter.StringVar()
        self.ymintext = Tkinter.StringVar()
        self.ymaxtext = Tkinter.StringVar()
        Tkinter.Label(frame, text = "X:[").pack(side = "left")                                   
        frame.xminbox = Tkinter.Entry(frame, width = 6, textvariable = self.xmintext)
        frame.xminbox.bind("<Return>", self.resizeit)
        frame.xminbox.pack(side = "left")
        Tkinter.Label(frame, text = ",").pack(side = "left")        
        frame.xmaxbox = Tkinter.Entry(frame, width = 6, textvariable = self.xmaxtext)
        frame.xmaxbox.bind("<Return>", self.resizeit)
        frame.xmaxbox.pack(side = "left")
        Tkinter.Label(frame, text = "] Y:[").pack(side = "left")        
        frame.yminbox = Tkinter.Entry(frame, width = 6, textvariable = self.ymintext)
        frame.yminbox.bind("<Return>", self.resizeit)
        frame.yminbox.pack(side = "left")
        Tkinter.Label(frame, text = ",").pack(side = "left")        
        frame.ymaxbox = Tkinter.Entry(frame, width = 6, textvariable = self.ymaxtext)
        frame.ymaxbox.bind("<Return>", self.resizeit)
        frame.ymaxbox.pack(side = "left")
        Tkinter.Label(frame, text = "]").pack(side = "left")        
        frame.resizebutton = Tkinter.Button(frame, text = "Resize", command = lambda: self.resizeit(frame))
        frame.resizebutton.pack(side = "right")

	self.ps_dir_default = "~"
	frame.savebutton = Tkinter.Button(frame, text = "Save", command = lambda: self.save())
	frame.savebutton.pack(side="right")
	frame.pack()
    
    def getDomain(self):
        return ((self.canvas.xmin, self.canvas.xmax), (self.canvas.ymin, self.canvas.ymax))

    def setDomain(self, (xmin, xmax), (ymin,ymax)):
	self.xmintext.set(`xmin`)
	self.xmaxtext.set(`xmax`)
	self.ymintext.set(`ymin`)
	self.ymaxtext.set(`ymax`)
	self.resizeit()

    def resizeit(self, event = None):
        self.canvas.xmin = float(self.xmintext.get())
        self.canvas.xmax = float(self.xmaxtext.get())
        self.canvas.ymin = float(self.ymintext.get())
        self.canvas.ymax = float(self.ymaxtext.get())
        self.canvas.draw()


class Color:
      
    #convert r, g, b values into a valid Tk color
    def tkcolor(self, r, g, b):
        return "#%02x%02x%02x" % (int(r/256.0), int(g/256.0), int(b/256.0))
    
    #convert a valid Tk color (within the widget) into r, g, b values
    def rgbcolor(self, tkcolor):
        if not type(self.widget) == NoneType:
            return self.widget.winfo_rgb(tkcolor)
        else:
            return GARBAGE
    
    def colormap(self):
        return self.colormap
    
    def color(self, scalar = GARBAGE):
        try:
            ind = int(clip(int(len(self.colormap)*(scalar-self.func.min)/(self.func.max-self.func.min)), 0, len(self.colormap)-1))
        except AttributeError:
            return self.colormap[0]
        except TypeError:
            return self.colormap[0]
        return self.colormap[ind]
    
    def function(self, f):
        self.func = f
    
    #generate a one-dimensional color map (gradient) given 
    #an accuracy (number of different colors to map)
    # and a list of 'color nodes' to stop at along the way
    def __init__(self, widget, nodes, accuracy):
        self.widget = widget
        self.nodes = nodes
        self.accuracy = int(accuracy)
        if len(self.nodes) == 1:
            self.colormap = [nodes[0]]
        else:
            colorsPerFence = self.accuracy/len(self.nodes)
            lastnode = self.nodes[0]
            temp = [lastnode]
            for i in self.nodes[1:]:
                last = self.rgbcolor(lastnode)
                curr = self.rgbcolor(i)
                rdiff = (curr[0]-last[0])/colorsPerFence
                gdiff = (curr[1]-last[1])/colorsPerFence
                bdiff = (curr[2]-last[2])/colorsPerFence
                for k in range(colorsPerFence-1):
                    r = int(last[0]+rdiff*(1+k))
                    g = int(last[1]+gdiff*(1+k))
                    b = int(last[2]+bdiff*(1+k))
                    col = self.tkcolor(r, g, b)
                    if not col == temp[-1]:
                        temp.append(col)
                temp.append(i)
                lastnode = i
            self.colormap = temp

class Function:
    
    def __init__(self, canvas, func, color):
        self.lambd = func
        self.min = self.max = GARBAGE
        self.width = 1
        self.canvas = canvas
        self.color = color
	if self.type() == SCALAR_FIELD:
        	self.color.function(self)

    def setInput(self, input):
        self.input = input
        argFor(self.input, self.tryrange)
        
    def tryrange(self, tryarg):
    	try:
        	trial = self.eval(tryarg)
        	if self.min == GARBAGE or trial < self.min:
            		self.min = trial
        	if self.max == GARBAGE or trial > self.max:
            		self.max = trial
	except:
		print "There was a problem with the function you passed"
class Continuous(Function):
    
    def type(self):
        return CONTINUOUS
    
    def eval(self, args):
        try:
            return self.lambd(args[0])
        except:
            return GARBAGE

class Continuousset(Function):
    
    def __init__(self, canvas, func, color):
	Function.__init__(self, canvas, func, color)
	self.xset = func[0]
	self.yset = func[1]

    def type(self):
        return CONTINUOUS_SET

    def eval(self,args):
	try:
		return self.yset[self.xset.index(args[0])]
	except:
		return GARBAGE	

class Scalarfield(Function):
    
    def type(self):
        return SCALAR_FIELD
    
    def eval(self, args):
        try:
            return self.lambd(args[0], args[1])
        except:
            return GARBAGE

class Slopefield(Function):
    
    def type(self):
        return SLOPE_FIELD
    
    def eval(self, args):
        try:
            return self.lambd(args[0], args[1])
        except:
            return GARBAGE

class Discrete(Function):
    
    def type(self):
        return DISCRETE_TIME
    
    def eval(self, args):
        try:
            arg = int(args[0])
            if arg == args[0]:
                return self.lambd(arg)
            else:
                return GARBAGE
        except:
            return GARBAGE

class GraphCanvas(Tkinter.Canvas):

    def __init__(self, parent, w = 300, h = 300, xmin = 0, xmax = 100, ymin = 0, ymax = 100, axeson = True, labelson = True):
        Tkinter.Canvas.__init__(self, parent, width = w, height = h, bg = 'white') 
        self.parent = parent
        self.width = w
        self.height = h
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.axeson = axeson
        self.labelson = labelson
        self.img = Tkinter.PhotoImage(width = w, height = h)
	self.create_image(0, 0, image = self.img, anchor=Tkinter.NW)
        self.functions = []
        self.initCBounds()
        self.initObjects()
        self.initPointSets()
        self.bind("<Button-1>", self.canvas_left_clicked_down)
	try:
		if platform.system() == 'Darwin':
			self.bind("<Button-2>", self.canvas_right_clicked_down)
		else:
			self.bind("<Button-3>", self.canvas_right_clicked_down)
        except:
		self.bind("<Button-3>", self.canvas_right_clicked_down)
	self.bind("<ButtonRelease-1>", self.canvas_left_clicked_up)
        self.bind("<B1-Motion>", self.canvas_left_moved)
        self.draw()
    
    def initCBounds(self):
        if self.labelson:
            self.usablecxmin = X_LABEL_WIDTH+1
        else:
            self.usablecxmin = 1
        self.usablecxmax = self.width
        self.usablecymin = 1
        if self.labelson:
            self.usablecymax = self.height-Y_LABEL_HEIGHT
        else:
            self.usablecymax = self.height
        self.usableheight = self.usablecymax-self.usablecymin
        self.usablewidth = self.usablecxmax-self.usablecxmin
        self.diagonalPixelLength = (self.usablewidth**2+self.usableheight**2)**(0.5)
    
    def initObjects(self):
        self.objects = {}
        self.objects[DISCRETE_TIME] = []
        self.objects[CONTINUOUS] = []
	self.objects[CONTINUOUS_SET] = []
        self.objects[SLOPE_FIELD] = []
        self.objects[LABELS] = []
        self.objects[RK] = []
        self.objects[AXES] = []
    
    def clear(self):
	for k in self.objects.keys():
		for j in self.objects[k]:
			self.delete(j)
		self.objects[k]= []        
	self.img = Tkinter.PhotoImage(width = self.width, height = self.height)
	self.create_image(0, 0, image = self.img, anchor=Tkinter.NW)

    def graphFunc(self, f, mode, color):
	if mode == CONTINUOUS:
	    func = Continuous(self, f, color)
	    self.functions.append(func)
        if mode == CONTINUOUS_SET:
            func = Continuousset(self, f, color)
            self.functions.append(func)
        elif mode == DISCRETE_TIME:
            func = Discrete(self, f, color)
            self.functions.append(func)
        elif mode == SLOPE_FIELD:
            func = Slopefield(self, f, color)
            self.functions.append(func)
        elif mode == SCALAR_FIELD:
            color = DEFAULT_COLORMAPS[0](self, int(self.diagonalPixelLength))
            func = Scalarfield(self, f, color)
            self.functions.append(func)
        self.draw()
        
    def updateInput(self):
        for f in self.functions:
            if f.type() == CONTINUOUS:
                f.setInput([self.xset])
            elif f.type() == DISCRETE_TIME:
                f.setInput([self.xdtset])
            elif f.type() == SLOPE_FIELD:
                f.setInput([self.xslopeset, self.yslopeset])
            elif f.type() == SCALAR_FIELD:
                f.setInput([self.xset, self.yset])
    
    def drawFunctions(self):
        for f in self.functions:
            if f.type() == DISCRETE_TIME:
		for i in range(len(self.xdtset)):
                    vx = self.xdtset[i]
                    cx = self.getCx(vx)
                    vy = f.eval([vx])
                    if not vy == GARBAGE and self.visible(cx):
                        col = f.color
                        cy = self.getCy(vy)
                        self.objects[DISCRETE_TIME].append(self.create_line(cx, self.getCy(0), cx, cy, width = f.width, fill = col, tags = ("f")))
                        self.objects[DISCRETE_TIME].append(self.create_oval(cx-2, cy-2, cx+2, cy+2, width = f.width, outline = col, fill = "white", tags = ("f")))
            elif f.type() == CONTINUOUS:  
		vy = f.eval([self.xset[0]])
                last = [0, self.getCy(vy)]
                for c in range(self.usablewidth-1):
                    x = self.xset[c+1]
                    next = [self.usablecxmin+c+1, self.getCy(f.eval([x]))]
                    if not last[1] == GARBAGE and self.visible(last[0], last[1]):
                        lastwasvisible = True
                    else:
                        lastwasvisible = False
                    if (lastwasvisible or self.visible(next[0], next[1])) and (last[1] != GARBAGE and next[1] != GARBAGE):
                        col = f.color
                        self.objects[CONTINUOUS].append(self.create_line(last[0], last[1], next[0], next[1], width = 1, fill = col))
		    else:
			lastwasvisible = False
                    last = next
  	    elif f.type() == CONTINUOUS_SET:
		last = [self.getCx(f.xset[0]), self.getCy(f.yset[0])]
		for i in range(len(f.xset)):
			next = [self.getCx(f.xset[i]), self.getCy(f.yset[i])]
			if self.visible(last[0],last[1]) or self.visible(next[0], next[1]):
			    col = f.color
			    self.objects[CONTINUOUS_SET].append(self.create_line(last[0], last[1], next[0], next[1], width = 1, fill = col))
			last = next
            elif f.type() == SLOPE_FIELD:
                for px in self.xslopeset:
                    for py in self.yslopeset:
                        cx = self.getCx(px)
                        cy = self.getCy(py)
                        if self.visible(cx, cy):
                            slope = f.eval([px, py])
                            if slope == 0:
                                dx = DEFAULT_SLOPE_SPACING-2
                                dy = 0
                            elif slope == GARBAGE:
                                dx = 0
                                dy = DEFAULT_SLOPE_SPACING-2
                            else:
                                dx = (((DEFAULT_SLOPE_SPACING-2)**2)/(1+slope**2))**(0.5)
                                dy = slope*dx
                            col = f.color
                            if self.visible(cx+(dx/2), cy-(dy/2)) or self.visible(cx-(dx/2), cy+(dy/2)):
                                self.objects[SLOPE_FIELD].append(self.create_line(cx-(dx/2), cy+(dy/2), cx+(dx/2), cy-(dy/2), width = f.width, fill = col))
            elif f.type() == SCALAR_FIELD:
                for i in range(len(self.cxset)):
                    for j in range(len(self.cyset)):
                        cx = self.cxset[i]
                        cy = self.cyset[j]
                        if self.visible(cx, cy):
                            val = f.eval([self.xset[i], self.yset[j]])
                            if not val == GARBAGE:
                                col = f.color.color(val)
                                self.img.put((col,), (cx, cy, cx+1, cy+1,))
        
    def initPointSets(self):
            self.cxset = [d+self.usablecxmin for d in range(self.usablewidth)]
            self.cyset = [d+self.usablecymin for d in range(self.usableheight)]
            self.xset = [self.xmin+i*(float(self.xmax-self.xmin)/float(self.usablewidth)) for i in range(self.usablewidth)]
            self.xdtset = [int(i+self.xmin) for i in range(int(self.xmax-self.xmin))]
            self.yset = [self.ymax-i*(float(self.ymax-self.ymin)/float(self.usableheight)) for i in range(self.usableheight)]
            self.xslopeset = [self.xmin+i*DEFAULT_SLOPE_SPACING*(self.xmax-self.xmin)/float(self.usablewidth) for i in range(self.usablewidth//DEFAULT_SLOPE_SPACING+1)]
            self.yslopeset = [self.ymin+i*DEFAULT_SLOPE_SPACING*(self.ymax-self.ymin)/float(self.usableheight) for i in range(self.usableheight//DEFAULT_SLOPE_SPACING+1)]
    
    def canvas_right_clicked_down(self, event):
        points = []
        for f in filter(lambda o: o.type() == SLOPE_FIELD, self.functions):
            stepsize=float(self.xmax-self.xmin)/float(self.usablewidth)
            x = self.getPx(event.x)
            y = self.getPy(event.y)
            for i in range(event.x-self.usablecxmin):
                try:
                    yi = y
                    ka = f.eval([x,y])
                    x = x-stepsize/4.
                    y = y-stepsize*ka/4.
                    kb = f.eval([x,y])
                    x = x-stepsize/4.
                    y = y-stepsize*kb/4.
                    kc = f.eval([x,y])
                    x = x-stepsize/4.
                    y = y-stepsize*kc/4.
                    kd = f.eval([x,y])
                    x = x-stepsize/4.
                    y = y-stepsize*kd/4.
                    k = (ka+2*kb+2*kc+kd)/6.0
                    y = yi-stepsize*k
                    cx = event.x-i
                    cy = self.getCy(y)
                    points.insert(0, [cx, cy])
                except:
                    pass
            x = self.getPx(event.x)
            y = self.getPy(event.y)
            for i in range(self.usablecxmax-event.x):
                try:
                    yi=y
                    ka = f.eval([x,y])
                    x = x+stepsize/4.
                    y = y+stepsize*ka/4.
                    kb = f.eval([x,y])
                    x = x+stepsize/4.
                    y = y+stepsize*kb/4.
                    kc = f.eval([x,y])
                    x = x+stepsize/4.
                    y = y+stepsize*kc/4.
                    kd = f.eval([x,y])
                    x = x+stepsize/4.
                    y = y+stepsize*kd/4.
                    k = (ka+2*kb+2*kc+kd)/6.0
                    y=yi+stepsize*k
                    cx = event.x+i
                    cy = self.getCy(y)
                    points.append([cx, cy])
                except:
                    pass
            col = RK4_COLOR
	    if col == f.color: col = "black"
            self.path(RK, points, col, 1)
            
    def canvas_left_clicked_down(self, event):
        self.lastleftx = event.x
        self.lastlefty = event.y
        self.scan_mark(event.x, event.y)
        
    def canvas_left_moved(self, event):
        self.scan_dragto(event.x, event.y, 1)
        
    def canvas_left_clicked_up(self, event):
        self.shift(self.lastleftx-event.x, self.lastlefty-event.y)
        self.scan_dragto(self.lastleftx, self.lastlefty)
        self.draw()
    
    def draw(self):
        self.clear()
        self.initPointSets()
        self.updateInput()
        if self.axeson:
            self.drawAxes()
        self.drawFunctions()
        if self.labelson:
            self.drawLabels()
        
    def getPx(self, cx):
	try:
        	return self.xmin+float(self.xmax-self.xmin)*(cx-self.usablecxmin)/float(self.usablewidth)
	except:
		return GARBAGE

    def getPy(self, cy):
	try:
        	return self.ymax-(cy-self.usablecymin)*float(self.ymax-self.ymin)/float(self.usableheight)
        except:
		return GARBAGE
    def getCx(self, px):
	try:
        	return int(self.usablecxmin + self.usablewidth*((px-self.xmin)/float(self.xmax-self.xmin)))
   	except:
		return GARBAGE 
    def getCy(self, py):  
	try:
        	return int(self.usablecymax-(self.usableheight*(py-self.ymin)/float(self.ymax-self.ymin)))
	except:
		return GARBAGE

    def visible(self, cx = GARBAGE, cy = GARBAGE):
        if cx == GARBAGE:
            cx = self.usablecxmin
        if cy == GARBAGE:
            cy = self.usablecymin
        return (cx <= self.usablecxmax) and (cx >= self.usablecxmin) and (cy <= self.usablecymax) and (cy >= self.usablecymin)

    def drawLabels(self, xshift = 0, yshift = 0):
        def round(fl):
            string = `fl`
            if not len(string) < 5:
                string = scinot(fl)
            return string
        self.objects[LABELS].append(self.create_rectangle(xshift, yshift, X_LABEL_WIDTH+xshift-1, self.height+yshift, fill = "white", outline = "white"))
        self.objects[LABELS].append(self.create_rectangle(xshift, self.height-Y_LABEL_HEIGHT+yshift+1, self.width+xshift, self.height+yshift, fill = "white", outline = "white"))
        self.objects[LABELS].append(self.create_line(X_LABEL_WIDTH+xshift, yshift, X_LABEL_WIDTH+xshift, self.height-Y_LABEL_HEIGHT+yshift, width = 1, fill = "black"))
        self.objects[LABELS].append(self.create_line(X_LABEL_WIDTH+xshift, self.height-Y_LABEL_HEIGHT+yshift, self.width+xshift, self.height-Y_LABEL_HEIGHT+yshift, width = 1, fill = "black"))
        self.objects[LABELS].append(self.create_text(2+xshift, yshift, text = round(self.ymax), font = LABEL_FONT, fill = "black", anchor = Tkinter.NW))
        self.objects[LABELS].append(self.create_text(2+xshift, self.height-Y_LABEL_HEIGHT+yshift, text = round(self.ymin), font = LABEL_FONT, fill = "black", anchor = Tkinter.SW))
        self.objects[LABELS].append(self.create_text(X_LABEL_WIDTH+xshift, self.height+yshift, text = round(self.xmin), font = LABEL_FONT, fill = "black", anchor = Tkinter.SW))
        self.objects[LABELS].append(self.create_text(self.width+xshift, self.height+yshift, text = round(self.xmax), font = LABEL_FONT, fill = "black", anchor = Tkinter.SE))
        if self.axeson:
            xaxis = self.getCy(0)
            yaxis = self.getCx(0)
            if xaxis > (2*LABEL_FONT[1])+yshift and xaxis < self.height-Y_LABEL_HEIGHT-(2*LABEL_FONT[1])+yshift:
                self.objects[LABELS].append(self.create_text(2+xshift, xaxis+yshift, text = round(0), font = LABEL_FONT, fill = "black", anchor = Tkinter.W))
            if yaxis > X_LABEL_WIDTH+(6*LABEL_FONT[1])+xshift and yaxis < self.width-(6*LABEL_FONT[1])+xshift:
                self.objects[LABELS].append(self.create_text(yaxis+xshift, self.height+yshift, text = round(0), font = LABEL_FONT, fill = "black", anchor = Tkinter.S))
            
    def drawAxes(self):
        xaxis = self.getCy(0)
        yaxis = self.getCx(0)
        ystart = self.usablecymin
        xstart = self.usablecxmin
        if xaxis >= ystart:
            self.create_dottedline(AXES, xstart, xaxis, self.usablecxmax, xaxis, 1, "red")
        if yaxis >= xstart:
            self.create_dottedline(AXES, yaxis, ystart, yaxis, self.usablecymax, 1, "red")
        
    def shift(self, xshift, yshift):
        if not xshift == 0:
            xoffset = ((self.xmax-self.xmin)*xshift)/float(self.usablewidth)
            self.xmin+=xoffset
            self.xmax+=xoffset
        if not yshift == 0:
            yoffset = -((self.ymax-self.ymin)*yshift)/float(self.usableheight)
            self.ymin+=yoffset
            self.ymax+=yoffset
        self.initPointSets()
        
################################
#drawing
    
    def path(self, id, pts, col, w):
        xa, ya = pts[0][0], pts[0][1]
        for p in pts[1:]:
            xb, yb = p[0], p[1]
            if self.visible(xa, ya) and self.visible(xb, yb):
                self.objects[id].append(self.create_line(xa, ya, xb, yb, width = w, fill = col))
            xa, ya = xb, yb
    
    def create_dottedline(self, id, xa, ya, xb, yb, w, col, spacing = DOTTED_LINE_SPACING):
        length = ((xb-xa)**2+(yb-ya)**2)**0.5
        ystep = (yb-ya)*spacing/length
        xstep = (xb-xa)*spacing/length
        beginx, beginy = xa, ya
        nextx, nexty = xa+xstep, ya+ystep
        while self.visible(beginx, beginy):
            self.objects[id].append(self.create_line(beginx, beginy, nextx, nexty, width = w, fill = col))
            beginx +=2*xstep
            beginy +=2*ystep
            nexty +=2*ystep
            nextx +=2*xstep
            
    

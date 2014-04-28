import Tkinter
from Tkinter import *
import sys

# quick and dirty EntryField to avoid needing Pmw package for this one
# dialog box.  Replace EntryField with Pmw.EntryField to use Pmw instead
# --sjf
class EntryField():
  def __init__(self, parent, labelpos='w', label_text='',
               value = '', command = None, validate = None,
               entry_width=40):
    self.frame = Frame(parent)
    self.label = Label(self.frame, text=label_text)
    self.entry = Entry(self.frame, width=entry_width)
    self.entry.insert(0, value)
    if command:
      self.entry.bind("<Return>", command)

  def pack(self, **opts):
    self.entry.pack(side=RIGHT)
    self.label.pack(side=RIGHT)
    self.frame.pack(opts)

  def getvalue(self):
    return self.entry.get()

def alignlabels(entryFields):
  maxlen = max([f.label.cget('width') for f in entryFields])
  for f in entryFields:
    f.label.config(width=maxlen)

class ScopeConfigWindow():
  def __init__(self, scope, allowGUIToAddProbes=False):
      self.scope = scope
      self.allowGUIToAddProbes = allowGUIToAddProbes
      self.window = Tkinter.Toplevel()
      self.window.wm_title("Configuration Panel")
      self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
      #self.grp = Pmw.Group(self.window)
      self.grp = Frame(self.window, borderwidth=2, relief=GROOVE)
      self.entries = []
      self.titleEntry = \
          self.makeEntryField('Title: ', 'Untitled', self.title)
      self.xlabelEntry = \
          self.makeEntryField('X Label: ', scope.opts['X Label'], self.xlabel)
      self.ylabelEntry = \
          self.makeEntryField('Y Label: ', scope.opts['Y Label'], self.ylabel)
      self.oldxscale = int(self.entryStr(scope.opts['X Scale']))
      self.oldyscale = self.entryStr(scope.opts['Y Scale'])
      self.xscaleEntry = \
          self.makeEntryField('X Scale: ', self.oldxscale, self.xscale)
      self.yscaleEntry = \
          self.makeEntryField('Y Scale: ', self.oldyscale, self.yscale)
      self.grp.pack(side=TOP, expand=1, padx=10, pady=10, fill='x')
      if self.allowGUIToAddProbes:
        self.probeGrp = Frame(self.window, borderwidth=2, relief=GROOVE)
        self.probeEntries = []
        for i in range(len(scope.probes)):
          self.makeProbeEntry(i)
        self.probeGrp.pack(side=TOP, expand=1, padx=10, pady=2, fill='x')
      alignlabels(self.entries)
      #self.buttonGrp = Pmw.Group(self.window)
      self.buttonGrp = Frame(self.window)
      self.buttonGrp.pack(expand=0, padx=10, pady=10, fill='x')
      self.applyButton = Tkinter.Button(self.buttonGrp,
                                       text="Apply", command = self.apply)
      self.applyButton.pack(side=LEFT, fill='x', padx = 50)
      self.closeButton = Tkinter.Button(self.buttonGrp,
                                        text="Close", command = self.done)
      self.closeButton.pack(side=LEFT, fill='x', padx=50)
      self.cancelButton = Tkinter.Button(self.buttonGrp,
                                         text="Cancel", 
                                         command = self.closeWindow)
      self.cancelButton.pack(side=LEFT, fill='x', padx = 50)
      self.buttonGrp.pack()
      
  def __del__(self):
      self.closeWindow()
      
  def apply(self):
      self.readConfig()
      self.scope.doneConfiguring()

  def done(self):
      self.apply()
      self.closeWindow()

  def closeWindow(self):
      if self.window:
          self.window.destroy()
          self.window = None

  def entryStr(self, x):
      if type(x) == tuple:
          return str(x)[1:-1]
      else: return str(x)

  def makeProbeEntry(self, idx):
      probeValid = self.scope.probes[idx] != None
      #g = Pmw.Group(self.grp)
      g = Frame(self.probeGrp)
      g.pack(side=TOP, expand=1, fill='x')
      nt = "" if not probeValid else self.scope.probes[idx].name
      n = EntryField(g, labelpos = 'w',
                     label_text = 'Probe '+str(idx)+' name: ', value = nt,
                     entry_width = 10)
      n.pack(side = LEFT, fill='x', expand=1, padx=5, pady=5)
      ft = "" if not probeValid else self.scope.probes[idx].functext
      f = EntryField(g, labelpos = 'w', value = ft,
                     label_text = 'value to plot: ',
                     entry_width = 30)
      f.pack(side = RIGHT, fill='x', expand=1, padx=5, pady=5)
      self.probeEntries.append((n,f))

  def readProbeEntries(self):
      for i in range(len(self.scope.probes)):
          name = self.probeEntries[i][0].getvalue()
          functext = self.probeEntries[i][1].getvalue()
          if (name != "" and functext != "" and 
              functext.find("<function") == -1):
              self.scope.setProbeText(i, name, functext)

  def makeEntryField(self, label_text, value, command):
    e = EntryField(self.grp, labelpos = 'w',
                   label_text = label_text, value = value,
                   command = command, validate = None,
                   entry_width=50)
    e.pack(fill='x', expand=1, padx=5, pady=5)
    self.entries.append(e)
    return e

  def readConfig(self):
    self.title()
    self.xlabel()
    self.ylabel()
    self.xscale()
    self.yscale()
    if self.allowGUIToAddProbes:
      self.readProbeEntries()

  def title(self, args=None):
    title = self.titleEntry.getvalue()
    self.scope.opts['Title'] = title
    self.scope.setStaticObjects()
    
  def xlabel(self, args=None):
    xlabel = self.xlabelEntry.getvalue()
    self.scope.opts['X Label'] = xlabel
    self.scope.setStaticObjects()

  def ylabel(self, args=None):
    ylabel = self.ylabelEntry.getvalue()
    self.scope.opts['Y Label'] = ylabel
    self.scope.setStaticObjects()

  def xscale(self, args=None):
    xscale = self.xscaleEntry.getvalue()
    parse = xscale.split(',')
    if len(parse) == 1:
      if int(parse[0]) != self.oldxscale:
        print 'changing x scale from ', self.oldxscale, ' to ', int(parse[0])
        self.oldxscale = int(parse[0])
        self.scope.opts['X Scale'] = self.oldxscale
        self.scope.setTimeAxis()
        self.scope.setStaticObjects()
        self.scope.draw()
    else:
      sys.stderr.write('Error setting time scale.  Should be one number.\n')
          
  def yscale(self, args=None):
    yscale = self.yscaleEntry.getvalue()
    try:
      parse = yscale.split(',')
      if len(parse) == 1:
        if parse[0] == 'auto':
          if self.oldyscale != 'auto':
            self.oldyscale = 'auto'
            self.scope.opts['Y Scale'] = self.oldyscale
        elif self.oldyscale != (0,float(parse[0])):
          self.oldyscale = (0, float(parse[0]))
          self.scope.opts['Y Scale'] = self.oldyscale
          self.scope.setStaticObjects()
          self.scope.draw()
      elif len(parse) == 2 and self.oldyscale != (float(parse[0]),
                                                  float(parse[1])):
        self.oldyscale = (float(parse[0]), float(parse[1]))
        self.scope.opts['Y Scale'] = self.oldyscale
        self.scope.setStaticObjects()
        self.scope.draw()
        # otherwise don't do anything
    except Exception, e:
      print e
      sys.stderr.write('Invalid y scale entered.\n')

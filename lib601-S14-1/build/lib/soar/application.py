###############################soar/application.py###############################
# soar3.0
#  / application.py
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
from time import time, sleep
import platform

import form
import form.widgets as widgets
import form.formulae as formulae
import form.common as common
import form.parallel as parallel
from soar.io import io
import soar.io.userfn
from soar.io.userfn import UserFunctionIF
import soar.graphics
from soar.graphics.sonarmonitor import SonarMonitor
from soar.graphics.scope import Oscilloscope
from soar.outputs.simulator import ROBOT_POINTS

import form.settings as settings

import subprocess
import os

import soar
import traceback

# This import hooks the version number into settings
import soar.version

#####################################Notes######################################
# This is the form startup script for soar. It configures form for all of
# soar's specific needs.
################################################################################

class application(object):
  ENABLED = 0
  DISABLED = 1
  UNCHANGED = 2
  def __init__(self):
    app.soar = self
    self.top = app.top
    app.top.wm_title('soar'+soar.version.format_version())
    app.top.protocol('WM_DELETE_WINDOW', self.exit)

    self.initializeNamespace()
    self.userfn = UserFunctionIF()
    io.configure_io(self.namespace)
    self.soar_toolbar_commands = formulae.FormulaPool()
    self.flowtriplets = [(self.startstepper, self.step, self.stopstepper)]
    soar_dir = soar.__path__[0]
    self.readConfigFile()
    if self.main_geom:
      app.top.geometry(self.main_geom[self.main_geom.find('+'):])
    media_dir = soar_dir + '/media'
    self.toolbar = widgets.ToolbarFrame(app.top, self.soar_toolbar_commands)
    self.toolbar.pack(side = TOP)
    start_images = {'normal' : media_dir + "/start.gif"}
    step_images = {'normal' : media_dir + "/step.gif"}
    stop_images = {'normal' : media_dir + "/stop.gif"}
    simulator_images = {'normal' : media_dir + "/simulator.gif"}
    robot_images = {'normal' : media_dir + "/robot.gif"}
    brain_images = {'normal' : media_dir + "/brain.gif"}
    joystick_images = {'normal' : media_dir + "/joystick.gif"}
    oscillo_images = {'normal' : media_dir + "/oscillo.gif"}
    wireless_images = {'normal' : media_dir + "/wireless.gif"}
    # if we're on the mac, the buttons won't stay pushed, so
    # we have a different image to indicate active buttons
    self.use_active_button_images = (platform.system() == 'Darwin')
    if (self.use_active_button_images):
      start_images['active'] = media_dir + "/start_active.gif"
      stop_images['active'] = media_dir + "/stop_active.gif"
      simulator_images['active'] = media_dir + "/simulator_active.gif"
      robot_images['active'] = media_dir + "/robot_active.gif"
      brain_images['active'] = media_dir + "/brain_active.gif"
      joystick_images['active'] = media_dir + "/joystick_active.gif"
      oscillo_images['active'] = media_dir + "/oscillo_active.gif"
      wireless_images['active'] = media_dir + "/wireless_active.gif"

    self.soar_toolbar_commands.addFormula(('start', self.startall, 'Start', 
                                            start_images, lambda: []))
    self.soar_toolbar_commands.addFormula(('step', self.stepall, 'Step', 
                                           step_images, lambda: []))
    self.soar_toolbar_commands.addFormula(('stop', self.stopall, 'Stop', 
                                           stop_images, lambda: [])) 
    self.pushToolbarButton('stop')
    self.disableToolbarButton('start')
    self.disableToolbarButton('step')

    Label(self.toolbar, text = "Outputs:").pack(side = LEFT)

    #self.simulator_dir_default = soar_dir + "/6.01/worlds"
    self.soar_toolbar_commands.addFormula(('simulator', self.openSimulator,
                                           'Simulator', simulator_images,
                                           self.openSimulatorDialog))

    self.soar_toolbar_commands.addFormula(('pioneer', self.openPioneer, 
                                           'Pioneer', robot_images,
                                           lambda: []))
    
    #self.soar_toolbar_commands.addFormula(('wireless', self.openWireless, 
    #                                       'Wireless', wireless_images,
    #                                       lambda: []))
    
    Label(self.toolbar, text = "Controls:").pack(side = LEFT)

    #self.brain_dir_default = '~'
    self.soar_toolbar_commands.addFormula(('brain', self.openBrain, 'Brain', 
                                           brain_images, self.openBrainDialog))
    self.disableToolbarButton('brain')

    self.soar_toolbar_commands.addFormula(('joystick', self.openJoystick, 
                                           'Joystick', joystick_images,
                                           lambda: []))
    self.disableToolbarButton('joystick')
#    self.soar_toolbar_commands.addFormula(('oscillo', self.openOscillo,
#                                           '    Oscilloscope ', oscillo_images,
#                                           lambda: []))


    self.minibuffer = widgets.MiniBuffer(app.mainframe, self.namespace, 
                                         width=78)
    self.minibuffer.pack(side = TOP, fill=X, expand=1)

    self.stderrbuffer = None
#    self.stderrframe = app.tabframe.addFrameWithHideCB("errors", 
#                                                       self.clearErrors)
#    self.stderrframe = app.tabframe.addFrame("errors")
    self.stderrbuffer = widgets.OutputBufferFrame(app.mainframe)#self.stderrframe)
    self.stderrbuffer.box_.config(foreground='red')
    self.stderrbuffer.pack(fill=BOTH, expand=1)
    sys.stderr = parallel.PipeSyndicator([sys.stderr, self.stderrbuffer])
    self.clearErrors()

    self.stdoutbuffer = None
#    self.stdoutframe = app.tabframe.addFrameWithHideCB("standard output", 
#                                                       self.clearOutput)
#    self.stdoutframe = app.tabframe.addFrame("standard output")
    self.stdoutbuffer = widgets.OutputBufferFrame(app.mainframe)#self.stdoutframe)
    self.stdoutbuffer.pack(fill=BOTH, expand=1)
    sys.stdout = parallel.PipeSyndicator([sys.stdout, self.stdoutbuffer])
    self.clearOutput()

    self.reloadAllButton = Button(app.mainframe, text="Reload Brain and World",
                                  command = self.reloadAll)
    self.reloadAllButton.pack()
    self.disableButton(self.reloadAllButton)

    self.reloadBrainButton = Button(app.mainframe, text="Reload Brain",
                                    command = self.reloadBrain)
    self.reloadBrainButton.pack()
    self.brainfile = ""
    self.disableButton(self.reloadBrainButton)
    #self.reloadWorldButton = Button(app.mainframe, text="Reload World",
    #                                command = self.reloadWorld)
    #self.reloadWorldButton.pack()
    #self.disableButton(self.reloadWorldButton)
    self.sonarMonitor = None
    self.oscope = None
    self.control = None
    self.output = None
    self.readfile = False
    self.writefile = False

  def readConfigFile(self):
    # defaults for if no file exists
    self.simulator_dir_default = soar.__path__[0] + "/worlds"
#    self.brain_dir_default = '~'
    self.brain_dir_default = os.getcwd()
    self.main_geom = None
    self.simulator_geom = None
    self.scope_geom = None
    self.sonarmon_geom = None
    homedir = os.path.expanduser('~')
    homedir.replace('\\', '/')
    try:
      f = open(homedir+"/.soarc")
    except:
      # it's okay if there's no config file; we'll write one at the end
      return
    vars = {}
    for line in f.readlines():
      if '=' in line:
        key,value = map(str.strip, line.split('=',1))
        vars[key] = value
    f.close()
    if vars.has_key('OPEN_PATH') and os.path.exists(vars['OPEN_PATH']):
      self.brain_dir_default = vars['OPEN_PATH']
    if vars.has_key('WORLD_PATH') and os.path.exists(vars['WORLD_PATH']):
      self.simulator_dir_default = vars['WORLD_PATH']
    # get geometry for the windows for each standard widget
    if vars.has_key('MAIN_GEOM'): self.main_geom = vars['MAIN_GEOM']
    if vars.has_key('SIM_GEOM'): self.simulator_geom = vars['SIM_GEOM']
    if vars.has_key('SCOPE_GEOM'): self.scope_geom = vars['SCOPE_GEOM']
    if vars.has_key('SONAR_MON_GEOM'): 
      self.sonarmon_geom = vars['SONAR_MON_GEOM']
  
  def writeConfigFile(self):
    homedir = os.path.expanduser('~')
    homedir.replace('\\', '/')
    try:
      f = open(homedir+"/.soarc", "w")
      f.write('%s=%s\n' % ('OPEN_PATH', self.brain_dir_default))
      f.write('%s=%s\n' % ('WORLD_PATH', self.simulator_dir_default))
      f.write('%s=%s\n' % ('MAIN_GEOM', self.top.geometry()))
      if self.simulator_geom:
        f.write('%s=%s\n' % ('SIM_GEOM', self.simulator_geom))
      if self.scope_geom:
        f.write('%s=%s\n' % ('SCOPE_GEOM', self.scope_geom))
      if self.sonarmon_geom:
        f.write('%s=%s\n' % ('SONAR_MON_GEOM', self.sonarmon_geom))
    except:
      sys.stderr.write("Could not write soar config file .soarc\n")

  def exit(self):
    # askyesno seems to be broken in current Tk (always returns False)
    #answer = form.widgets.askyesno("Exit", "Are you sure you want to exit?")

#    answer = form.widgets.askquestion("Exit", "Are you sure you want to exit?")
#    if answer == 'no':
#      return
    try:
      self.stopall()
    except:
      pass
    try:
      self.unloadModule(self.control)
    except:
      pass
    try:
      self.unloadModule(self.output)
    except:
      pass
    self.closeSonarMonitor()
    self.closeOscillo()
#    self.writeConfigFile()
    form.main.tk.destroy()
    form.main.sys.exit(0)

  def clearErrors(self):
    self.stderrbuffer.clear()
    sys.stderr.write ("Error output will appear in this window.\n")

  def clearOutput(self):
    self.stdoutbuffer.clear()
    print "Ordinary output will appear in this window."

  def openSimulator(self, world):
    import soar.outputs.simulator
    if (len(world) > 0):
      #self.enableButton(self.reloadWorldButton)
      # do this before we try to read the file so we can reload even
      # if there is an error in the file
      if self.control:
        self.enableButton(self.reloadAllButton)
      try:
        self.setOutput(lambda: \
                         soar.outputs.simulator.Simulator(world, 
                                                          self.simulator_geom))
      except:
        sys.stderr.write("Error loading world.  Perhaps you accidentally chose a brain file?\n")
        return
      self.pushToolbarButton('simulator')
      self.unpushToolbarButton('pioneer')
      #self.unpushToolbarButton('wireless')
      self.unpushToolbarButton('brain')
      self.unpushToolbarButton('joystick')
      self.reloadBrain(True)

  def openPioneer(self):
    import soar.outputs.pioneer
    # allow pioneer button to be unpushed to disconnect
    if self.toolbar.buttons['pioneer'].cget('relief') == SUNKEN:
      self.closePioneer(False)
    else:
      if self.setOutput(lambda: soar.outputs.pioneer.Pioneer()):
        #self.disableButton(self.reloadWorldButton)
        self.disableButton(self.reloadAllButton)
        # allowing reinit to pioneer is most likely to cause crashing, so don't
        self.pushToolbarButton('pioneer', self.ENABLED)
        self.enableToolbarButton('brain')
        self.enableToolbarButton('joystick')
        # can't step the real robot
        self.disableToolbarButton('step')
        if self.brainfile != "":
          self.enableButton(self.reloadBrainButton)
          self.enableButton(self.reloadAllButton)
      self.unpushToolbarButton('simulator')
      #self.unpushToolbarButton('wireless')
      self.reloadBrain(True)

  def closePioneer(self, callUserFn=True):
    self.stopall(callUserFn)
    self.setOutput(lambda: None)
    self.unpushToolbarButton('pioneer')
    # don't have output, so disable brain loading
    self.disableToolbarButton('joystick')
    self.disableToolbarButton('brain')
    self.disableButton(self.reloadBrainButton)
  
  def openWireless(self):
    import soar.outputs.pioneer
    # allow pioneer button to be unpushed to disconnect
    if self.toolbar.buttons['pioneer'].cget('relief') == SUNKEN:
      self.closePioneer(False)
    else:
      if self.setOutput(lambda: soar.outputs.pioneer.Pioneer(wireless=True)):
        #self.disableButton(self.reloadWorldButton)
        self.disableButton(self.reloadAllButton)
        # allowing reinit to pioneer is most likely to cause crashing, so don't
        self.pushToolbarButton('wireless', self.ENABLED)
        self.enableToolbarButton('brain')
        self.enableToolbarButton('joystick')
        # can't step the real robot
        self.disableToolbarButton('step')
        if self.brainfile != "":
          self.enableButton(self.reloadBrainButton)
          self.enableButton(self.reloadAllButton)
      self.unpushToolbarButton('simulator')
      self.unpushToolbarButton('pioneer')
      self.reloadBrain(True)

  def closePioneer(self, callUserFn=True):
    self.stopall(callUserFn)
    self.setOutput(lambda: None)
    self.unpushToolbarButton('pioneer')
    # don't have output, so disable brain loading
    self.disableToolbarButton('joystick')
    self.disableToolbarButton('brain')
    self.disableButton(self.reloadBrainButton)
    self.disableButton(self.reloadAllButton)
    self.disableButton(self.reloadAllButton)

  def openBrain(self, brainfile, reload=False):
    import soar.controls.brain
    if (len(brainfile) > 0):
      # clear error, output windows
      self.clearOutput()
      self.clearErrors()
      if ( reload ):
        print "***Reloading Brain***"
      else:
        print "***Loading Brain***" 
      print "'" + brainfile + "'" 
      self.setControl(lambda: soar.controls.brain.Brain(brainfile, reload), 
                      not reload)
      if self.control:
        self.pushToolbarButton('brain', self.ENABLED)
        self.enableButton(self.reloadBrainButton)
        self.chooseStop(self.output != None)
        if self.output:
          self.unpushToolbarButton('joystick')
          self.enableButton(self.reloadAllButton)
        print "Successfully loaded brain file" 
        print "'" + brainfile + "'" 
      else:
        #self.disableButton(self.reloadBrainButton)
        print "Failed to load brain file '" + brainfile + "'" 

  def reloadAll(self):
    self.reloadWorld()
    self.reloadBrain()

  def reloadBrain(self, quiet=False):
    if self.brainfile == "" and not quiet:
      sys.stderr.write("No valid brain filename to reload.\n")
    if self.control is not None:
      try:
        self.control.reload()
      except AttributeError:
        # we must have tried to reload the joystick (yes, this is ugly)
        if self.brainfile != "":
          self.openBrain(self.brainfile,True)
    # if we failed, and we have a brainfile, just try loading the brain
    # as opposed to REloading
    if self.control is None and self.brainfile != "":
      self.openBrain(self.brainfile,False)

  def reloadWorld(self):
    if self.output is not None:
      try:
        self.output.initGlobals(True)
      except AttributeError:
        pass

  def openSonarMonitor(self):
    if not self.sonarMonitor:
      self.sonarMonitor = SonarMonitor(soar.outputs.simulator.ROBOT_POINTS,
                                       self.sonarmon_geom)
    self.sonarMonitor.openWindow()

  def closeSonarMonitor(self):
    if self.sonarMonitor:
      self.sonarMonitor.closeWindow()

  def openJoystick(self):
    import soar.controls.joystick
    self.setControl(lambda: soar.controls.joystick.Joystick())
    self.pushToolbarButton('joystick')
    self.unpushToolbarButton('brain')

  def closeOscillo(self):
    if self.oscope:
      self.oscope.closeWindow()
    self.oscope = None

  def openOscillo(self):
    if not self.oscope:
      self.oscope = Oscilloscope(self.scope_geom)
    self.oscope.openWindow()

  def addScopeProbeFunction(self, name, func):
    self.oscope.addProbeFunction(name, func)

  def clearScope(self):
    if self.oscope:
      self.oscope.clearProbes()
      self.oscope.closeWindow()

  def openSimulatorDialog(self):
    filename = widgets.askopenfilename(title = "Open a World File...",
                                       initialdir = self.simulator_dir_default,
                                       filetypes = [("World Files", "*.py")]);
    if (len(filename) > 0):
      self.simulator_dir_default = filename[0:filename.rfind("/")]
    return [filename]

  def openBrainDialog(self):
    filename = widgets.askopenfilename(title = "Open a Brain File...",
                                       initialdir = self.brain_dir_default,
                                       filetypes = [("Brain Files", "*.py")]);
    self.brainfile = filename
    if (len(filename) > 0):
      self.brain_dir_default = filename[0:filename.rfind("/")]
      os.chdir(self.brain_dir_default)
      self.enableButton(self.reloadBrainButton)
    return [filename]

  def removeFlowTriplet(self, trip):
    self.flowtriplets.remove(trip)

  def addFlowTriplet(self, trip):
    self.flowtriplets.append(trip)

  def setReadLog(self, f):
    self.control.readfile = open(f, 'rb')

  def setWriteLog(self, f):
    self.control.writefile = open(f, 'wb')

  def enableToolbarButton(self, name):
    self.enableButton(self.toolbar.buttons[name])
  def disableToolbarButton(self, name):
    self.disableButton(self.toolbar.buttons[name])
  def pushToolbarButton(self, name, state=DISABLED):
    self.pushButton(self.toolbar.buttons[name], state)
    self.toolbar.buttonImage(name, 'active')
  def unpushToolbarButton(self, name, state=ENABLED):
    self.unpushButton(self.toolbar.buttons[name], state)
    self.toolbar.buttonImage(name, 'normal')
  def flashToolbarButton(self, name):
    self.toolbar.buttons[name].flash()

  def enableButton(self, button):
    button.config(state=NORMAL)
  def disableButton(self, button):
    button.config(state=DISABLED)
  def buttonState(self, button, state):
    if state == self.DISABLED:
      self.disableButton(button)
    elif state == self.ENABLED:
      self.enableButton(button)
  def pushButton(self, button, state=DISABLED):
    button.config(relief=SUNKEN)
    self.buttonState(button, state)
  def unpushButton(self, button, state=ENABLED):
    button.config(relief=RAISED)
    self.buttonState(button, state)

  def chooseStart(self):
    self.pushToolbarButton('start')
    self.unpushToolbarButton('stop')
    self.pushToolbarButton('step')
    # can't choose control or output while running
    self.disableToolbarButton('simulator')
    self.disableToolbarButton('pioneer')
    self.disableToolbarButton('brain')
    self.disableToolbarButton('joystick')
    self.disableButton(self.reloadBrainButton)
    self.disableButton(self.reloadAllButton)

  def chooseStop(self, allowStart=1):
    if (allowStart):
      self.unpushToolbarButton('start')
      self.unpushToolbarButton('step')
    else:
      self.unpushToolbarButton('start', self.DISABLED)
      self.unpushToolbarButton('step', self.DISABLED)
    self.unpushToolbarButton('stop', self.DISABLED)
    # now we can choose control and output again
    self.enableToolbarButton('simulator')
    self.enableToolbarButton('pioneer')
    self.enableToolbarButton('brain')
    self.enableToolbarButton('joystick')
    if self.brainfile != "":
      self.enableButton(self.reloadBrainButton)
      self.enableButton(self.reloadAllButton)

  def disableStartStop(self):
    self.unpushToolbarButton('start', self.DISABLED)
    self.unpushToolbarButton('stop', self.DISABLED)
    self.unpushToolbarButton('step', self.DISABLED)

  def setControl(self, lazy_control, allow_start=1):
    if self.readfile:
      self.readfile.close()
    if self.writefile:
      self.writefile.close()
    self.unloadModule(self.control)
    # try to read in the brain file.  if it fails, unload the module
    try:
      self.control = lazy_control()
    except Exception, e:
      self.disableStartStop()
      self.unloadModule(self.control)
      self.control = None
      raise e
    self.readfile = False
    self.writefile = False
    # if we did read in the file, try to call the setup function
    # if the setup function fails, unload the module
    if self.control != None:
      try:
        self.userfn.callFunctions('setup')
        self.loadModule(self.control) 
      except:
        self.unloadModule(self.control)
        self.control = None
    if ((self.output != None) and allow_start):
      self.chooseStop(True)
    elif (self.output is None):
      self.disableStartStop()

  def setOutput(self, lazy_output):
    self.unloadModule(self.output)
    try:
      self.output = lazy_output()
      if self.output == None:
        self.disableStartStop()
        return 0
      else:
        self.loadModule(self.output)
        self.logstep()
        if (self.control != None):
          self.chooseStop(True)
        else:
          self.disableStartStop()
        return 1
    except common.CancelGUIAction:
      self.output = None
      self.disableStartStop()
      return 0
    
  def registerUserFunction(self, type, f):
    self.userfn.registerFn(type, f)

  def initializeNamespace(self):
    if hasattr(self, 'namespace'):
      self.namespace.clear()
    else:
      self.namespace = {}
    self.setters = {}
    self.getters = {}
    self.cachedvalues = {}
    self.namespace["robot"] = common.Container()
    self.namespace["readLog"] = self.setReadLog
    self.namespace["writeLog"] = self.setWriteLog
    self.namespace["registerUserFunction"] = self.registerUserFunction 

  def startall(self):
    for i in self.flowtriplets:
      i[0]()
    self.chooseStart()
    try:
      self.userfn.callFunctions('brainStart')
      self.control.start()
    except AttributeError:
      pass
    self.disableButton(self.reloadBrainButton)
    self.disableButton(self.reloadAllButton)
    if (self.use_active_button_images):
      self.flashToolbarButton('stop')

  def stopall(self, callUserFn=True):
    for i in self.flowtriplets:
      i[2]()
    self.chooseStop()
    try:
      if callUserFn:
        self.userfn.callFunctions('brainStop')
    except AttributeError:
      pass
    try:
      self.control.stop()
    except AttributeError:
      pass
    if self.brainfile != "":
      self.enableButton(self.reloadBrainButton)
      self.enableButton(self.reloadAllButton)
    if (self.use_active_button_images):
      self.flashToolbarButton('start')

  def stepall(self, dt = 0.1):
    for i in self.flowtriplets:
      i[1](dt)

  def stopstepper(self):
    try:
      self.currentstepper.stop()
    except AttributeError:
      pass

  def startstepper(self):
    self.stopstepper()
    self.currentstepper = parallel.Stepper(self.step, 10.0)
    self.currentstepper.start()

  def logstep(self):
    if self.readfile:
      try:
        for pair in pickle.load(self.readfile):
          self.cachedvalues[pair[0]].set(pair[1])
      except KeyError:
        app.alert("Log from an incompatible getter/setter interface")
        self.stopall()
      except EOFError:
        app.alert("Log Finished")
        self.stopall()
    else:
      for k in self.getters:
        try:
          self.cachedvalues[k].set(self.getters[k]())
        except:
          common.formerror()
    if self.writefile:
      pickle.dump(map(lambda k: (k,self.cachedvalues[k].get()), 
                      self.cachedvalues[k]), 
                  self.writefile)

  def step(self, dt):
    if self.output is not None:
      try:
        self.userfn.callFunctions('step')
        if self.sonarMonitor:
          self.sonarMonitor.update(self.output.storedsonars.get())
        if self.oscope: self.oscope.step()
        self.logstep()
        self.control.step(dt)
      except KeyError:
        common.formerror()
#        self.stopall()
      except:
        self.stopall()
        #raise

  def unloadModule(self, obj):
    if (obj == None):
      return
    try:
      self.userfn.callFunctions('shutdown')
      obj.shutdown()
      self.userfn.clearFunctions()
    except:
      pass
    try:
      for name in obj.getters:
        self.getters.pop(name)
        self.namespace.pop(name)
    except AttributeError:
      pass
    try:
      for name in obj.setters:
        self.setters.pop(name)
        self.namespace.pop(name)
    except AttributeError:
      pass
    try:
      obj.destroy()
    except AttributeError:
      pass # OK if modules have no cleanup code
    except:
      common.formerror()

  def loadModule(self, obj):
    try:
      for name in obj.getters:
        self.getters[name] = obj.getters[name]
        self.cachedvalues[name] = parallel.SharedVar()
        self.namespace[name] = self.cachedvalues[name].get
    except AttributeError:
      obj.getters = {}
    try:
      for name in obj.setters:
        self.setters[name] = obj.setters[name]
        self.namespace[name] = obj.setters[name]
    except AttributeError:
      obj.setters = {}
    try:
      obj.setup()
    except AttributeError:
      pass


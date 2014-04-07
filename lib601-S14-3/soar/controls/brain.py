#############################soar/controls/brain.py##############################
# soar3.0
#  / controls/brain.py
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
import os, sys
from thread import start_new_thread

from form.common import formerror, formerrorfile, skip, Container, parseFile, CancelGUIAction

from os.path import dirname
from traceback import print_exc
####################################Settings####################################
import form.settings as settings
################################################################################

class Brain(object):
  def reload(self):
    self.parent.openBrain(self.file, 1)

  def __init__(self, infile, reload):
    self.file = infile
    if len(self.file) == 0:
      raise CancelGUIAction
    self.parent = app.soar
    self.brainStarted = False
    envin = self.parent.namespace
    # pop off the functions that are defined in the brain file
    # (in case we're loading a new brain file that doesn't define them all)
    for name in ["setup", "brainStart", "step", "brainStop", "shutdown"]:
      if envin.has_key(name): envin.pop(name)
    if not reload:
      self.clearmodules(envin)
    try:
      parseFile(self.file, envin)
    except:
        sys.stderr.write("\nError loading brain: this brain may have a bug, or may need to be loaded after a robot is selected. \n");
        raise
      
    try:
      self.setup = self.makewrapper(envin["setup"],
                                    "\nError running setup function.  Brain file may have a bug, or brain may need to be loaded after simulator or robot is loaded.\n")
    except:
      self.setup = skip
      
    def brainStartedFalse():
      self.brainStarted = False
    def brainStartedTrue():
      self.brainStarted = True
    def checkStarted():
      if not self.brainStarted:
        self.startFn()

    try:
      self.stop = self.makewrapper(envin["brainStop"],
                                   "\nError running stopBrain function.\n",
                                   afterfunc=brainStartedFalse)
    except:
      self.stop = brainStartedFalse
      
    try:
      self.start = skip
      self.startFn = self.makewrapper(envin["brainStart"],
                                      "\nError running startBrain function.\n",
                                      afterfunc=brainStartedTrue)
    except:
      self.startFn = brainStartedTrue
      
    try:
      self.shutdown = self.makewrapper(envin["shutdown"],
                                       "\nError running shutdown function.\n");
    except:
      self.shutdown = skip
    try:
      self.braindestroy = envin["destroy"]
    except:
      self.braindestroy = skip
    if 'step' in envin:
      envstep = self.makewrapper(envin["step"],
                                 "\nError running step function.\n",
                                 beforefunc=checkStarted)
      if envstep.func_code.co_argcount == 0:
        self.step = lambda dt: envstep()
      elif envstep.func_code.co_argcount == 1:
        self.step = envstep
    else:
      self.step = checkStarted
      '''
    self.win = app.tabframe.addFrame('Brain')
    Label(self.win, text= "Brain: ").pack()
    #Button(self.win, text = "Edit Brain", command = lambda: settings.editor_command(self.file,)).pack()
    Button(self.win, text = "Reload Brain", command = self.reload).pack()
    # XXX
    self.win = app.tabframe.addFrame('World F')
    Label(self.win, text= "World L: ").pack()
    #Button(self.win, text = "Edit Brain", command = lambda: settings.editor_command(self.file,)).pack()
    Button(self.win, text = "Reload World", command = self.reload).pack()
    '''
  # put a wrapper around the brain functions so we can print a sensible
  # error message when running the functions raises an exception
  # (in particular, note that the problem may be due to not having a 
  # robot or simulator selected)
  def makewrapper(self, brainfunc, message, beforefunc=None, afterfunc=None):
    def wrapper():
      if beforefunc:
        beforefunc()
      try:
        brainfunc()
      except Exception, e:
        formerrorfile(self.file)
        sys.stderr.write(message)
        raise
      if afterfunc:
        afterfunc()
    return wrapper
  def destroy(self):
    try:
      self.braindestroy()
    except:
      formerror()
    
  def clearmodules(self, envin):
    braindir = os.path.dirname(self.file)
    for (root, dirs, files) in os.walk(braindir):
      if len(root) > len(braindir):
        # turn the root into a module path
        modpath = root[len(braindir)+1:]
        modpath = modpath.replace('.','')
        modpath = modpath.replace('/','.')
        modpath = modpath.replace('\\','.')
        # set the module path directories to point here
        if sys.modules.has_key(modpath):
          sys.modules[modpath].__path__[0] = os.path.abspath(root)
        # pop any modules that were already imported
        submods = [modpath+"."+name for (name,suffix) in \
                     [s for s in [file.split('.') for file in files] if \
                        len(s) == 2]
                   if (suffix == 'py' or suffix == 'pyc') and name[0]!='_']
        for m in submods:
          if sys.modules.has_key(m): sys.modules.pop(m)
        

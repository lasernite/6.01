##################################form/main.py###################################
# form0.1
#  / main.py
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
from collections import deque
import sys
import os
################################################################################



################################################################################
# Now we bring in the rest of form's files
#
# Warning! This must stay first to allow tk_enqueue to be globally accessed by
# the rest of the files imported
import form.common as common
import form.parallel as parallel
import form.listener as listener
import form.spicy as spicy

tk = Tk()
tk.withdraw()
tk.tk_tasks = parallel.SharedVar(deque())
tk_tasks = tk.tk_tasks
def tk_enqueue(task):
  tk_tasks.op(spicy.curried_list_appender(task)) 
def tk_recycle():
  try:
    tk.destroy()
  except:
    pass
  tk = Tk()
  tk.withdraw()

####################################Settings####################################
import form.settings as settings
settings.GUI_FPS = 20 
settings.COMMAND_PORT = 25406
GUI_FPMS_INVERSE = 1000/float(settings.GUI_FPS)

settings.apply_theme = common.skip

def tk_update():
  """This function runs at the GUI_FPS frequency. It deals with alll asynchronous calls to the single-threaded GUI. It shouldn't be called directly, only added to the after queue once right before the mainloop statement in the Application object __init__"""
  start = time()
  size = tk_tasks.const_op(len)
  while size > 0:
    tk_tasks.lock.acquire()
    try:
      size = len(tk_tasks.val)
      if size:
        task = tk_tasks.val.popleft()
    finally:
      tk_tasks.lock.release()
      if size > 0:
#        try:
#          common.debug('> %s%s%s%s%s\n' % ('*Starting:',task.func_name,'from module',task.__module__,'*'))
#        except:
#          common.debug('> %s%s\n' % ('*starting:',task))
#        task()
#        try:
#          common.debug('> %s%s%s%s%s\n' % ('*Done:',task.func_name,'from module',task.__module__,'*'))
#        except:
#          common.debug('> %s%s\n' % ('*done:',task))
        try:
          task()
        except:
          print common.formerror()
      size -= 1
  # Not sure if I want to force these through unless I'm keeping the interface
  # held down myself.
  # tk.update()
  tk.after(int(GUI_FPMS_INVERSE), tk_update)

# Other modules are going to need this, but they can't depend on main since they are about to get imported. This probably includes form extensions.
common.tk_enqueue = tk_enqueue

# (From Previous Warning) For example, widgets and formulae may need tk_enqueue
# the rest of the files imported
import form.widgets as widgets
import form.formulae as formulae
################################################################################

class Application(object):

  def alert(self, str):
    print "Alert: ", str
 
  def __init__(self, startup = common.skip):
    """The main hook to start the form GUI. This doesn't exit until the end of the program since it calls Tk's mainloop, but it's ok, since we are in a class, we just assign self to a __builtin__ name. This becomes app."""
    __builtins__['app'] = self
    self.commands = formulae.FormulaPool()
    #try:
    #  self.command_listener = listener.CommandListener(settings.COMMAND_PORT,
    #                                                   self.commands)
    #  self.command_listener.start()
    #except:
    #  pass # for now..
    tk_enqueue(self.setUpInterface)
    tk_enqueue(startup)
    tk.after(int(common.clip(GUI_FPMS_INVERSE,0,GUI_FPMS_INVERSE)),
             tk_update)
    tk.mainloop()
    return 0
  
  def __del__(self):
    try:
      self.command_listener.stop()
    except AttributeError:
      pass

  def setUpInterface(self):
    self.top = Toplevel(tk)
    self.top.wm_title('form')
    self.top.tkraise()

    self.toolbar = widgets.ToolbarFrame(self.top, self.commands)
    self.toolbar.pack(side = TOP)
    
    self.mainframe = widgets.TabbedFrame(self.top)
    self.mainframe.pack(side = BOTTOM, fill=BOTH, expand=1)

    self.tabframe = widgets.TabbedFrame(self.top)
    self.tabframe.pack(side = BOTTOM)

    settings.apply_theme(self.top)

################################################################################
#TODO: move out to settings file
    self.top.wm_iconbitmap('hourglass')
    self.top.bind('<Alt-x>', lambda e: self.minibuffer.focus_force())
  
    self.mainframe.bind('<F11>', lambda e: self.mainframe.left())
    self.mainframe.bind('<F12>', lambda e: self.mainframe.right())

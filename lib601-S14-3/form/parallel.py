################################form/parallel.py#################################
# form0.1
#  / parallel.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
from threading import Thread, Lock
from time import time, sleep

import platform
import sys

import form.common as common
import form.spicy as spicy
####################################Settings####################################
import form.settings as settings
settings.DEFAULT_STEPPER_FPS = 5
################################################################################

class PipeSyndicator(object):
  def __init__(self, pipes):
    if platform.system() in ['Windows', 'Microsoft']:
      self.pipes = [p for p in pipes if (p is not sys.stderr) and (p is not sys.stdout)]
    else:
      self.pipes = pipes

  def write(self, s):
    for pipe in self.pipes:
      pipe.write(s)

class Buffer(object):
  def __init__(self, initial = None):
    self.buffer = SharedVar(initial)

  def append(self, s):
    self.buffer.op(spicy.curried_string_appender(s))

  def read(self):
    return self.buffer.const_op(spicy.identity)

  def write(self, s):
    return self.buffer.op(spicy.thunk(s))

#TODO:
#class BufferReaderWriter(object):
#  def __init__(self, read_buf, write_buf):

class Stepper(Thread):
  def __init__(self, function, fps=settings.DEFAULT_STEPPER_FPS):
    Thread.__init__(self)
    self.function = function
    self.minstep = 1.0 / fps

  def run(self):
    self.keepgoing = SharedVar(True)
    t = time()
    numCalls = 0
    startTime  = time()
    while self.keepgoing.get():
     dt = time()-t
     origt = t
     if dt < self.minstep:
       sleep(self.minstep-dt)
       t = time()
       try:
         numCalls += 1
         self.function(self.minstep)
       except:
         common.formerror()
     else:
       try:
         t = time()
         numCalls += 1
         self.function(dt)
       except:
         common.formerror()
#    print 'thread average time: ', (time()-startTime)/numCalls

  def stop(self):
    self.keepgoing.set(False)

  def running(self):
    return self.keepgoing.get()

class SharedVar(object):
  def __init__(self, initial=None):
    self.val = initial
    self.lock = Lock()

  def get(self):
    return self.const_op(spicy.identity)

  def set(self, val):
    return self.op(lambda v: val)

  def const_op(self, operation):
    self.lock.acquire()
    try:
      val = operation(self.val)
    except:
      common.formerror()
    finally:
      self.lock.release()
    try:
      return val
    except:
      pass

  def op(self, operation):
    self.lock.acquire()
    try:
      self.oldval = self.val
      self.val = operation(self.val)
    except:
      common.formerror()
    finally:
      self.lock.release()
    return self.oldval


# Creates a threadsafe function-queue that updates every so often in its
# own thread. Set update periods carefully so not to run away with the
# processor. Also, if any operations can nullify all previous operations
# still on the queue, pass them in as the first_task_of_new_era argument
# to clear_tasks for performance gains/reliability.
#
# Example: form.widgets.DrawingFrame.clear() clears all the tasks
# on its queue, and passes in a command to delete everything on its
# drawable area as the first_task_of_new_era.
class TaskThread(Stepper):
  def __init__(self, fps=None):
    if fps:
      Stepper.__init__(self, self._chunk_tasks, fps)
    else:
      Stepper.__init__(self, self._chunk_tasks)
    self.lock = Lock()
    self.tasks = []

  #add a task to the task queue
  def add_task(self, task, returnCallback = common.skip):
    self.lock.acquire()
    try:
      self.tasks.append((task, returnCallback))
    finally:
      self.lock.release()

  #clear all tasks on the queue currently. Also, optionally guarantee the first task to be executed by the queue is the parameter first_task_of_new_era. For example:
  ######################
  # tt = TaskThread()
  #--Code fragment 1:
  # >tt.clear_tasks()
  # >tt.add_task(task)
  #--Code fragment 2:
  # >tt.clear_tasks(task)
  #######################
  #Code fragment 1 might not work how you think it will always, but Code fragment 2 will
  def clear_tasks(self, first_task_of_new_era=False, first_return_callback=common.skip):
    self.lock.acquire()
    try:
      if first_task_of_new_era:
        self.tasks = [(first_task_of_new_era, first_return_callback)]
      else:
        self.tasks = []
    finally:
      self.lock.release()

  def _chunk_tasks(self, dt=None):
    start = time()
    size = len(self.tasks)
    while size > 0 and time()-start < self.minstep:
      self.lock.acquire()
      try:
        try:
          size = len(self.tasks)
          task = self.tasks[0]
          self.tasks = self.tasks.__getslice__(1,len(self.tasks))
        except IndexError:
          pass
      finally:
        self.lock.release()
      if size:
        task[1](task[0]())

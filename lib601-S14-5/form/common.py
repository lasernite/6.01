#################################form/common.py##################################
# form0.1
#  / common.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
import os
import os.path
import sys
from traceback import format_exception
#####################################Notes######################################
# Lots of things that occur commonly all over form and may be useful to many
# generations of future python programs.
################################################################################

def skip(*n, **kw): 
  """A blank function (for null callbacks)"""
  pass

class Container(object): 
  """A blank class (for using name.element instead of name['element'])"""
  pass

# 'clip' a value between a min and a max
def clip(val, vn, vx): 
  return min(vx, max(vn, val))

# A guaranteed unique pool of names that can be bound to objects with a
# built-in mechanism for doing name collision resolution.
class NamePool(object):
  def __init__(self, initial = {}):
    self.current = initial

  def request(self, s):
    if s in self.current:
      i = 1
      while True:
        tmp = "%s<%d>" % (s, i)
        if tmp in self.current:
          i += 1
        else:
          break
      self.current[tmp] = None
      return tmp
    else:
      self.current[s] = None
      return s

  def set(self, s, o):
    if s in self.current:
      self.current[s] = o

  def release(self, s):
    if s in self.current:
      self.current.pop(s)

# for when non-GUI code is expecting a result from GUI code and it is not
# going to get quite what it wanted.
class CancelGUIAction(Exception): pass

# Default thing to spit out for any errors that occured and more information
# isn't available.
def formerror():
   if sys.exc_type == CancelGUIAction:
     widgets.error_dialog(sys.exc_value)
   else: 
     error = "".join(format_exception(sys.exc_type, 
                                      sys.exc_value, 
                                      sys.exc_traceback))
     sys.stderr.write(error)

# Replace all instances of "File "<string>"" with a real filename
# and then print the error
def formerrorfile(file):
  shortfile = file.split('/')[-1]
  error = "".join(format_exception(sys.exc_type, 
                                   sys.exc_value, 
                                   sys.exc_traceback))
  error = error.replace("File \"<string>\"", shortfile)
  sys.stderr.write(error)

def debug(str):
  os.write(0,str)

# Actually execute a code block
def do(str, env):
  try:
    val = eval(str, env)
    if val:
      print "=>", repr(val)
      return val
  except:
    try:
      exec str in env
    except:
      formerror()
    return None

def parseFile(filename, envin):
  exec "import os" in envin
  exec "import sys" in envin
  exec "if not os.getcwd() in sys.path: sys.path.append(os.getcwd())" in envin

  # Deal with windows-style line-endings.
  lines = open(filename, 'r').readlines()
  if len(lines) > 0 and '\r' in lines[0]:
    lines = [line[:-2]+line[-1:] for line in lines]
  
  # Actually execute the code. I wish we didn't have to build this up so
  # slowly, but it is necessary to remove the windows line-endings.
  linestr = "".join(lines)
  try:
    exec linestr in envin
  except Exception, e:
    formerrorfile(filename)
    raise e

################################form/formulae.py#################################
# form0.1
#  / formulae.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
import form.widgets as widgets
import form.common as common
#####################################Notes######################################
# Data type formulae:
#
#formulae are either 2-tuples (no GUI information) or 5-tuples:
# (name, command[, iconpath, longname, argumentbuilder])
#  name is the literal name of the lambda to be registered in the minibuffer
#    namespace
#  longname shows up in tooltip/provides a more accurate description
#  iconpath is path to image of an icon for this function
################################################################################

# A pool to keep formulae and dispatch on their commands in a sensible way
#
# The add_callbacks are there to propagate changes to the formula pool to other
# objects that may depend on them. The example within form is a Toolbar that
# is tied to a FormulaPool can update it's button structure when a command is
# added.
class FormulaPool(object):
  def __init__(self, *n, **kw):
    self.namespace = {}
    self.add_callbacks = []
    self.remove_callbacks = []

  def addFormula(self, formula):
    self.namespace[formula[0]] = formula[1]
    for callback in self.add_callbacks:
      callback(formula)

  def removeFormula(self, formula): 
    self.namespace.pop(formula[0])
    for callback in self.remove_callbacks:
      callback(formula)

  def callbackOnAddFormula(self, callback):
    self.add_callbacks.append(callback)
  
  def callbackOnRemoveFormula(self, callback):
    self.remove_callbacks.append(callback)

# Formula to open a new file for editing
def openFileFormula(app, tabbedparent):
  def open(fpath):
    frame = tabbedparent.addFrame(fpath.split('/')[-1])
    fileframe = widgets.FileBufferFrame(frame, 
                                        filepath = fpath, 
                                        namespace = {'app':app})
    fileframe.pack()
    return frame
  return open

################################form/settings.py#################################
# form0.1
#  / settings.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
# This is a sign that theme code needs to be moved somewhere else.. I guess widgets
from Tkinter import TclError

import form.common as common

#THEME.WINDOW_ICON="hourglass"

#TANGO STUFF:
chameleon = ["#8AE234", "#73D216", "#4E9A06", "#000000"]
skyblue = ["#729FCF", "#3465A4", "#204A87", "#FFFFFF"]
scarletred = ["#EF2929", "#CC0000", "#A40000", "#FFFFFF"]
blackwhite = ["#222222", "#111111", "#000000", "#FFFFFF"]
current_theme = {}

def select_theme(theme):
  current_theme.clear()
  current_theme['background'] = theme[2]
#  current_theme['activebackground'] = theme[1]
#  current_theme['insertborderwidth'] = theme[1]
#  current_theme['highlightforeground'] = theme[2]
  current_theme['highlightbackground'] = theme[2]
  current_theme['foreground'] = theme[3]
#  current_theme['activeforeground'] = theme[3]
#  current_theme['disabledforeground'] = theme[0]
  current_theme['highlightcolor'] = theme[1]
  current_theme['insertbackground'] = theme[3]

select_theme(skyblue)

def apply_theme(widget = 0, exclude = ['canvas'], childrenlambda = 0):
  try:
    a = widget.dontcolor
    return widget
  except AttributeError:
    pass # keep going
  for k in current_theme:
    try:
      eval('%s%s%s%s%s' % ('widget.config(',k,' = "',current_theme[k],'")'))
    except TclError:
      pass # This is ok, not all widgets have the same options
  if not childrenlambda:
    childrenlambda = widget.winfo_children
  try:
    for child in childrenlambda():
      if not child.widgetName in exclude:
        apply_theme(child, exclude)
  except TclError:
    print "uh oh, tclerrrror"
  return widget

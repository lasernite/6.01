#############################soar/serial/__init__.py#############################
# soar3.0
#  / serial/__init__.py
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
#####################################Notes######################################
# This submodule provides cross-platform serial functionality for soar
################################################################################

if os.name == "posix":
  from serialposix import Serial
elif os.name == "nt":
  from serialwin32 import Serial
else:
  raise ImportError("Can't use serial in a non win32/posix friendly environment")


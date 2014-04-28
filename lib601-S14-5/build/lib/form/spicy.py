##################################form/spicy.py##################################
# form0.1
#  / spicy.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

#####################################Notes######################################
# This file is called 'spicy' because it contains some simple functions that
# wind up getting used in quite a few different places where functional
# programming is employed. They might make the code slightly confusing in
# places, but enable a gain of generality without a loss of efficiency.
################################################################################

# object -> function(list)
# Returned function will append the argument object to its own argument list. 
def curried_list_appender(item):
  def doit(lst):
    lst.append(item)
    return lst
  return doit

# string -> function(string) 
# Returned function will append the argument string to its own argument string.
def curried_string_appender(arg):
  def doit(str):
    str = "%s%s" % (str, arg)
  return doit

# The identity function.
def identity(x):
  return x

# Make a function that returns the argument.
def thunk(x):
  def f(*n, **kw):
    return x
  return f

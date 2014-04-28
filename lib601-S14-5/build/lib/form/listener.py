################################form/listener.py#################################
# form0.1
#  / listener.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################


####################################Imports#####################################
import socket
import thread

import form.parallel as parallel
import form.common as common
####################################Settings####################################
import form.settings as settings
settings.COMMAND_SEPARATOR = chr(0) #the null terminator for strings
################################################################################

class CommandListener(parallel.Stepper):
  def __init__(self, port, command_pool):
    self.port = port
    self.command_pool = command_pool
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind(('',port))
    
    self.incomplete_command = ""
    self.connection = None
    self.connected_address = None

    def listen():
      self.socket.listen(1)
      self.connection, self.connected_address = self.socket.accept()

    thread.start_new_thread(listen,tuple())    
    parallel.Stepper.__init__(self, self.do_queued_commands)

  def do_queued_commands(self, dt):
    if self.connection:
      str = self.connection.recv(4096)
      print "'",str,"'"
      split = str.split(settings.COMMAND_SEPARATOR)
      self.incomplete_command += split[0]
      split = split[1:]
      while len(split) > 0:
        complete_command = self.incomplete_command
        common.do(complete_command, self.command_pool.namespace)
        self.incomplete_command = split[0]
        split = split[1:]


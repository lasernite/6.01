#################################form/widgets.py#################################
# form0.1
#  / widgets.py
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
from tkMessageBox import showerror, askyesno, askquestion
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import os
import platform
from types import StringType

import form.parallel as parallel
import form.spicy as spicy
import form.common as common
from form.common import CancelGUIAction
####################################Settings####################################
import form.settings as settings
settings.BUFFER_CHUNK_SIZE = 1 
settings.TAB_WIDTH = 2
################################################################################

# in case we ever want to move away from tkMessageBox
error_dialog = showerror

class MiniBuffer(Entry):
  def __init__(self, tkparent, namespace, *n, **kw):
    # don't make the width bigger than 80 or tk hangs on the mac (sometimes)
    Entry.__init__(self, tkparent, width=80)
    self.namespace = namespace
    self.cmdhistory = []
    self.stringvar = StringVar()
    self.config(textvariable = self.stringvar)
    self.curcmd = -1
    self.ctrlx = False

    self.bind("<Return>", lambda e: self.entry())
    self.bind("<Up>", lambda e: self.cycle(-1))
    self.bind("<Down>", lambda e: self.cycle(1))

  def entry(self):
    cmd = self.stringvar.get()
    self.cmdhistory.append(cmd)
    self.curcmd = len(self.cmdhistory)
    common.do(cmd, self.namespace)
    self.delete(0, END)

  def cycle(self, direction):
    #self.curcmd = common.clip(-(abs(self.curcmd)-direction), -len(self.cmdhistory)-1, -1)
    cmd = self.curcmd+direction
    if cmd >= 0 and cmd < len(self.cmdhistory):
      self.curcmd = cmd
      self.stringvar.set(self.cmdhistory[self.curcmd])
    elif cmd >= len(self.cmdhistory):
      self.curcmd = len(self.cmdhistory)
      self.stringvar.set('')

class TabbedFrame(Frame):
  def __init__(self, tkparent, *n, **kw):
    Frame.__init__(self, tkparent, *n, **kw)
    self.tabframe = Frame(self)
    self.tabframe.pack()
    self.count = 0
    self.active_tabs = {}
    self.tabs = {}
    self.names_frames = {}
    self.frames_names = {}
    self.activeframe = None
    self.namepool = common.NamePool()
    self.hidecbs = {}

  def display(self, frame):
    if isinstance(frame,StringType):
      frame = self.names_frames[frame]
    self._show(frame)

  def _show(self, frame):
    cb = self.hidecbs[self.frames_names[frame]]
    if cb is not None:
      cb()
    if frame in self.tabs:
      frame.pack(fill=X, expand=1)
    else:
      raise CancelGUIAction("Requested frame not found: ", frame)

  def _hide(self, frame):
    if frame in self.tabs:
      frame.forget()
    else:
      raise CancelGUIAction("Requested frame not found: ", frame)

  def _toggle(self, frame):
    if self.active_tabs[frame].get():
      self._show(frame)
    else:
      self._hide(frame)

  def addFrameWithHideCB(self, title, hidecb):
    ret = self.addFrame(title)
    self.hidecbs[title] = hidecb
    return ret

  def addFrame(self, title):
    self.hidecbs[title] = None
    if title in self.names_frames:
      raise CancelGUIAction("Requested frame already exists: "+title)
    frame = Frame(self)
    self.active_tabs[frame] = IntVar()
    self.names_frames[title] = frame
    self.frames_names[frame] = title
    title_text = title
    if os.name == "posix" and platform.system() == "Darwin":
      title_text = " " + title_text + " "
    tab = Checkbutton(self.tabframe,
                      text = title_text,
                      indicatoron = False,
                      variable = self.active_tabs[frame],
                      command = lambda: self._toggle(frame))
    tab.select()
    tab.pack(fill=BOTH, side=LEFT)
    self.tabs[frame] = tab
    self._show(frame)
    return frame

  def removeFrame(self, frame): 
    if isinstance(frame,StringType):
      frame = self.names_frames[frame]
    if frame in self.tabs:
      self.tabs[frame].forget()
      frame.forget()
      self.tabs.pop(frame)
      self.active_tabs.pop(frame)
      title = self.frames_names.pop(frame)
      self.namepool.release(title)
      self.names_frames.pop(title)
    else:
      raise CancelGUIAction("Requested frame not found: ", frame)

class OutputBufferFrame(Frame):
  def __init__(self, tkparent, *n, **kw):
    Frame.__init__(self, tkparent, *n, **kw)
    self.scrollbar_ = Scrollbar(self)
    self.scrollbar_.pack(side=RIGHT, fill=Y)
    # DON'T set the width any higher than 76 (or tk hangs on the mac)
    self.box_ = Text(self, height = 15, width = 76, wrap = CHAR, yscrollcommand = self.scrollbar_.set)
    self.box_.pack(fill=BOTH,expand=1)
    self.scrollbar_.config(command=self.box_.yview)

  def state(self):
    try:
      str = self.box_.get(1.0, END)[:-1]
      return str
    except TclError:
      print formerror()

  def write(self, s):
    def writer():
      self.box_.insert(END,s)
      self.box_.see(END)
    common.tk_enqueue(writer)

  def clear(self):
    self.box_.delete(1.0, END)


class ToolbarFrame(Frame):
  def __init__(self, tkparent, formulapool, *n, **kw):
    Frame.__init__(self, tkparent, *n, **kw)
    self.formulae = formulapool 
    self.formulae.callbackOnAddFormula(self.formulaWasAdded)
    self.buttons = {}

  def formulaWasAdded(self, formula):
    try:
      buttonframe = Frame(self)
      button = Button(buttonframe, command = lambda: apply(formula[1], formula[4]()))
      button.stored_images = dict([(iname, PhotoImage(file = fname))
                                   for iname,fname in formula[3].iteritems()])
      button.config(image = button.stored_images['normal'])
      button.pack(side = TOP)
      self.buttons[formula[0]] = button
      Label(buttonframe, text = formula[2]).pack(side = BOTTOM)
      buttonframe.pack(side = LEFT)
    except IndexError:
      raise common.CancelGUIAction("Cannot add formula with no GUI information to a toolbar")
  def buttonImage(self, button_name, image_name):
    button = self.buttons[button_name]
    if (image_name in button.stored_images):
      button.config(image = button.stored_images[image_name])

class FileBufferFrame(Frame):
  def __init__(self, tkparent, *n, **kw):
    try:
      self.filepath = kw.pop('filepath')
    except KeyError:
      self.filepath = None 
    try:
      self.namespace = kw.pop('namespace')
    except KeyError:
      self.namespace = {}
    Frame.__init__(self, tkparent, *n, **kw)
    self.scrollbar = Scrollbar(self)
    self.scrollbar.pack(side=RIGHT, fill=Y)
    self.box = Text(self, height = 35, width = 80, wrap = CHAR, yscrollcommand = self.scrollbar.set)
    self.box.pack()
    self.scrollbar.config(command = self.box.yview)
    if self.filepath:
      f = open(self.filepath, 'r')
      self.box.insert(END, f.read())
      f.close()
      #self.autofile = open(self.filepath+'.swp', 'w')
      #self.autosaver = parallel.Autosaver(self.buffer, self.autofile)
      if self.filepath.split('.')[-1] == 'py':
        self.box.bind("<KeyRelease>", self.onKeyRelease)
        self.box.bind("<F2>", self.esc)
        self.box.tag_config("kw", foreground="blue")
        self.box.tag_config("string", foreground="green")
        self.box.tag_config("comment", foreground="red")
        self.kw = ["and","del","from","not","while","as","elif","global","or","with","assert","else","if","pass","yield","break","except","import","print","class","exec","in","raise","continue","finally","is","return","def","for","lambda","try"]
        self.quotes = ['"""', "'''", '"', "'"] 
        self.string_literals = [] 
        self.needs_recompute = True
	self.syntax_color(None)

  def onKeyRelease(self, e):
    self.needs_recompute = ((e.char == '"' or e.char == "'"))# or 
                            #(e.char == '\x08' and 
                            # self.box.get(INSERT+"-1c") in self.quotes))
    self.syntax_color(e)

  def indexInRanges(self, index, ranges):
    for start, stop in ranges:
      if self.box.compare(index, ">=", self.box.index(start)) and self.box.compare(index, "<", self.box.index(stop)):
        return True
    return False

  def syntax_color(self, e):
    self.box.tag_remove("kw", 1.0, END)
    self.box.tag_remove("string", 1.0, END)
    self.box.tag_remove("comment", 1.0, END)
    ignore = self.computeComments()
    if self.needs_recompute:
      self.computeStringLiterals()
      self.needs_recompute = False
    strings = self.string_literals
    self.computeKeywords(ignore)

  def computeKeywords(self, ignore):
    for kw in self.kw:
      for post in [':', ' ']:
        index = '1.0'
        done = []
        while True:
          kwindex = self.box.search(kw+post, index, exact=True)
          if kwindex == "" or kwindex in done:
            break
          done.append(kwindex)
          if (not self.indexInRanges(kwindex, ignore) and
              (float(kwindex)-int(float(kwindex)) == 0 or 
               self.box.get(kwindex+"-1c") == " ")): 
            newindex = kwindex+"+"+`len(kw)`+"c"
            self.box.tag_add("kw", kwindex, newindex)
            index = newindex
          else:
            index = kwindex+"+1c"

  def computeComments(self):
    comments = []
    for char in ["#"]:
      index = '1.0'
      done = []
      while True:
        commentindex = self.box.search(char, index, exact = True)
        if commentindex == "" or commentindex in done:
          break
        done.append(commentindex)
        newindex = commentindex+" lineend"
        if not self.indexInRanges(commentindex, strings):
         self.box.tag_add("comment", commentindex, newindex)
        index = newindex 
        start = 'c0%d' % (len(strings),)
        stop = 'c1%d' % (len(strings),)
        self.box.mark_set(start, quoteindex)
        self.box.mark_set(stop, index)
        self.box.mark_gravity(stop, LEFT)
        comments.append((start, stop))
    return comments

  def computeStringLiterals(self, ignore):
    for start,stop in self.string_literals:
      self.box.mark_unset(start)
      self.box.mark_unset(stop)
    strings = []
    done = []
    for quote_char in self.quotes:
      index = '1.0'
      while True:
        quoteindex = self.box.search(quote_char, index, exact = True)
        if quoteindex == "" or quoteindex in done:
          break
        done.append(quoteindex)
        newindex = quoteindex+"+1c"
        newdone = []
        while True:
          newindex = self.box.search(quote_char, newindex, exact = True)
          if newindex == "" or not self.box.get(newindex+"-1c") == "\\" or newindex in newdone:
            break
          newdone.append(newindex)
        if newindex == "":
          break
        index = newindex+"+1c"
        if (not self.indexInRanges(quoteindex, ignore) and
            not self.indexInRanges(index, ignore)):
          start = 's0%d' % (len(ignore),)
          stop = 's1%d' % (len(ignore),)
          self.box.mark_set(start, quoteindex)
          self.box.mark_set(stop, index)
          self.box.mark_gravity(stop, LEFT)
          self.box.tag_add("string", start, stop)
          ignore.append((start, stop))
    self.string_literals = strings

  def maybetab(self, e):
    last = self.box.get(1.0,INSERT).split('\n')[-1]
    num = 0
    for i in last:
      if i == ' ':
        num += 1
      else:
        break
    if len(last) > 0 and last[-1] == ':':
      num+=settings.TAB_WIDTH
    index = float(int(float(self.box.index(INSERT)))+1)
    self.box.insert(`index`, '\n'+' '*num)
    self.box.delete(`index+num/10.0`, END)

  def esc(self, e):
    common.do(self.box.get(SEL_FIRST, SEL_LAST), self.namespace)

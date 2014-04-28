"""Virtual oscilloscope.

If ran as a script, connects to a NIDAQserver and serves as a virtual oscilloscope.
If imported as a module, exports the various components of the oscilloscope as classes.
"""

__author__ = "Karim Liman-Tinguiri <klt@mit.edu>"
__version__ = "0.1"
__date__ = "25 June 2007"

import wx
import numpy
import os
import time
import threading
import random
random.seed()

class Pusher(threading.Thread):
    """Temporary NIDAQ server client, should not be used; prone to change."""
    
    def __init__(self, oscillframe):
        threading.Thread.__init__(self)
        self.oscillframe = oscillframe
        # The easiest way to get te sample rate is simply to execute /tmp/NIDAQserver/log
        settings = {}
        log = open('/tmp/NIDAQserver/log', 'r')
        exec log.read() in settings
        self.SAMPLES_PER_CHANNEL = settings['samplesperchan']
        self.NUM_OF_CHAN = len(settings['channels'].split(', '))
        log.close()

    def run(self):
        time.sleep(1)
        while(1):
            # It's better to open and close the pipe before and after each reading
            # because it forces the OS to flush it, making sure we always get the
            # latest measurements.
            binaryStream = open("/tmp/NIDAQserver/binary", "rb")
            chunk = binaryStream.read(self.SAMPLES_PER_CHANNEL * self.NUM_OF_CHAN * 8) # NUM_OF_CHAN channels of 64 bits (8 bytes) doubles
            binaryStream.close()
            array = numpy.fromstring(chunk, numpy.float64, self.SAMPLES_PER_CHANNEL * self.NUM_OF_CHAN)
            array.shape = (array.size / self.NUM_OF_CHAN, self.NUM_OF_CHAN)
            array.sort(axis=0)
            #for line in array:
            #    try:
            #        wx.CallAfter(self.oscillframe.push, line)
            #    except:
            #        pass
            wx.CallAfter(self.oscillframe.push, array[self.SAMPLES_PER_CHANNEL // 2])
            binaryStream.close()

class OscillFrame(wx.Frame):
    """Virtual oscilloscope's top-level wxFrame.

    wxFrame composed of an OscillView widget, a slider and two spinners to configure
    the settings of the display.

    Keyword arguments:
    channels : Tuple of 3-lists [name, color, visible] describing the channels to display
               passed down to OscillWindow eventually

    Public functions:
    buildPopupMenu:         Rebuild the right-click popupmenu (when channel name changed for example).
    push(measurement):      Pushe an array of length len(channels) of data to the display.
    SetChannels(channels):  Update the channels. Make sure the next push call has the right
                            number of elements.
    

    Usage example:
    
    import random, time, threading, v_oscillo, wx

    def generateRandomSamples(oscilloscope):
        while(1):
            wx.CallAfter(oscilloscope.push,
                         [random.gauss(2, 1),
                          random.random() * 2 - 2])
            time.sleep(0.2)

    app = wx.PySimpleApp()
    oscilloscope = v_oscillo.OscillFrame((
        ["Random gaussian", "blue", True],
        ["Random uniform", "green", True]))
    oscilloscope.Show()
    threading.Thread(target = generateRandomSamples, args = (oscilloscope,)).start()
    app.MainLoop()

    """

    
    def __init__(self, channels = (["ai0", "blue", True],
                                   ["ai1", "red", True],
                                   ["ai2", "orange", True],
                                   ["ai3", "green", True],
                                   ["ai4", "magenta", False],
                                   ["ai5", "gold", False],
                                   ["ai6", "plum", False],
                                   ["ai7", "sienna", False],
                                   ["ai8", "blue", False],
                                   ["ai9", "red", False],
                                   ["ai10", "orange", False],
                                   ["ai11", "green", False],
                                   ["ai12", "magenta", False],
                                   ["ai13", "gold", False],
                                   ["ai14", "plum", False],
                                   ["ai15", "sienna", False])):
        wx.Frame.__init__(self, None, -1, "Virtual Oscilloscope", size = (640,480))
        self.channels = channels
        self.panel = wx.Panel(self)
        self._layoutWindow()
        self.buildPopupMenu()

        
    def _layoutWindow(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-1, -1])

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.oscill = OscillView(self.panel, self.channels)
        self.oscill.Bind(wx.EVT_MOTION, self._OnMove)
        self.oscill.Bind(wx.EVT_CONTEXT_MENU, self._OnShowPopup)
        self.topSizer.Add(self.oscill, 1, wx.EXPAND)
        
        self.sizer.Add(self.topSizer, 1, wx.EXPAND | wx.ALL, 8)
        self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.samplesLabel = wx.StaticText(self.panel, label = "# of samples:")
        self.bottomSizer.Add(self.samplesLabel)

        self.slider = wx.Slider(self.panel, -1, self.oscill.measuresNum,
            10, 150, style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL, self._OnChangeSampleNum, self.slider)
        self.bottomSizer.Add(self.slider, 1)

        self.samplesTxt = wx.TextCtrl(self.panel, value=str(self.oscill.measuresNum), size = (30,-1))
        self.samplesTxt.Enable(False)
        self.bottomSizer.Add(self.samplesTxt, 0, wx.LEFT | wx.RIGHT, 6)
        
        self.minLabel = wx.StaticText(self.panel, label = "Min: ")
        self.bottomSizer.Add(self.minLabel, 0, wx.LEFT, 8)

        self.minSpinner = wx.SpinCtrl(self.panel, min=-15, max=15, initial = -5, size=(40,-1))
        self.bottomSizer.Add(self.minSpinner, 0, wx.RIGHT, 6)

        self.maxLabel = wx.StaticText(self.panel, label = "Max :")
        self.bottomSizer.Add(self.maxLabel)

        self.maxSpinner = wx.SpinCtrl(self.panel, min=-15, max=15, initial = 5, size=(40,-1))
        self.bottomSizer.Add(self.maxSpinner, 0, wx.RIGHT, 6)
        self.Bind(wx.EVT_SPINCTRL, self._OnSpin)

        self.sizer.Add(self.bottomSizer, 0, wx.EXPAND)
        
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)

    def buildPopupMenu(self):
        """buildPopupMenu() --> Update the pop-up menu (usually after an update to channel properties)."""
        self.popupMenu = wx.Menu()

        def MakeBitmap(color, side=16):  # Makes a uniformly colored, 16x16 bitmap for the popup menu
            bmp = wx.EmptyBitmap(side, side)
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(color))
            dc.Clear()
            dc.SelectObject(wx.NullBitmap)
            return bmp

        for channel in self.channels:
            channelItem = wx.MenuItem(self.popupMenu, -1, channel[0])
            color = channel[2] and channel[1] or self.GetBackgroundColour()
            bitmap = MakeBitmap(color)
            channelItem.SetBitmap(bitmap)
            self.popupMenu.AppendItem(channelItem)
            self.Bind(wx.EVT_MENU, self._OnTogglePopupMenuChannel, channelItem)

        self.popupMenu.AppendSeparator()
        customizeItem = self.popupMenu.Append(-1, "Customize...")
        self.Bind(wx.EVT_MENU, self._OnCustomize, customizeItem)

    def _OnShowPopup(self, evt):
        pos = evt.GetPosition()
        pos = self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.popupMenu, pos)

    def _OnTogglePopupMenuChannel(self, evt):
        item = self.popupMenu.FindItemById(evt.GetId())
        for i in xrange(len(self.channels)):
            if self.channels[i][0] == item.GetText():
                self.channels[i][2] = not self.channels[i][2] # Toggle the item
                self.buildPopupMenu()   # Rebuild the menu accordingly

    def _OnCustomize(self, evt): # Triggered when Customize... is clicked in the popup
        CustomizeDialog(self, self.channels).Show()

    def _OnChangeSampleNum(self, evt):
        self.oscill.measuresNum = self.slider.GetValue()
        self.samplesTxt.SetValue(str(self.oscill.measuresNum))

    def _OnMove(self, evt):
        pos = evt.GetPosition()
        self.statusbar.SetStatusText("Pos: %s" % pos, 0)

    def _OnSpin(self, evt):
        # Just update both min and max
        self.oscill.minV = self.minSpinner.GetValue()
        self.oscill.maxV = self.maxSpinner.GetValue()
        self.maxSpinner.SetRange(self.minSpinner.GetValue() + 1,15)
        self.minSpinner.SetRange(-15, self.maxSpinner.GetValue() - 1)
        self.oscill._DrawGraph(wx.BufferedDC(wx.ClientDC(self.oscill),self.oscill.buffer))

    def push(self, measurement):
        """push(measurements) --> update display with latest data.

        push takes an array (or list) of 1 row and n columns where n is the number of channels and
        passes it down to OscillView for display after updating the statusbar. See OscillView's docstring.
        """
        self.oscill.push(measurement)
        statusText = ""
        for i in xrange(len(self.channels)):
            if(self.channels[i][2]):
                statusText += "%s: %04.2fV " %(self.channels[i][0], measurement[i])
        self.statusbar.SetStatusText(statusText, 1)

    def SetChannels(self, channels):
        self.channels = channels
        self.oscill.SetChannels(channels)
        self.buildPopupMen()

class CustomizeDialog(wx.Dialog):
    """ A wxDialog for customizing the colors and name of the channels. Used in conjunction with OscillFrame."""

    def __init__(self, parent, channels):
        wx.Dialog.__init__(self, parent, title="Customize channels")
        self.channels = channels
        self.parent = parent
        self._layoutDialog()

    def _layoutDialog(self):
        gridSizer = wx.GridSizer(rows=0, cols=2, vgap=8, hgap=8)

        for i in xrange(len(self.channels)):
            vSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            checkbox = wx.CheckBox(self)
            checkbox.SetValue(self.channels[i][2])
            checkbox.channelNum = i
            vSizer.Add(checkbox, 0, wx.LEFT | wx.RIGHT, 4)
            
            colorBox = ColorWindow(self, self.channels[i][1])
            colorBox.channelNum = i
            vSizer.Add(colorBox, 0, wx.LEFT | wx.RIGHT, 4)
            
            textBox = wx.TextCtrl(self, value=self.channels[i][0])
            textBox.channelNum = i
            vSizer.Add(textBox, 1, wx.LEFT | wx.RIGHT, 4)

            self.Bind(wx.EVT_CHECKBOX, self._OnToggleCheckbox)
            colorBox.Bind(wx.EVT_LEFT_DCLICK, self._OnColorDblClick, colorBox)
            self.Bind(wx.EVT_TEXT, self._OnChangeChannelName)

            gridSizer.Add(vSizer, 0, wx.ALL, 6)
        
        self.SetSizer(gridSizer)
        gridSizer.Fit(self)

    def _OnToggleCheckbox(self, evt):
        checkbox = self.FindWindowById(evt.GetId())
        self.channels[checkbox.channelNum][2] = checkbox.GetValue()
        self.parent.buildPopupMenu()    # Updates popup-menu toggled items in parent

    def _OnColorDblClick(self, evt):
        colorDlg = wx.ColourDialog(self)
        colorDlg.GetColourData().SetChooseFull(True)    #Useful under MS-Windows only
        if colorDlg.ShowModal() == wx.ID_OK:
            colorBox = self.FindWindowById(evt.GetId())
            color = colorDlg.GetColourData().GetColour()
            colorBox.SetBackgroundColour(color)
            self.channels[colorBox.channelNum][1] = color
            self.parent.buildPopupMenu()

    def _OnChangeChannelName(self, evt):
        textBox = self.FindWindowById(evt.GetId())
        self.channels[textBox.channelNum][0] = textBox.GetValue()
        self.parent.buildPopupMenu()

class ColorWindow(wx.Panel):    # A little rectangle allowing to change the color of a channel
    def __init__(self, parent, color, size=(32,16)):
        wx.Panel.__init__(self, parent, size=size, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(color)


class OscillView(wx.Panel):
    """Oscilloscope's display. See OscillFrame's docstring for a usage example.

    Keyword arguments:
    channels:       Tuple of 3-lists [name, color, visible] describing the channels to display.
                    Each call to push must pass an array (or list) of the same length as the number
                    of channel and data is pushed to each channel in the same order as they are passed.
                    See OscillView.push docstring.
    measuresNum:    Number of samples that should be shown on the screen at any given time.
    minV:           Minimum voltage shown (corresponds to bottom of display).
    maxV:           Maximum voltage shown (corresponds to top of display).
    parent:         The parent wxWindow.

    Public functions:
    DisableChannel(channel):                Hide a channel.
    EnableChannel(channel, enable=True):    Toggle a channel's visibility to enable.
    push(measurements):     Update the display based on new data passed as an array or list of same dimension as the
                            number of channels

    """
    
    def __init__(self, parent, channels, measuresNum = 100, minV = -5, maxV = 5):
        wx.Panel.__init__(self, parent, size=(512,384))
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        
        self.measuresNum = measuresNum
        self.minV = minV
        self.maxV = maxV
        self.channels = channels
        
        self.data = [[] for channel in self.channels]
        self._InitBuffer()

    def EnableChannel(channel, enable=True):
        self.channels[channel][1] = enable

    def DisableChannel(channel):
        self.EnableChannel(channel, False)

    def _InitBuffer(self):
        w, h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w, h)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self._DrawGraph(dc)


    def _DrawGraph(self, dc):
        w, h = dc.GetSize()
        dc.SetBackground(wx.Brush('white'))
        dc.Clear()

        #Draw border
        dc.SetPen(wx.Pen("black", 1))
        dc.DrawLine(0,0,w-1,0)
        dc.DrawLine(w-1,0,w-1,h-1)
        dc.DrawLine(w-1,h-1,0,h-1)
        dc.DrawLine(0,h-1,0,0)

        #Draw 6.01
        dc.SetTextForeground("pink")
        dc.SetFont(wx.Font(min(w/6,h/4), wx.DEFAULT, wx.NORMAL, wx.LIGHT))
        tw, th = dc.GetTextExtent("6.01")
        dc.DrawText("6.01", (w-tw)/2, (h-th)/2)
        
        # Set the spacing as near as possible to 20x20
        def round(x):
            import math
            if(x - math.floor(x) < 0.5): return math.floor(x)
            else: return math.ceil(x)
        target_size = 25.0
        spacing = (h / round(h / target_size))
        

        #Draw horizontal lines
        dc.SetPen(wx.Pen("black", 1, wx.DOT))
        curPos = h
        while(curPos > 0):
            dc.DrawLine(0, curPos, w-1, curPos)
            curPos -= spacing

        #Draw vertical lines using the same spacing
        curPos = w
        while(curPos > 0):
            dc.DrawLine(curPos, 0, curPos, h - 1)
            curPos -= spacing

        #Converts a voltage to an alitutde on the display
        voltageToClient = lambda v,h: (h / (self.minV - self.maxV)) * v + h * self.maxV / (self.maxV - self.minV)

        hspacing = float(w) / (self.measuresNum - 1)

        #Draw a single channel
        def DrawChannel(channelNumber):
            if(len(self.data[channelNumber]) > 1):
                dc.SetPen(wx.Pen(self.channels[channelNumber][1], 1, wx.SOLID))
                for i in xrange(len(self.data[channelNumber]) - 1):
                    dc.DrawLine( -i * hspacing + w, voltageToClient(self.data[channelNumber][i],h),
                                 - (i + 1) * hspacing + w, voltageToClient(self.data[channelNumber][i+1],h))

        for i in xrange(len(self.data)):
            if(self.channels[i][2] == True):    # Draw only active channels
                DrawChannel(i)
    
    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer)

    def _OnSize(self, evt):
        self._InitBuffer()

    def push(self, measurements):
        """push(measurements) --> Update the display based on a new set of samples.

        Takes a list (or 1-D numpy array) of the same length as the number of channels, shifts all previous data to the left
        (removing data older than measuresNum samples away if needed) and adds a new set of sample to the right
        of the display.
        """
        for i in xrange(len(measurements)):
            self.data[i].insert(0, measurements[i])
        for i in xrange(len(self.data)):
            if(len(self.data[i]) > self.measuresNum):
                self.data[i] = self.data[i][:self.measuresNum]
        self._DrawGraph(wx.BufferedDC(wx.ClientDC(self),self.buffer))

    def SetChannels(self, channels):
        self.channels = channels

def run_oscillo():
    app = wx.PySimpleApp()
    oscillframe = OscillFrame()
    Pusher(oscillframe).start()
    oscillframe.Show()
    try:
        app.MainLoop()
    except:
        pass

if __name__ == '__main__':
    run_oscillo()

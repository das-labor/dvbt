#
#    DVB-T Encoder written in python and opencl
#    Copyright (C) 2012  Patrick Rudolph <siro@das-labor.org>
#
#    This program is free software; you can redistribute it and/or modify it under the terms 
#    of the GNU General Public License as published by the Free Software Foundation; either version 3 
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; 
#    if not, see <http://www.gnu.org/licenses/>.

import wx
import pyopencl as cl
import DVBT


########################################################################
class TabPaneldvbtSettings(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.bandwidth = 8.0
        self.coderate = 0.5
        self.odfmmode = 8192
        self.odfmcarriers = 6817
        self.odfmuseablecarriers = 6048
        self.guardinterval = 0.25
        self.modulation = 2
        self.alpha = 1
        self.ffmpegargs = ""
        self.ffmpeginputfile = ""
        self.computedevice = ""
        self.cellid = 0

        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        #self.logger = wx.TextCtrl(self, pos=(340,20), size=(290,240), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # label cell ID
        self.lblcellID = wx.StaticText(self, label="cell ID", pos=(10,30))
        self.editcellID = wx.TextCtrl(self, value="0", pos=(220, 30), size=(100,-1))

        # the combobox Control code rate
        self.coderateList = ['1/2', '2/3']  # TODO: ['3/4', '5/6', '7/8']
        self.lblcoderate = wx.StaticText(self, label="Puncturing pattern", pos=(10, 60))
        self.editcoderate = wx.ComboBox(self, pos=(220, 60), size=(95, -1), choices=self.coderateList, style=wx.CB_READONLY, value="1/2")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxcoderate, self.editcoderate)

	# the combobox Control ofdm mode
        self.ofdmmodeList = ['8K mode', '2K mode']
        self.lblofdmmode = wx.StaticText(self, label="OFDM mode", pos=(10, 90))
        self.editofdmmode = wx.ComboBox(self, pos=(220, 90), size=(95, -1), choices=self.ofdmmodeList, style=wx.CB_READONLY, value="8K mode")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxofdmmode, self.editofdmmode)

	# the combobox Control ofdm channel bandwidth
        self.channelbandwidthList = ['8Mhz', '7Mhz', '6Mhz']
        self.lblchannelbandwidth = wx.StaticText(self, label="channel bandwidth", pos=(10, 120))
        self.editchannelbandwidth = wx.ComboBox(self, pos=(220, 120), size=(95, -1), choices=self.channelbandwidthList, style=wx.CB_READONLY, value="8Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannelbandwidth, self.editchannelbandwidth)

	# the combobox Control Guard interval
        self.guardintervalList = ['1/4', '1/8', '1/16', '1/32']
        self.lblguardinteraval = wx.StaticText(self, label="OFDM Guard interval", pos=(10, 150))
        self.editguardinteraval = wx.ComboBox(self, pos=(220, 150), size=(95, -1), choices=self.guardintervalList, style=wx.CB_READONLY, value="1/4")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxguardinteraval, self.editguardinteraval)

	# the combobox Control modulation        
        self.modulationList = ['QPSK', '16-QAM', '64-QAM']
        self.lblmodulation = wx.StaticText(self, label="OFDM modulation", pos=(10, 180))
        self.editmodulation = wx.ComboBox(self, pos=(220, 180), size=(95, -1), choices=self.modulationList, style=wx.CB_READONLY, value="QPSK")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxmodulation, self.editmodulation)

	# the combobox Control modulation alpha        
        self.alphaList = ['1'] # TODO: ['2', '4']
        self.lblalpha = wx.StaticText(self, label="OFDM modulation alpha", pos=(10, 210))
        self.editalpha = wx.ComboBox(self, pos=(220, 210), size=(95, -1), choices=self.alphaList, style=wx.CB_READONLY, value="1")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxalpha, self.editalpha)


        # label X displays
        self.lblX11displays = wx.StaticText(self, label="X11 displays:", pos=(10, 490))

	# the combobox channel list
        self.x11displays = ['bla']
        #platform = pyglet.window.get_platform()
        #display = platform.get_default_display()
        #for displaystring in [':0.0',':0.1',':0.2']:
            #try:
                #display = platform.get_display(displaystring)
                #for screen in display.get_screens():
                    #self.x11displays.append("%s" % screen)
            #except:
                #break
        #if len(self.x11displays) == 0:
           #print "Error, no X11 display found"
           #return
        self.editx11displays = wx.ComboBox(self, pos=(220, 480), size=(400, -1), choices=self.x11displays, style=wx.CB_READONLY, value=self.x11displays[0])
        self.Bind(wx.EVT_COMBOBOX, self.Evtx11displays, self.editx11displays)


        self.Bind(wx.EVT_CLOSE, self.EvtClose)

        self.updateGlobalSettings()

    def EvtComboBoxcoderate(self, event):
        if event.GetString() == "1/2":
            self.coderate = 0.5
        if event.GetString() == "2/3":
            self.coderate = 2.0 / 3.0
        if event.GetString() == "3/4":
            self.coderate = 0.75
        if event.GetString() == "5/6":
            self.coderate = 5.0 / 6.0
        if event.GetString() == "7/8":
            self.coderate = 0.875
        self.updateGlobalSettings()

    def EvtComboBoxofdmmode(self, event):
        if event.GetString() == "8K mode":
            self.odfmmode = 8192
            self.odfmuseablecarriers = 6048
        if event.GetString() == "2K mode":
            self.odfmmode = 2048
            self.odfmuseablecarriers = 1512
        self.updateGlobalSettings()

    def EvtComboBoxchannelbandwidth(self, event):
        if event.GetString() == "8Mhz":
            self.bandwidth = 8
        if event.GetString() == "7Mhz":
            self.bandwidth = 7
        if event.GetString() == "6Mhz":
            self.bandwidth = 6
        self.updateGlobalSettings()

    def EvtComboBoxguardinteraval(self, event):
        if event.GetString() == "1/4":
            self.guardinterval = 0.25
        if event.GetString() == "1/8":
            self.guardinterval = 0.125
        if event.GetString() == "1/16":
            self.guardinterval = 0.0625
        if event.GetString() == "1/32":
            self.guardinterval = 0.03125
        self.updateGlobalSettings()

    def EvtComboBoxmodulation(self, event):
        if event.GetString() == "QPSK":
            self.modulation = 2
        if event.GetString() == "16-QAM":
            self.modulation = 4
        if event.GetString() == "64-QAM":
            self.modulation = 6
        self.updateGlobalSettings()

        
    def Evtx11displays(self, event):
        self.x11displaystring = event.GetString()
        #self.logger.AppendText("new X11 screen selected : %s\n" % event.GetString())

    def EvtComboBoxalpha(self, event):
        self.alpha = int(event.GetString())


    #def EvtText(self, event):
        #self.logger.AppendText('EvtText: %s\n' % event.GetString())


    def EvtClose(self, event):
        self.Destroy()

    def EvtCheckBox(self, event):
        #self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())
        print "blah"
        
    def updateGlobalSettings(self):
        ctx = None
        if self.computedevice == "":
            ctx = cl.create_some_context(interactive=False)
        else:
            for any_platform in cl.get_platforms():
                for found_device in any_platform.get_devices():
                    if found_device.name == self.computedevice:
                        ctx = cl.Context(devices=found_device)
                        break

        self.dvbt_encoder = DVBT.Encoder(ctx, self.odfmmode, self.bandwidth, self.modulation, self.coderate, self.guardinterval, self.alpha, self.cellid)

        self.symbolrate = self.dvbt_encoder.get_symbolrate()
        self.usablebitrate = self.dvbt_encoder.get_usablebitrate()

        #self.logger.AppendText("New Settings:\n")

        #self.logger.AppendText("Usable Bitrate: %sbit/sec\n" % self.toUnits(self.usablebitrate))
        #self.logger.AppendText("Channel symbolRate: %sS/sec\n" % self.toUnits(self.symbolrate))

    def toUnits(self, value):
        if value > 1000000:
            return "%4.3f M" % (value / 1000000)
        if value > 1000:
            return "%4.3f k" % (value / 1000)
        if value < 0.001:
            return "%4.3f u" % (value * 1000000)
        if value < 1:
            return "%4.3f m" % (value * 1000)
        return "%4.3f" % value
        
########################################################################
class TabPanelMain(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
         
        self.cbffmpeg = wx.CheckBox(self, -1, 'encode input stream using ffmpeg', (10, 30))
        self.cbffmpeg.SetValue(True)
       
        self.rb1 = wx.RadioButton(self, -1, 'write to file/fifo', (10, 90), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, -1, 'output using opengl', (10, 120))

        self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb1.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb2.GetId())

        # label input file name
        self.lblffmpegargs = wx.StaticText(self, label="input file:", pos=(10, 150))
        
        # text box for input file name
        self.TextCtrlinputfile = wx.TextCtrl(self, pos=(90,150), size=(300,-1), value="" , style=wx.TE_READONLY)
        
        # the button choose input file
        self.buttoninputfile =wx.Button(self, label="Choose input file", pos=(20, 180))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonInput,self.buttoninputfile)
        
        # label output file name
        self.lblffmpegargs = wx.StaticText(self, label="output file:", pos=(10, 230))
        
        # text box for output file name
        self.TextCtrloutputfile = wx.TextCtrl(self, pos=(90,230), size=(300,-1), value="" , style=wx.TE_READONLY)
        
        # the button choose output file
        self.buttonoutputfile =wx.Button(self, label="Choose output file", pos=(20, 260))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonOutput,self.buttonoutputfile)
	
        # the button (re)start
        self.buttonstart =wx.Button(self, label="(Re)Start", pos=(420, 300))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonStart,self.buttonstart)
        
    def OnClickButtonStart(self,event):
        #self.cellid = int(self.editcellID.GetValue())
        #self.dvbt_encoder.run()
        print "blah"
        
    def SetVal(self, event):
        print "blub"
        
    def OnClickButtonInput(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    self.inputfile = dialog.GetPath()
            self.TextCtrlinputfile.SetValue(self.inputfile)
	dialog.Destroy()
	
    def OnClickButtonOutput(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    self.outputfile = dialog.GetPath()
            self.TextCtrloutputfile.SetValue(self.outputfile)
	dialog.Destroy()

########################################################################
class TabPanelffmpegSettings(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        # label ffmpeg additional args
        self.lblffmpegargs = wx.StaticText(self, label="additional arguments:", pos=(10, 30))

        # text box for additional ffmpeg args
        self.TextCtrlffmpegaddargs = wx.TextCtrl(self, pos=(150,30), size=(300,-1), value="")
        self.Bind(wx.EVT_TEXT, self.EvtTextffmpegargs, self.TextCtrlffmpegaddargs)
        

        self.lblsp= wx.StaticText(self, label="service_provider:", pos=(10, 60))
        self.TextCtrlffmpegserviceprovider = wx.TextCtrl(self, pos=(150,60), size=(300,-1), value="")
        #self.Bind(wx.EVT_TEXT, self.EvtTextffmpegargs, self.TextCtrlffmpegserviceprovider)
        
        self.lblsn = wx.StaticText(self, label="service_name:", pos=(10, 90))
        self.TextCtrlffmpegservicename = wx.TextCtrl(self, pos=(150,90), size=(300,-1), value="")
        #self.Bind(wx.EVT_TEXT, self.EvtTextffmpegargs, self.TextCtrlffmpegservicename)
        
        self.lblsid = wx.StaticText(self, label="service_id:", pos=(10, 120))
        self.TextCtrlffmpegserviceid = wx.TextCtrl(self, pos=(150,120), size=(300,-1), value="")
        
        self.lblbr = wx.StaticText(self, label="Stream Bitrate:", pos=(10, 150))
        self.TextCtrlffmpegbitrate = wx.TextCtrl(self, pos=(150,150), size=(300,-1), value="")
        #self.Bind(wx.EVT_TEXT, self.EvtTextffmpegargs, self.TextCtrlffmpegserviceid)

    def EvtTextffmpegargs(self, event):
        self.ffmpegargs = event.GetString()


########################################################################
class TabPanelradioSettings(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.channelarray = ["21	474Mhz","22	482Mhz","23	490Mhz","24	498Mhz","25	506Mhz","26	514Mhz","27	522Mhz","28	530Mhz","29	538Mhz","30	546Mhz","31	554Mhz","32	562Mhz","33	570Mhz","34	578Mhz","35	586Mhz","36	594Mhz","37	602Mhz","38	610Mhz","39	618Mhz","40	626Mhz","41	634Mhz","42	642Mhz","43	650Mhz","44	658Mhz","45	666Mhz","46	674Mhz","47	682Mhz","48	690Mhz","49	698Mhz","50	706Mhz","51	714Mhz","52	722Mhz","53	730Mhz","54	738Mhz","55	746Mhz","56	754Mhz","57	762Mhz","58	770Mhz","59	778Mhz","60	786Mhz","61	794Mhz","62	802Mhz","63	810Mhz","64	818Mhz","65	826Mhz","66	834Mhz","67	842Mhz","68	850Mhz","69	858Mhz"]

        # label channel list
        self.lblchannel = wx.StaticText(self, label="UHF channel:", pos=(10, 30))

	# the combobox channel list
        self.editchannellist = wx.ComboBox(self, pos=(220, 30), size=(300, -1), choices=self.channelarray, style=wx.CB_READONLY, value="60	786Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannellist, self.editchannellist)

    def EvtComboBoxchannellist(self, event):
        #self.computedevice = event.GetString().split(':')[1].strip()
        #self.logger.AppendText("new radio settings: %s\n" % event.GetString())
        print "blah"
        
########################################################################
class TabPanelopenclsettings(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        # label Compute Platform
        self.lblcomputedevice = wx.StaticText(self, label="Compute Platform:", pos=(10, 30))

        # label Compute Device
        self.lblcomputedevice = wx.StaticText(self, label="Compute Device:", pos=(10, 60))

        computedeviceList = []
        clplatformList = []

        for any_platform in cl.get_platforms():
            clplatformList.append(any_platform.name)
            
        self.clplatform = clplatformList[0]
        
        for any_platform in cl.get_platforms():
            for found_device in any_platform.get_devices():
                if found_device.type == 4 :
                    computedeviceList.append("GPU: %s" % found_device.name)
                if found_device.type == 2 :
                    computedeviceList.append("CPU: %s" % found_device.name)
            break

	# the combobox cl platform
        self.editclplatform = wx.ComboBox(self, pos=(160, 30), size=(350, -1), choices=clplatformList, style=wx.CB_READONLY, value=clplatformList[0])
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxclplatform, self.editclplatform)

	# the combobox compute devices
        self.editcomputedevice = wx.ComboBox(self, pos=(160, 60), size=(350, -1), choices=computedeviceList, style=wx.CB_READONLY, value=computedeviceList[0])
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxcomputedevice, self.editcomputedevice)
        
    def EvtComboBoxclplatform(self, event):
       self.clplatform = event.GetString()
       
       computedeviceList = []
               
       for any_platform in cl.get_platforms():
       	   if any_platform.name == self.clplatform:
               for found_device in any_platform.get_devices():
                   if found_device.type == 4 :
                       computedeviceList.append("GPU: %s" % found_device.name)
                   if found_device.type == 2 :
                       computedeviceList.append("CPU: %s" % found_device.name)
               break
       self.editcomputedevice.choices = computedeviceList

    def EvtComboBoxcomputedevice(self, event):
       self.computedevice = event.GetString().split(':')[1].strip()
       

########################################################################
class Notebookdvbt(wx.Notebook):
    """
    Notebook class
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        # Create the first tab and add it to the notebook
        tabOne = TabPanelMain(self)
        tabOne.SetBackgroundColour("Gray")
        self.AddPage(tabOne, "Main")

        # Create and add the second tab
        tabTwo = TabPaneldvbtSettings(self)
        self.AddPage(tabTwo, "DVBT Settings")
        
        # Create and add the third tab
        tabThree = TabPanelffmpegSettings(self)
        self.AddPage(tabThree, "ffmpeg settings")
        
        # Create and add the fours tab
        tabFour = TabPanelopenclsettings(self)
        self.AddPage(tabFour, "OpenCL settings")
        
                # Create and add the fives tab
        tabFive = TabPanelradioSettings(self)
        self.AddPage(tabFive, "radio settings")


        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

########################################################################
class TabFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "DVBT Encoder GUI",
                          size=(600,400)
                          )
        panel = wx.Panel(self)

        notebook = Notebookdvbt(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = TabFrame()
    #frame = wx.Frame(None,-1,"Main Control",size = (650, 550))
    #panel = MainPanel(frame)
    #frame.Show()
    app.MainLoop()

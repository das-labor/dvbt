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
import pyglet
import DVBT

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.lblOFDMsettings = wx.StaticText(self, label="OFDM settings:", pos=(20, 20))
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

        self.channelarray = ["21	474Mhz","22	482Mhz","23	490Mhz","24	498Mhz","25	506Mhz","26	514Mhz","27	522Mhz","28	530Mhz","29	538Mhz","30	546Mhz","31	554Mhz","32	562Mhz","33	570Mhz","34	578Mhz","35	586Mhz","36	594Mhz","37	602Mhz","38	610Mhz","39	618Mhz","40	626Mhz","41	634Mhz","42	642Mhz","43	650Mhz","44	658Mhz","45	666Mhz","46	674Mhz","47	682Mhz","48	690Mhz","49	698Mhz","50	706Mhz","51	714Mhz","52	722Mhz","53	730Mhz","54	738Mhz","55	746Mhz","56	754Mhz","57	762Mhz","58	770Mhz","59	778Mhz","60	786Mhz","61	794Mhz","62	802Mhz","63	810Mhz","64	818Mhz","65	826Mhz","66	834Mhz","67	842Mhz","68	850Mhz","69	858Mhz"]

        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, pos=(340,20), size=(290,240), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # the button (re)start
        self.buttonstart =wx.Button(self, label="(Re)Start", pos=(520, 400))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonStart,self.buttonstart)

        # label cell ID
        self.lblcellID = wx.StaticText(self, label="cell ID", pos=(10,60))
        self.editcellID = wx.TextCtrl(self, value="0", pos=(220, 60), size=(100,-1))

        # the combobox Control code rate
        self.coderateList = ['1/2', '2/3']  # TODO: ['3/4', '5/6', '7/8']
        self.lblcoderate = wx.StaticText(self, label="Puncturing pattern", pos=(10, 90))
        self.editcoderate = wx.ComboBox(self, pos=(220, 90), size=(95, -1), choices=self.coderateList, style=wx.CB_READONLY, value="1/2")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxcoderate, self.editcoderate)

	# the combobox Control ofdm mode
        self.ofdmmodeList = ['8K mode', '2K mode']
        self.lblofdmmode = wx.StaticText(self, label="OFDM mode", pos=(10, 120))
        self.editofdmmode = wx.ComboBox(self, pos=(220, 120), size=(95, -1), choices=self.ofdmmodeList, style=wx.CB_READONLY, value="8K mode")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxofdmmode, self.editofdmmode)

	# the combobox Control ofdm channel bandwidth
        self.channelbandwidthList = ['8Mhz', '7Mhz', '6Mhz']
        self.lblchannelbandwidth = wx.StaticText(self, label="channel bandwidth", pos=(10, 150))
        self.editchannelbandwidth = wx.ComboBox(self, pos=(220, 150), size=(95, -1), choices=self.channelbandwidthList, style=wx.CB_READONLY, value="8Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannelbandwidth, self.editchannelbandwidth)

	# the combobox Control Guard interval
        self.guardintervalList = ['1/4', '1/8', '1/16', '1/32']
        self.lblguardinteraval = wx.StaticText(self, label="OFDM Guard interval", pos=(10, 180))
        self.editguardinteraval = wx.ComboBox(self, pos=(220, 180), size=(95, -1), choices=self.guardintervalList, style=wx.CB_READONLY, value="1/4")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxguardinteraval, self.editguardinteraval)

	# the combobox Control modulation        
        self.modulationList = ['QPSK', '16-QAM', '64-QAM']
        self.lblmodulation = wx.StaticText(self, label="OFDM modulation", pos=(10, 210))
        self.editmodulation = wx.ComboBox(self, pos=(220, 210), size=(95, -1), choices=self.modulationList, style=wx.CB_READONLY, value="QPSK")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxmodulation, self.editmodulation)

	# the combobox Control modulation alpha        
        self.alphaList = ['1'] # TODO: ['2', '4']
        self.lblalpha = wx.StaticText(self, label="OFDM modulation alpha", pos=(10, 240))
        self.editalpha = wx.ComboBox(self, pos=(220, 240), size=(95, -1), choices=self.alphaList, style=wx.CB_READONLY, value="1")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxalpha, self.editalpha)

        # label ffmpeg settings
        self.lblffmpegsettings = wx.StaticText(self, label="ffmpeg settings:", pos=(20, 290))

        # label ffmpeg additional args
        self.lblffmpegargs = wx.StaticText(self, label="additional arguments:", pos=(10, 310))

        # text box for additional ffmpeg args
        self.TextCtrlffmpegaddargs = wx.TextCtrl(self, pos=(220,310), size=(300,-1), value="")
        self.Bind(wx.EVT_TEXT, self.EvtTextffmpegargs, self.TextCtrlffmpegaddargs)

        # text box for ffmpeg -i file path
        self.TextCtrlffmpegfilename = wx.TextCtrl(self, pos=(220,340), size=(300,-1), value="" , style=wx.TE_READONLY)

        # the button open file
        self.buttonopenfile =wx.Button(self, label="Open File", pos=(30, 340))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonOpen,self.buttonopenfile)

        # label openclsettings
        self.lblopencl = wx.StaticText(self, label="opencl settings:", pos=(20, 380))

        # label Compute Device
        self.lblcomputedevice = wx.StaticText(self, label="Compute Device:", pos=(10, 400))

        computedeviceList = []
        clplatformList = []

        for any_platform in cl.get_platforms():
            clplatformList.append(any_platform.name)
            for found_device in any_platform.get_devices():
                if found_device.type == 4 :
                    computedeviceList.append("GPU: %s" % found_device.name)
                if found_device.type == 2 :
                    computedeviceList.append("CPU: %s" % found_device.name)
            break

	# the combobox cl platform
        self.editclplatform = wx.ComboBox(self, pos=(220, 370), size=(300, -1), choices=clplatformList, style=wx.CB_READONLY, value=clplatformList[0])
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxclplatform, self.editclplatform)

	# the combobox compute devices
        self.editcomputedevice = wx.ComboBox(self, pos=(220, 400), size=(300, -1), choices=computedeviceList, style=wx.CB_READONLY, value=computedeviceList[0])
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxcomputedevice, self.editcomputedevice)
 
        # label radiosettings
        self.lblradio = wx.StaticText(self, label="radio settings:", pos=(20, 420))

        # label channel list
        self.lblchannel = wx.StaticText(self, label="UHF channel:", pos=(10, 450))

	# the combobox channel list
        self.editchannellist = wx.ComboBox(self, pos=(220, 440), size=(300, -1), choices=self.channelarray, style=wx.CB_READONLY, value="60	786Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannellist, self.editchannellist)

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

    def EvtComboBoxchannellist(self, event):
        #self.computedevice = event.GetString().split(':')[1].strip()
        self.logger.AppendText("new radio settings: %s\n" % event.GetString())

    def Evtx11displays(self, event):
        self.x11displaystring = event.GetString()
        self.logger.AppendText("new X11 screen selected : %s\n" % event.GetString())

    def EvtComboBoxclplatform(self, event):
       self.clplatform = event.GetString()
       self.logger.AppendText("Opencl Platform: %s\n" % self.clplatform)

    def EvtComboBoxcomputedevice(self, event):
       self.computedevice = event.GetString().split(':')[1].strip()
       self.logger.AppendText("Opencl compute device: %s\n" % self.computedevice)

    def EvtComboBoxalpha(self, event):
        self.alpha = int(event.GetString())

    def OnClickButtonStart(self,event):
        self.cellid = int(self.editcellID.GetValue())
        self.dvbt_encoder.run()

    def OnClickButtonOpen(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    self.ffmpeginputfile = dialog.GetPath()
            self.TextCtrlffmpegfilename.SetValue(self.ffmpeginputfile)
	dialog.Destroy()

    #def EvtText(self, event):
        #self.logger.AppendText('EvtText: %s\n' % event.GetString())

    def EvtTextffmpegargs(self, event):
        self.ffmpegargs = event.GetString()

    def EvtClose(self, event):
        self.Destroy()

    def EvtCheckBox(self, event):
        self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())

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

        self.logger.AppendText("New Settings:\n")

        self.logger.AppendText("Usable Bitrate: %sbit/sec\n" % self.toUnits(self.usablebitrate))
        self.logger.AppendText("Channel symbolRate: %sS/sec\n" % self.toUnits(self.symbolrate))

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

if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None,-1,"Main Control",size = (650, 550))
    panel = MainPanel(frame)
    frame.Show()
    app.MainLoop()

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
import ffmpeg

class MainPanel(wx.Panel):
    def __init__(self, parent, globalsettings,eventstart,eventstop,lock):
        wx.Panel.__init__(self, parent)
	self.globalsettings = globalsettings
        self.lblOFDMsettings = wx.StaticText(self, label="OFDM settings:", pos=(20, 20))
        self.eventstart = eventstart
        self.eventstop = eventstop
        self.lock = lock
        self.globalsettings.bandwidth = 8.0
        self.globalsettings.coderate = 0.5
        self.globalsettings.odfmmode = 8192
        self.globalsettings.odfmcarriers = 6817
        self.globalsettings.odfmuseablecarriers = (self.globalsettings.odfmcarriers - 809)
        self.globalsettings.guardinterval = 0.25
        self.globalsettings.modulation = 2
        self.globalsettings.alpha = 1
        self.globalsettings.ffmpegargs = ""
        self.globalsettings.ffmpeginputfile = ""
        self.globalsettings.computedevice = ""
        self.globalsettings.cellid = 0

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

        self.computedeviceList = []
        try:
           for any_platform in cl.get_platforms():
              for found_device in any_platform.get_devices():
                 if found_device.type == 4 :
                    self.computedeviceList.append("GPU: %s" % found_device.name)
                 if found_device.type == 2 :
                    self.computedeviceList.append("CPU: %s" % found_device.name)
        except ValueError:
           self.computedeviceList.append("Error, opencl isn't available")

	# the combobox compute devices
        self.editcomputedevice = wx.ComboBox(self, pos=(220, 400), size=(300, -1), choices=self.computedeviceList, style=wx.CB_READONLY, value="")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxcomputedevice, self.editcomputedevice)
 
        # label radiosettings
        self.lblradio = wx.StaticText(self, label="radio settings:", pos=(20, 420))

        # label channel list
        self.lblchannel = wx.StaticText(self, label="UHF channel:", pos=(10, 440))

	# the combobox channel list
        self.editchannellist = wx.ComboBox(self, pos=(220, 440), size=(300, -1), choices=self.channelarray, style=wx.CB_READONLY, value="60	786Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannellist, self.editchannellist)



        self.Bind(wx.EVT_CLOSE, self.EvtClose)

        self.updateGlobalSettings()

    def EvtRadioBox(self, event):
        self.logger.AppendText('EvtRadioBox: %d\n' % event.GetInt())

    def EvtComboBoxcoderate(self, event):
        if event.GetString() == "1/2":
            self.globalsettings.coderate = 0.5
        if event.GetString() == "2/3":
            self.globalsettings.coderate = 2.0 / 3.0
        if event.GetString() == "3/4":
            self.globalsettings.coderate = 0.75
        if event.GetString() == "5/6":
            self.globalsettings.coderate = 5.0 / 6.0
        if event.GetString() == "7/8":
            self.globalsettings.coderate = 0.875
        self.updateGlobalSettings()

    def EvtComboBoxofdmmode(self, event):
        if event.GetString() == "8K mode":
            self.globalsettings.odfmmode = 8192
            self.globalsettings.odfmuseablecarriers = (6817 - 809)
        if event.GetString() == "2K mode":
            self.globalsettings.odfmmode = 2048
            self.globalsettings.odfmuseablecarriers = (1704 - 203)
        self.updateGlobalSettings()

    def EvtComboBoxchannelbandwidth(self, event):
        if event.GetString() == "8Mhz":
            self.globalsettings.bandwidth = 8
        if event.GetString() == "7Mhz":
            self.globalsettings.bandwidth = 7
        if event.GetString() == "6Mhz":
            self.globalsettings.bandwidth = 6
        self.updateGlobalSettings()

    def EvtComboBoxguardinteraval(self, event):
        if event.GetString() == "1/4":
            self.globalsettings.guardinterval = 0.25
        if event.GetString() == "1/8":
            self.globalsettings.guardinterval = 0.125
        if event.GetString() == "1/16":
            self.globalsettings.guardinterval = 0.0625
        if event.GetString() == "1/32":
            self.globalsettings.guardinterval = 0.03125
        self.updateGlobalSettings()

    def EvtComboBoxmodulation(self, event):
        if event.GetString() == "QPSK":
            self.globalsettings.modulation = 2
        if event.GetString() == "16-QAM":
            self.globalsettings.modulation = 4
        if event.GetString() == "64-QAM":
            self.globalsettings.modulation = 6
        self.updateGlobalSettings()

    def EvtComboBoxchannellist(self, event):
        #self.globalsettings.computedevice = event.GetString().split(':')[1].strip()
        self.logger.AppendText("new radio settings: %s\n" % event.GetString())
        #self.updateGlobalSettings()

    def EvtComboBoxcomputedevice(self, event):
       self.globalsettings.computedevice = event.GetString().split(':')[1].strip()
       self.logger.AppendText("Opencl compute device: %s\n" % self.globalsettings.computedevice)

    def EvtComboBoxalpha(self, event):
        self.globalsettings.alpha = int(event.GetString())

    def OnClickButtonStart(self,event):
        self.globalsettings.cellid = int(self.editcellID.GetValue())
        self.eventstart.set()

    def OnClickButtonOpen(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    self.globalsettings.ffmpeginputfile = dialog.GetPath()
            self.TextCtrlffmpegfilename.SetValue(self.globalsettings.ffmpeginputfile)
	dialog.Destroy()

    #def EvtText(self, event):
        #self.logger.AppendText('EvtText: %s\n' % event.GetString())

    def EvtTextffmpegargs(self, event):
        self.globalsettings.ffmpegargs = event.GetString()

    def EvtClose(self, event):
        self.eventstop.set()
        self.Destroy()

    def EvtCheckBox(self, event):
        self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())

    def updateGlobalSettings(self):
        self.globalsettings.symbolrate = self.globalsettings.bandwidth * 1000000 / 0.875
        self.globalsettings.ofdmsymbollengthuseful = (1 / self.globalsettings.symbolrate) * self.globalsettings.odfmmode
        self.globalsettings.ofdmguardintervallength = (1 / self.globalsettings.symbolrate) * self.globalsettings.odfmmode * self.globalsettings.guardinterval
        self.globalsettings.ofdmsymbollength = self.globalsettings.ofdmsymbollengthuseful + self.globalsettings.ofdmguardintervallength
        self.globalsettings.ofdmsymbolspersecond = self.globalsettings.symbolrate / self.globalsettings.odfmmode /  (1 + self.globalsettings.guardinterval)
        self.globalsettings.ofdmframespersecond = self.globalsettings.ofdmsymbolspersecond / 68
        # round the usablebitrate reported to ffmpeg
        self.globalsettings.usablebitrateperodfmsymbol = self.globalsettings.odfmuseablecarriers * self.globalsettings.modulation * self.globalsettings.coderate * 0.921182266
        self.globalsettings.usablebitrate = self.globalsettings.ofdmsymbolspersecond * self.globalsettings.usablebitrateperodfmsymbol
        self.globalsettings.tspacketspersecond = self.globalsettings.usablebitrate / (8 * 188)

        self.logger.AppendText("New Settings:\n")
        self.logger.AppendText("OFDM symbols: %s/sec\n" % self.toUnits(self.globalsettings.ofdmsymbolspersecond))
        self.logger.AppendText("OFDM frames: %s/sec\n" % self.toUnits(self.globalsettings.ofdmframespersecond))
        self.logger.AppendText("Usable Bitrate: %sbit/sec\n" % self.toUnits(self.globalsettings.usablebitrate))
        self.logger.AppendText("Usable Bitrate per OFDM Symbol: %sbit/sec\n" % self.toUnits(self.globalsettings.usablebitrateperodfmsymbol))

        self.logger.AppendText("Channel symbolRate: %sS/sec\n" % self.toUnits(self.globalsettings.symbolrate))
        self.logger.AppendText("OFDM useful symbol duration: %ss\n" % self.toUnits(self.globalsettings.ofdmsymbollengthuseful))
        self.logger.AppendText("guard interval duration: %ss\n" % self.toUnits(self.globalsettings.ofdmguardintervallength))
        self.logger.AppendText("symbol duration: %ss\n" % self.toUnits(self.globalsettings.ofdmsymbollength))
        self.logger.AppendText("ts packets: %s/sec\n\n" % self.toUnits(self.globalsettings.tspacketspersecond))

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

def gui(globalsettings,eventstart,eventstop,lock):
    app = wx.App(False)
    frame = wx.Frame(None,-1,"Main Control",size = (650, 500))
    panel = MainPanel(frame,globalsettings,eventstart,eventstop,lock)
    frame.Show()
    app.MainLoop()

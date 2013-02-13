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
import os
import string
import numpy
import time
import subprocess

try:
    import threading
except ImportError, e:
    raise Exception("Failed to import module 'threading'")

########################################################################
class GlobalSettings():
    """
    Stores global settings.
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
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
        self.inputfile = ""
        self.outputfile = ""
        self.addargs = ""
        self.service_provider = "ffmpeg_service_provider"
        self.service_name = "ffmpeg_service_name"
        self.service_id = 1
        self.writeoutputfile = 1
        self.radiofreq = 786
        self.symbolrate = 0
        self.usablebitrate = 0
        self.ctx = None
        self.symbolspersecondwritten = 0
    	self.totalsymbolswritten = 0
    	self.logofilename = "./logo.ts"
    	self.dvbt_encoder = None
    	        
    def update_global_settings(self):
    	if self.ctx is None:
    	    ctx = cl.create_some_context(interactive=False)
    	else:
    	    ctx = self.ctx
    	
    	#if self.dvbt_encoder is not None:
    	#    if self.dvbt_encoder.is_running():
    	#        return
        self.dvbt_encoder = DVBT.Encoder(ctx, self.odfmmode, self.bandwidth, self.modulation, self.coderate, self.guardinterval, self.alpha, self.cellid)

        self.symbolrate = self.dvbt_encoder.get_symbolrate()
        self.usablebitrate = self.dvbt_encoder.get_usablebitrate()
        #self.symbolspersecondwritten = self.dvbt_encoder.get_symbolspersecondwritten()
        
########################################################################
class TabPaneldvbtSettings(wx.Panel):
    """
    This will be the dvbtSettings notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.gs = gs
       
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

        self.Bind(wx.EVT_CLOSE, self.EvtClose)


    def EvtComboBoxcoderate(self, event):
        if event.GetString() == "1/2":
            self.gs.coderate = 0.5
        if event.GetString() == "2/3":
            self.gs.coderate = 2.0 / 3.0
        if event.GetString() == "3/4":
            self.gs.coderate = 0.75
        if event.GetString() == "5/6":
            self.gs.coderate = 5.0 / 6.0
        if event.GetString() == "7/8":
            self.gs.coderate = 0.875

    def EvtComboBoxofdmmode(self, event):
        if event.GetString() == "8K mode":
            self.gs.odfmmode = 8192
            self.gs.odfmuseablecarriers = 6048
        if event.GetString() == "2K mode":
            self.gs.odfmmode = 2048
            self.gs.odfmuseablecarriers = 1512

    def EvtComboBoxchannelbandwidth(self, event):
        if event.GetString() == "8Mhz":
            self.gs.bandwidth = 8
        if event.GetString() == "7Mhz":
            self.gs.bandwidth = 7
        if event.GetString() == "6Mhz":
            self.gs.bandwidth = 6

    def EvtComboBoxguardinteraval(self, event):
        if event.GetString() == "1/4":
            self.gs.guardinterval = 0.25
        if event.GetString() == "1/8":
            self.gs.guardinterval = 0.125
        if event.GetString() == "1/16":
            self.gs.guardinterval = 0.0625
        if event.GetString() == "1/32":
            self.gs.guardinterval = 0.03125

    def EvtComboBoxmodulation(self, event):
        if event.GetString() == "QPSK":
            self.gs.modulation = 2
        if event.GetString() == "16-QAM":
            self.gs.modulation = 4
        if event.GetString() == "64-QAM":
            self.gs.modulation = 6
            
    def EvtComboBoxalpha(self, event):
        self.gs.alpha = int(event.GetString())

    def EvtClose(self, event):
        self.Destroy()

        
########################################################################
class TabPanelMain(wx.Panel):
    """
    This will be the Main notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
         
        self.gs = gs
        
        self.cbffmpeg = wx.CheckBox(self, -1, 'encode input stream using ffmpeg', (10, 30))
        self.cbffmpeg.SetValue(True)
        
        self.cbtransmitlogo = wx.CheckBox(self, -1, 'standby: transmit logo', (10, 60))
        self.cbtransmitlogo.SetValue(True)
        
        # text box for logo file name
        self.TextCtrllogofile = wx.TextCtrl(self, pos=(200,60), size=(300,-1), value="./logo.ts" )
        self.Bind(wx.EVT_TEXT, self.EvtTextlogo, self.TextCtrllogofile)
        
        self.rb1 = wx.RadioButton(self, -1, 'write to file/fifo', (10, 120), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, -1, 'output using opengl', (10, 150))

        self.Bind(wx.EVT_RADIOBUTTON, self.RadioButtonEvent, id=self.rb1.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.RadioButtonEvent, id=self.rb2.GetId())

        # label input file name
        self.lblffmpegargs = wx.StaticText(self, label="input file:", pos=(10, 180))
        
        # text box for input file name
        self.TextCtrlinputfile = wx.TextCtrl(self, pos=(90,180), size=(300,-1), value="" )
        
        # the button choose input file
        self.buttoninputfile =wx.Button(self, label="Choose input file", pos=(20, 210))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonInput,self.buttoninputfile)
        
        # label output file name
        self.lblffmpegargs = wx.StaticText(self, label="output file:", pos=(10, 260))
        
        # text box for output file name
        self.TextCtrloutputfile = wx.TextCtrl(self, pos=(90,260), size=(300,-1), value="" )
        
        # the button choose output file
        self.buttonoutputfile =wx.Button(self, label="Choose output file", pos=(20, 290))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonOutput,self.buttonoutputfile)
	
        # the button start
        self.buttonstart =wx.Button(self, label="(Re)Start", pos=(250, 300))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonStart,self.buttonstart)
        
        # the button stop
        self.buttonstop =wx.Button(self, label="Stop", pos=(400, 300))
        self.Bind(wx.EVT_BUTTON, self.OnClickButtonStop,self.buttonstop)
        
        self.thread_event = threading.Event()
        self.thread_lock = threading.Lock()
                
    def OnClickButtonStart(self,event):
        print "bandwidth %f" % self.gs.bandwidth
        print "coderate %f" % self.gs.coderate
        print "odfmmode %f" % self.gs.odfmmode
        print "odfmcarriers %f" % self.gs.odfmcarriers
        print "odfmuseablecarriers %f" % self.gs.odfmuseablecarriers
        print "guardinterval %f" % self.gs.guardinterval
        print "modulation %f" % self.gs.modulation
        print "alpha %f" % self.gs.alpha
        print "cellid %f" % self.gs.cellid
        print "addargs %s" % self.gs.addargs
        print "service_provider %s" % self.gs.service_provider
        print "service_name %s" % self.gs.service_name
        print "service_id %f" % self.gs.service_id
        print "inputfile %s" % self.gs.inputfile
        print "outputfile %s" % self.gs.outputfile
        print "write outputfile %f" % self.gs.writeoutputfile
        print "radio freq %f" % self.gs.radiofreq
        
        if self.gs.logofilename[0] == ".":
            self.gs.logofilename = "%s%s" % (os.getcwd(), string.lstrip(self.gs.logofilename,"."))
        print "logo file %s" % self.gs.logofilename      
        if self.gs.writeoutputfile == 0:
            try:
                os.mkfifo("/tmp/glfifo")
            except:
                print "bla"
            self.gs.outputfile = "/tmp/glfifo"
            self.glDrawPixel_process = subprocess.Popen(['./glDrawPixels', '-geometry', '1024x768+0+0', self.gs.outputfile])
            
        self.gs.update_global_settings()
        self.thread_event.clear()

        if (self.cbtransmitlogo.GetValue() or len(self.gs.inputfile)) and len(self.gs.outputfile):
            self.buffersize = 5
            self.cl_inputbuffer_array = [cl.Buffer(self.gs.ctx, cl.mem_flags.READ_ONLY, size=int(self.gs.dvbt_encoder.get_tspacketspersuperframe() * 188) )] * self.buffersize 
            self.cl_outputbuffer_array = [cl.Buffer(self.gs.ctx, cl.mem_flags.WRITE_ONLY, size=int(self.gs.dvbt_encoder.get_symbolspersuperframe() * 8) )] * self.buffersize 
            self.cl_inputevent_array = [None] * self.buffersize
            self.cl_outputevent_array = [None] * self.buffersize       
            self.workingthread = threading.Thread(target=self.worker_thread)            
            self.workingthread.start()

    def OnClickButtonStop(self,event):
        self.thread_event.set()

    def worker_thread(self):
        outputfifo = open(self.gs.outputfile, 'w')

        self.str_inputbuf= ""
        encoded_data = [numpy.array(numpy.zeros(self.gs.dvbt_encoder.get_symbolspersuperframe() * 8) ,dtype=numpy.uint8)] * self.buffersize

        for i in range(0,self.buffersize):
            self.cl_inputevent_array[i] = self.gs.dvbt_encoder.enqueue_copy_to_device(self.get_input_buf(), self.cl_inputbuffer_array[i])
            
        for i in range(0,self.buffersize):
            self.cl_inputevent_array[i].wait()
        
        while not self.thread_event.isSet():
            for i in range(0,self.buffersize):
                #self.cl_inputevent_array[i].wait()
                if self.cl_outputevent_array[i] is not None:
                    self.cl_outputevent_array[i].wait()
                    outputfifo.write(encoded_data[i])
                    
                t = time.time() 
                self.gs.dvbt_encoder.encode_superframe(self.cl_inputbuffer_array[i],self.cl_outputbuffer_array[i],self.cl_inputevent_array[i])
                print "execution time %f " % (time.time() -t)
                #enqueue a transfer
                self.cl_inputevent_array[i] = self.gs.dvbt_encoder.enqueue_copy_to_device(self.get_input_buf(), self.cl_inputbuffer_array[i])
                self.cl_outputevent_array[i] = self.gs.dvbt_encoder.enqueue_copy_to_host(self.cl_outputbuffer_array[i],encoded_data[i] )
                
        self.glDrawPixel_process.terminate()
        outputfifo.close()
        
        #fifo.close()
        
    def get_input_buf(self):
        tmp = ""
        logo = open(self.gs.logofilename, 'r')
        logo_array = logo.read()
        logo.close()
     	bytestocopy = self.gs.dvbt_encoder.tspacketspersuperframe * 188
        while len(self.str_inputbuf) < bytestocopy:
            self.str_inputbuf = "%s%s" % (self.str_inputbuf,logo_array)
        tmp = self.str_inputbuf[:bytestocopy]
        self.str_inputbuf = self.str_inputbuf[len(self.str_inputbuf)-bytestocopy:]
        return tmp
      
        
    def RadioButtonEvent(self, event):
        self.TextCtrloutputfile.SetEditable(self.rb1.GetValue())
        self.gs.writeoutputfile = self.rb1.GetValue()
        
        if self.rb2.GetValue():
            self.gs.outputfile = self.TextCtrloutputfile.GetValue()
            self.TextCtrloutputfile.SetValue("")
            self.buttonoutputfile.Disable()
        else:
            self.TextCtrloutputfile.SetValue(self.gs.outputfile)
            self.buttonoutputfile.Enable()    
            
    def OnClickButtonInput(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    inputfile = dialog.GetPath()
            self.TextCtrlinputfile.SetValue(inputfile)
            self.gs.inputfile = inputfile
	dialog.Destroy()
	
    def OnClickButtonOutput(self,event):
        dialog = wx.FileDialog ( None, style = wx.OPEN )
	if dialog.ShowModal() == wx.ID_OK:
   	    outputfile = dialog.GetPath()
            self.TextCtrloutputfile.SetValue(outputfile)
            self.gs.outputfile = outputfile
	dialog.Destroy()

    def EvtTextlogo(self, event):
        self.gs.logofilename = event.GetString()

        
########################################################################
class TabPanelffmpegSettings(wx.Panel):
    """
    This will be the ffmpegSettings notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.gs = gs
        
        # label ffmpeg additional args
        self.lblffmpegargs = wx.StaticText(self, label="additional arguments:", pos=(10, 30))

        # text box for additional ffmpeg args
        self.TextCtrlffmpegaddargs = wx.TextCtrl(self, pos=(150,30), size=(300,-1), value="")
        self.Bind(wx.EVT_TEXT, self.EvtTextadargs, self.TextCtrlffmpegaddargs)
        
        self.lblsp= wx.StaticText(self, label="service_provider:", pos=(10, 60))
        self.TextCtrlffmpegserviceprovider = wx.TextCtrl(self, pos=(150,60), size=(300,-1), value="ffmpeg_service_provider")
        self.Bind(wx.EVT_TEXT, self.EvtTextsp, self.TextCtrlffmpegserviceprovider)
        
        self.lblsn = wx.StaticText(self, label="service_name:", pos=(10, 90))
        self.TextCtrlffmpegservicename = wx.TextCtrl(self, pos=(150,90), size=(300,-1), value="ffmpeg_service_name")
        self.Bind(wx.EVT_TEXT, self.EvtTextsn, self.TextCtrlffmpegservicename)
        
        self.lblsid = wx.StaticText(self, label="service_id:", pos=(10, 120))
        self.TextCtrlffmpegserviceid = wx.TextCtrl(self, pos=(150,120), size=(300,-1), value="1")
        self.Bind(wx.EVT_TEXT, self.EvtTextsid, self.TextCtrlffmpegservicename)
                
        self.lblbr = wx.StaticText(self, label="Stream Bitrate:", pos=(10, 150))
        self.TextCtrlffmpegbitrate = wx.TextCtrl(self, pos=(150,150), size=(300,-1), value="", style=wx.TE_READONLY)

    def EvtTextadargs(self, event):
        self.gs.addargs = event.GetString()
        
    def EvtTextsp(self, event):
        self.gs.service_provider = event.GetString()
        
    def EvtTextsn(self, event):
        self.gs.service_name = event.GetString()

    def EvtTextsid(self, event):
        self.gs.service_id = event.GetString()
        
    def update(self):
        self.TextCtrlffmpegbitrate.Value = "%sbit/s" % self.toUnits(self.gs.usablebitrate)

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
class TabPanelradioSettings(wx.Panel):
    """
    This will be the radioSettings notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.gs = gs
        
        self.channelarray = ["21	474Mhz","22	482Mhz","23	490Mhz","24	498Mhz","25	506Mhz","26	514Mhz","27	522Mhz","28	530Mhz","29	538Mhz","30	546Mhz","31	554Mhz","32	562Mhz","33	570Mhz","34	578Mhz","35	586Mhz","36	594Mhz","37	602Mhz","38	610Mhz","39	618Mhz","40	626Mhz","41	634Mhz","42	642Mhz","43	650Mhz","44	658Mhz","45	666Mhz","46	674Mhz","47	682Mhz","48	690Mhz","49	698Mhz","50	706Mhz","51	714Mhz","52	722Mhz","53	730Mhz","54	738Mhz","55	746Mhz","56	754Mhz","57	762Mhz","58	770Mhz","59	778Mhz","60	786Mhz","61	794Mhz","62	802Mhz","63	810Mhz","64	818Mhz","65	826Mhz","66	834Mhz","67	842Mhz","68	850Mhz","69	858Mhz"]

        # label channel list
        self.lblchannel = wx.StaticText(self, label="UHF channel:", pos=(10, 30))

	# the combobox channel list
        self.editchannellist = wx.ComboBox(self, pos=(150, 30), size=(300, -1), choices=self.channelarray, style=wx.CB_READONLY, value="60	786Mhz")
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxchannellist, self.editchannellist)
        
        # label symbol rate
        self.lblchannel = wx.StaticText(self, label="symbolrate:", pos=(10, 60))
        self.TextCtrlsr = wx.TextCtrl(self, pos=(150,60), size=(300,-1), value="", style=wx.TE_READONLY)
        
        # label channel bandwidth
        self.lblchannel = wx.StaticText(self, label="bandwidth:", pos=(10, 90))
        self.TextCtrlbw = wx.TextCtrl(self, pos=(150,90), size=(300,-1), value="", style=wx.TE_READONLY)
        
    def EvtComboBoxchannellist(self, event):
        self.gs.radiofreq = event.GetString().split('	')[1].split('Mhz')[0]
        
    def update(self):
        self.TextCtrlbw.Value = "%s Mhz" % self.gs.bandwidth
        self.TextCtrlsr.Value = "%shz" % self.toUnits(self.gs.symbolrate)
        
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
class TabPanelstatus(wx.Panel):
    """
    This will be the status notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.gs = gs
        # OFDM
        self.lblrate = wx.StaticText(self, label="rate:", pos=(10, 90))
        
        # total
        self.lblSymbolswritten = wx.StaticText(self, label="total symbols:", pos=(10, 30))
        self.lblframeswritten = wx.StaticText(self, label="total frames:", pos=(10, 60))
        
       
    def update(self):
    	if self.gs.dvbt_encoder is not None:
    	    self.gs.symbolspersecondwritten = self.gs.dvbt_encoder.get_symbolspersecondwritten()
    	    self.gs.totalsymbolswritten = self.gs.dvbt_encoder.get_totalsymbolswritten()
    	
        self.lblrate.Value = "rate: %3.1f" % (self.gs.symbolspersecondwritten / self.gs.symbolrate * 100)
        self.lblSymbolswritten.Value = "total symbols: %s" % self.toUnits(self.gs.totalsymbolswritten)
        self.lblframeswritten.Value = "total frames: %s" % self.toUnits(self.gs.totalsymbolswritten/68)
        
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
class TabPanelopenclsettings(wx.Panel):
    """
    This will be the openclsettings notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, gs):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.gs = gs
        
        # label Compute Platform
        self.lblcomputedevice = wx.StaticText(self, label="Compute Platform:", pos=(10, 30))

        # label Compute Device
        self.lblcomputedevice = wx.StaticText(self, label="Compute Device:", pos=(10, 60))

        computedeviceList = []
        clplatformList = []

        for any_platform in cl.get_platforms():
            clplatformList.append(any_platform.name)
            
        self.gs.clplatform =  cl.get_platforms()[0]
        self.gs.clcomputedevice = self.gs.clplatform.get_devices()[0]
        self.gs.ctx = cl.Context(devices=[self.gs.clcomputedevice], properties=None, dev_type=None)
        
        any_platform = cl.get_platforms()[0]
        for found_device in any_platform.get_devices():
            if found_device.type == 4 :
                computedeviceList.append("GPU: %s" % found_device.name)
            elif found_device.type == 2 :
                computedeviceList.append("CPU: %s" % found_device.name)
            else:
                computedeviceList.append("???: %s" % found_device.name)


	
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
               self.gs.clplatform = any_platform
               self.gs.clcomputedevice = any_platform.get_devices()[0]
               
               for found_device in any_platform.get_devices():
                   if found_device.type == 4 :
                       computedeviceList.append("GPU: %s" % found_device.name)
                   if found_device.type == 2 :
                       computedeviceList.append("CPU: %s" % found_device.name)
               break
       self.editcomputedevice.choices = computedeviceList
       self.gs.ctx = cl.Context(devices=[self.gs.clcomputedevice], properties=None, dev_type=None)
       	
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
        # class holding all the settings
        self.gs = GlobalSettings(self)
        
        # Create the first tab and add it to the notebook
        self.tabOne = TabPanelMain(self,self.gs)
        self.tabOne.SetBackgroundColour("Gray")
        self.AddPage(self.tabOne, "Main")

        # Create and add the second tab
        self.tabTwo = TabPaneldvbtSettings(self,self.gs)
        self.AddPage(self.tabTwo, "DVBT Settings")
        
        # Create and add the third tab
        self.tabThree = TabPanelffmpegSettings(self,self.gs)
        self.AddPage(self.tabThree, "ffmpeg settings")
        
        # Create and add the fours tab
        self.tabFour = TabPanelopenclsettings(self,self.gs)
        self.AddPage(self.tabFour, "OpenCL settings")
        
        # Create and add the fives tab
        self.tabFive = TabPanelradioSettings(self,self.gs)
        self.AddPage(self.tabFive, "radio settings")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
        # Create and add the sixs tab
        self.tabSix = TabPanelstatus(self,self.gs)
        self.AddPage(self.tabSix, "OFDM status")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        self.gs.update_global_settings()
        self.tabThree.update()
        self.tabFive.update()
        self.tabSix.update()
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
    


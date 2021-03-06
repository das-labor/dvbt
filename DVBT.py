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

try:
    import pyopencl as cl
except ImportError, e:
    raise Exception("Please install pyopencl from 'http://pypi.python.org/pypi/pyopencl'")

try:
    import numpy
except ImportError, e:
    raise Exception("Please install numpy from 'http://pypi.python.org/pypi/numpy'")

try:
    import time
except ImportError, e:
    raise Exception("Failed to import module 'time'")

try:
    import threading
except ImportError, e:
    raise Exception("Failed to import module 'threading'")

try:
    import tempfile
except ImportError, e:
    raise Exception("Failed to import module 'tempfile'")

try:
    import os
except ImportError, e:
    raise Exception("Failed to import module 'os'")

try:
    import string
except ImportError, e:
    raise Exception("Failed to import module 'string'")
    
class Encoder:
    def __init__(self, ctx=None, mode=2048, bandwidth=8, modulation=2, coderate=0.5, guardinterval=0.25, alpha=1, cellid=0):

        ######################################
        # test the settings
        if mode != 2048 and mode != 8192:
            raise Exception("mode not supported! use 2048 or 8192")

        if modulation != 2 and modulation != 4 and modulation != 6:
            raise Exception("modulation not supported! use 2 for QPSK, 4 for 16-QAM, 6 for 64-QAM")

        if (coderate != 0.5) and (coderate != 2.0 / 3.0) and (coderate != 0.75):
            raise Exception("coderate %f not supported! use 1/2 or 2/3 or 3/4" % coderate)

        if guardinterval != 0.25 and guardinterval != 0.125 and guardinterval != 0.0625 and guardinterval != 0.03125:
            raise Exception("guardinterval not supported! use 0.5 or 0.125 or 0.0625 or 0.03125")

        if bandwidth != 8 and bandwidth != 7 and bandwidth != 6:
            raise Exception("bandwidth not supported! use 8 for 8Mhz,7 for 6Mhz, 6 for 6Mhz")

        if alpha != 1:
            raise Exception("alpha not supported! use alpha=1")

        if ctx is None:
            raise Exception("Please specify opencl a valid opencl context!")

        # create a event for signaling data can be processed
        #self.thread_event = threading.Event()

        # locks the opencl access
       # self.cl_thread_lock = threading.Lock()
        self.event = None
        
	# save the opencl context
        self.ctx = ctx

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx, properties=cl.command_queue_properties.OUT_OF_ORDER_EXEC_MODE_ENABLE)

        # helper class for loading kernels
        self.kernelh = Kernelhelper(self.ctx)

        ######################################
        # user settings
        
        self.use_double = int(0)
        self.debug = int(1)

        ######################################
        # calculate all settings

        self.ctx = ctx
        self.queue = self.queue

        self.bandwidth = int(bandwidth)
        self.coderate = coderate
        self.ofdmmode = int(mode)
        self.ofdmmode_half = int(mode/2)
        self.guardinterval = guardinterval
        self.modulation = modulation
        self.alpha = alpha
        self.cellid = int(cellid)

        if mode == 8192:
            self.ofdmcarriers = int(6817)
            self.ofdmuseablecarriers = int(6048)
        elif mode == 2048:
            self.ofdmcarriers = int(1705)
            self.ofdmuseablecarriers = int(1512)

        # const
        self.framespersuperframe = int(4)
        self.symbolsperframe = int(68)
        self.bytespertspacket = int(188)
        self.bytesperrspacket = int(204)
        self.ofdmsymbolspersuperframe = int(self.framespersuperframe * self.symbolsperframe)
        
        self.symbolrate = self.bandwidth * 1000000.0 / 0.875
        #self.ofdmsymbol_useful = (1 / self.symbolrate) * self.ofdmmode
        #self.ofdmguardintervallength = (1 / self.symbolrate) * self.ofdmmode * self.guardinterval
        #self.ofdmsymbollength = self.ofdmsymbollengthuseful + self.ofdmguardintervallength
        self.ofdmmode_guardint = int(self.ofdmmode  * (1+self.guardinterval)) 
        self.ofdmsymbolspersecond = self.symbolrate / self.ofdmmode_guardint
        #self.ofdmframespersecond = self.ofdmsymbolspersecond / self.symbolsperframe
        self.symbolspersuperframe = self.ofdmmode_guardint * self.framespersuperframe * self.symbolsperframe

        
        # stats
        self.totalsymbolswritten = 0
        self.symbolswrittentofifo = 0
        self.symbolcounter = 0
        
        # round the usablebitrate reported to ffmpeg
        self.usablebitrateperofdmsymbol = self.ofdmuseablecarriers * self.modulation * self.coderate * 0.921182266
        self.usablebitrate = self.ofdmsymbolspersecond * self.usablebitrateperofdmsymbol
        self.tspacketspersecond = self.usablebitrate / (8 * 188)
        
        # bits per superframe 
        self.bitspersuperframe = self.ofdmuseablecarriers * self.symbolsperframe * self.framespersuperframe * self.modulation
        # usable bits per superframe
        self.usablebitspersuperframe = self.ofdmuseablecarriers * self.symbolsperframe * self.framespersuperframe * self.modulation * self.coderate
        # bytes including reed-solomon parity bytes per superframe
        self.bytespersuperframe = int(self.usablebitspersuperframe / 8)
        # tspacketspersuperframe per superframe  
        self.tspacketspersuperframe = self.bytespersuperframe / self.bytesperrspacket
        
        self.conv_enc_uints_in = self.usablebitspersuperframe / 32
        self.conv_enc_uints_out = self.bitspersuperframe

        self.sizeofreal2_t = int(8 + 8 * self.use_double)
        if self.use_double:
            self.numpycomplex = numpy.complex128
        else:
            self.numpycomplex = numpy.complex64
        self.sizeofint = int(4)
        self.compilerflags = "-D CONFIG_USE_DOUBLE=%d" % self.use_double
        
        if self.debug :
            print "symbolrate %f" % self.symbolrate
            print "ofdmsymbolspersecond %f" % self.ofdmsymbolspersecond 
            print "bitspersuperframe %f " % self.bitspersuperframe
            print "coderate %f " % self.coderate
            print "usablebitspersuperframe %f " % self.usablebitspersuperframe
            print "bytespersuperframe %f" % self.bytespersuperframe 
            print "tspacketspersuperframe %f" % self.tspacketspersuperframe
            print "ofdmsymbolspersecond %f" % self.ofdmsymbolspersecond 
            print "conv_enc_uints_in %f " % self.conv_enc_uints_in
            print "use_double %f " % self.use_double  
            print "compilerflags %s " % self.compilerflags  
            print "inner interleaver thread count %d " % int(self.bitspersuperframe/(self.modulation*127))
            print "ofdmsymbolspersuperframe %d" % self.ofdmsymbolspersuperframe
        
        ######################################
        # load the opencl kernels

        self.ockernelA = self.kernelh.load('outer_coding.cl','run_pbrs_rs', self.compilerflags)
        
        self.ockernelB = self.kernelh.load('outer_coding.cl','run_oi_A', self.compilerflags)
        
        self.ickernel = self.kernelh.load('inner_coding.cl','run_ic_A', self.compilerflags)
        
        self.iikernel = self.kernelh.load('inner_interleaver.cl','run_ii_A', self.compilerflags)
        
        if self.modulation == 2:
            self.smkernel = self.kernelh.load('signal_mapper.cl','run_qpsk', self.compilerflags)
        if self.modulation == 4:
            self.smkernel = self.kernelh.load('signal_mapper.cl','run_qam16', self.compilerflags)
        if self.modulation == 6:
            self.smkernel = self.kernelh.load('signal_mapper.cl','run_qam64', self.compilerflags)
            
        if self.ofdmmode == 2048:
            self.sikernel = self.kernelh.load('symbol_interleaver.cl','run2K_A', self.compilerflags)
            
        elif self.ofdmmode == 8192:
            self.sikernel = self.kernelh.load('symbol_interleaver.cl','run8K_A', self.compilerflags)
            
        self.fill_continual_kernel = self.kernelh.load('pilots_and_ifft_mapper.cl','fill_continual', self.compilerflags)
        
        self.fill_tps_kernel = self.kernelh.load('pilots_and_ifft_mapper.cl','fill_tps', self.compilerflags)
        
        self.fill_scattered_kernel = self.kernelh.load('pilots_and_ifft_mapper.cl','fill_scattered', self.compilerflags)
        
        self.fill_data_kernel = self.kernelh.load('pilots_and_ifft_mapper.cl','fill_data', self.compilerflags)
        
        self.fftRadix2Kernel = self.kernelh.load('FFT.cl','fftRadix2Kernel', self.compilerflags)
        
        self.fftswaprealimagKernel = self.kernelh.load('FFT.cl','fftswaprealimag', self.compilerflags)
        
        self.fftRadix2KernelStart = self.kernelh.load('FFT.cl','fftRadix2Kernel_start', self.compilerflags)
                
        #self.fftRadix2KernelEnd = self.kernelh.load('FFT.cl','fftRadix2Kernel_end_guard', self.compilerflags)
        self.fftRadix2KernelEnd = self.kernelh.load('FFT.cl','fftRadix2Kernel_end', self.compilerflags)
        #self.quantisationKernel = self.kernelh.load('quantisation.cl','floattoint', self.compilerflags)
        self.quantisationKernel = self.kernelh.load('quantisation.cl','floattosignedfloat', self.compilerflags)
        #self.quantisationKernel = self.kernelh.load('quantisation.cl','floattofloat', self.compilerflags)        
        
        ######################################
        # create tps arrays

        self.polarity = 1
        # the bch polynom in octal is 041567
        # the reverse is 076541
        #self.bchpolynom = [1,1,1,0,1,1,1,0,1,1,0,0,0,0,1]
        self.tps_bits = []

        # tps bits change per frame
        for frame in range(0,4):
            bitarray = []
            bitarray.append(0) #s0 is always 0, this bit isn't included in BCH parity bits

            # sync word
            if (frame & 0x00000001) > 0:
                bitarray.append(0) 
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(1)
                bitarray.append(0)
            else:
                bitarray.append(1) 
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(1)
        
            # tps length indicator
            bitarray.append(0) 
            bitarray.append(1)
            bitarray.append(1)
            bitarray.append(1)
            bitarray.append(1)
            bitarray.append(1)

            # frame bits
            bitarray.append(((frame & 0x02)>>1))
            bitarray.append((frame & 0x01))

            # constelation bits
            if self.modulation == 2:
                bitarray.append(0)
                bitarray.append(0)
            elif self.modulation == 4:
                bitarray.append(0)
                bitarray.append(1)
            elif self.modulation == 6:
                bitarray.append(1)
                bitarray.append(0)

            # Hierarchical Mode, HARDCODE: Non hierarchical, alpha = 1
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)

            # code rate bits
            if self.coderate == 0.5:
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(0)
            elif self.coderate == (2.0 / 3.0):
                bitarray.append(0)
                bitarray.append(0)
                bitarray.append(1)
            elif self.coderate == 0.75:
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(0)
            elif self.coderate == (5.0 / 6.0):
                bitarray.append(0)
                bitarray.append(1)
                bitarray.append(1)
            elif self.coderate == 0.875:
                bitarray.append(1)
                bitarray.append(0)
                bitarray.append(0)


            # code rate bits for hierarchical, HARDCODE: none
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)

            # guard interval bits
            if self.guardinterval == 0.25:
                bitarray.append(1)
                bitarray.append(1)
            elif self.guardinterval == 0.125:
                bitarray.append(1)
                bitarray.append(0)
            elif self.guardinterval == 0.0625:
                bitarray.append(0)
                bitarray.append(1)
            elif self.guardinterval == 0.03125:
                bitarray.append(0)
                bitarray.append(0)


            # transmission mode bits
            if self.ofdmmode == 8192:
                bitarray.append(0)
                bitarray.append(1)
            elif self.ofdmmode == 2048:
                bitarray.append(0)
                bitarray.append(0)

            if (frame & 1) == 1:
                bitarray.append((self.cellid & 0x00008000)>>15)
                bitarray.append((self.cellid & 0x00004000)>>14)
                bitarray.append((self.cellid & 0x00002000)>>13)
                bitarray.append((self.cellid & 0x00001000)>>12)
                bitarray.append((self.cellid & 0x00000800)>>11)
                bitarray.append((self.cellid & 0x00000400)>>10)
                bitarray.append((self.cellid & 0x00000200)>>9)
                bitarray.append((self.cellid & 0x00000100)>>8)
            else:
                bitarray.append((self.cellid & 0x00000080)>>7)
                bitarray.append((self.cellid & 0x00000040)>>6)
                bitarray.append((self.cellid & 0x00000020)>>5)
                bitarray.append((self.cellid & 0x00000010)>>4)
                bitarray.append((self.cellid & 0x00000008)>>3)
                bitarray.append((self.cellid & 0x00000004)>>2)
                bitarray.append((self.cellid & 0x00000002)>>1)
                bitarray.append((self.cellid & 0x00000001)>>0)

            #unused bits
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)
            bitarray.append(0)
            
            #do bch encoding, this functions returns an array of parity bits   
            temp = self.BCH_127_113_2(bitarray)
            
            # append parity bits
            for j in temp:
                 bitarray.append(j)
                 
            if self.debug :
            	print "tps bit array for frame %d" % frame   
                print bitarray
                print len(bitarray)
                
            #self.shreg = bitarray

            # insert 0's
            #for j in range(0,(67-53)):
            #     self.shreg.insert(0,0)

            #print len(self.shreg)

            # bch encode the tps bits
            #for j in range(0,53):
            #     for i in range(0,j):
            #         self.shreg.insert(0,self.shreg.pop(66))
            #     for p in self.bchpolynom:
            #         self.shreg.insert(0,self.shreg.pop(66)^p)
            #     for i in range(0,53-j):
            #         self.shreg.insert(0,self.shreg.pop(66))

            #print "tps BCH shiftreg"
            #print self.shreg

            # copy paritiy bits
            #for j in range(0,(67-53)):
            #     bitarray.append(self.shreg.pop(0))

            #print "tps bit array + parity bits"
            #print bitarray
	    self.tps_bits.append(bitarray)

        ######################################
        # pilots
        
        # this pilots are constant, hardcode them
        if self.ofdmmode == 8192:
            self.tpspilots = [34, 50, 209, 346, 413, 569, 595, 688, 790, 901, 1073, 1219, 1262, 1286, 1469, 1594, 1687, 1738, 1754, 1913, 2050, 2117, 2273, 2299, 2392, 2494, 2605, 2777, 2923, 2966, 2990, 3173, 3298, 3391, 3442, 3458, 3617, 3754, 3821, 3977, 4003, 4096, 4198, 4309, 4481, 4627, 4670, 4694, 4877, 5002, 5095, 5146, 5162, 5321, 5458, 5525, 5681, 5707, 5800, 5902, 6013, 6185, 6331, 6374, 6398, 6581, 6706, 6799]
            self.continualpilots = [48,54,87,141,156,192,201,255,279,282,333,432,450,483,525,531,618,636,714,759,765,780,804,873,888,918,939,942,969,984,1050,1101,1107,1110,1137,1140,1146,1206,1269,1323,1377,1491,1683,1704,1752,1758,1791,1845,1860,1896,1905,1959,1983,1986,2037,2136,2154,2187,2229,2235,2322,2340,2418,2463,2469,2484,2508,2577,2592,2622,2643,2646,2673,2688,2754,2805,2811,2814,2841,2844,2850,2910,2973,3027,3081,3195,3387,3408,3456,3462,3495,3549,3564,3600,3609,3663,3687,3690,3741,3840,3858,3891,3933,3939,4026,4044,4122,4167,4173,4188,4212,4281,4296,4326,4347,4350,4377,4392,4458,4509,4515,4518,4545,4548,4554,4614,4677,4731,4785,4899,5091,5112,5160,5166,5199,5253,5268,5304,5313,5367,5391,5394,5445,5544,5562,5595,5637,5643,5730,5748,5826,5871,5877,5892,5916,5985,6000,6030,6051,6054,6081,6096,6162,6213,6219,6222,6249,6252,6258,6318,6381,6435,6489,6603,6795]
        elif self.ofdmmode == 2048:
            self.tpspilots = [34, 50, 209, 346, 413, 569, 595, 688, 790, 901, 1073, 1219, 1262, 1286, 1469, 1594, 1687]
            self.continualpilots = [48,54,87,141,156,192,201,255,279,282,333,432,450,483,525,531,618,636,714,759,765,780,804,873,888,918,939,942,969,984,1050,1101,1107,1110,1137,1140,1146,1206,1269,1323,1377,1491,1683,1704]
       
        # generate the scattered pilots sequence
        self.scatteredpilots = []
        for i in range(0,4):
            p = 0
            k = 0
            sc = []
            while k <  self.ofdmcarriers:
                k = 0 + 3 * (i % 4) + 12 * p
                p += 1
                sc.append(k)
            self.scatteredpilots.append(sc)

        # generate a list of data pilots
        self.datapilots = []
        for j in range(0,4):
            datapilot = []
            for i in range(0,self.ofdmcarriers):
                tmp = 0
                for tpspilot in self.tpspilots:
                    if tpspilot == i:
                        tmp = 1
                        break
                if tmp == 0:
                    for continualpilot in self.continualpilots:
                        if continualpilot == i:
                            tmp = 2
                            break
                if tmp == 0:
                    for scatteredpilot in self.scatteredpilots:
                        if scatteredpilot == i:
                            tmp = 3
                            break
                if tmp == 0:
                    datapilot.append(i)
            self.datapilots.append(datapilot)
        
        # generate the pbrs pilot sequence
        generator = 2047
        pbrsbit = 0
        temp = 0
        self.pbrssequence = []
        for i in range(0,self.ofdmcarriers):
	    # pilot pbrs generator, reinit every ofdm symbol
            pbrsbit = generator >> 10
            temp = ((generator >> 10)&1)^((generator >> 8)&1) # polynomial x^11 + x^2 + 1
            generator <<= 1
            generator |= (temp & 1)
            generator &= 2047
            self.pbrssequence.append(pbrsbit)
            
        if self.debug :
            print "len pilots:"
            print "tpspilots: %d" % len(self.tpspilots)
            print "continualpilots: %d" % len(self.continualpilots)  
            print "scatteredpilots frame 0: %d" % len(self.scatteredpilots[0])
            print "scatteredpilots frame 1: %d" % len(self.scatteredpilots[1])
            print "scatteredpilots frame 2: %d" % len(self.scatteredpilots[2])
            print "scatteredpilots frame 3: %d" % len(self.scatteredpilots[3])        
            print "datapilots frame 0: %d" % len(self.datapilots[0])
            print "datapilots frame 1: %d" % len(self.datapilots[1])
            print "datapilots frame 2: %d" % len(self.datapilots[2])
            print "datapilots frame 3: %d" % len(self.datapilots[3])
            print "pbrssequence: %d" % len(self.pbrssequence)

        ######################################
        # create the opencl buffers

        # buffer transfering data to the compute device
        #self.cl_input_buf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=int(self.tspacketspersuperframe * self.bytespertspacket) )

        # buffer holding the data from rs encoder
        self.dest_buf_A = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(self.bytespersuperframe+17*11*4) )

        # buffer holding the data from outer interleaver
        self.dest_buf_B = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(self.bytespersuperframe+4) )

        # buffer holding the data from inner coder
        self.dest_buf_C = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.bitspersuperframe * 4) # 4 bytes per uint

        # buffer holding the data from inner interleaver
        self.dest_buf_D = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.bitspersuperframe * 4) # 4 bytes per uint 

        # buffer holding the data from signal mapper
        # realt2_t, count: self.conv_enc_uints_out / self.modulation
        self.dest_buf_E = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, (self.bitspersuperframe / self.modulation) * self.sizeofreal2_t)

        # the following buffers need to exist multiple times due to loop unrolling

        # buffer holding the data from symbol interleaver
        # same size as signal mapper buffer, as the data is just interleaved
        self.dest_buf_F = [cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, (self.bitspersuperframe / self.modulation) * self.sizeofreal2_t)] * self.ofdmsymbolspersuperframe
        
        # buffer holding the data from pilot insertion kernel
        self.dest_buf_G = [cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.ofdmcarriers * self.sizeofreal2_t)] * self.ofdmsymbolspersuperframe
        
        # input buffer for ifft
        # size=self.ofdmmode * sizeof(real2_t)
        self.dest_buf_H = [cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.ofdmmode * self.sizeofreal2_t)] * self.ofdmsymbolspersuperframe
        
        # output buffer for ifft
        # size=self.ofdmmode * sizeof(real2_t)
        self.dest_buf_I = [cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.ofdmmode * self.sizeofreal2_t)] * self.ofdmsymbolspersuperframe
        
        # output buffer for ifft guardinterval
        # size=self.ofdmmode * sizeof(real2_t) * (1+guardinterval)
        self.dest_buf_J = [cl.Buffer( self.ctx, cl.mem_flags.READ_WRITE, int( self.ofdmmode_guardint * self.sizeofreal2_t ) )] * self.ofdmsymbolspersuperframe
        
        # output buffer for all ifft guardinterval
        # size=self.ofdmmode * sizeof(real2_t) * (1+guardinterval)
        #self.cl_output_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size= int( self.ofdmmode * (1+self.guardinterval) * 8 * self.framespersuperframe * self.symbolsperframe ) ) # 8 bytes per int2
        
        # an empty buffer to fill dest_buf_H with 0s
        self.dest_buf_H_empty = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY, self.ofdmmode * self.sizeofreal2_t)
        
        # const buffer for pilots
        self.scatteredpilots_array = []
        self.datapilots_array = []
        self.tpspilots_array = cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.tpspilots) )
        self.continualpilots_array = cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.continualpilots) )
        self.scatteredpilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.scatteredpilots[0]) ) )
        self.scatteredpilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.scatteredpilots[1]) ) )
        self.scatteredpilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.scatteredpilots[2]) ) )
        self.scatteredpilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.scatteredpilots[3]) ) )
        self.datapilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.datapilots[0]) ) )
        self.datapilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.datapilots[1]) ) )
        self.datapilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.datapilots[2]) ) )
        self.datapilots_array.append( cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.datapilots[3]) ) )
        self.pbrssequence_array = cl.Buffer( self.ctx, cl.mem_flags.READ_ONLY, 4 * len(self.pbrssequence) )

        # fill buffers
        cl.enqueue_copy( self.queue, self.tpspilots_array, numpy.array(self.tpspilots, dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.continualpilots_array, numpy.array(self.continualpilots, dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.scatteredpilots_array[0], numpy.array(self.scatteredpilots[0], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.scatteredpilots_array[1], numpy.array(self.scatteredpilots[1], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.scatteredpilots_array[2], numpy.array(self.scatteredpilots[2], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.scatteredpilots_array[3], numpy.array(self.scatteredpilots[3], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.datapilots_array[0], numpy.array(self.datapilots[0], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.datapilots_array[1], numpy.array(self.datapilots[1], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.datapilots_array[2], numpy.array(self.datapilots[2], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.datapilots_array[3], numpy.array(self.datapilots[3], dtype=numpy.uint32) )
        cl.enqueue_copy( self.queue, self.pbrssequence_array, numpy.array(self.pbrssequence, dtype=numpy.float32) )
        
        self.memset(self.dest_buf_A, 0, 11*17, None).wait()
        self.memset(self.dest_buf_H_empty, 0, self.ofdmmode * self.sizeofreal2_t, None).wait()
        
        self.fft_shift_A_bytecount = ((self.ofdmcarriers-1)/2)*self.sizeofreal2_t
        self.fft_shift_A_destoffset = (self.ofdmmode-(self.ofdmcarriers-1)/2)*self.sizeofreal2_t       
        self.fft_shift_B_bytecount = ((self.ofdmcarriers+1)/2)*self.sizeofreal2_t
        self.fft_shift_B_destoffset = ((self.ofdmcarriers-1)/2)*self.sizeofreal2_t
        
        self.guard_intervalA_bytecount = int(self.sizeofreal2_t*self.ofdmmode)
        self.guard_intervalA_destoffset = int(self.ofdmmode*self.guardinterval*self.sizeofreal2_t)   
        self.guard_intervalB_bytecount = int(self.ofdmmode*self.guardinterval*self.sizeofreal2_t)
        self.guard_intervalB_srcoffset = int((self.ofdmmode - self.ofdmmode*self.guardinterval)*self.sizeofreal2_t)    
        
        # numpy consts
        self.np_int32_1 = numpy.int32(1)
        self.np_int32_2 = numpy.int32(2)
        self.np_int32_4 = numpy.int32(4)
        self.np_int32_8 = numpy.int32(8)
        self.np_int32_16 = numpy.int32(16)
        self.np_int32_32 = numpy.int32(32)
        self.np_int32_64 = numpy.int32(64)
        self.np_int32_128 = numpy.int32(128)
        self.np_int32_256 = numpy.int32(256)
        self.np_int32_512 = numpy.int32(512)
        self.np_int32_1024 = numpy.int32(1024)
        self.np_int32_2048 = numpy.int32(2048)        
        self.np_int32_4096 = numpy.int32(4096)
        self.np_int32_ofdmmode = numpy.int32(self.ofdmmode)
        self.np_int32_modulation = numpy.int32(self.modulation)
        self.np_int32_ofdmmode_guard_int = numpy.int32(self.ofdmmode_guardint)
        
        if self.debug :
            print "thread count:"
            print "outer coder %d " % int(self.tspacketspersuperframe)
            print "outer interleaver %d " % int(self.bytespersuperframe/4)
            print "inner coder %d " % int(self.bytespersuperframe/4)
            print "inner interleaver %d " % int(self.bitspersuperframe/(self.modulation*127))
            print "symbol mapper %d " % int(self.bitspersuperframe*2/self.modulation)

    def get_symbolrate(self):
        return self.symbolrate

    def get_usablebitrate(self):
        return self.usablebitrate

    def get_tspacketspersecond(self):
        return self.tspacketspersecond
        
    def get_tspacketspersuperframe(self):
        return self.tspacketspersuperframe

    def get_ofdmsymbolspersecond(self):
        return self.ofdmsymbolspersecond

    def get_bytespersuperframe(self):
        return self.bytespersuperframe
        
    def get_symbolspersuperframe(self):
        return self.symbolspersuperframe
        
    def get_symbolswritten(self):
    	#self.cl_thread_lock.acquire()
        return self.symbolcounter
        #self.cl_thread_lock.release()
        
    def memset(self, buf, val, length, event):
    	data = numpy.array([val] * length, dtype=numpy.uint8)
    	if event is None:
    	    #self.cl_thread_lock.acquire()
    	    event = cl.enqueue_copy( self.queue, buf, data, is_blocking=False )
    	    #self.cl_thread_lock.release()
            return event
        else:
            #self.cl_thread_lock.acquire()
            event = cl.enqueue_copy( self.queue, buf, data, wait_for=[event], is_blocking=False )
            #self.cl_thread_lock.release()
            return event
    
    def BCH_127_113_2(self,data): 
    	temp = list(data)
    	if len(temp) < 113:
    	    for i in range(0,113-len(temp)):
    	        temp.append(0)
        feedback = 0
        length = 127
        k = 113
        bb = [0] * (length - k)
        # generator polynom g(x) = 1 + x^1 +x^2 + x^4 + x^5 +x^6 + x^8 +x^9 + x^14
        g = [1,1,1,0,1,1,1,0,1,1,0,0,0,0,1]
        i = k - 1
        while i >= 0:
	    feedback = temp[i] ^ bb[length - k - 1]
	    if (feedback != 0):
		j = length - k - 1
		while j > 0:
			if (g[j] != 0):
				bb[j] = bb[j - 1] ^ feedback
			else:
				bb[j] = bb[j - 1]
			j -= 1
		bb[0] = g[0] & feedback
	    else:
		j = length - k - 1
		while j > 0:
			bb[j] = bb[j - 1]
			j -= 1
		bb[0] = 0
	    i -= 1
	return bb

    #input_buf has to be a string, dest_buf has to be a opencl buffer
    def enqueue_copy_to_device(self, input_buf, dest_buf):
    	#self.cl_thread_lock.acquire()
    	if self.event is not None:
            event = cl.enqueue_copy( self.queue, dest_buf, numpy.fromstring(input_buf, dtype=numpy.uint32), wait_for=[self.event], is_blocking=False )
    	else:
            event = cl.enqueue_copy( self.queue, dest_buf, numpy.fromstring(input_buf, dtype=numpy.uint32), is_blocking=False )
        #self.cl_thread_lock.release()
        return event
        
    #input_buf has to be a opencl buffer, dest_buf has to be a string
    def enqueue_copy_to_host(self, input_buf, dest_buf):
    	#self.cl_thread_lock.acquire()
    	if self.event is not None:
    	    self.event = cl.enqueue_copy( self.queue, dest_buf, input_buf, wait_for=[self.event], is_blocking=False )
    	else:
    	    self.event = cl.enqueue_copy( self.queue, dest_buf, input_buf, is_blocking=False )
        #self.cl_thread_lock.release()
        return self.event
        
    #input_buf has to be a opencl buffer
    def encode_superframe(self,input_buf,dest_buf,waitfor_event):
        evt_inner_loop = []
       
        self.symbolcounter = 0
      
	evt_prepare_buf_B = self.memset(self.dest_buf_B, 0, 4, None)

        # ockernelA: pbrs, rs-encoder
        #  encode all ts packet per superframe at once
        #  input is litte endian, output is litte endian
        #  in: $x * 188 bytes, out: $x * 204 bytes
        
        #self.ockernelA.set_args(self.cl_input_buf, self.dest_buf_A)
        self.ockernelA.set_args( input_buf, self.dest_buf_A )            
        evt_kernel_ocA = cl.enqueue_nd_range_kernel( self.queue, self.ockernelA, (int(self.tspacketspersuperframe),), None, wait_for=[waitfor_event] )         
        
        # ockernelB: convolutional interleaver:
        #  input is litte endian, output is big endian
        #  inner encoder needs data in big endian format
        #  in: 11*17*4bytes + $x * 204 bytes, out: $x * 204 bytes + 4 bytes
        #  11*17*4bytes last bytes of previous kernel run

        self.ockernelB.set_args( self.dest_buf_A, self.dest_buf_B )
        evt_kernel_ocB = cl.enqueue_nd_range_kernel( self.queue, self.ockernelB, (int(self.bytespersuperframe/4),), None, wait_for=[evt_kernel_ocA,evt_prepare_buf_B] )
        
        # prepare dest_buf_A for next kernel run
        evt_prepare_buf_A = cl.enqueue_copy( self.queue, self.dest_buf_A, self.dest_buf_B, byte_count=17*11, src_offset=self.bytespersuperframe-17*11 , dest_offset=0, wait_for=[evt_kernel_ocB] )

        # convolutional encoder 1/2:
        #  encode all rs packets per superframe at once
        #  input is big endian
        #  process 32 bits per kernel
        #  always store as bitstream in uints (1 bit per uint)
        # todo implement self.coderate
     
        self.ickernel.set_args( self.dest_buf_B, self.dest_buf_C, self.np_int32_2 )
        evt_kernel_ic = cl.enqueue_nd_range_kernel( self.queue, self.ickernel, (int(self.bytespersuperframe/4),), None, wait_for=[evt_kernel_ocB] )

        # TODO:
        #  implement puncturing

        # bitwise convolutional interleaver:
        #  interleave (modulation * 127) bits at once
        #  always store as bitstream in uints (1 bit per uint)

        self.iikernel.set_args( self.dest_buf_C, self.dest_buf_D, self.np_int32_modulation )
        evt_kernel_ii = cl.enqueue_nd_range_kernel( self.queue,self.iikernel, (int(self.bitspersuperframe/(self.modulation*127)),), None, wait_for=[evt_kernel_ic] )

        # symbolmapper:
        #  convert <modulation bits> into a complex number
        #  store as real2_t
        
        self.smkernel.set_args(self.dest_buf_D, self.dest_buf_E )
        evt_kernel_sm = cl.enqueue_nd_range_kernel( self.queue,self.smkernel, (int(self.bitspersuperframe/self.modulation),), None, wait_for=[evt_kernel_ii] )
        
        for frame in range(0, self.framespersuperframe):
            for symbol in range(0, self.symbolsperframe):
                evt_inner_loop.append(self.inner_loop(evt_kernel_sm, frame , symbol, dest_buf))

        self.event = cl.enqueue_marker(self.queue, evt_inner_loop)

        return self.event

    def inner_loop(self, waitfor_event, frame , symbol, dest_buf):
	    j = symbol + (frame * self.symbolsperframe)
	    
	    event = None
	    # sikernel: symbol interleaver:
	    #  inerleave the symbols using a lfsr
	    #  input is ofdmcarriers real2_t, output is ofdmcarriers real2_t
	    #  threadcount: 1
	    #  TODO: find faster implementation
	    
	    self.sikernel.set_args(self.dest_buf_E, self.dest_buf_F[j], numpy.uint32(frame))
	    event = cl.enqueue_nd_range_kernel( self.queue, self.sikernel, (1,), None, wait_for=[waitfor_event] )
	    
	    # fill_continual_kernel: pilot insertion
	    #  insert continual pilots, tps pilots and scattered pilots and non pilot data carriers
	    #  input is ofdmusefulcarriers real2_t data and tps bits, output is ofdmcarriers real2_t
		  
	    self.fill_continual_kernel.set_args( self.dest_buf_G[j], self.continualpilots_array, self.pbrssequence_array)
	    eventA = cl.enqueue_nd_range_kernel( self.queue, self.fill_continual_kernel, (len(self.continualpilots),), None, wait_for=[waitfor_event] )
	
	    self.fill_tps_kernel.set_args( self.dest_buf_G[j], self.tpspilots_array, self.pbrssequence_array, numpy.float32(self.tps_bits[frame][symbol]) )
	    eventB = cl.enqueue_nd_range_kernel( self.queue, self.fill_tps_kernel, (len(self.tpspilots),), None, wait_for=[waitfor_event] )
	    
	    index = symbol % 4
	    
	    self.fill_scattered_kernel.set_args( self.dest_buf_G[j], self.scatteredpilots_array[index], self.pbrssequence_array)
	    eventC = cl.enqueue_nd_range_kernel( self.queue, self.fill_scattered_kernel, (len(self.scatteredpilots[index]),), None, wait_for=[waitfor_event] )
	    
	    self.fill_data_kernel.set_args(self.dest_buf_F[j], self.dest_buf_G[j], self.datapilots_array[index])
	    eventD = cl.enqueue_nd_range_kernel( self.queue, self.fill_data_kernel, (len(self.datapilots[index]),), None, wait_for=[event] )
	
	    # do fftshift
	    # fill self.dest_buf_H with zeros
	    event = cl.enqueue_copy(self.queue, self.dest_buf_H[j], self.dest_buf_H_empty, wait_for=[waitfor_event] )
	    event = cl.enqueue_copy(self.queue, self.dest_buf_H[j], self.dest_buf_G[j], byte_count=self.fft_shift_A_bytecount, src_offset=0, dest_offset=self.fft_shift_A_destoffset, wait_for=[eventA,eventB,eventC,eventD,event])
	    event = cl.enqueue_copy(self.queue, self.dest_buf_H[j], self.dest_buf_G[j], byte_count=self.fft_shift_B_bytecount, src_offset=self.fft_shift_B_destoffset, dest_offset=0, wait_for=[event])

	    # swap real and imag part, to do an inverse transform
	    # fftswaprealimagKernel: swap real and imag part of complex number
	    #  threadcount: ofdmmode
	    #  input is ofdmmode real2_t
	    
	    #self.fftswaprealimagKernel.set_args(self.dest_buf_H[j])
	    #event = cl.enqueue_nd_range_kernel(self.queue, self.fftswaprealimagKernel, (self.ofdmmode,), None, wait_for=[event])
	    
	    # fftRadix2Kernel: radix-2 fft
	    #  threadcount: ofdmmode / 2
	    #  input is ofdmmode real2_t, output is ofdmmode real2_t, const p
	    #   for(p=1, p < ofdmmode ,p=p*2)
	    
	    self.fftRadix2KernelStart.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_1 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2KernelStart,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_2 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_4 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_8 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_16 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_32 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_64 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_128 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_256 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
	    self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_512 )
	    event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	    
	    if self.ofdmmode == 8192:
	        self.fftRadix2Kernel.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_1024 )
	        event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	    else:
	    	#self.fftRadix2KernelEnd.set_args(self.dest_buf_H[j], self.dest_buf_J[j], self.np_int32_1024, numpy.float32(self.guardinterval) )
	    	self.fftRadix2KernelEnd.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_1024 )
	        event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2KernelEnd,(self.ofdmmode_half,),None, wait_for=[event])	
	        
	    if self.ofdmmode == 8192:
		self.fftRadix2Kernel.set_args(self.dest_buf_I[j], self.dest_buf_H[j], self.np_int32_2048 )
		event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2Kernel,(self.ofdmmode_half,),None, wait_for=[event])
	
		#self.fftRadix2KernelEnd.set_args(self.dest_buf_H[j], self.dest_buf_J[j], self.np_int32_4096 , numpy.float32(self.guardinterval))
		self.fftRadix2KernelEnd.set_args(self.dest_buf_H[j], self.dest_buf_I[j], self.np_int32_4096)
		event = cl.enqueue_nd_range_kernel(self.queue,self.fftRadix2KernelEnd,(self.ofdmmode_half,),None, wait_for=[event])
		
	    # swap real and imag part, to do an inverse transform
	    # fftswaprealimagKernel: swap real and imag part of complex number
	    #  threadcount: ofdmmode
	    #  input is ofdmmode real2_t
	    #self.fftswaprealimagKernel.set_args(self.dest_buf_I[j])
	    #event = cl.enqueue_nd_range_kernel(self.queue, self.fftswaprealimagKernel, (self.ofdmmode,), None, wait_for=[event])
	    
	    # create the guard interval
	    eventA = cl.enqueue_copy(self.queue, self.dest_buf_J[j], self.dest_buf_I[j], byte_count=self.guard_intervalA_bytecount, src_offset=0, dest_offset=self.guard_intervalA_destoffset, wait_for=[event])
	    eventB = cl.enqueue_copy(self.queue, self.dest_buf_J[j], self.dest_buf_I[j], byte_count=self.guard_intervalB_bytecount, src_offset=self.guard_intervalB_srcoffset ,dest_offset=0, wait_for=[event])
	    
	    # quantisationKernel: convert complex number real2_t to int2, multiplies each value with p
	    #  threadcount: ofdm_mode * (1+self.guardinterval)
	    #  input is ofdmmode_guardint real2_t, output is ofdmmode_guardint int2, const <factor to scale>, const <dest buffer offset>
	    destoffset = self.ofdmmode_guardint * j

	    self.quantisationKernel.set_args(self.dest_buf_J[j], dest_buf, numpy.float32(self.ofdmmode*0.0025), numpy.int32(destoffset) )                    
	    #event = cl.enqueue_nd_range_kernel(self.queue, self.quantisationKernel,(self.ofdmmode_guardint,), None, wait_for=[event])
	    event = cl.enqueue_nd_range_kernel(self.queue, self.quantisationKernel,(self.ofdmmode_guardint,), None, wait_for=[eventA,eventB])
	    self.symbolcounter += 2 * self.ofdmmode_guardint
	    
	    return event

class Kernelhelper:
    def __init__(self,ctx):
        self.ctx = ctx
    def load(self,filepath,kernelname,compilerflags):
        #read in the OpenCL source file as a string
        self.f = open(filepath, 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(self.ctx, fstr).build(options=[compilerflags])
        self.f.close()

        #create the opencl kernel
        return cl.Kernel(self.program,kernelname)
        


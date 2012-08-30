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

# this module maps *usefulcarriers* complex values and pilots onto one ofdm symbol
# pilot-positions and data-positions varies with frame index and symbol index
# the symbol needs to be transformed by an ifft to the time domain in the next step

import pyopencl as cl
import numpy

class mapper():
    def __init__(self, globalsettings, ctx, queue, cl_thread_lock): #ofdm symbol index, max carriers for current mode, one tps bit

        # save settings
        self.globalsettings = globalsettings
        self.tpssarray = [34, 50, 209, 346, 413, 569, 595, 688, 790, 901, 1073, 1219, 1262, 1286, 1469, 1594, 1687, 1738, 1754, 1913, 2050, 2117, 2273, 2299, 2392, 2494, 2605, 2777, 2923, 2966, 2990, 3173, 3298, 3391, 3442, 3458, 3617, 3754, 3821, 3977, 4003, 4096, 4198, 4309, 4481, 4627, 4670, 4694, 4877, 5002, 5095, 5146, 5162, 5321, 5458, 5525, 5681, 5707, 5800, 5902, 6013, 6185, 6331, 6374, 6398, 6581, 6706, 6799]

        self.continualpilotsarray = [48,54,87,141,156,192,201,255,279,282,333,432,450,483,525,531,618,636,714,759,765,780,804,873,888,918,939,942,969,984,1050,1101,1107,1110,1137,1140,1146,1206,1269,1323,1377,1491,1683,1704,1752,1758,1791,1845,1860,1896,1905,1959,1983,1986,2037,2136,2154,2187,2229,2235,2322,2340,2418,2463,2469,2484,2508,2577,2592,2622,2643,2646,2673,2688,2754,2805,2811,2814,2841,2844,2850,2910,2973,3027,3081,3195,3387,3408,3456,3462,3495,3549,3564,3600,3609,3663,3687,3690,3741,3840,3858,3891,3933,3939,4026,4044,4122,4167,4173,4188,4212,4281,4296,4326,4347,4350,4377,4392,4458,4509,4515,4518,4545,4548,4554,4614,4677,4731,4785,4899,5091,5112,5160,5166,5199,5253,5268,5304,5313,5367,5391,5394,5445,5544,5562,5595,5637,5643,5730,5748,5826,5871,5877,5892,5916,5985,6000,6030,6051,6054,6081,6096,6162,6213,6219,6222,6249,6252,6258,6318,6381,6435,6489,6603,6795]
    
        # the predefined symbol will be end here
        self.mappedsymbols = []

        # save the scatter pilots here
        self.scatteredpilots = []

        # reference to opencl buffers
        self.skeleton_opencl_buffers = []

        # save a reference to the opencl context
        self.ctx = ctx

        # save a reference to the opencl context
        self.queue = queue

        # hold a refernce to opencl_thread lock
        self.cl_thread_lock = cl_thread_lock

        # counter for symbol mapping
        self.symbol_counter = 0

        mf = cl.mem_flags

        #read in the OpenCL source file as a string
        self.fd = open('fft_mapper.cl', 'r')
        fstr = "".join(self.fd.readlines())
        self.program = cl.Program(ctx, fstr).build()

        #create the opencl kernel
        self.kernel_symbols0_6817 = cl.Kernel(self.program,"map_symbols0_6817")

        #create the opencl kernel
        self.kernel_symbols1_6817 = cl.Kernel(self.program,"map_symbols1_6817")

        #create the opencl kernel
        self.kernel_symbols2_6817 = cl.Kernel(self.program,"map_symbols2_6817")

        #create the opencl kernel
        self.kernel_symbols3_6817 = cl.Kernel(self.program,"map_symbols3_6817")

        #create the opencl kernel
        self.kernel_symbols0_1704 = cl.Kernel(self.program,"map_symbols0_1704")

        #create the opencl kernel
        self.kernel_symbols1_1704 = cl.Kernel(self.program,"map_symbols1_1704")

        #create the opencl kernel
        self.kernel_symbols2_1704 = cl.Kernel(self.program,"map_symbols2_1704")

        #create the opencl kernel
        self.kernel_symbols3_1704 = cl.Kernel(self.program,"map_symbols3_1704")

        self.fd.close()

	# save the opencl queue
	self.queue = queue
	# save the opencl context
	self.ctx = ctx
        # thread lock for opencl
        self.thread_lock = thread_lock

        # init all the buffers and copy them to the compute device
        self.create_skeletons()

    # resets the symbol_counter
    def map_symbols_reset(self):
        self.symbol_counter = 0

    # map the symbols using the skeletons and the actual data
    # takes a opencl buffer as argument that holds *usefulcarriers* complex values
    def map_symbols(self, inputbuffer, destbuffer):
        # load the correct skeleton
        skeleton = self.skeleton_opencl_buffers.index(self.symbol_counter)

        self.cl_thread_lock.acquire()

        # copy the skeleton into the destination buffer
        cl.enqueue_copy(self.queue, destbuffer, skeleton)

        # enqueue the corrent kernel, depending on odfmcarriers and symbol_counter
        if self.globalsettings.odfmcarriers == 6817:
            if self.symbol_counter % 4 == 0:
                self.kernel_symbols0_6817.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols0_6817,(1,),None )
            if self.symbol_counter % 4 == 1:
                self.kernel_symbols1_6817.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols1_6817,(1,),None )
            if self.symbol_counter % 4 == 2:
                self.kernel_symbols2_6817.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols2_6817,(1,),None )
            if self.symbol_counter % 4 == 3:
                self.kernel_symbols3_6817.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols3_6817,(1,),None )

        elif self.globalsettings.odfmcarriers == 1704:
            if self.symbol_counter % 4 == 0:
                self.kernel_symbols0_1704.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols0_1704,(1,),None )
            if self.symbol_counter % 4 == 1:
                self.kernel_symbols1_1704.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols1_1704,(1,),None )
            if self.symbol_counter % 4 == 2:
                self.kernel_symbols2_1704.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols2_1704,(1,),None )
            if self.symbol_counter % 4 == 3:
                self.kernel_symbols3_1704.set_args( inputbuffer, destbuffer)
                cl.enqueue_nd_range_kernel(self.queue,self.kernel_symbols3_1704,(1,),None )

        self.cl_thread_lock.release()

        self.symbol_counter += 1
        if self.symbol_counter == 272:
            self.symbol_counter = 0

    # create all the 272 symbols
    def create_skeletons(self):
        # for every frame
        for f in range(0,4):
            self.tps_pilots = tps(self.globalsettings,f)
            #for every symbol
            for i in range(0, 68):
                 # generate a new symbol
                 self.create_symbol_skeleton(i,self.tps_pilots.get_next())
                 tmp = numpy.array(self.mappedsymbols, dtype=numpy.complex64)
                 newbuf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=8*self.globalsettings.odfmuseablecarriers)
                 cl.enqueue_copy(self.queue, newbuf, tmp)
                 self.skeleton_opencl_buffers.append(newbuf)

    # input the current symbol [0,67], fills the scatteredpilots array with data
    def scatteredpilots_generate_array(self, symbol_index):
        self.p = 0
        self.k = 0
        self.scatteredpilots = []
        while self.k < self.globalsettings.usefulcarriers:
            self.k = 0 + 3 * (symbol_index % 4) + 12 * self.p
            self.p += 1
            self.scatteredpilots.append(self.k)

    # generates a new mappedsymbols array with: scattered-pilots, continual-pilots, tps-pilots
    def create_symbol_skeleton(self, symbol_index, tps_bit):
        # create the scatteredpilots array
        self.scatteredpilots_generate_array(symbol_index)

        # this one generates the pbrs sequence for pilots, reinit on each new ofdm symbol
        self.pbrs = pbrs()

        # create the skeleton
        for i in range(0,self.globalsettings.odfmuseablecarriers):
            # get the next wk
            self.wk = self.pbrs.get_next()

            if self.tpssarray.count(i) > 0:
                if self.wk == 1:
                    self.tmp = complex(-1.0, 0)
                else:
                    self.tmp = complex(1.0, 0)
                if self.symbol_index == 0:
                    self.mappedsymbols.append(self.tmp)
                else:
                    self.tmp = complex(self.tmp.real * self.tpsbit, 0)
                    self.mappedsymbols.append(self.tmp)

            elif self.continualpilotsarray.count(i) > 0:
                if self.wk == 1:
                    self.tmp = complex(-4.0 / 3.0, 0)
                else:
                    self.tmp = complex(4.0 / 3.0, 0)
                self.mappedsymbols.append(self.tmp)

            elif self.scatteredpilots.count(i) > 0:
                if self.wk == 1:
                    self.tmp = complex(-4.0 / 3.0, 0)
                else:
                    self.tmp = complex(4.0 / 3.0, 0)
                self.mappedsymbols.append(self.tmp)

            else:
                self.mappedsymbols.append(complex(0, 0))  # dummy data

class pbrs():
    def __init__(self): #one bit per carrier
        self.generator = 2047

    def get_next(self):
        self.ret = self.generator >> 10
        self.temp = ((self.generator >> 10)&1)^((self.generator >> 8)&1)
        self.generator <<= 1
        self.generator |= (self.temp & 1)
        self.generator &= 2047
        return self.ret

class tps():
    def __init__(self,globalsettings,frame_index):
        self.polarity = 1
        # the bch polynom in octal is 041567
        # the reverse is 076541
        self.bchpolynom = [1,1,1,0,1,1,1,0,1,1,0,0,0,0,1]
        self.bitarray = []
        self.shreg = []
        self.bitarray.append(0) #s0 is always 0, this bit isn't included in BCH parity bits

        # sync word
        if (frame_index & 0x00000001) == 0x00000001:
            self.bitarray.append(0) 
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(1)
            self.bitarray.append(0)
        else:
            self.bitarray.append(1) 
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(1)
        
        # tps length indicator
        self.bitarray.append(0) 
        self.bitarray.append(1)
        self.bitarray.append(1)
        self.bitarray.append(1)
        self.bitarray.append(1)
        self.bitarray.append(1)

        # frame bits
        self.bitarray.append((frame_index & 0x02))
        self.bitarray.append((frame_index & 0x01))

        # constelation bits
        if globalsettings.modulation == 2:
            self.bitarray.append(0)
            self.bitarray.append(0)
        elif globalsettings.modulation == 4:
            self.bitarray.append(0)
            self.bitarray.append(1)
        elif globalsettings.modulation == 6:
            self.bitarray.append(0)
            self.bitarray.append(0)

        # Non hierarchical, alpha = 1, ignore other alpha settings
        self.bitarray.append(0)
        self.bitarray.append(0)
        self.bitarray.append(0)

        # code rate bits
        if globalsettings.coderate == 0.5:
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(0)
        elif globalsettings.coderate == (2.0 / 3.0):
            self.bitarray.append(0)
            self.bitarray.append(0)
            self.bitarray.append(1)
        elif globalsettings.coderate == 0.75:
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(0)
        elif globalsettings.coderate == (5.0 / 6.0):
            self.bitarray.append(0)
            self.bitarray.append(1)
            self.bitarray.append(1)
        elif globalsettings.coderate == 0.875:
            self.bitarray.append(1)
            self.bitarray.append(0)
            self.bitarray.append(0)

        # code rate bits, Non hierarchical, set other bits to zero
        self.bitarray.append(0)
        self.bitarray.append(0)
        self.bitarray.append(0)

        # guard interval bits
        if globalsettings.guardinterval == 0.25:
            self.bitarray.append(1)
            self.bitarray.append(1)
        elif globalsettings.guardinterval == 0.125:
            self.bitarray.append(1)
            self.bitarray.append(0)
        elif globalsettings.guardinterval == 0.0625:
            self.bitarray.append(0)
            self.bitarray.append(1)
        elif globalsettings.guardinterval == 0.03125:
            self.bitarray.append(0)
            self.bitarray.append(0)

        # transmission mode bits
        if globalsettings.odfmmode == 8192:
            self.bitarray.append(0)
            self.bitarray.append(1)
        elif globalsettings.odfmmode == 2048:
            self.bitarray.append(0)
            self.bitarray.append(0)

        if (frame_index & 0x00000001) == 0x00000001:
            self.bitarray.append((globalsettings.modulation & 0x00008000)>>15)
            self.bitarray.append((globalsettings.modulation & 0x00004000)>>14)
            self.bitarray.append((globalsettings.modulation & 0x00002000)>>13)
            self.bitarray.append((globalsettings.modulation & 0x00001000)>>12)
            self.bitarray.append((globalsettings.modulation & 0x00000800)>>11)
            self.bitarray.append((globalsettings.modulation & 0x00000400)>>10)
            self.bitarray.append((globalsettings.modulation & 0x00000200)>>9)
            self.bitarray.append((globalsettings.modulation & 0x00000100)>>8)
        else:
            self.bitarray.append((globalsettings.modulation & 0x00000080)>>7)
            self.bitarray.append((globalsettings.modulation & 0x00000040)>>6)
            self.bitarray.append((globalsettings.modulation & 0x00000020)>>5)
            self.bitarray.append((globalsettings.modulation & 0x00000010)>>4)
            self.bitarray.append((globalsettings.modulation & 0x00000008)>>3)
            self.bitarray.append((globalsettings.modulation & 0x00000004)>>2)
            self.bitarray.append((globalsettings.modulation & 0x00000002)>>1)
            self.bitarray.append((globalsettings.modulation & 0x00000001)>>0)


        self.shreg = self.bitarray

        # insert 0's
        for j in range(0,(67-53)):
             self.shreg.insert(0,0)

        print len(self.shreg)

        # bch encode the tps bits
        for j in range(0,53):
             for i in range(0,j):
                 self.shreg.insert(0,self.shreg.pop(66))
             for p in self.bchpolynom:
                 self.shreg.insert(0,self.shreg.pop(66)^p)
             for i in range(j,(67-53)):
                 self.shreg.insert(0,self.shreg.pop(66))
        print self.shreg

        # copy paritiy bits
        for j in range(0,(67-53)):
             self.bitarray.append(self.shreg.pop(0))

        print self.bitarray

    def get_next(self):
        # do differntial encoding
        # if s=1 invert the last bit
        if self.bitarray.pop(0) == 1:
            self.polarity *= -1
        return self.polarity

 

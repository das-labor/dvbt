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

#try:
    #import pyfft
#except ImportError, e:
    #raise Exception("Please install numpy from 'http://pypi.python.org/pypi/pyfft'")

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
        self.thread_event = threading.Event()

        # locks the opencl access
        self.cl_thread_lock = threading.Lock()


        ######################################
        # create input and output fifos

        tmpdir = tempfile.mkdtemp()
        self.inputfd = os.path.join(tmpdir, 'dvbtinputfifo')
        try:
            os.mkfifo(self.inputfd)
        except OSError, e:
            raise Exception("Failed to create FIFO: %s" % e)

        self.outputfd = os.path.join(tmpdir, 'dvbtoutputfifo')
        try:
            os.mkfifo(self.outputfd)
        except OSError, e:
            raise Exception("Failed to create FIFO: %s" % e)

	# save the opencl context
        self.ctx = ctx

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)

        # helper class for loading kernels
        self.kernelh = Kernelhelper(ctx)


        ######################################
        # calculate all settings

        self.ctx = ctx
        self.queue = self.queue

        self.bandwidth = bandwidth
        self.coderate = coderate
        self.odfmmode = mode
        self.guardinterval = guardinterval
        self.modulation = modulation
        self.alpha = alpha
        self.cellid = cellid

        if mode == 8192:
            self.odfmcarriers = 6817
            self.odfmuseablecarriers = 6048
        elif mode == 2048:
            self.odfmcarriers = 1705
            self.odfmuseablecarriers = 1512

        self.framespersuperframe = 4
        self.symbolsperframe = 68
        self.bytespertspacket = 188
        self.bytesperrspacket = 204

        self.symbolrate = self.bandwidth * 1000000 / 0.875
        self.ofdmsymbollengthuseful = (1 / self.symbolrate) * self.odfmmode
        self.ofdmguardintervallength = (1 / self.symbolrate) * self.odfmmode * self.guardinterval
        self.ofdmsymbollength = self.ofdmsymbollengthuseful + self.ofdmguardintervallength
        self.ofdmsymbolspersecond = self.symbolrate / self.odfmmode /  (1 + self.guardinterval)
        self.ofdmframespersecond = self.ofdmsymbolspersecond / self.symbolsperframe

        # round the usablebitrate reported to ffmpeg
        self.usablebitrateperodfmsymbol = self.odfmuseablecarriers * self.modulation * self.coderate * 0.921182266
        self.usablebitrate = self.ofdmsymbolspersecond * self.usablebitrateperodfmsymbol
        self.tspacketspersecond = self.usablebitrate / (8 * 188)
        self.bitspersuperframe = self.odfmuseablecarriers * self.symbolsperframe * self.framespersuperframe * self.modulation / self.coderate 
        self.conv_enc_uints_in = self.odfmuseablecarriers * self.symbolsperframe * self.framespersuperframe * self.modulation * 2 / 32
        self.conv_enc_uints_out = self.odfmuseablecarriers * self.symbolsperframe * self.framespersuperframe * self.modulation * 2
        self.bytespersuperframe = self.bitspersuperframe / 8
        self.tspacketspersuperframe = self.bytespersuperframe / self.bytespertspacket

        
        ######################################
        # load the opencl kernels

        self.ockernelA = self.kernelh.load('outer_coding.cl','run_pbrs_rs')
        self.ockernelB = self.kernelh.load('outer_coding.cl','run_oi_A')
        self.ickernel = self.kernelh.load('inner_coding.cl','run_ic_A')
        self.iikernel = self.kernelh.load('inner_interleaver.cl','run_ii_A')
        self.smkernel = self.kernelh.load('signal_mapper.cl','run_A')
        if self.odfmmode == 2048:
            self.sikernel = self.kernelh.load('symbol_interleaver.cl','run2K_A')
        elif self.odfmmode == 8192:
            self.sikernel = self.kernelh.load('symbol_interleaver.cl','run8K_A')
        return
        self.fmkernel = self.kernelh.load('symbol_mapper.cl','run')

        self.idftkernel = self.kernelh.load('ochafik.com_fft.cl','dft')

        #self.fftplan = pyfft.cl.Plan(self.odfmmode, dtype=numpy.complex128, normalize=True, fast_math=True, context=self.ctx, queue=self.queue)

        ######################################
        # create the opencl buffers depending on self

        # buffer transfering data to the compute device
        self.cl_input_buf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=(self.tspacketspersuperframe*self.bytespertspacket) )

        # buffer holding the data from rs encoder
        self.dest_buf_A = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=(self.tspacketspersuperframe*self.bytesperrspacket+17*11) )

        # buffer holding the data from outer interleaver
        self.dest_buf_B = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=(self.tspacketspersuperframe*self.bytesperrspacket+4) )

        # buffer holding the data from inner coder
        self.dest_buf_C = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.conv_enc_uints_in * 4) # 4 bytes per uint

        # buffer holding the data from inner coder
        self.dest_buf_D = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.conv_enc_uints_out * 4) # 4 bytes per uint (bitspersuperframe)

        # buffer holding the data from inner interleaver
        # same size as inner coder buffer, as the data is just interleaved
        self.dest_buf_E = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.conv_enc_uints_out * 4) # 4 bytes per uint (bitspersuperframe)

        # buffer holding the data used by pyfft
        #self.fftbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=self.odfmmode * 16) # holding to complex values

        self.cl_output_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size= self.odfmmode * (1+self.guardinterval) * 16 * self.framespersuperframe * self.symbolsperframe ) # holding to complex values

    def get_input_fifo(self):
        return self.inputfd

    def get_output_fifo(self):
        return self.outputfd

    def get_symbolrate(self):
        return self.symbolrate

    def get_usablebitrate(self):
        return self.usablebitrate

    def get_tspacketspersecond(self):
        return self.tspacketspersecond

    def get_ofdmsymbolspersecond(self):
        return self.ofdmsymbolspersecond

    def get_bytespersuperframe(self):
        return self.bytespersuperframe

    def get_symbolspersecondwritten(self):
        return self.symbolswrittentofifo

    def stop(self):
        self.thread_event.set()
        try:
            self.workingthread.join(10)
        except:
            pass
        try:
            self.timerobj.cancel()
        except:
            pass

    def run(self):
        self.thread_event.clear()
        self.workingthread = threading.Thread(target=self.worker_thread)
        self.workingthread.start()
        self.timerobj = threading.Timer(1.0, self.update_timer)
        self.timerobj.start()

    def update_timer(self):
        self.cl_thread_lock.acquire()
        self.symbolswrittentofifo = self.symbolcounter
        self.symbolcounter = 0
        self.cl_thread_lock.release()

        self.timerobj = threading.Timer(1.0, self.update_timer)
        self.timerobj.start()

    def worker_thread(self):
        event = None
        inputfifo = open(self.inputfd,"r")
        outputfifo = open(self.outputfd,"w")

        self.symbolcounter = 0
        encoded_data = numpy.array(zeros(self.odfmmode * (1+self.guardinterval) * 2 * self.framespersuperframe * self.symbolsperframe) ,dtype=numpy.complex64)

        event = cl.enqueue_fill_buffer( self.queue, self.dest_buf_A , numpy.array(0,dtype=numpy.uint8), 0, 11*17, wait_for=None )
        event = cl.enqueue_fill_buffer( self.queue, self.dest_buf_B , numpy.array(0,dtype=numpy.uint8), 0, 4, wait_for=event )

        while not self.thread_event.isSet():
            # read data from fifo
            tspacket = inputfifo.read( self.bytespersuperframe )
            if len(tspacket) == 0:
                break

            #copy to CL device, the more the better
            event = cl.enqueue_copy( self.queue, self.cl_input_buf, numpy.fromstring(tspacket, dtype=numpy.uint32), wait_for=event )

            # pbrs, rs-encoder
            #  encode all ts packet per superframe at once
            #  input is litte endian, output is litte endian
            #  in: $x * 188 bytes, out: $x * 204 bytes

            self.ockernelA.set_args(self.cl_input_buf, self.dest_buf_A)
            event = cl.enqueue_nd_range_kernel( self.queue, self.ockernelA, (self.tspacketspersuperframe,), None, wait_for=event )

            # convolutional interleaver:
            #  input is litte endian, output is big endian
            #  inner encoder needs data in big endian format
            #  in: 11*17*4bytes + $x * 204 bytes, out: $x * 204 bytes + 4 bytes
            #  11*17*4bytes last bytes of previous kernel run

            self.ockernelB.set_args(self.dest_buf_A, self.dest_buf_B)
            event = cl.enqueue_nd_range_kernel( self.queue, self.ockernelB, (self.tspacketspersuperframe*self.bytesperrspacket,), None, wait_for=event )

            # prepare dest_buf_A for next kernel run
            event = cl.enqueue_copy( self.queue, self.dest_buf_A, self.dest_buf_B, byte_count=17*11, src_offset=self.tspacketspersuperframe*self.bytesperrspacket-17*11 , dest_offset=0, wait_for=event )

            # convolutional encoder 1/2:
            #  encode all rs packets per superframe at once
            #  input is big endian
            #  process 32 bits per kernel
            #  always store as bitstream in uints (1 bit per uint)

            self.ickernel.set_args( self.dest_buf_B, self.dest_buf_C, numpy.uint32(self.modulation) )
            event = cl.enqueue_nd_range_kernel( self.queue, self.ickernel, (self.bitspersuperframe,), None, wait_for=event )

            # TODO:
            #  implement puncturing

            # bitwise convolutional interleaver:
            #  interleave (modulation * 127) bits at once
            #  always store as bitstream in uints (1 bit per uint)

            self.iikernel.set_args( self.dest_buf_C, self.dest_buf_D, numpy.uint32(self.modulation) )
            event = cl.enqueue_nd_range_kernel( self.queue,self.iikernel, (int(self.bitspersuperframe*2/self.modulation),), None, wait_for=event )

            # symbolmapper:
            #  convert <modulation bits> into a complex number
            #  store as float2 / double2

            self.smkernel.set_args(self.dest_buf_D, self.dest_buf_E, numpy.uint32(self.modulation))
            event = cl.enqueue_nd_range_kernel( self.queue,self.smkernel, (int(self.bitspersuperframe*2/self.modulation),), None, wait_for=event )

            for symbol in range(0, self.symbolsperframe):
                for frame in range(0, self.framespersuperframe):

                    # symbol interleaver:
                    #  inerleave the symbols using a lfsr
                    #  input is odfmcarriers float2 / double2, output is odfmcarriers float2 / double2
                    #  threadcount: 1
                    #  TODO: find faster implementation

                    self.sikernel.set_args(self.dest_buf_E, self.dest_buf_F)
                    event = cl.enqueue_nd_range_kernel( self.queue, self.sikernel, (1,), None, wait_for=event )

                    # pilot insertion:
                    #  insert continual pilots, tps pilots and scattered pilots
                    #  input is odfmcarriers float2 / double2 and tps bits, output is odfmmode float2 / double2

                    self.fmkernel.set_args(self.dest_buf_F, self.dest_buf_G)
                    event = cl.enqueue_nd_range_kernel( self.queue, self.fmkernel, (1,), None, wait_for=event )

                    # TODO
                    tmp = [float(0) + 1j*float(0)] * ofdm_mode
                    for i in range(0,size):
                        tmp[(ofdm_mode-size+1)/2+i] = data_to_encode[i]
                    for i in range(0,ofdm_mode/2):
                        data_to_encode[i] = tmp[ofdm_mode/2+i]
                        data_to_encode[i+ofdm_mode/2] = tmp[i]

                    # this is for pyfft
                    #cl.enqueue_copy(self.queue, self.fftbuffer, data_to_encode).wait()
                    #ffttcommandqueue = self.fftplan.execute( self.fftbuffer, data_out=None, inverse=True, batch=1, wait_for_finish=False )
                    #fftEvent = cl.enqueue_barrier(ffttcommandqueue)

                    # idft, TODO: use radix-2 ifft instead
                    # threadcount: odfmmode
                    self.idftkernel.set_args(self.dest_buf_G, self.dest_buf_H)
                    event = cl.enqueue_nd_range_kernel( self.queue, self.idftkernel, (self.odfmmode,), None, wait_for=event )

                    # create the guard interval
                    destoffset = (self.odfmmode * (1+self.guardinterval) * 16) * (frame+symbol*self.framespersuperframe)
                    event = cl.enqueue_copy( self.queue, self.cl_output_buf, self.dest_buf_H, byte_count=int(16 * self.odfmmode), src_offset=0, dest_offset=int(self.odfmmode * self.guardinterval * 16)+destoffset,wait_for=event)
                    event = cl.enqueue_copy( self.queue, self.cl_output_buf, self.dest_buf_H, byte_count=int(self.odfmmode * self.guardinterval * 16), src_offset=int(self.odfmmode - self.odfmmode * self.guardinterval) * 16 ,dest_offset=destoffset,wait_for=event)
         
                    self.cl_thread_lock.acquire()
                    self.symbolcounter += 2 * self.odfmmode * (1+self.guardinterval)
                    self.cl_thread_lock.release()

            #copy superframe at once
            event = cl.enqueue_copy( self.queue, encoded_data, self.cl_output_buf, wait_for=event ) # waits for completition by default

            #TODO float to uint conversion ?
            outputfifo.write(encoded_data)


        inputfifo.close()
        outputfifo.close()

        self.cleanup()


    def cleanup(self):
        print "bla"


class Kernelhelper:
    def __init__(self,ctx):
        self.ctx = ctx
    def load(self,filepath,kernelname):
        #read in the OpenCL source file as a string
        self.f = open(filepath, 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(self.ctx, fstr).build()
        self.f.close()

        #create the opencl kernel
        return cl.Kernel(self.program,kernelname)


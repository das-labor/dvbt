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

import pyopencl as cl
import numpy
from pyfft.cl import Plan
import pyopencl.array as cl_array

import outer_coding
import time
import threading
import mapper
import clfifo
import inner_coding
import guardinterval

class DVBTencoder:
    def __init__(self,globalsettings,eventstop,lock):
        # store the settings
        self.globalsettings = globalsettings
        self.eventstop = eventstop
        self.globallock = lock

        # create a event for signaling data can be processed
        self.thread_event = threading.Event()

        # locks the opencl access
        self.cl_thread_lock = threading.Lock()

        # open the input fifo
        self.inputfd = open(globalsettings.ffmpegfifo, 'r+')

        # open the output fifo
        self.outputfd = open(globalsettings.openglfifo, 'w+')

	# create a opencl context
        try:
           self.ctx = cl.create_some_context()
           for any_platform in cl.get_platforms():
              for found_device in any_platform.get_devices():
                 if found_device.name == globalsettings.computedevice:
		    self.ctx = cl.Context(devices=[found_device])
                    break
        except ValueError:
            print "ERROR %s" % ValueError

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)

        # opencl fifo ffmpeg -> outer coder, 128 * 188 * uint
        self.cfifo1 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*32*188)

        # opencl fifo outer coder -> inner coder, 128 * 204 * uint
        self.cfifo2 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*32*204)

        # opencl fifo inner coder -> symbol interleaver and mapper
        self.cfifo3 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.complex64), 32*1024)

        # opencl fifo symbol interleaver and mapper -> ifft
        self.cfifo4 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.complex64), 32*1024)

        # opencl fifo ifft -> guard interval / opengl output
        #self.cfifo5 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.complex64), 32*1024)

        print "compiling kernels, this may take a while\nTODO: precompile binaries"
        # create the outer encoder
        self.fifo_buf_size = 32
	self.oc = outer_coding.encoder(self.ctx,self.queue,self.cl_thread_lock, self.cfifo1, self.cfifo2, self.fifo_buf_size)

        # create the inner encoder
	self.ic = inner_coding.encoder(globalsettings, self.ctx, self.queue, self.cl_thread_lock, self.cfifo2, self.cfifo3)

        # create the ofdm symbol mapper
        self.symbolmapper = mapper.mapper(globalsettings, self.ctx, self.queue, self.cl_thread_lock, self.cfifo3, self.cfifo4 )

        # create a fft plan
        self.fftplan = Plan(self.globalsettings.odfmmode,dtype=numpy.complex64,normalize=True, fast_math=True,context=self.ctx, queue=self.queue)

        # opencl buffer holding data for the ifft - including pilots # 8k or 2k size ???
        self.fftbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=(self.globalsettings.odfmmode*8))

        self.gi = guardinterval.encoder(globalsettings, self.ctx, self.queue, self.cl_thread_lock, self.fftbuffer, self.outputfd)

        # create a new thread for reading input data asyncronly
        self.thread_input_fifo = threading.Thread(group=None,target=self.thread_input_from_fifo)

        # create a new thread for outer coder
        self.thread_oc = threading.Thread(group=None,target=self.thread_outer_coder)

        # create a new thread for inner coder
        self.thread_ic = threading.Thread(group=None,target=self.thread_inner_coder)

        # create a new thread for symbol mapper
        self.thread_sm = threading.Thread(group=None,target=self.thread_symbol_mapper)

        # create a new thread for ifft and guard interval creation
        self.thread_if = threading.Thread(group=None,target=self.thread_ifft)

    def thread_input_from_fifo(self):
        
        fifo_dest_buf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=(self.fifo_buf_size*188))
        while self.eventstop.is_set() == False:
            tspacket = self.inputfd.read(self.fifo_buf_size*188)
            if len(tspacket) == 0:
                break
            fifo_data = numpy.fromstring(tspacket, dtype=numpy.uint32)
            
            self.cl_thread_lock.acquire()
            cl.enqueue_copy(self.queue, fifo_dest_buf, fifo_data)
            self.cl_thread_lock.release()

            # no need to lock the fifo
            self.cfifo1.append(fifo_dest_buf,(self.fifo_buf_size*188)/4) 


    def thread_outer_coder(self):
        while self.eventstop.is_set() == False:
            self.oc.encode()

    def thread_inner_coder(self):
        while self.eventstop.is_set() == False:
            self.ic.encode()

    def thread_symbol_mapper(self):
        while self.eventstop.is_set() == False:
            self.symbolmapper.map_symbols()

    def thread_ifft(self):
        iteration = 0
        t = time.time()
        while self.eventstop.is_set() == False:
            iteration += 1
            # copy data from fifo
            self.cfifo4.pop(self.fftbuffer , self.globalsettings.odfmmode)
            self.cl_thread_lock.acquire()
            self.fftplan.execute(self.fftbuffer, data_out=None, inverse=True, batch=1, wait_for_finish=True)
            self.gi.encode()
            self.cl_thread_lock.release()
            if (time.time() - t) > 1.0:
                self.debugprint( "MSymbols/s out %f " % (self.globalsettings.odfmmode*2.0*iteration/0x100000) )
                iteration = 0
                t = time.time()

            # write data to fifo
            #self.cfifo5.append(self.fftbuffer, self.globalsettings.odfmmode)


    def run(self):
        self.debugprint("Opencl backend alive!")

        self.thread_input_fifo.start()
        self.thread_oc.start()
        self.thread_ic.start()
        self.thread_sm.start()
        self.thread_if.start()

        self.eventstop.wait()

        self.debugprint("exiting!")
        self.thread_input_fifo.cancel()
        self.thread_input_fifo.join()
        self.thread_oc.cancel()
        self.thread_oc.join()
        self.thread_ic.cancel()
        self.thread_ic.join()
        self.thread_sm.cancel()
        self.thread_sm.join()
        self.thread_if.cancel()
        self.thread_if.join()
        self.cleanup()

    def cleanup(self):

        self.inputfd.close()
        self.outputfd.close()

    def debugprint(self, value):
        self.globallock.acquire()
        print value
        self.globallock.release()


def startbackend(globalsettings,eventstop,lock):
    backend = DVBTencoder(globalsettings,eventstop,lock)
    backend.run()


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

class OpenCL:
    def __init__(self,globalsettings,eventstart,eventstop,lock):
        # store the settings
        self.globalsettings = globalsettings
        self.eventstart = eventstart
        self.eventstop = eventstop
        self.globallock = lock

        # create a event for signaling data can be processed
        self.thread_event = threading.Event()

        # locks the opencl access
        self.cl_thread_lock = threading.Lock()

        # open the input fifo
        self.fd = open(globalsettings.ffmpegfifo, 'r+')

        # create a new thread for reading input data asyncronly
        self.thread_input_fifo = threading.Thread(group=None,target=self.thread_input_from_fifo)

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

        # opencl fifo 1, 128 * 188 * uint
        self.cfifo1 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*128*188)

        # opencl fifo 2, 128 * 204 * uint
        self.cfifo2 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*128*204)

        # opencl fifo 3, TODO
        self.cfifo3 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*128*204*2)

        # opencl fifo 4, TODO
        self.cfifo4 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*128*204*2)

        # opencl fifo 5, TODO
        self.cfifo5 = clfifo.Fifo(self.ctx, self.queue, self.cl_thread_lock, numpy.dtype(numpy.uint32), 4*128*204*2)

        print "compiling kernels, this may take a while\nTODO: precompile binaries"
        # create the outer encoder
	self.oc = outer_coding.encoder(self.ctx,self.queue,self.cl_thread_lock, self.cfifo1, self.cfifo2)

        # create the ofdm symbol mapper
        #self.symbolmapper = mapper.mapper(globalsettings, self.ctx, self.queue, self.cl_thread_lock)

        # create a fft plan
        #self.fftplan = Plan((16, 16), queue=self.queue)

        # opencl buffer holding data for the ifft - including pilots # 8k or 2k size ???
        self.fftbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=(self.globalsettings.odfmcarriers*8))

        # opencl buffer holding the ofdm symbol data - no pilots are stored yet
        self.ofdmsymbolbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=(self.globalsettings.odfmuseablecarriers*8))

        # opencl buffer holding the time domain data, Tu + Tg
        self.timedomainbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=int(self.globalsettings.odfmuseablecarriers*8*(1+self.globalsettings.guardinterval)))


    def thread_input_from_fifo(self):
        dest_buf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=188*8*4)
        while self.eventstop.is_set() == False:
            tspacket = self.fd.read(188*8)
            if len(tspacket) == 0:
                break
            data = numpy.fromstring(tspacket, dtype=numpy.uint32)
            
            self.cl_thread_lock.acquire()
            cl.enqueue_copy(self.queue, dest_buf, data)
            self.cl_thread_lock.release()

            # no need to lock the fifo
            self.cfifo1.append(dest_buf,188*8)

            # any thread can set this event to wake the main statemachine
            self.thread_event.set()

    def run(self):
        self.debugprint("Opencl backend alive!")

        self.thread_input_fifo.start()

        while self.eventstop.is_set() == False:
            
            t = time.time()
	    
            #check for new data available from pipe
            
            self.oc.encode()


            # map $activecarriers complex data values onto one ofdm symbol
            #self.symbolmapper.map_symbols(self.ofdmsymbolbuffer,self.fftbuffer)

            # do an inverse FFT
            #self.fftplan.execute(self.fftbuffer, inverse=True) #gpu_data.data

            # start a thread for processing the final data
            #threading.Timer((1/30),self.output_to_fifo).start()
            
            self.debugprint( "%.9f sec/pass" % (time.time() - t))
            self.thread_event.clear()
            # TODO: how long to wait ?
            self.thread_event.wait(10000)

        self.debugprint("exiting!")
        self.cleanup()

    def cleanup(self):
        self.thread_output_fifo.cancel()
        self.thread_input_fifo.join()
        self.fd.close()

    def debugprint(self, value):
        self.globallock.acquire()
        print value
        self.globallock.release()

    # TODO: all
    #def output_to_fifo(self):

def startbackend(globalsettings,eventstart,eventstop,lock):
    backend = OpenCL(globalsettings,eventstart,eventstop,lock)
    backend.run()


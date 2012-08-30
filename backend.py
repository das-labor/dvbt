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
import outer_coding
import time
import threading
import mapper

class OpenCL:
    def __init__(self,globalsettings,eventstart,eventstop,lock):
        # store the settings
        self.globalsettings = globalsettings
        self.eventstart = eventstart
        self.eventstop = eventstop
        self.globallock = lock

        # create a delayed thread
        self.thread_output_fifo = threading.Timer((1/30),self.output_to_fifo)

        # create a event for signaling data can be processed
        self.thread_event = threading.Event()

        # locks the opencl access
        self.cl_thread_lock = threading.Lock()

        # locks the input queue
        self.input_thread_lock = threading.Lock()

        # holds a cl.Buffer already on the compute device
        self.queue_input = []

        # holds a cl.Buffer that has been outer encoded and is ready for inner coding
        self.queue_ic_input = []

        # holds a cl.Buffer that has the final output data
        self.queue_output = []

        # open the input fifo
        self.fd = open(globalsettings.ffmpegfifo, 'r+')

        # create a new thread for reading input data asyncronly
        self.thread_input_fifo = threading.Thread(group=None,target=self.thread_input_from_fifo)

	# create a opencl context
        try:
           for any_platform in cl.get_platforms():
              for found_device in any_platform.get_devices():
                 if found_device.name == globalsettings.computedevice:
		    self.ctx = cl.Context(devices=[found_device])
                    break
        except ValueError:
           self.ctx = cl.create_some_context()

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)

        # create the outer encoder
	self.oc = outer_coding.encoder(self.ctx,self.queue,self.cl_thread_lock)
   
        # create the ofdm symbol mapper
        self.symbolmapper = mapper.mapper(globalsettings, self.ctx, self.queue, self.cl_thread_lock)

    #cl.enqueue_write_buffer(self.queue, newbuf, data_to_encode)
    def thread_input_from_fifo(self):
        while self.eventstop.is_set() == False:
            tspacket = self.fd.read(188*8)
            if len(tspacket) == 0:
                break
            data_to_encode = numpy.fromstring(tspacket, dtype=numpy.uint32)
            newbuf = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=188*8)

            self.cl_thread_lock.acquire()
            cl.enqueue_copy(self.queue, newbuf, data_to_encode)
            self.cl_thread_lock.release()

            # make sure only one thread access this data at time
            self.input_thread_lock.acquire()
            self.queue_input.append(newbuf)
            self.input_thread_lock.release()

            # any thread can set this event to wake the main statemachine
            self.thread_event.set()

    def run(self):
        self.debugprint("Opencl backend alive!")

        #self.thread_output_fifo.start()
        self.thread_input_fifo.start()

        while self.eventstop.is_set() == False:
            
            t = time.time()
	    
            #check for new data available from pipe
            self.input_thread_lock.acquire()
            if len(self.queue_input) > 0:
                self.debugprint("input queue size %d" % (len(self.queue_input) * 188*8))
                opencl_buffer = self.queue_input.pop(0) 
                self.queue_ic_input.append(self.oc.encode(opencl_buffer))

            self.input_thread_lock.release()

            #check for data in the inner coding queue
            #if len(self.queue_ic_input) > 0: 
	        #self.queue_ic_input.append(self.oc.encode(opencl_buffer))
                #self.debugprint("data is here")


            # map 6008 complex data values onto one ofdm symbol
            #self.symbolmapper.map_symbols(inputbuffer,destbuffer)

            #self.oc.encode(self.tspacket)
	    #self.queue.finish()
            #self.lock.acquire()
	    #print "c:" , c[0]
	    #print "c:" , c[1]
	    #print "c:" , c[2]
	    #print "c:" , c[3]
	    #print "c:" , c[4]
	    #print "c:" , c[5]
	    #print "c:" , c[6]
	    #print "c:" , c[7]
            self.debugprint( "%.9f sec/pass" % (time.time() - t))
            self.thread_event.clear()
            # TODO: how long to wait ?
            self.thread_event.wait(10000)

        self.debugprint("exiting!")
        self.cleanup()

    def cleanup(self):
        self.thread_output_fifo.cancel()
        self.thread_input_fifo.join()

    def debugprint(self, value):
        self.globallock.acquire()
        print value
        self.globallock.release()

    # TODO: all
    def output_to_fifo(self):
        self.output_queue_lock.acquire()

        self.output_queue_lock.release()
        #self.timer_output_to_fifo.start()



def startbackend(globalsettings,eventstart,eventstop,lock):
    backend = OpenCL(globalsettings,eventstart,eventstop,lock)
    backend.run()


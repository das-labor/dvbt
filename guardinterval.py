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
import clfifo

class encoder():
    def __init__(self,globalsettings, ctx, queue, thread_lock, in_buffer, out_fifo):
        mf = cl.mem_flags

        #read in the OpenCL source file as a string
        self.f = open('guardinterval.cl', 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(ctx, fstr).build()
        self.f.close()

        # save globalsettings
        self.globalsettings = globalsettings
        
        #create the opencl kernel
        self.kernel1 = cl.Kernel(self.program,"encode")

        self.out_fifo = out_fifo

	# save the opencl queue
	self.queue = queue

	# save the opencl context
	self.ctx = ctx

        # thread lock for opencl
        self.cl_thread_lock = thread_lock
        
        #size of destination buffer
        self.dest_buf_size = 0.5*self.globalsettings.odfmmode*(1+self.globalsettings.guardinterval)

        #size of guard buffer
        self.guard_size = self.globalsettings.odfmmode*self.globalsettings.guardinterval   
        
        #size of source buffer
        self.src_buf_size = self.globalsettings.odfmmode
        
        # opencl buffer holding the computed data
        self.dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, int(self.dest_buf_size*4) )

        # opencl buffer holding the input data
        self.src_buf = in_buffer

        self.gi_data = numpy.array(numpy.zeros(int(self.dest_buf_size)), dtype=numpy.uint32)

    def encode(self):
        # copy data from fifo
        
        #self.cl_thread_lock.acquire()
        self.kernel1.set_args(self.src_buf, self.dest_buf, numpy.array(self.guard_size, dtype=numpy.uint32))
        cl.enqueue_nd_range_kernel(self.queue,self.kernel1,(int(self.src_buf_size/2),),None )
        cl.enqueue_copy(self.queue, self.gi_data, self.dest_buf).wait()
        #self.cl_thread_lock.release()

        # write data to fifo
        self.out_fifo.write(self.gi_data)



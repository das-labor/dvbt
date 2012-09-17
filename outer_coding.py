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
    def __init__(self, ctx, queue, thread_lock, in_fifo, out_fifo, batchsize):
        mf = cl.mem_flags

        #read in the OpenCL source file as a string
        self.f = open('outer_coding.cl', 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(ctx, fstr).build()
        self.f.close()

        # save the batch size
        self.batchsize = batchsize

        # save the dest buffer size
        self.dest_buf_size = batchsize * 204

        # save the src buffer size
        self.src_buf_size = batchsize * 188

        #create the opencl kernel
        self.kernel1 = cl.Kernel(self.program,"run")

	# save the opencl queue
	self.queue = queue

	# save the opencl context
	self.ctx = ctx

        # thread lock for opencl
        self.cl_thread_lock = thread_lock

        # opencl buffer holding the computed data
        self.dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.dest_buf_size*4)

        # opencl buffer holding the input data
        self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.src_buf_size*4)

        # opencl fifo
        self.inputfifo = in_fifo

        # opencl fifo
        self.outputfifo = out_fifo

    def encode(self):
        # copy data from fifo
        self.inputfifo.pop(self.src_buf,self.src_buf_size)
        self.cl_thread_lock.acquire()
        #self.program.run(self.queue, (self.batchsize,), None, src_buf, dest_buf)
        self.kernel1.set_args(self.src_buf, self.dest_buf)
        cl.enqueue_nd_range_kernel(self.queue,self.kernel1,(self.batchsize,),None )
        self.cl_thread_lock.release()
        # write data to fifo
        self.outputfifo.append(self.dest_buf,self.dest_buf_size)


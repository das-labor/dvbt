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

class encoder():
    def __init__(self, ctx, queue, thread_lock):
        mf = cl.mem_flags
        #read in the OpenCL source file as a string
        self.f = open('outer_coding.cl', 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(ctx, fstr).build()
        #create the opencl kernel
        self.kernel1 = cl.Kernel(self.program,"run")
	# save the opencl queue
	self.queue = queue
	# save the opencl context
	self.ctx = ctx
        # thread lock for opencl
        self.thread_lock = thread_lock
        #g = open('pbrs.bin', 'rb')
        #self.pbrs = numpy.fromstring(g.read(188*8), dtype=numpy.uint32)
        #self.pbrs_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.pbrs)

    def encode(self, src_buf):
        #init buffers
        self.thread_lock.acquire()
        dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, 204*8)

        #self.program.run(self.queue, (8,), None, src_buf, dest_buf)
        self.kernel1.set_args( src_buf, dest_buf)
        cl.enqueue_nd_range_kernel(self.queue,self.kernel1,(8,),None )
        self.thread_lock.release()

        #cl.enqueue_read_buffer(self.queue, self.dest_buf, c).wait()

	return dest_buf


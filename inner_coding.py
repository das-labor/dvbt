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
    def __init__(self, globalsettings, ctx, queue, thread_lock, in_fifo, out_fifo):
        mf = cl.mem_flags

        #read in the OpenCL source file as a string
        self.f = open('inner_coding.cl', 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(ctx, fstr).build()
        self.f.close()

        #save the global settings
        self.globalsettings = globalsettings

	# save the opencl queue
	self.queue = queue

	# save the opencl context
	self.ctx = ctx

        #create the opencl kernel
        if self.globalsettings.coderate == 0.5:
            if self.globalsettings.modulation == 2:
                self.kernel1 = cl.Kernel(self.program,"run_1_2_qpsk")
                self.inputsize = 63*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)

            if self.globalsettings.modulation == 4:
                self.kernel1 = cl.Kernel(self.program,"run_1_2_16qam")
                self.inputsize = 126*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)


            if self.globalsettings.modulation == 6:
                self.kernel1 = cl.Kernel(self.program,"run_1_2_64qam")
                self.inputsize = 189*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)


            self.num_workgroups = 16
            self.outputsize = 2016*8
            # opencl buffer holding the computed data
            self.dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.outputsize)

        elif self.globalsettings.coderate == 2.0 / 3.0:
            if self.globalsettings.modulation == 2:
                self.kernel1 = cl.Kernel(self.program,"run_2_3_qpsk")
                self.inputsize = 189*1*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)

            if self.globalsettings.modulation == 4:
                self.kernel1 = cl.Kernel(self.program,"run_2_3_16qam")
                self.inputsize = 189*2*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)

            if self.globalsettings.modulation == 6:
                self.kernel1 = cl.Kernel(self.program,"run_2_3_64qam")
                self.inputsize = 189*3*4
                self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.inputsize)

            self.num_workgroups = 32
            self.outputsize = 4032*8
            # opencl buffer holding the computed data
            self.dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, self.outputsize)
        else:
	    print "inner coding: unknown coderate ! exting ..."
            return

        self.inputsize /= 4 # convert to num_uint
        self.outputsize /= 8 # convert to num_float2

        # thread lock for opencl
        self.cl_thread_lock = thread_lock

        # opencl fifo
        self.inputfifo = in_fifo

        # opencl fifo
        self.outputfifo = out_fifo



    def encode(self):
        # copy data from fifo
        self.inputfifo.pop(self.src_buf, self.inputsize)
        self.cl_thread_lock.acquire()
        self.kernel1.set_args(self.src_buf, self.dest_buf)
        cl.enqueue_nd_range_kernel(self.queue,self.kernel1,(self.num_workgroups*63,),(63,),None )
        self.cl_thread_lock.release()
        # write data to fifo
        self.outputfifo.append(self.dest_buf, self.outputsize)


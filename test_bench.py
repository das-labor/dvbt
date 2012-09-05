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
#
# This script creates all the .cl files if neccessary.
#

import numpy
import pyopencl as cl
import time
import threading

import clfifo

class test_bench():
    def __init__(self,computedevice, duration):
	# create a opencl context
        try:
            self.ctx = cl.Context(devices=[computedevice])
        except ValueError:
            self.ctx = cl.create_some_context()
            print "error %s: couldn't find device %s, using default" % (ValueError, computedevice.name)

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)

        # create a event
        self.thread_event = threading.Event()

        # save duration
        self.duration = duration
        print "Benchmark will run for %d seconds..." % duration
        
    def test_execution_time(self, index):
        kernelname = []
        if index == 1:
            filename = "outer_coding.cl"
            kernelname.append("run")
            buffersize_in = 1504
            buffersize_out = 1632
            kernel_parallel_task = 8
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        elif index == 2:
            filename = "fft_mapper.cl"
            kernelname.append("map_symbols0_6817")
            kernelname.append("map_symbols1_6817")
            kernelname.append("map_symbols2_6817")
            kernelname.append("map_symbols3_6817")
            kernelname.append("map_symbols0_1704")
            kernelname.append("map_symbols1_1704")
            kernelname.append("map_symbols2_1704")
            kernelname.append("map_symbols3_1704")
            buffersize_in = 6049*8 # 6817 * float2
            buffersize_out = 6817*8 # 6817 * float2
            kernel_parallel_task = 1
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.complex64)

        else:
            print "index out of range"
            return
        
        for k in kernelname:
            print "Kernel \"%s\" from file \"%s\" :" % (k,filename)
            kernel = tb.load_kernel(filename, k)
        
            # opencl buffer
            self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=buffersize_in)
            # opencl buffer
            self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.WRITE_ONLY, size=buffersize_out)
            # copy data to the compute unit
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode)
            
            self.thread_event.clear()

            # create a delayed thread
            threading.Timer(self.duration,self.test_stop).start()

            t = time.time()
            testcycles = 0
            while self.thread_event.is_set() == False:
                kernel.set_args(self.inputbuffer, self.outputbuffer)
                cl.enqueue_nd_range_kernel(self.queue,kernel,(kernel_parallel_task,),None ).wait()
                testcycles += 1
                
            print "Test duration: %.9f sec" % (time.time() - t)
            print "testcycles: %d" % testcycles
            print "testcycles/sec: %f\n" % (testcycles / (time.time() - t))

    def test_stop(self):
        self.thread_event.set()

    def test_fifo(self):
        teststring = ""
        testarray = []
        passed = 0

        cf = clfifo.Fifo(self.ctx, self.queue, threading.Lock(), numpy.dtype(numpy.uint32), 100)

        # opencl buffer
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=4*10)
        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=8*10)

        data_to_decode = numpy.fromstring(numpy.random.bytes(80), dtype=numpy.uint32)

        for i in range(0,10):
            data_to_encode = numpy.fromstring(numpy.random.bytes(40), dtype=numpy.uint32)
            # copy data to the compute unit
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode)
            cf.append(self.inputbuffer,10)
            testarray.append(data_to_encode)

        
        #data_to_decode = numpy.empty_like(data_to_encode) #numpy.array(numpy.zeros(10000), dtype=numpy.uint32)
        for i in range(0,5):
            cf.pop(self.outputbuffer, 20)
            print "%d loop, %d items left" % (i,cf.len())
            cl.enqueue_copy(self.queue, data_to_decode, self.outputbuffer).wait()
            for j in range(0,10):
                if testarray[i*2][j] == data_to_decode[j]:
                    passed += 1
            for j in range(0,10):
                if testarray[i*2+1][j] == data_to_decode[j+10]:
                    passed += 1
        print "%d pass out of 100" % passed

    def load_kernel(self, filename, kernelname):
        mf = cl.mem_flags
        #read in the OpenCL source file as a string
        self.f = open(filename, 'r')
        fstr = "".join(self.f.readlines())
        #print "building programm"
        self.program = cl.Program(self.ctx, fstr)
        self.program.build()
        self.f.close()
        #print "building kernel"
        #create the opencl kernel
        return cl.Kernel(self.program,kernelname)

if __name__ == '__main__':
    for any_platform in cl.get_platforms():
        for found_device in any_platform.get_devices():
            if found_device.type == 4 :
                print "GPU: %s" % found_device.name
            elif found_device.type == 2 :
                print "CPU: %s" % found_device.name
            # for each compute unit
            tb = test_bench(found_device, 5)
            tb.test_fifo()
            tb.test_execution_time(1)
            tb.test_execution_time(2)

            


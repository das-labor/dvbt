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
        self.cd = computedevice
        # create a event
        self.thread_event = threading.Event()

        # save duration
        self.duration = duration
        print "Benchmark will run for %d seconds..." % duration
        
    def test_execution_time(self, index):
        print "test_execution_time:"
        kernelname = []
        if index == 1:
            filename = "outer_coding.cl"
            kernelname.append("run")
            buffersize_in = 1504
            buffersize_out = 1632
            kernel_parallel_task = 8
            kernel_workgroupsize = kernel_parallel_task
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
            kernel_workgroupsize = kernel_parallel_task
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.complex64)
        elif index == 3:
            filename = "signal_constellation2.cl"
            kernelname.append("qpsk")
            kernelname.append("qam_16")
            kernelname.append("qam_64")
            buffersize_in = 800*8/4 # 6049 * uint / 4
            buffersize_out = 800*8 # 6049 * float2 
            kernel_parallel_task = 800/4
            kernel_workgroupsize = kernel_parallel_task
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        elif index == 4:
            filename = "inner_coding.cl"
            kernelname.append("run_1_2_qpsk")
            kernelname.append("run_1_2_16qam")
            kernelname.append("run_3_4_qpsk")
            kernelname.append("run_3_4_16qam")
            buffersize_in = 126*4*2# 126 * uint
            buffersize_out = 2016*8 # 2016 * float2 
            kernel_parallel_task = 1008 #1024
            kernel_workgroupsize = 63 #64
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        elif index == 5:
            filename = "symbol_interleaver_mapper.cl"
            kernelname.append("interleaver_and_map_symbols0_6817")
            #kernelname.append("interleaver_and_map_symbols1_6817")
            #kernelname.append("interleaver_and_map_symbols2_6817")
            #kernelname.append("interleaver_and_map_symbols3_6817")
            buffersize_in = 6048*8# 6048 * float2 
            buffersize_out = 6817*8 # 6817 * float2 
            kernel_parallel_task = 6048
            kernel_workgroupsize = 216
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.complex64)
        elif index == 6:
            filename = "symbol_interleaver_mapper.cl"
            kernelname.append("interleaver_and_map_symbols0_1704")
            #kernelname.append("interleaver_and_map_symbols1_1704")
            #kernelname.append("interleaver_and_map_symbols2_1704")
            #kernelname.append("interleaver_and_map_symbols3_1704")
            buffersize_in = 1512*8# 1512 * float2 1512
            buffersize_out = 1704*8 # 1704 * float2 
            kernel_parallel_task = 1512
            kernel_workgroupsize = 216
            # generate random bytes
            data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.complex64)
        else:
            print "index out of range"
            return
        
        for k in kernelname:
            kernel = tb.load_kernel(filename, k)
            #print kernel.get_work_group_info(cl.kernel_work_group_info.COMPILE_WORK_GROUP_SIZE, self.cd)
            print "Max WORKGROUPSIZE is " 
            print kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, self.cd)
            print "requested: %d" % kernel_workgroupsize

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
                
                cl.enqueue_nd_range_kernel(self.queue,kernel,[kernel_parallel_task,],[kernel_workgroupsize,],g_times_l=False ).wait()
                testcycles += 1
                
            print "Test duration: %.9f sec" % (time.time() - t)
            print "testcycles: %d" % testcycles
            print "testcycles/sec: %f\n" % (testcycles / (time.time() - t))

    def test_stop(self):
        self.thread_event.set()

    def test_reedsolomon(self):
        print "test_reedsolomon:"
        testcycles = 0
        self.fd_input = open('test_bench_rs_input.csv', 'r')
        self.fd_output = open('test_bench_rs_output.csv', 'r')

        for line in self.fd_input:
            data_to_encode = numpy.fromstring(line, dtype=numpy.uint8, sep=",").tostring()
            data_to_encode = numpy.fromstring(data_to_encode, dtype=numpy.uint32)

            encoded_data = numpy.array(numpy.zeros(51), dtype=numpy.uint32)
            reference_data = numpy.fromstring(self.fd_output.readline(), dtype=numpy.uint8, sep=",")

            # opencl buffer uint
            self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=48*4)
            # opencl buffer uint
            self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=51*4)

            kernel = tb.load_kernel("outer_coding.cl", "test_rsencode")

            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
            kernel.set_args(self.inputbuffer, self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
            cl.enqueue_copy(self.queue, encoded_data, self.outputbuffer).wait()
            #print encoded_data.astype(numpy.uint8)
            if numpy.array_equal(numpy.fromstring(reference_data.tostring(), dtype=numpy.uint32), encoded_data):
                testcycles += 1
                print "Test PASS"
            else:
                print "Test FAIL"
                print "input data:"
                print numpy.fromstring(data_to_encode.tostring(), dtype=numpy.uint8)
                print "encoded data:"
                print numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8)
                print "reference data:"
                print reference_data

        if testcycles == 49:
            print "All tests PASS\n"
        else:
            print "more than one test FAILED\n"
        self.fd_input.close()
        self.fd_output.close()

    def test_energydispersal(self):
        print "test_energydispersal:"
        # opencl buffer uint
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=48*4)
        # opencl buffer uint
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=48*4)

        kernel = tb.load_kernel("outer_coding.cl", "test_ed")
        data_to_encode = numpy.random.random_integers(0,255,48).astype(numpy.uint32)
        data_to_decode = numpy.empty_like(data_to_encode)
        print data_to_encode.astype(numpy.uint8)
        cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
        kernel.set_args(self.inputbuffer, self.outputbuffer)
        cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
        cl.enqueue_copy(self.queue, data_to_decode, self.outputbuffer).wait()
        print data_to_decode.astype(numpy.uint8)

    def test_signalmapping(self):
        print "test_signalmapping:"
        # opencl buffer uint
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=4)
        # opencl buffer float2
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=8*4)

        kernel = tb.load_kernel("signal_constellation.cl", "qpsk")
        data_to_decode = numpy.array([0,0,0,0], dtype=numpy.complex64)
            
        for i in range(0,4):
            data_to_encode = numpy.array([i], dtype=numpy.uint32)
            print "%d%d%d%d%d%d" % ((i & 0x20)>>5,(i & 0x10)>>4,(i & 0x08)>>3,(i & 0x04)>>2,(i & 0x02)>>1,(i & 0x01)>>0)
            print "DVB-SPEC: %d%d" % ((i & 0x01)>>0,(i & 0x02)>>1)

            # copy data to the compute unit
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
            kernel.set_args(self.inputbuffer, self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
            cl.enqueue_copy(self.queue, data_to_decode, self.outputbuffer).wait()
            print data_to_decode

        kernel = tb.load_kernel("signal_constellation.cl", "qam_16")
        data_to_decode = numpy.array([0,0,0,0], dtype=numpy.complex64)

        for i in range(0,16):
            data_to_encode = numpy.array([i], dtype=numpy.uint32)
            print "%d%d%d%d%d%d" % ((i & 0x20)>>5,(i & 0x10)>>4,(i & 0x08)>>3,(i & 0x04)>>2,(i & 0x02)>>1,(i & 0x01)>>0)
            print "DVB-SPEC: %d%d%d%d" % ((i & 0x01)>>0,(i & 0x02)>>1,(i & 0x04)>>2,(i & 0x08)>>3)

            # copy data to the compute unit
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
            kernel.set_args(self.inputbuffer, self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
            cl.enqueue_copy(self.queue, data_to_decode, self.outputbuffer).wait()
            print data_to_decode

        kernel = tb.load_kernel("signal_constellation.cl", "qam_64")
        data_to_decode = numpy.array([0,0,0,0], dtype=numpy.complex64)

        for i in range(0,64):
            data_to_encode = numpy.array([i], dtype=numpy.uint32)
            print "%d%d%d%d%d%d" % ((i & 0x20)>>5,(i & 0x10)>>4,(i & 0x08)>>3,(i & 0x04)>>2,(i & 0x02)>>1,(i & 0x01)>>0)
            print "DVB-SPEC: %d%d%d%d%d%d" % ((i & 0x01)>>0,(i & 0x02)>>1,(i & 0x04)>>2,(i & 0x08)>>3,(i & 0x10)>>4,(i & 0x20)>>5)

            # copy data to the compute unit
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
            kernel.set_args(self.inputbuffer, self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
            cl.enqueue_copy(self.queue, data_to_decode, self.outputbuffer).wait()
            print data_to_decode

    def test_fifo(self):
        print "test_fifo:"
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
        if passed == 100:
            print "Test PASS"
        else:
            print "Test FAIL"

    def load_kernel(self, filename, kernelname):
        print "Kernel \"%s\" from file \"%s\" :" % (kernelname,filename)
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
    test_algorithm = 0
    for any_platform in cl.get_platforms():
        for found_device in any_platform.get_devices():
            if found_device.type == 4 :
                print "GPU: %s" % found_device.name
            elif found_device.type == 2 :
                print "CPU: %s" % found_device.name
            #print "max_work_group_size: %d" % found_device.max_work_group_size
            # for each compute unit
            tb = test_bench(found_device, 15)
            if test_algorithm == 0:
                tb.test_fifo()
                tb.test_energydispersal()
                tb.test_reedsolomon()
                test_algorithm = 1

            #tb.test_execution_time(1)
            #tb.test_execution_time(2)
            #tb.test_execution_time(3)
            #tb.test_execution_time(4)
            #tb.test_execution_time(5)
            #tb.test_execution_time(6)

            


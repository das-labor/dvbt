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

import os
import numpy
import pyopencl as cl
import time
import threading
import time
import string

class file_creator():
    def __init__(self):
        f = open('copyright', 'r')
        copyright = f.read()
        f.close()

        f = open('pbrs_kernel.cl', 'w')
        f.write(copyright)

        self.create_pbrs_kernel_start(f,"A")
        self.create_pbrs(f)
        self.create_pbrs_kernel_end(f)
        f.close()

        for any_platform in cl.get_platforms():
            for found_device in any_platform.get_devices():
                if found_device.type == 4 :
                    print "GPU: %s" % found_device.name
                    computedevice = found_device
                elif found_device.type == 2 :
                    print "CPU: %s" % found_device.name
        
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
        self.duration = 15

        self.kernelname = []
        self.filename = "pbrs_kernel.cl"
        self.kernelname.append("test_pbrs_A")

    def create_pbrs_kernel_start(self, f, name):
        f.write("/* input mpeg-ts packets, each packet has 188bytes */\n")
        f.write("__kernel void test_pbrs_%s( __global uint *in, __global uint *out)\n{\n" % name)
        f.write("uint workingreg[51];\nint pbrs_index = get_global_id(0);\nint dimN = pbrs_index*47;\n")

    def create_pbrs_kernel_end(self, f):
        for i in range(0,51):
            f.write("out[%d+dimN] = workingreg[%d];\n" % (i,i))
        f.write("}\n\n")

    def create_pbrs(self, f):
        j = 0
        pbrs = 0x0152
        i = 0
        pbrsarray = []
        for i in range(0,188*8):
            shiftout = 0
            for j in range(0,8):
                shiftout=shiftout<<1
                if (pbrs&0x8000)^((pbrs<<1)&0x8000) :
                    pbrs|=1
                    shiftout|=1
                pbrs<<=1
            pbrsarray.append(shiftout)

        f.write("/* this function takes a uint ( 4-bytes) and xors it with the output of the pbrs */\n")
        f.write("/* the first byte of one packet is a sync byte ( 0xb8 or 0x47 ) and is not xor'd */\n")
        f.write("/* the pbrs is reinitialized on every 8th packet (after 1504 bytes) */\n")

        f.write("switch(pbrs_index%8)\n{\n")
        for j in range(0,8):
            f.write("\tcase %d:\n" % j)
            if j > 0:
                pbrsarray.pop(0)
            f.write("\t\tworkingreg[0] = in[dimN+0] ^ 0x%02X%02X%02X%02X;\n" % (pbrsarray.pop(2),pbrsarray.pop(1),pbrsarray.pop(0),0))
            if j == 0:
                f.write("\t\tworkingreg[0] = ((workingreg[0]&0xffffff00)|0x000000b8);\n")
            else:
                f.write("\t\tworkingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);\n")

            for i in range(0,46):
                f.write("\t\tworkingreg[%d] = in[dimN+%d] ^ 0x%02X%02X%02X%02X;\n" % ((i+1),(i+1),pbrsarray.pop(3),pbrsarray.pop(2),pbrsarray.pop(1),pbrsarray.pop(0)))

            f.write("\t\tbreak;\n")

        f.write("}\n\n")
        f.write("\n")

    def test_execution_time(self):
        print "test_execution_time:"

        buffersize_in = 188*8
        buffersize_out = 188*8
        kernel_parallel_task = 8
        kernel_workgroupsize = 8
        # generate random bytes
        data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        for k in self.kernelname:
            kernel = self.load_kernel(self.filename, k)
            #print kernel.get_work_group_info(cl.kernel_work_group_info.COMPILE_WORK_GROUP_SIZE, self.cd)
            print "Max WORKGROUPSIZE is %d " % int(kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, self.cd))
            print "requested %d" % kernel_workgroupsize

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

    def load_kernel(self, filename, kernelname):
        print "Kernel \"%s\" from file \"%s\" :" % (kernelname,filename)
        mf = cl.mem_flags
        #read in the OpenCL source file as a string
        self.f = open(filename, 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(self.ctx, fstr)
        self.program.build()
        self.f.close()
        #create the opencl kernel
        return cl.Kernel(self.program,kernelname)

    def test_algorithm(self):
        print "\n**************************"
        print "test_pbrs:"
        passed = 0
        buffersize_in = 188*8
        buffersize_out = 188*8
        # opencl buffer uint
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=buffersize_in*4)
        # opencl buffer uint
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=buffersize_out*4)

        for k in self.kernelname:
            kernel = self.load_kernel(self.filename, k)
            passed = 0
            self.fd_input = open('test_bench_pbrs_input.csv', 'r')
            self.fd_output = open('test_bench_pbrs_output.csv', 'r')
            for j in range(0,6):
                encoded_data = numpy.array(numpy.zeros(buffersize_out/4), dtype=numpy.uint32)
                data_to_encode = string.replace(self.fd_input.readline(),'\n','')
                reference_data = string.replace(self.fd_output.readline(),'\n','')
                for i in range(0,7):
                    data_to_encode = "%s,%s" % (data_to_encode, string.replace(self.fd_input.readline(),'\n',''))
                    reference_data = "%s,%s" % (reference_data, string.replace(self.fd_output.readline(),'\n',''))

                data_to_encode = numpy.fromstring(numpy.fromstring(data_to_encode, dtype=numpy.uint8, sep=",").tostring(), dtype=numpy.uint32)
                reference_data = numpy.fromstring(reference_data, dtype=numpy.uint8, sep=",")

                cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
                kernel.set_args(self.inputbuffer, self.outputbuffer)
                cl.enqueue_nd_range_kernel(self.queue,kernel,(8,),(8,),None ).wait()
                cl.enqueue_copy(self.queue, encoded_data, self.outputbuffer).wait()
                encoded_data = (numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8))

                
                if encoded_data.tostring() == reference_data.tostring():
                    passed += 1
                    print "Test %d PASSED" % (j+1)
                else:
                    print "Test %d FAILED" % (j+1)
                    print "input data:"
                    print numpy.fromstring(data_to_encode.tostring(), dtype=numpy.uint8)
                    print "encoded data:"
                    print numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8)
                    print "reference data:"
                    print reference_data
                    print "error data:"
                    print (reference_data - numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8))
            print "%d pass out of 6" % passed
            self.fd_input.close()
            self.fd_output.close()
            if passed == 6:
                print "All pbrs tests PASS\n"
                return True
            else:
                print "at least one pbrs test FAILED\n"
                return False

if __name__ == '__main__':
    alltestpass = True
    create_files = file_creator()
    create_files.test_execution_time()
    alltestpass &= create_files.test_algorithm()
    print "All tests passed: %s" % alltestpass

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

class test_bench():
    def __init__(self,computedevice, duration):
	# create a opencl context
        try:
           for any_platform in cl.get_platforms():
              for found_device in any_platform.get_devices():
                 if found_device.name == computedevice:
		    self.ctx = cl.Context(devices=[found_device])
                    break
        except ValueError:
           self.ctx = cl.create_some_context()
           print "error: couldn't find device %s, using default" % computedevice

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)

        # generate 10M random uints
        data_to_encode = numpy.fromstring(numpy.random.bytes(40000000), dtype=numpy.uint32)

        # opencl buffer holding 10M random uints
        self.randominputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=40000000)

        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.WRITE_ONLY, size=40000000)

        # copy data to the compute unit
        cl.enqueue_copy(self.queue, self.randominputbuffer, data_to_encode)

        # create a delayed thread
        self.thread_stop_benchmark = threading.Timer(duration,self.test_stop)
        print "Benchmark will run for %d seconds..." % duration

        # create a event
        self.thread_event = threading.Event()

    def test_run(self, filename, kernelname):
        print "Kernel \"%s\" from file \"%s\" :" % (kernelname,filename)
        kernel = tb.load_kernel(filename, kernelname)
        self.thread_stop_benchmark.start()
        t = time.time()
        testcycles = 0
        while self.thread_event.is_set() == False:
            kernel.set_args(self.randominputbuffer, self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,kernel,(8,),None ).wait()
            testcycles += 1

        print "Test duration: %.9f sec" % (time.time() - t)
        print "testcycles: %d" % testcycles
        print "testcycles/sec: %f" % (testcycles / (time.time() - t))

    def test_stop(self):
        self.thread_event.set()


    def load_kernel(self, filename, kernelname):
        mf = cl.mem_flags
        #read in the OpenCL source file as a string
        self.f = open(filename, 'r')
        fstr = "".join(self.f.readlines())
        self.program = cl.Program(self.ctx, fstr).build()
        self.f.close()
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
            tb = test_bench(found_device.name, 5)
            tb.test_run("outer_coding.cl","run")
            print ""


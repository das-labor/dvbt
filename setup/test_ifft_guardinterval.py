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
from pyfft.cl import Plan

class file_creator():
    def __init__(self):
        # create a opencl context
        try:
            self.ctx = cl.create_some_context()
        except ValueError:
            print "error %s\nExiting." % (ValueError)

        # create a opencl command queue
        self.queue = cl.CommandQueue(self.ctx)
        #self.cd = computedevice
        # create a event
        self.thread_event = threading.Event()
        self.duration = 15

    def python_ifft_guardinterval_func(self, ofdmmode, guardinterval, inputdata):
        # create a fft plan
        self.fftplan = Plan(ofdmmode,dtype=numpy.complex64,normalize=True, fast_math=True,context=self.ctx, queue=self.queue)

        # opencl buffer holding data for the ifft - including pilots # 8k or 2k size ???
        fftbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdmmode*8)

        #size of guiardinterval destination buffer
        self.dest_buf_size = ofdmmode*(1+guardinterval)

        # opencl buffer holding the computed data
        dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(self.dest_buf_size*8) )

        self.ret_buf = numpy.array(numpy.zeros(self.dest_buf_size), dtype=numpy.complex64)

        cl.enqueue_copy(self.queue, fftbuffer, inputdata).wait()
        self.fftplan.execute(fftbuffer, data_out=None, inverse=True, batch=1, wait_for_finish=True)

        cl.enqueue_copy(self.queue, dest_buf, fftbuffer, byte_count=int(8*ofdmmode), src_offset=0, dest_offset=int(ofdmmode*guardinterval)).wait()
        cl.enqueue_copy(self.queue, dest_buf, fftbuffer, byte_count=int(ofdmmode*guardinterval), src_offset=int(ofdmmode - ofdmmode*guardinterval) ,dest_offset=0).wait()
        cl.enqueue_copy(self.queue, self.ret_buf, dest_buf).wait()

        return self.ret_buf


    def test_execution_time(self):
        print "test_execution_time:"
        print "TODO"

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

    def test_algorithmA(self, ofdm_mode, guardinterval):
        print "\n**************************"
        print "test ofdm numpy ifft with fftshift"
        passed = 0
        linecnt = 1
        g = 0
        size = 0
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_8K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_8K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval
                
        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_2K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_2K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval

             
        if g == 0:
            print "wrong guardinterval specified"
            return

        if size == 0:
            print "wrong ofdm_mode"
            return
        

        for line in self.fd_input:
            data_to_encode = [float(0) + 1j*float(0)] * ofdm_mode
            counter = (ofdm_mode-size-1)/2+1
            #counter = 0
            for tmp in line.split(","):
                if string.find(tmp, " + ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))
                counter += 1
            data_to_encode = numpy.array(data_to_encode, dtype=numpy.complex128)

            reference_data = []
            for tmp in self.fd_output.readline().split(","):
                if string.find(tmp, " + ") > -1:
                    reference_data.append(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    reference_data.append(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))

            reference_data = numpy.array(reference_data, dtype=numpy.complex128)


            encoded_data = numpy.fft.ifft(numpy.fft.fftshift(data_to_encode))

            # add guard interval
            tmp = []
            for i in range(0,int(ofdm_mode*g)):
                tmp.append(encoded_data[(ofdm_mode*(1-g))+i])
            for i in range(0,ofdm_mode):
                tmp.append(encoded_data[i])
            encoded_data = tmp

            if numpy.allclose(reference_data, encoded_data, rtol=1.0000000000000001e-04, atol=1e-06):
                passed += 1
                print "Test %d PASSED" % linecnt
            else:
                print "Test %d FAILED" % linecnt
                print "input data:"
                print data_to_encode
                print "encoded data[0]:"
                print encoded_data[0]
                print "reference data[0]:"
                print reference_data[0]
                print "error data:"
                print reference_data - encoded_data
            linecnt += 1
        print "%d pass out of %d" % (passed, linecnt-1)
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All ofdm ifft tests PASS\n"
            return True
        else:
            print "at least one ofdm ifft test FAILED\n"
            return False

    def test_algorithmB(self, ofdm_mode, guardinterval):
        print "\n**************************"
        print "test ofdm numpy ifft w/o fftshift"
        passed = 0
        linecnt = 1
        g = 0
        size = 0
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_8K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_8K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval
                
        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_2K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_2K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval

        if g == 0:
            print "wrong guardinterval specified"
            return
        
        if size == 0:
            print "wrong ofdm_mode"
            return
        
        for line in self.fd_input:
            data_to_encode = [float(0) + 1j*float(0)] * ofdm_mode
            #counter = (2048-size-1)/2+1
            counter = 0
            for tmp in line.split(","):
                if string.find(tmp, " + ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))
                counter += 1
            data_to_encode = numpy.array(data_to_encode, dtype=numpy.complex128)

            reference_data = []
            for tmp in self.fd_output.readline().split(","):
                if string.find(tmp, " + ") > -1:
                    reference_data.append(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    reference_data.append(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))

            reference_data = numpy.array(reference_data, dtype=numpy.complex128)

            # do fftshift
            tmp = [float(0) + 1j*float(0)] * ofdm_mode
            for i in range(0,size):
                tmp[(ofdm_mode-size+1)/2+i] = data_to_encode[i]
            for i in range(0,ofdm_mode/2):
                data_to_encode[i] = tmp[ofdm_mode/2+i]
                data_to_encode[i+ofdm_mode/2] = tmp[i]


            encoded_data = numpy.fft.ifft(data_to_encode)

            # add guard interval
            tmp = []
            for i in range(0,int(ofdm_mode*g)):
                tmp.append(encoded_data[(ofdm_mode*(1-g))+i])
            for i in range(0,ofdm_mode):
                tmp.append(encoded_data[i])
            encoded_data = tmp

            if numpy.allclose(reference_data, encoded_data, rtol=1.0000000000000001e-04, atol=1e-06):
                passed += 1
                print "Test %d PASSED" % linecnt
            else:
                print "Test %d FAILED" % linecnt
                print "input data:"
                #print data_to_encode
                print "encoded data[0]:"
                print encoded_data[0]
                print "reference data[0]:"
                print reference_data[0]
                print "error data:"
                #print reference_data - encoded_data
            linecnt += 1
        print "%d pass out of %d" % (passed, linecnt-1)
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All ofdm ifft tests PASS\n"
            return True
        else:
            print "at least one ofdm ifft test FAILED\n"
            return False

    def test_algorithmC(self, ofdm_mode, guardinterval):
        print "\n**************************"
        print "test ofdm opencl ifft w/o fftshift"
        passed = 0
        linecnt = 1
        g = 0
        size = 0
        # create a fft plan
        self.fftplan = Plan(ofdm_mode,dtype=numpy.complex128,normalize=True, fast_math=True,context=self.ctx, queue=self.queue)
        # opencl buffer holding data for the ifft - including pilots # 8k or 2k size ???
        fftbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdm_mode*16)

        #size of guiardinterval destination buffer
        dest_buf_size = ofdm_mode*(1+guardinterval)

        # opencl buffer holding the computed data
        dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(dest_buf_size*16) )

        encoded_data = numpy.array(numpy.zeros(dest_buf_size), dtype=numpy.complex128)
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_8K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_8K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval
                
        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_2K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_2K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval

        if g == 0:
            print "wrong guardinterval specified"
            return
        
        if size == 0:
            print "wrong ofdm_mode"
            return
        
        for line in self.fd_input:
            data_to_encode = [float(0) + 1j*float(0)] * ofdm_mode
            #counter = (2048-size-1)/2+1
            counter = 0
            for tmp in line.split(","):
                if string.find(tmp, " + ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))
                counter += 1
            data_to_encode = numpy.array(data_to_encode, dtype=numpy.complex128)

            reference_data = []
            for tmp in self.fd_output.readline().split(","):
                if string.find(tmp, " + ") > -1:
                    reference_data.append(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    reference_data.append(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))

            reference_data = numpy.array(reference_data, dtype=numpy.complex128)

            # do fftshift
            tmp = [float(0) + 1j*float(0)] * ofdm_mode
            for i in range(0,size):
                tmp[(ofdm_mode-size+1)/2+i] = data_to_encode[i]
            for i in range(0,ofdm_mode/2):
                data_to_encode[i] = tmp[ofdm_mode/2+i]
                data_to_encode[i+ofdm_mode/2] = tmp[i]



            cl.enqueue_copy(self.queue, fftbuffer, data_to_encode).wait()
            self.fftplan.execute(fftbuffer, data_out=None, inverse=True, batch=1, wait_for_finish=True)

            # add guard interval
            cl.enqueue_copy(self.queue, dest_buf, fftbuffer, byte_count=int(16*ofdm_mode), src_offset=0, dest_offset=int(ofdm_mode*guardinterval*16)).wait()
            cl.enqueue_copy(self.queue, dest_buf, fftbuffer, byte_count=int(ofdm_mode*guardinterval*16), src_offset=int(ofdm_mode - ofdm_mode*guardinterval)*16 ,dest_offset=0).wait()
            cl.enqueue_copy(self.queue, encoded_data, dest_buf).wait()


            if numpy.allclose(reference_data, encoded_data, rtol=1.0000000000000001e-04, atol=1e-06):
                passed += 1
                print "Test %d PASSED" % linecnt
            else:
                print "Test %d FAILED" % linecnt
                print "input data:"
                #print data_to_encode
                print "encoded data[0]:"
                print encoded_data[0]
                print "reference data[0]:"
                print reference_data[0]
                print "error data:"
                #print reference_data - encoded_data
            linecnt += 1
        print "%d pass out of %d" % (passed, linecnt-1)
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All ofdm ifft tests PASS\n"
            return True
        else:
            print "at least one ofdm ifft test FAILED\n"
            return False

    def test_algorithmD(self, ofdm_mode, guardinterval):
        print "\n**************************"
        print "test ofdm opencl ifft w/o fftshift http://ochafik.com/ dft"
        passed = 0
        linecnt = 1
        g = 0
        size = 0
        # create a kernel
        kernel = self.load_kernel("DiscreteFourierTransformProgram.cl", "dft")

        #size of guiardinterval destination buffer
        dest_buf_size = ofdm_mode*(1+guardinterval)

        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdm_mode*16)
        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdm_mode*16)

        # opencl buffer holding the computed data
        dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(dest_buf_size*16) )

        encoded_data = numpy.array(numpy.zeros(dest_buf_size), dtype=numpy.complex128)
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_8K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_8K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval
                
        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_2K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_2K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval

        if g == 0:
            print "wrong guardinterval specified"
            return
        
        if size == 0:
            print "wrong ofdm_mode"
            return
        
        for line in self.fd_input:
            data_to_encode = [float(0) + 1j*float(0)] * ofdm_mode

            counter = 0
            for tmp in line.split(","):
                if string.find(tmp, " + ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))
                counter += 1
            data_to_encode = numpy.array(data_to_encode, dtype=numpy.complex128)

            reference_data = []
            for tmp in self.fd_output.readline().split(","):
                if string.find(tmp, " + ") > -1:
                    reference_data.append(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    reference_data.append(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))

            reference_data = numpy.array(reference_data, dtype=numpy.complex128)

            # do fftshift
            tmp = [float(0) + 1j*float(0)] * ofdm_mode
            for i in range(0,size):
                tmp[(ofdm_mode-size+1)/2+i] = data_to_encode[i]
            for i in range(0,ofdm_mode/2):
                data_to_encode[i] = tmp[ofdm_mode/2+i]
                data_to_encode[i+ofdm_mode/2] = tmp[i]



            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode)

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(ofdm_mode),numpy.int32(-1))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode),),None).wait()
            cl.enqueue_copy(self.queue, dest_buf, self.outputbuffer, byte_count=int(16*ofdm_mode), src_offset=0, dest_offset=int(ofdm_mode*guardinterval*16)).wait()
            cl.enqueue_copy(self.queue, dest_buf, self.outputbuffer, byte_count=int(ofdm_mode*guardinterval*16), src_offset=int(ofdm_mode - ofdm_mode*guardinterval)*16 ,dest_offset=0).wait()
            cl.enqueue_copy(self.queue, encoded_data, dest_buf)

            if numpy.allclose(reference_data, encoded_data, rtol=1.0000000000000001e-04, atol=1e-06):
                passed += 1
                print "Test %d PASSED" % linecnt
            else:
                print "Test %d FAILED" % linecnt
                print "input data:"
                print data_to_encode
                print "encoded data[0]:"
                print encoded_data[0]
                print "reference data[0]:"
                print reference_data[0]
                print "error data:"
                #print reference_data - encoded_data
            linecnt += 1
        print "%d pass out of %d" % (passed, linecnt-1)
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All ofdm ifft tests PASS\n"
            return True
        else:
            print "at least one ofdm ifft test FAILED\n"
            return False

    def test_algorithmE(self, ofdm_mode, guardinterval):
        print "\n**************************"
        print "test ofdm opencl ifft bealto.com radix 2 fft"
        passed = 0
        linecnt = 1
        g = 0
        size = 0
        # create a fft plan
        kernel = self.load_kernel("../FFT.cl", "fftRadix2Kernel")
        swapkernel = self.load_kernel("../FFT.cl", "fftswaprealimag")

        #size of guiardinterval destination buffer
        dest_buf_size = ofdm_mode*(1+guardinterval)

        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdm_mode*8)
        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=ofdm_mode*8)

        # opencl buffer holding the computed data
        dest_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, size=int(dest_buf_size*8) )

        encoded_data = numpy.array(numpy.zeros(dest_buf_size), dtype=numpy.complex64)
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_8K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_8K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_8K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_8K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval
                
        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"
            if guardinterval == 0.25:
                self.fd_input = open('test_bench_ofdm_input_2K_1_4.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_4.csv', 'r')
                print "1/4 guard interval"
                g = guardinterval
            if guardinterval == 0.125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_8.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_8.csv', 'r')
                print "1/8 guard interval"
                g = guardinterval
            if guardinterval == 0.0625:
                self.fd_input = open('test_bench_ofdm_input_2K_1_16.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_16.csv', 'r')
                print "1/16 guard interval"
                g = guardinterval
            if guardinterval == 0.03125:
                self.fd_input = open('test_bench_ofdm_input_2K_1_32.csv', 'r')
                self.fd_output = open('test_bench_ofdm_output_2K_1_32.csv', 'r')
                print "1/32 guard interval"
                g = guardinterval

        if g == 0:
            print "wrong guardinterval specified"
            return
        
        if size == 0:
            print "wrong ofdm_mode"
            return
        
        for line in self.fd_input:
            data_to_encode = numpy.array([float(0) + 1j*float(0)] * ofdm_mode, dtype=numpy.complex64)

            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode)
            cl.enqueue_copy(self.queue, self.outputbuffer, data_to_encode)

            counter = 0
            for tmp in line.split(","):
                if string.find(tmp, " + ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    data_to_encode[counter]=(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))
                counter += 1
            data_to_encode = numpy.array(data_to_encode, dtype=numpy.complex64)

            reference_data = []
            for tmp in self.fd_output.readline().split(","):
                if string.find(tmp, " + ") > -1:
                    reference_data.append(float(tmp.split(" + ")[0]) + 1j * float(string.replace(tmp.split(" + ")[1],"i","")))
                if string.find(tmp, " - ") > -1:
                    reference_data.append(float(tmp.split(" - ")[0]) - 1j * float(string.replace(tmp.split(" - ")[1],"i","")))

            reference_data = numpy.array(reference_data, dtype=numpy.complex64)

            # do fftshift
            tmp = [float(0) + 1j*float(0)] * ofdm_mode
            for i in range(0,size):
                tmp[(ofdm_mode-size+1)/2+i] = data_to_encode[i]
            for i in range(0,ofdm_mode/2):
                data_to_encode[i] = tmp[ofdm_mode/2+i]
                data_to_encode[i+ofdm_mode/2] = tmp[i]


            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode)

            swapkernel.set_args(self.inputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,swapkernel,(int(ofdm_mode),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(1))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(2))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(4))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(8))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(16))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(32))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(64))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(128))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(256))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(512))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(1024))
            cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            if ofdm_mode == 8192:
                kernel.set_args(self.outputbuffer, self.inputbuffer, numpy.int32(2048))
                cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

                kernel.set_args(self.inputbuffer, self.outputbuffer, numpy.int32(4096))
                cl.enqueue_nd_range_kernel(self.queue,kernel,(int(ofdm_mode/2),),None).wait()

            swapkernel.set_args(self.outputbuffer)
            cl.enqueue_nd_range_kernel(self.queue,swapkernel,(int(ofdm_mode),),None).wait()

            cl.enqueue_copy(self.queue, dest_buf, self.outputbuffer, byte_count=int(8*ofdm_mode), src_offset=0, dest_offset=int(ofdm_mode*guardinterval*8)).wait()
            cl.enqueue_copy(self.queue, dest_buf, self.outputbuffer, byte_count=int(ofdm_mode*guardinterval*8), src_offset=int(ofdm_mode - ofdm_mode*guardinterval)*8 ,dest_offset=0).wait()
            cl.enqueue_copy(self.queue, encoded_data, dest_buf)


            if numpy.allclose(reference_data, encoded_data, rtol=1.0000000000000001e-04, atol=1e-06):
                passed += 1
                print "Test %d PASSED" % linecnt
            else:
                print "Test %d FAILED" % linecnt
                print "input data:"
                print data_to_encode
                print "encoded data[0]:"
                print encoded_data[0]
                print "reference data[0]:"
                print reference_data[0]
                print "error data:"
                #print reference_data - encoded_data

            linecnt += 1
        print "%d pass out of %d" % (passed, linecnt-1)
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All ofdm ifft tests PASS\n"
            return True
        else:
            print "at least one ofdm ifft test FAILED\n"
            return False

if __name__ == '__main__':
    create_files = file_creator()
    create_files.test_execution_time()
    alltestpass = True
    for mode in [2048, 8192]:
        for guardinterval in [0.25,0.125,0.0625,0.03125]:
            alltestpass &= create_files.test_algorithmA(mode,guardinterval)
            alltestpass &= create_files.test_algorithmB(mode,guardinterval)
            alltestpass &= create_files.test_algorithmC(mode,guardinterval)
            alltestpass &= create_files.test_algorithmD(mode,guardinterval)
            alltestpass &= create_files.test_algorithmE(mode,guardinterval)

    print "All tests passed: %s" % alltestpass
    
    

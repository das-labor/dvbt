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

        f = open('ic_kernel.cl', 'w')
        f.write(copyright)

        #self.create_inner_coder_kernel_start(f,"A")
        self.create_inner_coder_A(f)
        #self.create_inner_coder_kernel_end(f)
        f.close()

        for any_platform in cl.get_platforms():
            print any_platform.name
            for found_device in any_platform.get_devices():
                computedevice = found_device
                if found_device.type == 4 :
                    print "GPU: %s" % found_device.name
                    break
                elif found_device.type == 2 :
                    print "CPU: %s" % found_device.name
                    break
            break

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
        self.filename = "ic_kernel.cl"
        self.kernelname.append("run_ic_A")
        #self.kernelname.append("run_ic_B")
        #self.kernelname.append("run_ic_C")
        #self.kernelname.append("run_ic_AB")

        return



    def create_inner_coder(self, f):
        coderatearray = ["1_2","3_4"]
        modulation = ["qpsk","16qam","64qam"]
        for cr in coderatearray:
            if cr == "1_2":
                crbitsx = [0]
                crbitsy = [0]
                outbits = 1
            elif cr == "2_3":
                crbitsx = [0]
                crbitsy = [0,1]
                outbits = 2
            elif cr == "3_4":
                crbitsx = [0,2]
                crbitsy = [0,1]
                outbits = 3
            elif cr == "5_6":
                crbitsx = [0,2,4]
                crbitsy = [0,1,3]
                outbits = 5
            elif cr == "7_8":
                crbitsx = [0,2,4,6]
                crbitsy = [0,1,3,5]
                outbits = 7

            #coderate outbits -1 = inbits
            #eat multiple of inbits from datastream
            #one workitem per bit
            #get_global_id(0) / outbits * inbits, to get correct input bit
            #calculate x/y depending on crbits 
            for i in range(0,len(modulation)):
                md = modulation[i]
                mdbits = (i+1)*2
                infotext = " inner coder: folding code: %s, bitwise interleaving, %s signal mapping\n" % (cr, md)
                infotext += " use %d interleavers (%s mode)\n" % (mdbits,md) 
                infotext += " execute with 63 work group size.\n"
                infotext += " each workgroup processes %d*126 bit\n" % (i+1)
                infotext += " workgroup input 126 bit, output 126 float2\n"
                infotext += " execute TODO workgroups at once: TODO uints in, 16*126 = 2016 float2 out\n"
                f.write("/*\n %s */\n" % infotext)

                #f.write("#define WORKGROUPSIZE 63\n")
                f.write("__kernel void run_%s_%s( __global uint *in, __global float2 *out)\n" % (cr,md))
                f.write("{\n")
                #f.write("\t__local uint interleaved_bits[%d][126];\n" % mdbits)
                f.write("\tuint workingreg[2];\n")
                f.write("\tuint resultreg[%d];\n\n" % mdbits)
                #f.write("\tfloat2 tmp;\n")
                f.write("\tint i = get_global_id(0);\n")
                f.write("\tint j = i*%d;\n\n" % ((i+1)*2))
                for j in range(0,mdbits):
                    f.write("\tresultreg[%d] = 0;\n" % j)
                f.write("\tworkingreg[0] = 0;\n")
                f.write("\tworkingreg[1] = 0;\n\n")
                f.write("\t/* load bit from global memory */\n")
                f.write("\tworkingreg[0] =in[(int)(j>>5)];\n")
                f.write("\tworkingreg[1] =in[(int)(j>>5) +1];\n")
                f.write("\tworkingreg[0] <<= (j&0x001f);\n")
                f.write("\tworkingreg[0] |= workingreg[1]>>(32-(j&0x001f));\n\n")

                f.write("\n\t/* inner coder & inner interleaver*/\n")
                t = 0
                for xx in range(0,2):
                    j = 0
                    while j < 2:
                        if crbitsx.count(t) > 0:
                            f.write("\t\t/* generate X */\n")
                            f.write("\t\tresultreg[%d] = (workingreg[0] * 0x9E) & 0x80000000;\n" % j)
                            f.write("\t\tresultreg[%d] >>= 31;\n" % j)
                            j += 1
                        if crbitsy.count(t) > 0:
                            f.write("\t\t/* generate Y */\n")
                            f.write("\t\tresultreg[%d] = (workingreg[0] * 0xDA) & 0x80000000;\n" % j)
                            f.write("\t\tresultreg[%d] >>= 31;\n\n" % j)
                            j += 1
                        f.write("\t\tworkingreg[0] <<= 1;\n\n")
                        t += 1
                        t %= outbits
                    f.write("\t\t/* interleaver 0, y = x + 0 mod 126 */\n")
                    f.write("\t\tinterleaved_bits[0][j+%d] = resultreg[0];\n\n" % xx)
                    f.write("\t\t/* interleaver 1, y = x + 63 mod 126 */\n")
                    f.write("\t\tinterleaved_bits[1][((j+63+%d) %% 126)] = resultreg[1];\n\n" % xx)
                    
                    if i > 0:
                        j = 0
                        while j < 2:
                            if crbitsx.count(t) > 0:
                                f.write("\t\t/* generate X */\n")
                                f.write("\t\tresultreg[%d] = (workingreg[0] * 0x9E) & 0x80000000;\n" % j)
                                f.write("\t\tresultreg[%d] >>= 31;\n" % j)
                                j += 1
                            if crbitsy.count(t) > 0:
                                f.write("\t\t/* generate Y */\n")
                                f.write("\t\tresultreg[%d] = (workingreg[0] * 0xDA) & 0x80000000;\n" % j)
                                f.write("\t\tresultreg[%d] >>= 31;\n\n" % j)
                                j += 1
                            f.write("\t\tworkingreg[0] <<= 1;\n\n")
                            t += 1
                            t %= outbits
                        f.write("\t\t/* interleaver 2, y = x + 105 mod 126 */\n")
                        f.write("\t\tinterleaved_bits[2][((j+105+%d) %% 126)] = resultreg[2];\n\n" % xx)
                        f.write("\t\t/* interleaver 3, y = x + 42 mod 126 */\n")
                        f.write("\t\tinterleaved_bits[3][((j+42+%d) %% 126)] = resultreg[3];\n\n" % xx)
                        
                    if i > 1:
                        j = 0
                        while j < 2:
                            if crbitsx.count(t) > 0:
                                f.write("\t\t/* generate X */\n")
                                f.write("\t\tresultreg[%d] = (workingreg[0] * 0x9E) & 0x80000000;\n" % j)
                                f.write("\t\tresultreg[%d] >>= 31;\n" % j)
                                j += 1
                            if crbitsy.count(t) > 0:
                                f.write("\t\t/* generate Y */\n")
                                f.write("\t\tresultreg[%d] = (workingreg[0] * 0xDA) & 0x80000000;\n" % j)
                                f.write("\t\tresultreg[%d] >>= 31;\n\n" % j)
                                j += 1
                            f.write("\t\tworkingreg[0] <<= 1;\n\n")
                            t += 1
                            t %= outbits
                        f.write("\t\t/* interleaver 4, y = x + 21 mod 126 */\n")
                        f.write("\t\tinterleaved_bits[4][((j+21+%d) %% 126)] = resultreg[4];\n\n" % xx )
                        f.write("\t\t/* interleaver 5, y = x + 84 mod 126 */\n")
                        f.write("\t\tinterleaved_bits[5][((j+84+%d) %% 126)] = resultreg[5];\n\n" % xx)


                f.write("\t/* interleaving has be done by inserting at the correct position */\n")
                return
                f.write("\n\t/* signal constellation mapping */\n")
                f.write("\tbarrier(CLK_LOCAL_MEM_FENCE);\n")
                f.write("\tj = get_local_id(0) *2;\n")
                if i == 0:
                    f.write("\ttmp.x = 1.0f - 2.0f * interleaved_bits[0][get_local_id(0)*2];\n")
                    f.write("\ttmp.y = 1.0f - 2.0f * interleaved_bits[1][get_local_id(0)*2];\n")
                    f.write("\tout[i] = tmp;\n")
                    f.write("\ttmp.x = 1.0f - 2.0f * interleaved_bits[0][get_local_id(0)*2+1];\n")
                    f.write("\ttmp.y = 1.0f - 2.0f * interleaved_bits[1][get_local_id(0)*2+1];\n")
                    f.write("\tout[i+1] = tmp;\n")
                elif i == 1:
                    f.write("\ttmp.x = 3.0f - interleaved_bits[2][j] * 2.0f;\n")
                    f.write("\ttmp.y = 3.0f - interleaved_bits[3][j] * 2.0f;\n")
                    f.write("\ttmp.x *= 1.0f- interleaved_bits[0][j] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[1][j] * 2.0f;\n")
                    f.write("\tout[i] = tmp;\n")
                    f.write("\ttmp.x = 3.0f - interleaved_bits[2][j+1] * 2.0f;\n")
                    f.write("\ttmp.y = 3.0f - interleaved_bits[3][j+1] * 2.0f;\n")
                    f.write("\ttmp.x *= 1.0f- interleaved_bits[0][j+1] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[1][j+1] * 2.0f;\n")
                    f.write("\tout[i+1] = tmp;\n")
                elif i == 2:
                    f.write("\ttmp.x = 3.0f - interleaved_bits[4][j] * 2.0f;\n")
                    f.write("\ttmp.y = 3.0f - interleaved_bits[5][j] * 2.0f;\n")
                    f.write("\ttmp.x *= 1.0f - interleaved_bits[2][j] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[3][j] * 2.0f;\n")
                    f.write("\ttmp.x += 4.0f;\n")
                    f.write("\ttmp.y += 4.0f;\n")
                    f.write("\ttmp.x *= 1.0f - interleaved_bits[0][j] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[1][j] * 2.0f;\n")
                    f.write("\tout[i] = tmp;\n")
                    f.write("\ttmp.x = 3.0f - interleaved_bits[4][j+1] * 2.0f;\n")
                    f.write("\ttmp.y = 3.0f - interleaved_bits[5][j+1] * 2.0f;\n")
                    f.write("\ttmp.x *= 1.0f - interleaved_bits[2][j+1] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[3][j+1] * 2.0f;\n")
                    f.write("\ttmp.x += 4.0f;\n")
                    f.write("\ttmp.y += 4.0f;\n")
                    f.write("\ttmp.x *= 1.0f - interleaved_bits[0][j+1] * 2.0f;\n")
                    f.write("\ttmp.y *= 1.0f - interleaved_bits[1][j+1] * 2.0f;\n")
                    f.write("\tout[i+1] = tmp;\n")
                f.write("}\n\n")


    def create_inner_coder_A(self, f):
        
            #coderate outbits -1 = inbits
            #eat multiple of inbits from datastream
            #one workitem per bit
            #get_global_id(0) / outbits * inbits, to get correct input bit
            #calculate x/y depending on crbits 
                infotext = " inner coder: folding code:, bitwise interleaving,  signal mapping\n"
                infotext += " coderate 1/2 \n"
                f.write("/*\n %s */\n" % infotext)
                f.write("__kernel void run_ic_A( __global uint *in, __global uint *out, __const uint cr)\n")
                f.write("{\n")
                f.write("\tulong workingreg;\n")
                f.write("\tuint resultreg;\n\n")
                f.write("\tint i = get_global_id(0);\n")
                f.write("\t/* start offset is 26th bit */\n")
                f.write("\tlong j = i/cr + 0;\n\n")
                f.write("\t/* load bit from global memory */\n")
                f.write("\tworkingreg =((ulong)in[(j>>5)])<<32|((ulong)in[(j>>5) +1]);\n")
                f.write("\tworkingreg <<= (j&31);\n\n")
                f.write("\tresultreg = 0;\n")

                f.write("\tif(!(i&0x00000001))\n")
                f.write("\t{\n")
                f.write("\t\tif(workingreg & 0x2000000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0400000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0200000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0100000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0080000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\t}\n")
                f.write("\t\telse\n")
                f.write("\t\t{\n")
                f.write("\t\tif(workingreg & 0x2000000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x1000000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0400000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0200000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t\tif(workingreg & 0x0080000000UL)\n")
                f.write("\t\tresultreg++;\n")
                f.write("\t}\n\n")
                f.write("\tout[i] = resultreg&0x01;\n")
                f.write("}\n")

    def test_execution_time(self):
        print "test_execution_time:"

        ofdm_useful_carriers = 1512
        frames_per_superframe = 4
        ofdm_symbols_per_frame = 68
        coderate = 0.5
        bits_per_carrier = 2
        buffersize_in = int( ofdm_useful_carriers * frames_per_superframe * ofdm_symbols_per_frame * coderate * bits_per_carrier / 32 * 4 + 4 )#uints
        buffersize_out = int(ofdm_useful_carriers * frames_per_superframe * ofdm_symbols_per_frame * coderate * bits_per_carrier * 4 )#uints
        # opencl buffer
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=buffersize_in)
        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.WRITE_ONLY, size=buffersize_out)

        #kernel_parallel_task = 8
        #kernel_workgroupsize = 8
        # generate random bytes
        data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        for k in self.kernelname:
            kernel = self.load_kernel(self.filename, k)
            encoded_data = numpy.array(numpy.zeros(buffersize_in), dtype=numpy.uint32)
            cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
                            
            self.thread_event.clear()

            # create a delayed thread
            threading.Timer(self.duration,self.test_stop).start()

            t = time.time()
            testcycles = 0
            while self.thread_event.is_set() == False:
                kernel.set_args(self.inputbuffer, self.outputbuffer,numpy.uint32(2))
                
                cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),(1,)).wait()
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
        print "test_inner coder:"
        passed = 0
        linecnt = 1
        ofdm_useful_carriers = 1512
        frames_per_superframe = 4
        ofdm_symbols_per_frame = 68
        coderate = 0.5
        bits_per_carrier = 2 #qpsk
        buffersize_in = int(ofdm_useful_carriers * frames_per_superframe * ofdm_symbols_per_frame * coderate * bits_per_carrier / 8) #input 32bits per uint (4 byte)
        buffersize_out = int(ofdm_useful_carriers * frames_per_superframe * ofdm_symbols_per_frame * coderate * bits_per_carrier * 2 * 4) #output one bit per uint, coderate 0.5 only

        # opencl buffer
        self.transferbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=buffersize_in)
        # opencl buffer
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_ONLY, size=buffersize_in+4)
        # opencl buffer
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.WRITE_ONLY, size=buffersize_out)

        zero_data = numpy.array(numpy.zeros(buffersize_in/4+1), dtype=numpy.uint32)
        cl.enqueue_copy(self.queue, self.inputbuffer, zero_data).wait()

        #kernel_parallel_task = 8
        #kernel_workgroupsize = 8
        # generate random bytes
        #data_to_encode = numpy.fromstring(numpy.random.bytes(buffersize_in), dtype=numpy.uint32)
        for k in self.kernelname:
            kernel = self.load_kernel(self.filename, k)

            if coderate == 0.5: 
                self.fd_input = open('test_bench_conv_12_input.csv', 'r')
                self.fd_output = open('test_bench_conv_12_output.csv', 'r')
            else:
                print "coderate not supported"
                return
            for line in self.fd_input:
                raw_data_to_encode = numpy.fromstring(line, dtype=numpy.uint8, sep=",")
                data_to_encode = numpy.packbits(raw_data_to_encode)

                tmp = numpy.array(numpy.zeros(len(data_to_encode)/4), dtype=numpy.uint32) #uint32, divide by 4
                for i in range(0,len(data_to_encode)/4):
                    tmp[i] = (data_to_encode[i*4+0]<<24|data_to_encode[i*4+1]<<16|data_to_encode[i*4+2]<<8|data_to_encode[i*4+3]<<0)
                data_to_encode = tmp

                encoded_data = numpy.array(numpy.zeros(buffersize_out/4), dtype=numpy.uint32) #uint32, divide by 4
                reference_data = numpy.fromstring(self.fd_output.readline(), dtype=numpy.uint8, sep=",")

                cl.enqueue_copy(self.queue, self.transferbuffer, data_to_encode).wait() #store in transferbuffer
                cl.enqueue_copy(self.queue, self.inputbuffer, self.transferbuffer, byte_count=buffersize_in,dest_offset=4).wait()

                kernel.set_args(self.inputbuffer, self.outputbuffer,numpy.uint32(2))
                cl.enqueue_nd_range_kernel(self.queue,kernel,(buffersize_out/4,),None ).wait()
                cl.enqueue_copy(self.queue, encoded_data, self.outputbuffer).wait()

                
                if numpy.array_equal(encoded_data, reference_data):
                    passed += 1
                    print "Test %d PASSED" % linecnt
                else:
                    print "Test %d FAILED" % linecnt
                    failed = 0

                    print len(reference_data)
                    print len(encoded_data)
 
                    failed = 0
                    for i in range(0,len(reference_data)-1):
                        if reference_data[i] !=  encoded_data[i]:
                            if failed < 20:
                                print "FAIL: %d (%d): %d %d" % (i,i%32,reference_data[i] , encoded_data[i])
                            failed += 1
                    print "total %d out of %d" % (failed,buffersize_out/4)


                linecnt += 1
            print "%d pass out of %d" % (passed,linecnt-1)
            self.fd_input.close()
            self.fd_output.close()
            #self.fd_outputy.close()
            if passed == (linecnt-1):
                print "All inner coder tests PASS\n"
                return True
            else:
                print "at least one inner coder test FAILED\n"
                return False

if __name__ == '__main__':
    alltestpass = True
    create_files = file_creator()
    #create_files.test_execution_time()
    alltestpass &= create_files.test_algorithm()
    print "All tests passed: %s" % alltestpass


if __name__ == '__main__':
    create_files = file_creator()



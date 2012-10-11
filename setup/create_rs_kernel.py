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

class file_creator():
    def __init__(self):
        f = open('copyright', 'r')
        copyright = f.read()
        f.close()
        f = open('rs_kernel.cl', 'w')
        f.write(copyright)
        self.create_rs_helper_func(f)
        self.create_rs_kernel_start(f,"A")
        self.create_rs_encoderA(f)
        self.create_rs_kernel_end(f)
        self.create_rs_kernel_start(f,"B")
        self.create_rs_encoderB(f)
        self.create_rs_kernel_end(f)
        self.create_rs_kernel_start(f,"C")
        self.create_rs_encoderC(f)
        self.create_rs_kernel_end(f)
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
        self.filename = "rs_kernel.cl"
        self.kernelname.append("test_rsencode_A")
        self.kernelname.append("test_rsencode_B")
        self.kernelname.append("test_rsencode_C")

    # input: file descriptor
    # rs -generator polynomial
    #
    # 1x16+	59x15+	13x14+	104x13+	189x12+	68x11+	209x10+	30x9+	8x8+	163x7+	65x6+	41x5+	229x4+	98x3+	50x2+	36x1+	59x0
    # in hex:
    # 3B 0D 68 BD 44 D1 1E 08 A3 41 29 E5 62 32 24 3B
    # non optimized version
    # gf init poly = x^8 + x^4 +x^3+x^2 + 1
    def create_rs_encoderA(self, f):

        f.write("uint wreg[17];\n")
        f.write("const uchar gen_poly[16]={0x3B, 0x0D, 0x68, 0xBD, 0x44, 0xD1, 0x1E, 0x08, 0xA3, 0x41, 0x29, 0xE5, 0x62, 0x32, 0x24, 0x3B};\n")

        f.write("int i,j;\n")
        f.write("/* load data into wreg */\n")
        f.write("for(i = 0; i < 16; i++)\n")
        f.write("{\n")
        f.write("\twreg[i]= (workingreg[i>>2]>>((i&0x00000003)<<3))&0x000000ff;\n")
        f.write("}\n")
        f.write("for(i = 0; i < 172; i++)\n")
        f.write("{\n")
        f.write("\t/* load new byte into wreg[16] */\n")
        f.write("\twreg[16]=workingreg[(i+16)>>2];\n")
        f.write("\twreg[16]>>=((i+16)&0x00000003)<<3;\n")
        f.write("\twreg[16]&=0x000000ff;\n")
        f.write("\tfor(j = 0; j<16;j++){\n")
        f.write("\twreg[j+1]^=galoisMultiplication_arith(wreg[0],gen_poly[j]);\n")
        f.write("\t}\n")
        f.write("\t/* shift all bytes left */\n")
        f.write("\tfor(j = 0; j<16;j++){\n")
        f.write("\t\twreg[j]=wreg[j+1];\n")
        f.write("\t}\n")
        f.write("}\n\n")
        f.write("for(i = 0; i < 16; i++)\n")
        f.write("{\n")
        f.write("\twreg[16]=0;\n")
        f.write("\tfor(j = 0; j<16;j++){\n")
        f.write("\t\twreg[j+1]^=galoisMultiplication_arith(wreg[0],gen_poly[j]);\n")
        f.write("\t}\n")
        f.write("\tfor(j = 0; j<16;j++){\n")
        f.write("\t\twreg[j]=wreg[j+1];\n")
        f.write("\t}\n")
        f.write("}\n")
        f.write("/* convert back to uint32 */\n") 
        f.write("workingreg[47] = (wreg[3]<<24)|(wreg[2]<<16)|(wreg[1]<<8)|wreg[0];\n") 
        f.write("workingreg[48] = (wreg[7]<<24)|(wreg[6]<<16)|(wreg[5]<<8)|wreg[4];\n") 
        f.write("workingreg[49] = (wreg[11]<<24)|(wreg[10]<<16)|(wreg[9]<<8)|wreg[8];\n") 
        f.write("workingreg[50] = (wreg[15]<<24)|(wreg[14]<<16)|(wreg[13]<<8)|wreg[12];\n\n") 

    def create_rs_encoderB(self, f):
        f.write("uint16 wreg;\n")
        f.write("uint tmp;\n")
        f.write("uint shadow;\n")

        a_init_1 = 0xA34129E56232243B
        a_init_2 = 0x3B0D68BD44D11E08
        cnt = 0
        a1 = a_init_1
        a2 = a_init_2
        poly = 0x1d
        rega1 = a_init_1
        rega2 = a_init_2
        f.write("const uint16 gen_poly[8]={\n")
        for cnt in range(0, 8):

            f.write("(uint16)(%d,%d,%d,%d,%d,%d,%d,%d," % ((a2>>56)&0xff,(a2>>48)&0xff,(a2>>40)&0xff,(a2>>32)&0xff,(a2>>24)&0xff,(a2>>16)&0xff,(a2>>8)&0xff,(a2>>0)&0xff))
            f.write("%d,%d,%d,%d,%d,%d,%d,%d),\n" % ((a1>>56)&0xff,(a1>>48)&0xff,(a1>>40)&0xff,(a1>>32)&0xff,(a1>>24)&0xff,(a1>>16)&0xff,(a1>>8)&0xff,(a1>>0)&0xff))

            rega1 = 0
            if ((a1>>56) & 0x80) > 0:
                rega1 |=(poly<<56);
            if ((a1>>48) & 0x80) > 0:
                rega1 |=(poly<<48);
            if ((a1>>40) & 0x80) > 0:
                rega1 |=(poly<<40);
            if ((a1>>32) & 0x80) > 0:
                rega1 |=(poly<<32);
            if ((a1>>24) & 0x80) > 0:
                rega1 |=(poly<<24);
            if ((a1>>16) & 0x80) > 0:
                rega1 |=(poly<<16);
            if ((a1>>8) & 0x80) > 0:
                rega1 |=(poly<<8);
            if ((a1>>0) & 0x80) > 0:
                rega1 |=(poly<<0);
  
            a1 &= 0x7f7f7f7f7f7f7f7f
            a1 <<= 1
            a1 ^= rega1

            rega2 = 0
            if ((a2>>56) & 0x80) > 0:
                rega2 |=(poly<<56);
            if ((a2>>48) & 0x80) > 0:
                rega2 |=(poly<<48);
            if ((a2>>40) & 0x80) > 0:
                rega2 |=(poly<<40);
            if ((a2>>32) & 0x80) > 0:
                rega2 |=(poly<<32);
            if ((a2>>24) & 0x80) > 0:
                rega2 |=(poly<<24);
            if ((a2>>16) & 0x80) > 0:
                rega2 |=(poly<<16);
            if ((a2>>8) & 0x80) > 0:
                rega2 |=(poly<<8);
            if ((a2>>0) & 0x80) > 0:
                rega2 |=(poly<<0);
  
            a2 &= 0x7f7f7f7f7f7f7f7f
            a2 <<= 1
            a2 ^= rega2
        
        f.write("};\n")
        f.write("int i;\n")
        f.write("/* load data into wreg */\n")

        f.write("shadow = (workingreg[0]>>0)&0x000000ff;\n")
        for i in range(0,16):
            f.write("wreg.s%1x = (workingreg[%d]>>%d)&0x000000ff;\n" % (i, ((i+1)>>2),(((i+1)&3)<<3)))

        f.write("for(i = 0; i < 172; i++)\n")
        f.write("{\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf = workingreg[(i+16)>>2];\n")
        f.write("\twreg.sf >>=((i+16)&0x00000003)<<3;\n")
        f.write("\twreg.sf &=0x000000ff;\n")
        f.write("\n")

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & gen_poly[%d]);\n" % cnt )
            f.write("\tshadow >>=1;\n")

        f.write("\t/* shadow .s0 */\n")
        f.write("\tshadow = wreg.s0;\n")
        f.write("\n")

        f.write("\t/* shift all bytes left */\n")
        for i in range(0, 15):
            f.write("\twreg.s%1x = wreg.s%1x;\n" % (i,i+1) )
        f.write("\n")

        f.write("}\n\n")
        f.write("for(i = 0; i < 15; i++)\n")
        f.write("{\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf=0;\n")
        f.write("\n")

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & gen_poly[%d]);\n" % cnt )
            f.write("\tshadow >>=1;\n")
        f.write("\n")

        f.write("\t/* shadow .s0 */\n")
        f.write("\tshadow = wreg.s0;\n")
        f.write("\n")

        f.write("\t/* shift all bytes left */\n")
        for i in range(0, 15):
            f.write("\twreg.s%1x = wreg.s%1x;\n" % (i,i+1) )
        f.write("\n")

        f.write("}\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf=0;\n")
        f.write("\n")

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & gen_poly[%d]);\n" % cnt )
            f.write("\tshadow >>=1;\n")
        f.write("\n")

        f.write("\t/* dont shift left */\n\n")

        f.write("/* convert back to uint32 */\n") 
        f.write("workingreg[47] = (wreg.s3<<24)|(wreg.s2<<16)|(wreg.s1<<8)|wreg.s0;\n") 
        f.write("workingreg[48] = (wreg.s7<<24)|(wreg.s6<<16)|(wreg.s5<<8)|wreg.s4;\n") 
        f.write("workingreg[49] = (wreg.sb<<24)|(wreg.sa<<16)|(wreg.s9<<8)|wreg.s8;\n") 
        f.write("workingreg[50] = (wreg.sf<<24)|(wreg.se<<16)|(wreg.sd<<8)|wreg.sc;\n\n") 

    def create_rs_encoderC(self, f):
        f.write("uint16 wreg;\n")
        f.write("uint tmp;\n")
        f.write("uint shadow;\n")

        
        f.write("int i;\n")
        f.write("/* load data into wreg */\n")

        f.write("shadow = (workingreg[0]>>0)&0x000000ff;\n")
        for i in range(0,16):
            f.write("wreg.s%1x = (workingreg[%d]>>%d)&0x000000ff;\n" % (i, ((i+1)>>2),(((i+1)&3)<<3)))

        f.write("for(i = 0; i < 172; i++)\n")
        f.write("{\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf = workingreg[(i+16)>>2];\n")
        f.write("\twreg.sf >>=((i+16)&0x00000003)<<3;\n")
        f.write("\twreg.sf &=0x000000ff;\n")
        f.write("\n")

        a_init_1 = 0xA34129E56232243B
        a_init_2 = 0x3B0D68BD44D11E08
        cnt = 0
        a1 = a_init_1
        a2 = a_init_2
        poly = 0x1d
        rega1 = a_init_1
        rega2 = a_init_2

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & ")
            f.write("(uint16)(%d,%d,%d,%d,%d,%d,%d,%d," % ((a2>>56)&0xff,(a2>>48)&0xff,(a2>>40)&0xff,(a2>>32)&0xff,(a2>>24)&0xff,(a2>>16)&0xff,(a2>>8)&0xff,(a2>>0)&0xff))
            f.write("%d,%d,%d,%d,%d,%d,%d,%d));\n" % ((a1>>56)&0xff,(a1>>48)&0xff,(a1>>40)&0xff,(a1>>32)&0xff,(a1>>24)&0xff,(a1>>16)&0xff,(a1>>8)&0xff,(a1>>0)&0xff))
            f.write("\tshadow >>=1;\n")

            rega1 = 0
            if ((a1>>56) & 0x80) > 0:
                rega1 |=(poly<<56);
            if ((a1>>48) & 0x80) > 0:
                rega1 |=(poly<<48);
            if ((a1>>40) & 0x80) > 0:
                rega1 |=(poly<<40);
            if ((a1>>32) & 0x80) > 0:
                rega1 |=(poly<<32);
            if ((a1>>24) & 0x80) > 0:
                rega1 |=(poly<<24);
            if ((a1>>16) & 0x80) > 0:
                rega1 |=(poly<<16);
            if ((a1>>8) & 0x80) > 0:
                rega1 |=(poly<<8);
            if ((a1>>0) & 0x80) > 0:
                rega1 |=(poly<<0);
  
            a1 &= 0x7f7f7f7f7f7f7f7f
            a1 <<= 1
            a1 ^= rega1

            rega2 = 0
            if ((a2>>56) & 0x80) > 0:
                rega2 |=(poly<<56);
            if ((a2>>48) & 0x80) > 0:
                rega2 |=(poly<<48);
            if ((a2>>40) & 0x80) > 0:
                rega2 |=(poly<<40);
            if ((a2>>32) & 0x80) > 0:
                rega2 |=(poly<<32);
            if ((a2>>24) & 0x80) > 0:
                rega2 |=(poly<<24);
            if ((a2>>16) & 0x80) > 0:
                rega2 |=(poly<<16);
            if ((a2>>8) & 0x80) > 0:
                rega2 |=(poly<<8);
            if ((a2>>0) & 0x80) > 0:
                rega2 |=(poly<<0);
  
            a2 &= 0x7f7f7f7f7f7f7f7f
            a2 <<= 1
            a2 ^= rega2



        f.write("\t/* shadow .s0 */\n")
        f.write("\tshadow = wreg.s0;\n")
        f.write("\n")

        f.write("\t/* shift all bytes left */\n")
        for i in range(0, 15):
            f.write("\twreg.s%1x = wreg.s%1x;\n" % (i,i+1) )
        f.write("\n")

        f.write("}\n\n")
        f.write("for(i = 0; i < 15; i++)\n")
        f.write("{\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf=0;\n")
        f.write("\n")

        a_init_1 = 0xA34129E56232243B
        a_init_2 = 0x3B0D68BD44D11E08
        cnt = 0
        a1 = a_init_1
        a2 = a_init_2
        poly = 0x1d
        rega1 = a_init_1
        rega2 = a_init_2

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & ")
            f.write("(uint16)(%d,%d,%d,%d,%d,%d,%d,%d," % ((a2>>56)&0xff,(a2>>48)&0xff,(a2>>40)&0xff,(a2>>32)&0xff,(a2>>24)&0xff,(a2>>16)&0xff,(a2>>8)&0xff,(a2>>0)&0xff))
            f.write("%d,%d,%d,%d,%d,%d,%d,%d));\n" % ((a1>>56)&0xff,(a1>>48)&0xff,(a1>>40)&0xff,(a1>>32)&0xff,(a1>>24)&0xff,(a1>>16)&0xff,(a1>>8)&0xff,(a1>>0)&0xff))
            f.write("\tshadow >>=1;\n")

            rega1 = 0
            if ((a1>>56) & 0x80) > 0:
                rega1 |=(poly<<56);
            if ((a1>>48) & 0x80) > 0:
                rega1 |=(poly<<48);
            if ((a1>>40) & 0x80) > 0:
                rega1 |=(poly<<40);
            if ((a1>>32) & 0x80) > 0:
                rega1 |=(poly<<32);
            if ((a1>>24) & 0x80) > 0:
                rega1 |=(poly<<24);
            if ((a1>>16) & 0x80) > 0:
                rega1 |=(poly<<16);
            if ((a1>>8) & 0x80) > 0:
                rega1 |=(poly<<8);
            if ((a1>>0) & 0x80) > 0:
                rega1 |=(poly<<0);
  
            a1 &= 0x7f7f7f7f7f7f7f7f
            a1 <<= 1
            a1 ^= rega1

            rega2 = 0
            if ((a2>>56) & 0x80) > 0:
                rega2 |=(poly<<56);
            if ((a2>>48) & 0x80) > 0:
                rega2 |=(poly<<48);
            if ((a2>>40) & 0x80) > 0:
                rega2 |=(poly<<40);
            if ((a2>>32) & 0x80) > 0:
                rega2 |=(poly<<32);
            if ((a2>>24) & 0x80) > 0:
                rega2 |=(poly<<24);
            if ((a2>>16) & 0x80) > 0:
                rega2 |=(poly<<16);
            if ((a2>>8) & 0x80) > 0:
                rega2 |=(poly<<8);
            if ((a2>>0) & 0x80) > 0:
                rega2 |=(poly<<0);
  
            a2 &= 0x7f7f7f7f7f7f7f7f
            a2 <<= 1
            a2 ^= rega2

        f.write("\n")

        f.write("\t/* shadow .s0 */\n")
        f.write("\tshadow = wreg.s0;\n")
        f.write("\n")

        f.write("\t/* shift all bytes left */\n")
        for i in range(0, 15):
            f.write("\twreg.s%1x = wreg.s%1x;\n" % (i,i+1) )
        f.write("\n")

        f.write("}\n")

        f.write("\t/* load new byte into wreg.sf */\n")
        f.write("\twreg.sf=0;\n")
        f.write("\n")

        a_init_1 = 0xA34129E56232243B
        a_init_2 = 0x3B0D68BD44D11E08
        cnt = 0
        a1 = a_init_1
        a2 = a_init_2
        poly = 0x1d
        rega1 = a_init_1
        rega2 = a_init_2

        for cnt in range(0, 8):
            f.write("\ttmp= 0x00000000 - (shadow & 0x00000001);\n")
            f.write("\twreg ^= (tmp & ")
            f.write("(uint16)(%d,%d,%d,%d,%d,%d,%d,%d," % ((a2>>56)&0xff,(a2>>48)&0xff,(a2>>40)&0xff,(a2>>32)&0xff,(a2>>24)&0xff,(a2>>16)&0xff,(a2>>8)&0xff,(a2>>0)&0xff))
            f.write("%d,%d,%d,%d,%d,%d,%d,%d));\n" % ((a1>>56)&0xff,(a1>>48)&0xff,(a1>>40)&0xff,(a1>>32)&0xff,(a1>>24)&0xff,(a1>>16)&0xff,(a1>>8)&0xff,(a1>>0)&0xff))
            f.write("\tshadow >>=1;\n")

            rega1 = 0
            if ((a1>>56) & 0x80) > 0:
                rega1 |=(poly<<56);
            if ((a1>>48) & 0x80) > 0:
                rega1 |=(poly<<48);
            if ((a1>>40) & 0x80) > 0:
                rega1 |=(poly<<40);
            if ((a1>>32) & 0x80) > 0:
                rega1 |=(poly<<32);
            if ((a1>>24) & 0x80) > 0:
                rega1 |=(poly<<24);
            if ((a1>>16) & 0x80) > 0:
                rega1 |=(poly<<16);
            if ((a1>>8) & 0x80) > 0:
                rega1 |=(poly<<8);
            if ((a1>>0) & 0x80) > 0:
                rega1 |=(poly<<0);
  
            a1 &= 0x7f7f7f7f7f7f7f7f
            a1 <<= 1
            a1 ^= rega1

            rega2 = 0
            if ((a2>>56) & 0x80) > 0:
                rega2 |=(poly<<56);
            if ((a2>>48) & 0x80) > 0:
                rega2 |=(poly<<48);
            if ((a2>>40) & 0x80) > 0:
                rega2 |=(poly<<40);
            if ((a2>>32) & 0x80) > 0:
                rega2 |=(poly<<32);
            if ((a2>>24) & 0x80) > 0:
                rega2 |=(poly<<24);
            if ((a2>>16) & 0x80) > 0:
                rega2 |=(poly<<16);
            if ((a2>>8) & 0x80) > 0:
                rega2 |=(poly<<8);
            if ((a2>>0) & 0x80) > 0:
                rega2 |=(poly<<0);
  
            a2 &= 0x7f7f7f7f7f7f7f7f
            a2 <<= 1
            a2 ^= rega2

        f.write("\n")

        f.write("\t/* dont shift left */\n\n")

        f.write("/* convert back to uint32 */\n") 
        f.write("workingreg[47] = (wreg.s3<<24)|(wreg.s2<<16)|(wreg.s1<<8)|wreg.s0;\n") 
        f.write("workingreg[48] = (wreg.s7<<24)|(wreg.s6<<16)|(wreg.s5<<8)|wreg.s4;\n") 
        f.write("workingreg[49] = (wreg.sb<<24)|(wreg.sa<<16)|(wreg.s9<<8)|wreg.s8;\n") 
        f.write("workingreg[50] = (wreg.sf<<24)|(wreg.se<<16)|(wreg.sd<<8)|wreg.sc;\n\n") 

    def create_rs_helper_func(self,f):
        f.write("\n/* galois field multiply helper function,this is faster than 2x 256 uint lookup table */\n")
        f.write("uint galoisMultiplication_arith(uint a, uint b)\n")
        f.write("{\n")
        f.write("\tuint p = 0;\n")
        f.write("\tuint temp = 0;\n")
        f.write("\tfor(int i = 0; i < 8; i++)\n")
        f.write("\t{\n")
        f.write("\t\ttemp = 8 - ((b & 0x00000001)<<3);\n")
        f.write("\t\tp ^= (a>>temp);\n")
        f.write("\t\ttemp = 8- ((a & 0x00000080)>>4);\n")
        f.write("\t\ta <<= 1;\n")
        f.write("\t\ta &= 0x000000ff;\n")
        f.write("\t\ta ^= (0x0000001d>>temp);\n")
        f.write("\t\tb >>= 1;\n")
        f.write("\t}\n")
        f.write("\treturn p;\n")
        f.write("}\n\n")

    def create_rs_kernel_start(self, f, name):
        f.write("__kernel void test_rsencode_%s( __global uint *in, __global uint *out)\n{\n" % name)
        f.write("uint workingreg[51];\n")
        for i in range(0,47):
            f.write("workingreg[%d] = in[%d];\n" % (i,i))

    def create_rs_kernel_end(self, f):
        for i in range(0,51):
            f.write("out[%d] = workingreg[%d];\n" % (i,i))
        f.write("}\n\n")

    def test_execution_time(self):
        print "test_execution_time:"

        buffersize_in = 188
        buffersize_out = 204
        kernel_parallel_task = 1
        kernel_workgroupsize = 1
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
        print "test_reedsolomon:"
        passed = 0
        linecnt = 1

        # opencl buffer uint
        self.inputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=48*4)
        # opencl buffer uint
        self.outputbuffer = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=51*4)

        for k in self.kernelname:
            kernel = self.load_kernel(self.filename, k)
            self.fd_input = open('test_bench_rs_input.csv', 'r')
            self.fd_output = open('test_bench_rs_output.csv', 'r')
            for line in self.fd_input:
                data_to_encode = numpy.fromstring(line, dtype=numpy.uint8, sep=",").tostring()
                data_to_encode = numpy.fromstring(data_to_encode, dtype=numpy.uint32)

                encoded_data = numpy.array(numpy.zeros(51), dtype=numpy.uint32)
                reference_data = numpy.fromstring(self.fd_output.readline(), dtype=numpy.uint8, sep=",")

                cl.enqueue_copy(self.queue, self.inputbuffer, data_to_encode).wait()
                kernel.set_args(self.inputbuffer, self.outputbuffer)
                cl.enqueue_nd_range_kernel(self.queue,kernel,(1,),None ).wait()
                cl.enqueue_copy(self.queue, encoded_data, self.outputbuffer).wait()

                if encoded_data.tostring() == reference_data.tostring():
                    passed += 1
                    print "Test %d PASSED" % linecnt
                else:
                    print "Test %d FAILED" % linecnt
                    print "input data:"
                    print numpy.fromstring(data_to_encode.tostring(), dtype=numpy.uint8)
                    print "encoded data:"
                    print numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8)
                    print "reference data:"
                    print reference_data
                    print "error data:"
                    print (reference_data - numpy.fromstring(encoded_data.tostring(), dtype=numpy.uint8))
                linecnt += 1
        print "%d pass out of %d" % (passed,(linecnt-1))
        self.fd_input.close()
        self.fd_output.close()
        if passed == (linecnt-1):
            print "All reedsolomon tests PASS\n"
            return True
        else:
            print "at least one reedsolomon test FAILED\n"
            return False


if __name__ == '__main__':
    alltestpass = True
    create_files = file_creator()
    create_files.test_execution_time()
    alltestpass &= create_files.test_algorithm()
    print "All tests passed: %s" % alltestpass

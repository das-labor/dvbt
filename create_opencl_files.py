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
    
class file_creator():
    def __init__(self):
        copyright = "/*\n#\n#    DVB-T Encoder written in python and opencl\n#    Copyright (C) 2012  Patrick Rudolph <siro@das-labor.org>\n#\n#    This program is free software; you can redistribute it and/or modify it under the terms \n#    of the GNU General Public License as published by the Free Software Foundation; either version 3 \n#    of the License, or (at your option) any later version.\n#\n#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; \n#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n#    See the GNU General Public License for more details.\n#\n#    You should have received a copy of the GNU General Public License along with this program; \n#    if not, see <http://www.gnu.org/licenses/>.\n*/\n"
        if not os.path.isfile("outer_coding.cl"):
            print "outer_coding.cl doesn't exist ! creating file ..."
            f = open('outer_coding.cl', 'w')
            f.write(copyright)
            self.create_rs_helper_func(f)
            f.write("/* input mpeg-ts packets, each packet has 188bytes\nnumpy converts to input data stream to this format\nwhere uint is 0xAaBbCcDd\n0: Dd\n1: Cc\n2: Bb\n3: Aa\n...\n\nthe output has reverse alignment\nwhere uint is 0xAaBbCcDd\n0: Aa\n1: Bb\n2: Cc\n3: Dd\n...\n\nThis is needed for inner-coding, as the uint can be shifted bitwise left\n\n*/\n\n")
            f.write("__kernel void run( __global uint *in, __global uint *out)\n{\n")
            f.write("uint workingreg[51];\nint pbrs_index = get_global_id(0);\nint dimN = pbrs_index*47;\n")
            self.create_pbrs(f)
            self.create_rs_encoder(f)
            self.create_outer_interleaver(f)
            f.write("}\n\n")

            f.write("__kernel void test_ed( __global uint *in, __global uint *out)\n{\n")
            f.write("uint workingreg[51];\nint pbrs_index = get_global_id(0);\nint dimN = pbrs_index*47;\n")

            self.create_pbrs(f)
            for i in range(0,47):
                f.write("out[%d] = workingreg[%d];\n" % (i,i))
            f.write("}\n\n")

            f.write("__kernel void test_rsencode( __global uint *in, __global uint *out)\n{\n")
            f.write("uint workingreg[51];\n")
            for i in range(0,47):
                f.write("workingreg[%d] = in[%d];\n" % (i,i))
            self.create_rs_encoder(f)

            for i in range(0,51):
                f.write("out[%d] = workingreg[%d];\n" % (i,i))
            f.write("}\n\n")

            f.write("__kernel void test_oi( __global uint *in, __global uint *out)\n{\n")
            f.write("uint workingreg[64];\nint pbrs_index = 0;\nint dimN = pbrs_index*47;\n")
            for i in range(0,51):
                f.write("workingreg[%d] = in[%d];\n" % (i,i))
            self.create_outer_interleaver(f)
            f.write("}\n\n")
            f.close()

        if not os.path.isfile("symbol_interleaver_mapper.cl"):
            print "symbol_interleaver_mapper.cl doesn't exist ! creating file ..."
            f = open('symbol_interleaver_mapper.cl', 'w')
            f.write(copyright)
            self.create_symbol_interleaver_and_fft_mapper(f,0,6817)
            self.create_symbol_interleaver_and_fft_mapper(f,1,6817)
            self.create_symbol_interleaver_and_fft_mapper(f,2,6817)
            self.create_symbol_interleaver_and_fft_mapper(f,3,6817)
            self.create_symbol_interleaver_and_fft_mapper(f,0,1704)
            self.create_symbol_interleaver_and_fft_mapper(f,1,1704)
            self.create_symbol_interleaver_and_fft_mapper(f,2,1704)
            self.create_symbol_interleaver_and_fft_mapper(f,3,1704)
            f.close()
        if not os.path.isfile("guardinterval.cl"):
            print "guardinterval.cl doesn't exist ! creating file ..."
            f = open('guardinterval.cl', 'w')
            f.write(copyright)
            self.create_guardinterval(f)
            f.close()
        if not os.path.isfile("inner_coding.cl"):
            print "inner_coding.cl doesn't exist ! creating file ..."
            f = open('inner_coding.cl', 'w')
            f.write(copyright)
            self.create_inner_coder(f)
            f.close()

        return



        if not os.path.isfile("fft_mapper.cl"):
            print "fft_mapper.cl doesn't exist ! creating file ..."
            f = open('fft_mapper.cl', 'w')
            f.write(copyright)
            self.create_mapper(f,0,6817)
            self.create_mapper(f,1,6817)
            self.create_mapper(f,2,6817)
            self.create_mapper(f,3,6817)
            self.create_mapper(f,0,1704)
            self.create_mapper(f,1,1704)
            self.create_mapper(f,2,1704)
            self.create_mapper(f,3,1704)
            f.close()
        if not os.path.isfile("signal_constellation.cl"):
            print "signal_constellation.cl doesn't exist ! creating file ..."
            f = open('signal_constellation.cl', 'w')
            f.write(copyright)
            self.create_signal_constellation(f)
            f.close()
        if not os.path.isfile("symbol_interleaver.cl"):
            print "symbol_interleaver.cl doesn't exist ! creating file ..."
            f = open('symbol_interleaver.cl', 'w')
            f.write(copyright)
            self.create_symbol_interleaver(f)
            f.close()
        if not os.path.isfile("symbol_interleaverA.cl"):
            print "symbol_interleaverA.cl doesn't exist ! creating file ..."
            f = open('symbol_interleaverA.cl', 'w')
            f.write(copyright)
            self.create_symbol_interleaverA(f)
            f.close()
        if not os.path.isfile("symbol_interleaverB.cl"):
            print "symbol_interleaverB.cl doesn't exist ! creating file ..."
            f = open('symbol_interleaverB.cl', 'w')
            f.write(copyright)
            self.create_symbol_interleaverB(f)
            f.close()
    
    # input: file descriptor, 0-3, usefulcarriers
    def create_mapper(self, f, symbol_index, usefulcarriers):
        self.tpssarray = [34, 50, 209, 346, 413, 569, 595, 688, 790, 901, 1073, 1219, 1262, 1286, 1469, 1594, 1687, 1738, 1754, 1913, 2050, 2117, 2273, 2299, 2392, 2494, 2605, 2777, 2923, 2966, 2990, 3173, 3298, 3391, 3442, 3458, 3617, 3754, 3821, 3977, 4003, 4096, 4198, 4309, 4481, 4627, 4670, 4694, 4877, 5002, 5095, 5146, 5162, 5321, 5458, 5525, 5681, 5707, 5800, 5902, 6013, 6185, 6331, 6374, 6398, 6581, 6706, 6799]
        self.continualpilotsarray = [48,54,87,141,156,192,201,255,279,282,333,432,450,483,525,531,618,636,714,759,765,780,804,873,888,918,939,942,969,984,1050,1101,1107,1110,1137,1140,1146,1206,1269,1323,1377,1491,1683,1704,1752,1758,1791,1845,1860,1896,1905,1959,1983,1986,2037,2136,2154,2187,2229,2235,2322,2340,2418,2463,2469,2484,2508,2577,2592,2622,2643,2646,2673,2688,2754,2805,2811,2814,2841,2844,2850,2910,2973,3027,3081,3195,3387,3408,3456,3462,3495,3549,3564,3600,3609,3663,3687,3690,3741,3840,3858,3891,3933,3939,4026,4044,4122,4167,4173,4188,4212,4281,4296,4326,4347,4350,4377,4392,4458,4509,4515,4518,4545,4548,4554,4614,4677,4731,4785,4899,5091,5112,5160,5166,5199,5253,5268,5304,5313,5367,5391,5394,5445,5544,5562,5595,5637,5643,5730,5748,5826,5871,5877,5892,5916,5985,6000,6030,6051,6054,6081,6096,6162,6213,6219,6222,6249,6252,6258,6318,6381,6435,6489,6603,6795]
        self.p = 0
        self.k = 0
        self.scatteredpilots = []
        while self.k < usefulcarriers:
            self.k = 0 + 3 * (symbol_index % 4) + 12 * self.p
            self.p += 1
            self.scatteredpilots.append(self.k)
        self.p = 0
        f.write("/* this maps the v-bit data words onto the fft input buffer among with the pilots */\n")
        f.write("/* input is usfulcarriers * float2, output is odfmcarriers * float2 */\n")
        f.write("__kernel void map_symbols%d_%d( __global float2 *in,  __global float2 *out)\n" % (symbol_index,usefulcarriers))
        f.write("{\n")
        
        for i in range(0, usefulcarriers):
            if self.tpssarray.count(i) > 0:
                f.write("/* %d is tps-pilot, skip*/\n" % i)
            elif self.continualpilotsarray.count(i) > 0:
                f.write("/* %d is continual-pilot, skip*/\n" % i)
            elif self.scatteredpilots.count(i) > 0:
                f.write("/* %d is scattered-pilot, skip*/\n" % i)
            else:
                f.write("out[%d] = in[%d];\n" % (i,self.p))
                self.p += 1
        f.write("}\n\n")

    # input: file descriptor
    def create_outer_interleaver(self, f):
        fifo = [[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(0,12):
            for j in range(0,i):
                fifo[i].append(-1)
        in_a = list(xrange(204))
        output_array = []
        pointer = 0

        f.write("/* interleave the 204 bytes packet */\n")
        f.write("dimN = pbrs_index*51;\n")
        while len(output_array) < 204:
            if len(fifo[pointer]) == 0:
                if len(in_a) > 0:
                    output_array.append(in_a.pop(0))
            else:
                pop_data = fifo[pointer].pop(0)
                if pop_data != -1:
                    output_array.append(pop_data)
                if len(in_a) > 0:
                    fifo[pointer].append(in_a.pop(0))
                else:
                    fifo[pointer].append(-1)

            pointer +=1
            pointer %= 12
            print fifo
            print "\n"

        for i in range(0,204):
            print "out[%d] = %d\n" % (i , output_array[i])

        out_cnt = 0
        for i in range(0,51):
            f.write("out[dimN+%d] = (((workingreg[%d]>>%d)&0x000000ff)<<24)|(((workingreg[%d]>>%d)&0x000000ff)<<16)|(((workingreg[%d]>>%d)&0x000000ff)<<8)|((workingreg[%d]>>%d)&0x000000ff);\n" % (i, output_array[i*4+0]/4,(output_array[i*4+0]%4)*8,output_array[i*4+1]/4,(output_array[i*4+1]%4)*8,output_array[i*4+2]/4,(output_array[i*4+2]%4)*8,output_array[i*4+3]/4,(output_array[i*4+3]%4)*8))
    

    # input: file descriptor
    # rs -generator polynomial
    #
    # 1x16+	59x15+	13x14+	104x13+	189x12+	68x11+	209x10+	30x9+	8x8+	163x7+	65x6+	41x5+	229x4+	98x3+	50x2+	36x1+	59x0
    # in hex:
    # 3B 0D 68 BD 44 D1 1E 08 A3 41 29 E5 62 32 24 3B
    # optimized for 64bit systems
    # gf init poly = x^8 + x^4 +x^3+x^2 + 1
    def create_rs_encoder(self, f):

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
            for i in range(0,47):
                if i == 0:
                    f.write("\tcase %d:\n" % j)
                    pbrsarray.pop(0)
                    f.write("\t\tworkingreg[0] = in[dimN+0] ^ 0x%02X%02X%02X%02X;\n" % (pbrsarray.pop(2),pbrsarray.pop(1),pbrsarray.pop(0),0))
                    if j == 0:
                        f.write("\t\tworkingreg[0] = ((workingreg[0]&0xffffff00)|0x000000b8);\n")
                    else:
                        f.write("\t\tworkingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);\n")
                else:
                    f.write("\t\tworkingreg[%d] = in[dimN+%d] ^ 0x%02X%02X%02X%02X;\n" % (i,i,pbrsarray.pop(3),pbrsarray.pop(2),pbrsarray.pop(1),pbrsarray.pop(0)))

            f.write("\t\tbreak;\n")

        f.write("}\n\n")

        f.write("\n")

    def create_signal_constellation(self, f):
        f.write("/* use lookup-table instead ??? */\n")
        f.write("/* this function takes a uint ( 4-bytes) and threads each byte as one v-bit word */\n")
        f.write("/* where v is 2 for qpsk, 4 for 16-qam and 6 for 64-qam */\n")
        f.write("/* for every uint 4 float2 are generated (a complex number) */\n")

        f.write("__kernel void qpsk( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 1.0f - ((in[i] & 0x00000001)>>%d) * 2.0f;\ntmp.y = 1.0f - ((in[i] & 0x00000002)>>%d) * 2.0f;\nout[i+%d] = tmp;\n\n" % (i*8,i*8+1,i))
        f.write("}\n\n")
        f.write("__kernel void qam_16( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 3.0f - ((in[i] & 0x00000004)>>%d) * 2.0f;\n" % (i*8+2))
            f.write("tmp.y = 3.0f - ((in[i] & 0x00000008)>>%d) * 2.0f;\ntmp.x *= 1.0f-((in[i] & 0x00000001)>>%d) * 2.0f;\ntmp.y *= 1.0f -((in[i] & 0x00000002)>>%d) * 2.0f;\nout[i+%d] = tmp;\n" % (i*8+3,i*8,i*8+1,i))
        f.write("}\n\n")
        f.write("__kernel void qam_64( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 3.0f -((in[i] & 0x00000010)>>%d) * 2.0f;\ntmp.y = 3.0f -((in[i] & 0x00000020)>>%d) * 2.0f;\n" % (i*8+4,i*8+5))
            f.write("tmp.x *= 1.0f -((in[i] & 0x00000004)>>%d) * 2.0f;\ntmp.y *= 1.0f -((in[i] & 0x00000008)>>%d) * 2.0f;\n" % (i*8+2,i*8+3))
            f.write("tmp.x += 4.0f;\ntmp.y += 4.0f;\n") 
            f.write("tmp.x *= 1.0f -((in[i] & 0x00000001)>>%d) * 2.0f;\ntmp.y *= 1.0f -((in[i] & 0x00000002)>>%d) * 2.0f;\n" % (i*8+0,i*8+1))
            f.write("out[i+%d] = tmp;\n\n" % i)
        f.write("}\n\n")

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
                f.write("\t__local uint interleaved_bits[%d][126];\n" % mdbits)
                f.write("\tuint workingreg[2];\n")
                f.write("\tuint resultreg[%d];\n\n" % mdbits)
                f.write("\tfloat2 tmp;\n")
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

    def create_symbol_interleaver(self, f):
        infotext = " symbol interleaver: permutation function is inverted for odd odfm symbols\n"
        infotext += " 2k mode:\n"
        infotext += "  input/output is 1512 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 10 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 0 7 5 1 8 2 6 9 3 4\n"

        infotext += " 8k mode:\n"
        infotext += "  input/output is 6048 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 12 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7\n\n"
        infotext += " each workgroup processes work_dim*2 items\n"

        f.write("/*\n %s */\n" % infotext)
        rs_xor = 0
        rs = 0
        workgroupsize = 24
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_2K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            f.write("\tuint shift_reg = 0;\n\tconst uint shift_reg_init[%d] = {" % (int(1512/workgroupsize)+1) )

            for i in range(0,1512):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>3) & 1)
                    rs >>= 1
                    rs |= rs_xor<<9
                if i % workgroupsize == 0:
                    f.write(" %d " % rs)
                    if i < int(1512/workgroupsize)*workgroupsize:
                        f.write(",")

            f.write("};\n")
            f.write("\tshift_reg = shift_reg_init[get_group_id(0)*2];\n")
            f.write("\tuint r = 0;\n")
            f.write("\tuint q = 0;\n")
            f.write("\tfor(uint i = 0; q < get_local_id(0);i++)\n\t{\n")
            f.write("\t\tshift_reg |= (((shift_reg)^(shift_reg>>3))&0x00000001)<<9;\n")
            f.write("\t\tshift_reg >>= 1;\n")
            f.write("\t\tr = 0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000001)<<4;\n")
            f.write("\t\tr |= (shift_reg & 0x00000002)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000004)<<7;\n")
            f.write("\t\tr |= (shift_reg & 0x00000008)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000010)>>2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000020)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000040)>>5;\n")
            f.write("\t\tr |= (shift_reg & 0x00000080)>>2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000100)>>1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000200)>>9;\n")
            f.write("\t\tr |= (i & 0x00000001)<<10;\n")
            f.write("\t\t/* if r < 1512: q += 1 */\n")
            f.write("\t\tq+=(((r-1512)&0x80000000)>>31);\n")
            f.write("\t}\n")
            f.write("\t/* r holds now the destination value H(q) */\n")
            if parity == "even":
                f.write("\tout[r] = in[get_group_id(0)*2*get_local_size(0)+get_local_id(0)];\n")
            elif parity == "odd":
                f.write("\tout[get_group_id(0)*2*get_local_size(0)+get_local_id(0)] = in[r];\n")

            f.write("\tshift_reg = shift_reg_init[get_group_id(0)*2+1];\n")
            f.write("\tq = 0;\n")
            f.write("\tfor(uint i = 0; q < (get_local_size(0)-get_local_id(0));i++)\n\t{\n")
            f.write("\t\tshift_reg |= (((shift_reg)^(shift_reg>>3))&0x00000001)<<9;\n")
            f.write("\t\tshift_reg >>= 1;\n")
            f.write("\t\tr = 0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000001)<<4;\n")
            f.write("\t\tr |= (shift_reg & 0x00000002)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000004)<<7;\n")
            f.write("\t\tr |= (shift_reg & 0x00000008)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000010)>>2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000020)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000040)>>5;\n")
            f.write("\t\tr |= (shift_reg & 0x00000080)>>2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000100)>>1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000200)>>9;\n")
            f.write("\t\tr |= (i & 0x00000001)<<10;\n")
            f.write("\t\t/* if r < 1512: q += 1 */\n")
            f.write("\t\tq+=(((r-1512)&0x80000000)>>31);\n")
            f.write("\t}\n")
            f.write("\t/* r holds now the destination value H(q) */\n")
            if parity == "even":
                f.write("\tout[r] = in[get_group_id(0)*2*get_local_size(0)+(get_local_size(0)-get_local_id(0))];\n")
            elif parity == "odd":
                f.write("\tout[get_group_id(0)*2*get_local_size(0)+(get_local_size(0)-get_local_id(0))] = in[r];\n")
            f.write("}\n\n")

        rs_xor = 0
        rs = 0
        workgroupsize = 96
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_8K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            f.write("\tuint shift_reg = 0;\n\tconst uint shift_reg_init[%d] = {" % (int(6048/workgroupsize)+1) )

            for i in range(0,6048):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1)
                    rs >>= 1
                    rs |= rs_xor<<11
                if i % workgroupsize == 0:
                    f.write(" %d " % rs)
                    if i < int(6048/workgroupsize)*workgroupsize:
                        f.write(",")

            f.write("};\n")
            f.write("\tshift_reg = shift_reg_init[get_group_id(0)*2];\n")
            f.write("\tuint r = 0;\n")
            f.write("\tuint q = 0;\n")
            f.write("\tfor(uint i = 0; q < get_local_id(0);i++)\n\t{\n")
            f.write("\t\tshift_reg |= (((shift_reg)^(shift_reg>>1)^(shift_reg>>4)^(shift_reg>>6))&0x00000001)<<11;\n")
            f.write("\t\tshift_reg >>= 1;\n")
            f.write("\t\tr = 0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000001)<<7;\n")
            f.write("\t\tr |= (shift_reg & 0x00000002)<<0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000004)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000008)>>1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000010)<<5;\n")
            f.write("\t\tr |= (shift_reg & 0x00000020)<<1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000040)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000080)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000100)>>8;\n")
            f.write("\t\tr |= (shift_reg & 0x00000200)>>6;\n")
            f.write("\t\tr |= (shift_reg & 0x00000400)<<1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000800)>>6;\n")
            f.write("\t\tr |= (i & 0x00000001)<<12;\n")
            f.write("\t\t/* if r < 6048: q += 1 */\n")
            f.write("\t\tq+=(((r-6048)&0x80000000)>>31);\n")
            f.write("\t}\n")
            f.write("\t/* r holds now the destination value H(q) */\n")
            if parity == "even":
                f.write("\tout[r] = in[get_group_id(0)*2*get_local_size(0)+get_local_id(0)];\n")
            elif parity == "odd":
                f.write("\tout[get_group_id(0)*2*get_local_size(0)+get_local_id(0)] = in[r];\n")

            f.write("\tshift_reg = shift_reg_init[get_group_id(0)*2+1];\n")
            f.write("\tq = 0;\n")
            f.write("\tfor(uint i = 0; q < (get_local_size(0)-get_local_id(0));i++)\n\t{\n")
            f.write("\t\tshift_reg |= (((shift_reg)^(shift_reg>>1)^(shift_reg>>4)^(shift_reg>>6))&0x00000001)<<11;\n")
            f.write("\t\tshift_reg >>= 1;\n")
            f.write("\t\tr = 0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000001)<<7;\n")
            f.write("\t\tr |= (shift_reg & 0x00000002)<<0;\n")
            f.write("\t\tr |= (shift_reg & 0x00000004)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000008)>>1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000010)<<5;\n")
            f.write("\t\tr |= (shift_reg & 0x00000020)<<1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000040)<<2;\n")
            f.write("\t\tr |= (shift_reg & 0x00000080)<<3;\n")
            f.write("\t\tr |= (shift_reg & 0x00000100)>>8;\n")
            f.write("\t\tr |= (shift_reg & 0x00000200)>>6;\n")
            f.write("\t\tr |= (shift_reg & 0x00000400)<<1;\n")
            f.write("\t\tr |= (shift_reg & 0x00000800)>>6;\n")
            f.write("\t\tr |= (i & 0x00000001)<<12;\n")
            f.write("\t\t/* if r < 6048: q += 1 */\n")
            f.write("\t\tq+=(((r-6048)&0x80000000)>>31);\n")
            f.write("\t}\n")
            f.write("\t/* r holds now the destination value H(q) */\n")
            if parity == "even":
                f.write("\tout[r] = in[get_group_id(0)*2*get_local_size(0)+(get_local_size(0)-get_local_id(0))];\n")
            elif parity == "odd":
                f.write("\tout[get_group_id(0)*2*get_local_size(0)+(get_local_size(0)-get_local_id(0))] = in[r];\n")
            f.write("}\n\n")

    def create_symbol_interleaverA(self, f):
        infotext = " symbol interleaver: permutation function is inverted for odd odfm symbols\n"
        infotext += " 2k mode:\n"
        infotext += "  input/output is 1512 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 10 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 0 7 5 1 8 2 6 9 3 4\n"

        infotext += " 8k mode:\n"
        infotext += "  input/output is 6048 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 12 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7\n\n"
        infotext += " each workgroup processes work_dim*2 items\n"

        f.write("/*\n %s */\n" % infotext)
        rs_xor = 0
        rs = 0
        r = 0
        workgroupsize = 216
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_2K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            #f.write("\tuint shift_reg = 0;\n\t__const ushort shift_reg_init[%d] = {" % (int(1512/workgroupsize)+1) )
            f.write("__const short il_array[1512]={\n")
            for i in range(0,1512):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>3) & 1)
                    rs >>= 1
                    rs |= rs_xor<<9
                r = (rs & 0x00000001)<<4
                r |= (rs & 0x00000002)<<2
                r |= (rs & 0x00000004)<<7
                r |= (rs & 0x00000008)<<3
                r |= (rs & 0x00000010)>>2
                r |= (rs & 0x00000020)<<3
                r |= (rs & 0x00000040)>>5
                r |= (rs & 0x00000080)>>2
                r |= (rs & 0x00000100)>>1
                r |= (rs & 0x00000200)>>9
                r |= (i & 0x00000001)<<10
                if r < 1512:
                    f.write("%d" % r)
                    if i < 1510:
                        f.write(",")
                    if i % 32 == 31:
                        f.write("\n")

            f.write("};\n")
            f.write("out[get_global_id(0)]=in[il_array[get_global_id(0)]];\n")

            f.write("}\n\n")
        rs_xor = 0
        rs = 0
        r = 0

        workgroupsize = 216
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_8K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            #f.write("\tuint shift_reg = 0;\n\t__const ushort shift_reg_init[%d] = {" % (int(1512/workgroupsize)+1) )
            f.write("__const short il_array[6048]={\n")
            for i in range(0,6048):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1)
                    rs >>= 1
                    rs |= rs_xor<<11
                r = (rs & 0x00000001)<<7
                r |= (rs & 0x00000002)<<0
                r |= (rs & 0x00000004)<<2
                r |= (rs & 0x00000008)>>1
                r |= (rs & 0x00000010)<<5
                r |= (rs & 0x00000020)<<1
                r |= (rs & 0x00000040)<<2
                r |= (rs & 0x00000080)<<3
                r |= (rs & 0x00000100)>>8
                r |= (rs & 0x00000200)>>6
                r |= (rs & 0x00000400)<<1
                r |= (rs & 0x00000800)>>6
                r |= (i & 0x00000001)<<12
                if r < 6048:
                    f.write("%d" % r)
                    if i < 6046:
                        f.write(",")
                    if i % 32 == 31:
                        f.write("\n")

            f.write("};\n")
            f.write("out[get_global_id(0)]=in[il_array[get_global_id(0)]];\n")

            f.write("}\n\n")

    def create_symbol_interleaverB(self, f):
        infotext = " symbol interleaver: permutation function is inverted for odd odfm symbols\n"
        infotext += " 2k mode:\n"
        infotext += "  input/output is 1512 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 10 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 0 7 5 1 8 2 6 9 3 4\n"

        infotext += " 8k mode:\n"
        infotext += "  input/output is 6048 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 12 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7\n\n"
        infotext += " each workgroup processes work_dim*2 items\n"

        f.write("/*\n %s */\n" % infotext)
        rs_xor = 0
        rs = 0
        r = 0
        workgroupsize = 216
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_2K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            #f.write("\tuint shift_reg = 0;\n\t__const ushort shift_reg_init[%d] = {" % (int(1512/workgroupsize)+1) )
            f.write("uint tmp=0;\n")
            f.write("switch(get_global_id(0)){\n")
            for i in range(0,1512):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>3) & 1)
                    rs >>= 1
                    rs |= rs_xor<<9
                r = (rs & 0x00000001)<<4
                r |= (rs & 0x00000002)<<2
                r |= (rs & 0x00000004)<<7
                r |= (rs & 0x00000008)<<3
                r |= (rs & 0x00000010)>>2
                r |= (rs & 0x00000020)<<3
                r |= (rs & 0x00000040)>>5
                r |= (rs & 0x00000080)>>2
                r |= (rs & 0x00000100)>>1
                r |= (rs & 0x00000200)>>9
                r |= (i & 0x00000001)<<10
                if r < 1512:
                    f.write("\t\tcase %d:\n\t\ttmp = %d;\n\t\tbreak;\n" % (i,r))
            f.write("};\n")
            f.write("out[get_global_id(0)]=in[tmp];\n")

            f.write("}\n\n")
        rs_xor = 0
        rs = 0
        r = 0

        workgroupsize = 216
        for parity in ["even","odd"]:
            f.write("__kernel void run_%s_8K( __global float2 *in, __global float2 *out)\n{\n" % parity)
            #f.write("\tuint shift_reg = 0;\n\t__const ushort shift_reg_init[%d] = {" % (int(1512/workgroupsize)+1) )
            f.write("\tuint tmp=0;\n")
            f.write("\tswitch(get_global_id(0)){\n")
            for i in range(0,6048):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1)
                    rs >>= 1
                    rs |= rs_xor<<11
                r = (rs & 0x00000001)<<7
                r |= (rs & 0x00000002)<<0
                r |= (rs & 0x00000004)<<2
                r |= (rs & 0x00000008)>>1
                r |= (rs & 0x00000010)<<5
                r |= (rs & 0x00000020)<<1
                r |= (rs & 0x00000040)<<2
                r |= (rs & 0x00000080)<<3
                r |= (rs & 0x00000100)>>8
                r |= (rs & 0x00000200)>>6
                r |= (rs & 0x00000400)<<1
                r |= (rs & 0x00000800)>>6
                r |= (i & 0x00000001)<<12
                if r < 6048:
                    f.write("\t\tcase %d:\n\t\ttmp = %d;\n\t\tbreak;\n" % (i,r))

            f.write("\t};\n")
            f.write("\tout[get_global_id(0)]=in[tmp];\n")
            f.write("}\n\n")

    def create_symbol_interleaver_and_fft_mapper(self, f,symbol_index,usefulcarriers ):
        self.tpssarray = [34, 50, 209, 346, 413, 569, 595, 688, 790, 901, 1073, 1219, 1262, 1286, 1469, 1594, 1687, 1738, 1754, 1913, 2050, 2117, 2273, 2299, 2392, 2494, 2605, 2777, 2923, 2966, 2990, 3173, 3298, 3391, 3442, 3458, 3617, 3754, 3821, 3977, 4003, 4096, 4198, 4309, 4481, 4627, 4670, 4694, 4877, 5002, 5095, 5146, 5162, 5321, 5458, 5525, 5681, 5707, 5800, 5902, 6013, 6185, 6331, 6374, 6398, 6581, 6706, 6799]
        self.continualpilotsarray = [48,54,87,141,156,192,201,255,279,282,333,432,450,483,525,531,618,636,714,759,765,780,804,873,888,918,939,942,969,984,1050,1101,1107,1110,1137,1140,1146,1206,1269,1323,1377,1491,1683,1704,1752,1758,1791,1845,1860,1896,1905,1959,1983,1986,2037,2136,2154,2187,2229,2235,2322,2340,2418,2463,2469,2484,2508,2577,2592,2622,2643,2646,2673,2688,2754,2805,2811,2814,2841,2844,2850,2910,2973,3027,3081,3195,3387,3408,3456,3462,3495,3549,3564,3600,3609,3663,3687,3690,3741,3840,3858,3891,3933,3939,4026,4044,4122,4167,4173,4188,4212,4281,4296,4326,4347,4350,4377,4392,4458,4509,4515,4518,4545,4548,4554,4614,4677,4731,4785,4899,5091,5112,5160,5166,5199,5253,5268,5304,5313,5367,5391,5394,5445,5544,5562,5595,5637,5643,5730,5748,5826,5871,5877,5892,5916,5985,6000,6030,6051,6054,6081,6096,6162,6213,6219,6222,6249,6252,6258,6318,6381,6435,6489,6603,6795]
        self.p = 0
        self.k = 0
        self.scatteredpilots = []
        self.datacarriers = []
        while self.k < usefulcarriers:
            self.k = 0 + 3 * (symbol_index % 4) + 12 * self.p
            self.p += 1
            self.scatteredpilots.append(self.k)
        self.p = 0
        infotext = " symbol interleaver: permutation function is inverted for odd odfm symbols\n"
        infotext += " 2k mode:\n"
        infotext += "  input/output is 1512 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 10 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 0 7 5 1 8 2 6 9 3 4\n"

        infotext += " 8k mode:\n"
        infotext += "  input/output is 6048 float2\n"
        infotext += "  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )\n"
        infotext += "  shift_reg has size 12 bits\n"
        infotext += "  R -> R' mapping\n"
        infotext += "  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0\n"
        infotext += "  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7\n\n"
        infotext += " each workgroup processes work_dim*2 items\n"

        infotext += "\n symbol mapper: maps float2 onto the fft input buffer, prevents pilots to be overritten\n"
        infotext += " this maps the v-bit data words onto the fft input buffer among with the pilots\n"
        infotext += " input is usfulcarriers * float2, output is odfmcarriers * float2\n"

        f.write("/*\n %s */\n" % infotext)

        f.write("__kernel void interleaver_and_map_symbols%d_%d( __global float2 *in,  __global float2 *out)\n" % (symbol_index,usefulcarriers))
        f.write("{\n")
        
        for i in range(0, usefulcarriers):
            if not (self.tpssarray.count(i) > 0) and not (self.continualpilotsarray.count(i) > 0) and not (self.scatteredpilots.count(i) > 0):
                self.datacarriers.append(i)

        rs_xor = 0
        rs = 0
        r = 0

        #todo
        if (symbol_index & 1) == 0:
            parity = "even"
        else:
            parity = "odd"
        f.write("\tuint inpos=0;\n")
        f.write("\tuint outpos=0;\n")
        f.write("\tswitch(get_global_id(0)){\n")
        if usefulcarriers == 1704:
            for i in range(0,1512):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>3) & 1)
                    rs >>= 1
                    rs |= rs_xor<<9
                r = (rs & 0x00000001)<<4
                r |= (rs & 0x00000002)<<2
                r |= (rs & 0x00000004)<<7
                r |= (rs & 0x00000008)<<3
                r |= (rs & 0x00000010)>>2
                r |= (rs & 0x00000020)<<3
                r |= (rs & 0x00000040)>>5
                r |= (rs & 0x00000080)>>2
                r |= (rs & 0x00000100)>>1
                r |= (rs & 0x00000200)>>9
                r |= (i & 0x00000001)<<10
                if r < 1512:
                    f.write("\t\tcase %d:\n\t\t\tinpos = %d;\n\t\t\toutpos = %d;\n\t\t\tbreak;\n" % (i,r,self.datacarriers[i]))
        elif usefulcarriers == 6817:
            for i in range(0,6048):
                if i < 2:
                    rs = 0
                elif i == 2:
                     rs = 1
                else:
                    rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1)
                    rs >>= 1
                    rs |= rs_xor<<11
                r = (rs & 0x00000001)<<7
                r |= (rs & 0x00000002)<<0
                r |= (rs & 0x00000004)<<2
                r |= (rs & 0x00000008)>>1
                r |= (rs & 0x00000010)<<5
                r |= (rs & 0x00000020)<<1
                r |= (rs & 0x00000040)<<2
                r |= (rs & 0x00000080)<<3
                r |= (rs & 0x00000100)>>8
                r |= (rs & 0x00000200)>>6
                r |= (rs & 0x00000400)<<1
                r |= (rs & 0x00000800)>>6
                r |= (i & 0x00000001)<<12
                if r < 6048:
                    f.write("\t\tcase %d:\n\t\t\tinpos = %d;\n\t\t\toutpos = %d;\n\t\t\tbreak;\n" % (i,r,self.datacarriers[i]))

        f.write("\t};\n")
        f.write("\tout[outpos]=in[inpos];\n")
        f.write("}\n\n")

    def create_guardinterval(self, f):
        f.write("__kernel void encode( __global float2 *in, __global uint *out, __const uint guardrange)\n{\n")
        f.write("\tfloat2 tmp=clamp (in[get_global_id(0)<<1], -127, 127);\n")
        f.write("\tfloat2 tmp2=clamp (in[(get_global_id(0)<<1)+1], -127, 127);\n")
        f.write("\tuint out_val;\n")
        f.write("\tout_val = ((uchar)tmp.x+127)|((uchar)tmp.y+127)<<8|((uchar)tmp.x+127)<<16|((uchar)tmp.y+127)<<24;\n")
        f.write("\tout[get_global_id(0)] = out_val;\n")
        f.write("\tif(get_global_id(0) < guardrange)\n")
        f.write("\t{\n")
        f.write("\t\tout[get_global_id(0)+get_global_size(0)] = out_val;\n")
        f.write("\t}\n")
        f.write("}\n")


if __name__ == '__main__':
    create_files = file_creator()



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
            f.write("/* input mpeg-ts packets, each packet has 188bytes\nnumpy converts to input data stream to this format\nwhere uint is 0xAaBbCcDd\n0: Dd\n1: Cc\n2: Bb\n3: Aa\n...\n\nthe output has reverse alignment\nwhere uint is 0xAaBbCcDd\n0: Aa\n1: Bb\n2: Cc\n3: Dd\n...\n\nThis is needed for inner-coding, as the uint can be shifted bitwise left\n\n*/\n\n")
            f.write("__kernel void run( __global uint *in, __global uint *out)\n{\nuint workingreg[64];\nulong rs_shift_reg[4];\nint b,o,p,i;\nint pbrs_index = get_global_id(0);\nint dimN = pbrs_index*47;\n")
            self.create_pbrs(f)
            self.create_rs_encoder(f)
            self.create_outer_interleaver(f)
            f.write("}\n")
            f.close()
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
        fifo = [[],[-1],[-1,-1],[-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
        in_a = list(xrange(204))
        out = []
        out_cnt = 0
        pointer = 0

        f.write("dimN = pbrs_index*51;\n")
        while out_cnt < 204:
            if len(in_a):
                y = in_a.pop(0)
            else:
                y = -1
            if pointer == 0:
                if not y == -1:
                    out.append(y)
                    out_cnt += 1
            else:
                if len(fifo[pointer]):
                    r = fifo[pointer].pop(0)
                else:
                    r = -1
                if not r == -1:
                    out.append(r)
                    out_cnt += 1
                fifo[pointer].append(y)
            pointer += 1
            if pointer == 11:
                pointer = 0

        #for i in range(0,204):
            #print "out[%d] = %d\n" % (i , out[i])

        out_cnt = 0
        for i in range(0,51):
            f.write("out[dimN+%d] = (((workingreg[%d]>>%d)&0x000000ff)<<24)|(((workingreg[%d]>>%d)&0x000000ff)<<16)|(((workingreg[%d]>>%d)&0x000000ff)<<8)|((workingreg[%d]>>%d)&0x000000ff);\n" % (i, out[i*4+0]/4,(out[i*4+0]%4)*8,out[i*4+1]/4,(out[i*4+1]%4)*8,out[i*4+2]/4,(out[i*4+2]%4)*8,out[i*4+3]/4,(out[i*4+3]%4)*8))
    

    # input: file descriptor
    # rs -generator polynomial
    #
    # 1x16+	59x15+	13x14+	104x13+	189x12+	68x11+	209x10+	30x9+	8x8+	163x7+	65x6+	41x5+	229x4+	98x3+	50x2+	36x1+	59x0
    # optimized for 64bit systems
    # gf init poly = x^8 + x^4 +x^3+x^2 + 1
    def create_rs_encoder(self, f):
        a_init_1 = 0xA34129E56232243B
        a_init_2 = 0x3B0D68BD44D11E08
        cnt = 0
        a = a_init_1
        poly = 0x1d
        rega = a_init_1
        f.write("rs_shift_reg[2] = 0;\n")
        f.write("rs_shift_reg[3] = 0;\n\no = 0;\n")
        f.write("/* do a rs(255,236,8) reed-solomon encoding */\n")
        f.write(" for(i = 0; i < 255; i++)\n{\n")
        f.write("\tb = (workingreg[i / 4]>>((i%4)*8))&0x000000ff;\n")
        f.write("\tb ^= o;\n") 

        while cnt < 8:
            #f.write( "/* %d */\n" % cnt)
            f.write("\trs_shift_reg[0] ^= ((long)(b & 0x01)* 0x%016xULL);\n" % a )
    
            rega = 0
            if ((a>>56) & 0x80) > 0:
                rega |=(poly<<56);
            if ((a>>48) & 0x80) > 0:
                rega |=(poly<<48);
            if ((a>>40) & 0x80) > 0:
                rega |=(poly<<40);
            if ((a>>32) & 0x80) > 0:
                rega |=(poly<<32);
            if ((a>>24) & 0x80) > 0:
                rega |=(poly<<24);
            if ((a>>16) & 0x80) > 0:
                rega |=(poly<<16);
            if ((a>>8) & 0x80) > 0:
                rega |=(poly<<8);
            if ((a>>0) & 0x80) > 0:
                rega |=(poly<<0);
  
            a &= 0x7f7f7f7f7f7f7f7f
            a <<= 1
            a ^= rega

            f.write("\tb >>= 1;\n")
            cnt += 1

        f.write("\tb = (workingreg[i / 4]>>((i%4)*8))&0x000000ff;\n")
        f.write("\tb ^= o;\n") 
        cnt = 0
        a = a_init_2
        while cnt < 8:
            #f.write("/* %d */\n" % cnt)
            f.write("\trs_shift_reg[1] ^= ((long)(b & 0x01)* 0x%016xULL);\n" % a )
    
            rega = 0
            if ((a>>56) & 0x80) > 0:
                rega |=(poly<<56);
            if ((a>>48) & 0x80) > 0:
                rega |=(poly<<48);
            if ((a>>40) & 0x80) > 0:
                rega |=(poly<<40);
            if ((a>>32) & 0x80) > 0:
                rega |=(poly<<32);
            if ((a>>24) & 0x80) > 0:
                rega |=(poly<<24);
            if ((a>>16) & 0x80) > 0:
                rega |=(poly<<16);
            if ((a>>8) & 0x80) > 0:
                rega |=(poly<<8);
            if ((a>>0) & 0x80) > 0:
                rega |=(poly<<0);
  
            a &= 0x7f7f7f7f7f7f7f7f
            a <<= 1
            a ^= rega

            f.write("\tb >>= 1;\n")
            cnt += 1

        f.write("\to = (rs_shift_reg[3]&0xff00000000000000ULL)>>56;\n") 
        f.write("\tp = (rs_shift_reg[2]&0xff00000000000000ULL)>>56;\n") 
        f.write("\trs_shift_reg[2] <<= 8;\n") 
        f.write("\trs_shift_reg[3] <<= 8;\n") 
        f.write("\trs_shift_reg[3] |= p;\n") 
        f.write("\trs_shift_reg[2] ^= rs_shift_reg[0];\n") 
        f.write("\trs_shift_reg[3] ^= rs_shift_reg[1];\n}\n\n") 
        f.write("/* convert back to uint32 */\n") 
        f.write("workingreg[47] = (rs_shift_reg[2]&0x00000000ffffffffULL);\n") 
        f.write("workingreg[48] = (rs_shift_reg[2]&0xffffffff00000000ULL)>>32;\n") 
        f.write("workingreg[49] = (rs_shift_reg[3]&0x00000000ffffffffULL);\n") 
        f.write("workingreg[50] = (rs_shift_reg[3]&0xffffffff00000000ULL)>>32;\n\n") 

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

        f.write("switch(pbrs_index)\n{\n")
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
        f.write("/* fill with zeros */\n")
        for i in range(0,17):
	    f.write("workingreg[%d] = 0;\n" % (47+i))
        f.write("\n")

    def create_signal_constellation(self, f):
        f.write("/* use lookup-table instead ??? */\n")
        f.write("__kernel void qpsk( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 1.0f;\ntmp.y = 1.0f;\ntmp.x = ((in[i] & 0x00000001)>>%d) * -1.0f;\ntmp.y = ((in[i] & 0x00000002)>>%d) * -1.0f;\nout[i+%d] = tmp;\n\n" % (i*8,i*8+1,i))
        f.write("}\n\n")
        f.write("__kernel void qam_16( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 3.0f;\ntmp.y = 3.0f;\ntmp.x -= ((in[i] & 0x00000004)>>%d) * 2.0f;\n" % (i*8+2))
            f.write("tmp.y -= ((in[i] & 0x00000008)>>%d) * 2.0f;\ntmp.x *= -((in[i] & 0x00000001)>>%d);\ntmp.y *= -((in[i] & 0x00000002)>>%d);\n\n" % (i*8+3,i*8,i*8+1))
        f.write("}\n\n")
        f.write("__kernel void qam_64( __global uint *in, __global float2 *out)\n{\nint i = get_global_id(0) * 4;\nfloat2 tmp;\n")
        for i in range(0,4):
            f.write("tmp.x = 3.0f -((in[i] & 0x00000010)>>%d) * 2.0f;\ntmp.y = 3.0f -((in[i] & 0x00000020)>>%d) * 2.0f;\n" % (i*8+4,i*8+5))
            f.write("tmp.x *= -((in[i] & 0x00000004)>>%d);\ntmp.y *= -((in[i] & 0x00000008)>>%d);\n" % (i*8+2,i*8+3))
            f.write("tmp.x += 4.0f;\ntmp.y += 4.0f;\n") 
            f.write("tmp.x *= -((in[i] & 0x00000001)>>%d);\ntmp.y *= -((in[i] & 0x00000002)>>%d);\n\n" % (i*8+0,i*8+1))
        f.write("}\n\n")




if __name__ == '__main__':
    create_files = file_creator()



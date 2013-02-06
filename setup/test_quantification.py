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
import string

class file_creator():
    def __init__(self):
        print "init"

    def test_algorithm(self, ofdm_mode, md, quantsize):
        g = 0.25
        size = 0
        errors = 0
        bitsinarray = 0
        
        if ofdm_mode == 8192:
            size = 6817
        elif ofdm_mode == 2048:
            size = 1705

        if g == 0:
            print "wrong guardinterval specified"
            return

        if size == 0:
            print "wrong ofdmmode"
            return

        # init sinc filter
        sincarray = []
        for i in range(0,32):
            sincarray.append(numpy.sinc((i-16)/2))

        inarray = []
        outarray = []
        data_to_encode = []

        for i in range(0, size):
            bits = md*2+2
            bitsinarray += bits
            val = numpy.random.randint(64)
            tmpsymbolA = symbol(bits)
            tmpsymbolA.set_information(val)
            tmpsymbolB = symbol(bits)
            inarray.append(tmpsymbolA)
            outarray.append(tmpsymbolB)
            data_to_encode.append(tmpsymbolA.get_value())

        for i in range(0, ofdm_mode-size):
            data_to_encode.append(numpy.complex64(0))

        # move data to time domain
        encoded_data = numpy.fft.ifft(numpy.fft.fftshift(data_to_encode))

        #maxval = 0
        #for tmp in encoded_data:
        #    if abs(numpy.real(tmp)) > maxval:
        #        maxval = abs(numpy.real(tmp))
        #    if abs(numpy.imag(tmp)) > maxval:
        #        maxval = abs(numpy.imag(tmp))
        
        # quantification
	quant_data = []
        for tmp in encoded_data:
            real = numpy.float(numpy.int32(numpy.real(tmp) * quantsize))
            imag = numpy.float(numpy.int32(numpy.imag(tmp) * quantsize))
            val = numpy.complex64(real / quantsize + imag / quantsize * 1j)
            #print (val, tmp)
            quant_data.append(val)

        encoded_data = numpy.fft.ifftshift(numpy.fft.fft(quant_data))

        #evaluate
        for i in range(0, size):
            outarray[i].set_value(encoded_data[i])
            for j in range(0,outarray[i].get_bits()):
                if( (outarray[i].get_information() & (2^j)) != (inarray[i].get_information() & (2^j)) ):
                    errors += 1
                    
        print "errors %d out of %d = %3.2f %%" % (errors,bitsinarray,numpy.float(errors)/numpy.float(bitsinarray)*100)  
        if errors == 0:
            print "test PASS"
            return True
        else:
            print "test FAILED"
            return False



# a symbol holds up to <bits> bits information
class symbol():
    def __init__(self, bits):
        self.bits = bits
        self.value = numpy.complex64(0)
        self.information = numpy.uint8(0)

    # value is complex64
    def set_value(self, value):
        self.information = 0
        self.value = value

        if self.bits == 2:
            if numpy.real(self.value) < 0:
                self.information |= 1
            if numpy.imag(self.value) < 0:
                self.information |= 2
        elif self.bits == 4:
            if numpy.real(self.value) < 0:
                self.information |= 1
            if numpy.imag(self.value) < 0:
                self.information |= 2
            if abs(numpy.real(self.value)) < 2:
                self.information |= 4
            if abs(numpy.imag(self.value)) < 2:
                self.information |= 8
        elif self.bits == 6:
            if numpy.real(self.value) < 0:
                self.information |= 1
            if numpy.imag(self.value) < 0:
                self.information |= 2
            if abs(numpy.real(self.value)) < 4:
                self.information |= 4
            if abs(numpy.imag(self.value)) < 4:
                self.information |= 8
            if abs(numpy.real(self.value)) > 2 and abs(numpy.real(self.value)) < 6:
                self.information |= 16
            if abs(numpy.imag(self.value)) > 2 and abs(numpy.imag(self.value)) < 6:
                self.information |= 32

    def set_information(self, information):

        self.value = numpy.complex64(0)

        if self.bits == 2:
            self.information = information & 3

            if self.information & 1:
                self.value = numpy.complex64(-1 + 1j * numpy.imag(self.value))
            else:
                self.value = numpy.complex64(1 + 1j * numpy.imag(self.value))

            if self.information & 2:
                self.value = numpy.complex64(numpy.real(self.value) - 1j )
            else:
                self.value = numpy.complex64(numpy.real(self.value) + 1j )

        elif self.bits == 4:
            self.information = information & 15

            if self.information & 1:
                self.value = numpy.complex64(-1 + 1j * numpy.imag(self.value))
            else:
                self.value = numpy.complex64(1 + 1j * numpy.imag(self.value))

            if self.information & 2:
                self.value = numpy.complex64(numpy.real(self.value) - 1j )
            else:
                self.value = numpy.complex64(numpy.real(self.value) + 1j )

            if not (self.information & 4):
                self.value = numpy.complex64(numpy.real(self.value)*3 + 1j * numpy.imag(self.value))

            if not (self.information & 8):
                self.value = numpy.complex64(numpy.real(self.value) + 1j * numpy.imag(self.value)*3)

        elif self.bits == 6:
            self.information = information & 63
            offsetreal = 0
            offsetimag = 0

            if self.information & 32:
                offsetimag = 1
            else:
                offsetimag = 3

            if self.information & 16:
                offsetreal = 1
            else:
                offsetreal = 3

            if self.information & 8:
                offsetimag *= -1


            if self.information & 4:
                offsetreal *= -1

            self.value = numpy.complex64(4 + offsetreal + (4+offsetimag) * 1j )
            if self.information & 2:
                self.value = numpy.complex64(numpy.real(self.value) - 1j * numpy.imag(self.value))

            if self.information & 1:
                self.value = numpy.complex64(-numpy.real(self.value) + 1j * numpy.imag(self.value))

    def get_value(self):
        return self.value

    def get_information(self):
        return self.information

    def get_bits(self):
        return self.bits


if __name__ == '__main__':
    create_files = file_creator()
    alltestpass = True
    print "\n**************************"
    print "test quantisation of timedomain values"
    for quantsize in [64,128,256,512,1024]:
        for md in [0,1,2]:
            for mode in [2048, 8192]:
                print "\n**************************"
                if md == 0:
                    print "QPSK"
                elif md == 1:
                    print "16QAM"
                elif md == 2:
                    print "64QAM"
    	        print "%d mode - %d quantsize " % (mode,quantsize)
                alltestpass &= create_files.test_algorithm(mode, md, quantsize)
    print "All tests passed: %s" % alltestpass
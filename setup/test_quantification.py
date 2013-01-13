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
import time
import string

class file_creator():
    def __init__(self):
        print "init"

    def test_algorithm(self, ofdm_mode):
        print "\n**************************"
        print "test quantisation of timedomain values"
        passed = 0
        linecnt = 1
        g = 0.25
        size = 0
        
        if ofdm_mode == 8192:
            size = 6817
            print "8k mode"

        elif ofdm_mode == 2048:
            size = 1705
            print "2k mode"

        if g == 0:
            print "wrong guardinterval specified"
            return

        if size == 0:
            print "wrong ofdm_mode"
            return

        # init sinc filter
        sincarray = []
        for i in range(0,32):
            sincarray.append(numpy.sinc((i-16)/2))

        for i in range(0,8):
            inarray = []
            outarray = []
            data_to_encode = []
            for i in range(0, size):
                bits = numpy.random.randint(3)*2+2
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

	    # quantification
            maxval = 0
            a = 256

            for tmp in encoded_data:
                if abs(numpy.real(tmp)) > maxval:
                    maxval = abs(numpy.real(tmp))
                if abs(numpy.imag(tmp)) > maxval:
                    maxval = abs(numpy.imag(tmp))

            print "maxval: %f" % maxval
            print "amplification for 8 bit: %d" % (128/maxval)
            print "amplification for 10 bit: %d" % (512/maxval)

	    quant_data = []
            for tmp in encoded_data:
                real = numpy.float(numpy.int32(numpy.real(tmp) * a/maxval))
                imag = numpy.float(numpy.int32(numpy.imag(tmp) * a/maxval))
                val = numpy.complex64(real / a*maxval + imag / a * 1j*maxval)
                #print (val, tmp)
                quant_data.append(val)


            encoded_data = numpy.fft.ifftshift(numpy.fft.fft(quant_data))

            for i in range(0, size):
                outarray[i].set_value(encoded_data[i])
                #print ( outarray[i].get_value() , inarray[i].get_value())

                if(outarray[i].get_information() == inarray[i].get_information() ):
                    passed += 1

            #print "%d pass" % (passed)

        if passed == size*8:
            print "All quantisation tests PASS\n"
            return True
        else:
            print "at least one quantisation test FAILED\n"
            return False



    
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
    for mode in [2048, 8192]:
        alltestpass &= create_files.test_algorithm(mode)
    print "All tests passed: %s" % alltestpass
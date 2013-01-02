/*
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
*/

/*
  inner coder: 
   convolutional encoder coderate 1/2
   threadcount: T = <bitstoencode>
   input      : N + 1 uints, N = <bitstoencode> / 32 
                the first uint has to be zero and is not part of the bitstream
                data is big endian
   output     : <bitstoencode> * 2 uints
                one bit per uint

                TODO: use 32 bits per uint
 */
__kernel void run_ic_A( __global uint *in, __global uint *out, const uint cr)
{
	ulong workingreg;
	uint resultreg;

	int i = get_global_id(0);
	/* start offset is 26th bit */
	long j = i/cr + 0;

	/* load bit from global memory */
	workingreg =((ulong)in[(j>>5)])<<32|((ulong)in[(j>>5) +1]);
	workingreg <<= (j&31);

	resultreg = 0;
	if(!(i&0x00000001))
	{
		if(workingreg & 0x2000000000UL)
		resultreg++;
		if(workingreg & 0x0400000000UL)
		resultreg++;
		if(workingreg & 0x0200000000UL)
		resultreg++;
		if(workingreg & 0x0100000000UL)
		resultreg++;
		if(workingreg & 0x0080000000UL)
		resultreg++;
		}
		else
		{
		if(workingreg & 0x2000000000UL)
		resultreg++;
		if(workingreg & 0x1000000000UL)
		resultreg++;
		if(workingreg & 0x0400000000UL)
		resultreg++;
		if(workingreg & 0x0200000000UL)
		resultreg++;
		if(workingreg & 0x0080000000UL)
		resultreg++;
	}

	out[i] = resultreg&0x01;
}

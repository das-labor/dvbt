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
*/
/*
 input float2
 output float2
 make sure that tpsbit=1 if (symbol == 0)
 *pilots contain information what to do on any carrier

 */



__kernel void run( __global const float2 *in,  __global float2 *out, const uint *pilots, const uint tpsbit)
{
	uint i;
	float2 *in_ptr = in;
        uint generator = 2047;
        uint pbrsbit, temp;

	for(i = 0; i < get_global_size(0); i++)
	{
		/* pilot pbrs generator */
        	pbrsbit = generator >> 10;
        	temp = ((generator >> 10)&1)^((generator >> 8)&1);
        	generator <<= 1;
        	generator |= (temp & 1);
        	generator &= 2047;

		/* map pilots and data symbols */
		switch(pilots(i))
		{
			case 0:	/* data */
				*(out+i) = *in_ptr;
				in_ptr++;
			break;
			case 1:	/* tpspilot */
					*(out+i) = (float2)((1 - 2 * pbrsbit) * tpsbit, 0);
			break;
			case 2:	/* continualpilot */
					*(out+i) = (float2)((1 - 2 * pbrsbit) * 4.0 / 3.0 , 0);
			break;
			case 3:	/* scatteredpilot */
					*(out+i) = (float2)((1 - 2 * pbrsbit) * 4.0 / 3.0 , 0);
			break;
		}
	}
}


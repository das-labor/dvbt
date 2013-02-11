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
  inner interleaver
 interleave modulation * 127 bits at once
 */
__kernel void run_ii_A( __global const uint *in, __global uint *out, const int mod)
{
	 local int row[6][127];
	 int i= get_global_id(0);
	 int j,k;

	 int shiftoffset[7][6] = {{0,0,0,0,0,0},{0,0,0,0,0,0},{0,63,0,0,0,0},{0,0,0,0,0,0},{0,63,105,42,0,0},{0,0,0,0,0,0},{0,63,105,42,21,84}};

	 /* load bits from global memory */
	 for(k=0;k<mod;k++){
		for(j=0;j<127;j++)
			row[k][j] = in[mod*i*127+j+127*k];
         }
	 /* interleave by inserting */
	 for(k=0;k<mod;k++){
		 for(j=0;j<127;j++)
			 out[mod*i*127+j+127*k] = row[k][(j+shiftoffset[mod][k])%126];
         }
}

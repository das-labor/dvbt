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
	
__kernel void run_A( __global const uint *in, __global float2 *out, const uint md)
{
   uint j;
   float2 tmp;

    switch(md)
    {
      case 2:
        /* signal constellation mapping */
	j = get_global_id(0) * 2;
	tmp.x = 1.0f - 2.0f * in[j];
	tmp.y = 1.0f - 2.0f * in[j+1];
	out[get_global_id(0)] = tmp;
        break;
      case 4:
	/* signal constellation mapping */
	j = get_global_id(0) * 4;
	tmp.x = 3.0f - in[j+2] * 2.0f;
	tmp.y = 3.0f - in[j+3] * 2.0f;
	tmp.x *= 1.0f - in[j+0] * 2.0f;
	tmp.y *= 1.0f - in[j+1] * 2.0f;
	out[get_global_id(0)] = tmp;
        break;
      case 6:
	/* signal constellation mapping */
	j = get_global_id(0) * 6;
	tmp.x = 3.0f - in[j+4] * 2.0f;
	tmp.y = 3.0f - in[j+5] * 2.0f;
	tmp.x *= 1.0f - in[j+2] * 2.0f;
	tmp.y *= 1.0f - in[j+3] * 2.0f;
	tmp.x += 4.0f;
	tmp.y += 4.0f;
	tmp.x *= 1.0f - in[j+0] * 2.0f;
	tmp.y *= 1.0f - in[j+1] * 2.0f;
	out[get_global_id(0)] = tmp;
        break;
    }
}
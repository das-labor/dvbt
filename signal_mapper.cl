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

#ifndef CONFIG_USE_DOUBLE
#define CONFIG_USE_DOUBLE 0
#endif

#if CONFIG_USE_DOUBLE

#if defined(cl_khr_fp64)  // Khronos extension available?
#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#elif defined(cl_amd_fp64)  // AMD extension available?
#pragma OPENCL EXTENSION cl_amd_fp64 : enable
#endif

/* double */
typedef double real_t;
typedef double2 real2_t;
#define FFT_PI 3.14159265358979323846
#define FFT_SQRT_1_2 0.70710678118654752440

#else

/* float */
typedef float real_t;
typedef float2 real2_t;
#define FFT_PI       3.14159265359f
#define FFT_SQRT_1_2 0.707106781187f

#endif

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
	out[get_global_id(0)] = tmp / sqrt( 2.0f );
        break;
      case 4:
	/* signal constellation mapping */
	j = get_global_id(0) * 4;
	tmp.x = 3.0f - in[j+2] * 2.0f;
	tmp.y = 3.0f - in[j+3] * 2.0f;
	tmp.x *= 1.0f - in[j+0] * 2.0f;
	tmp.y *= 1.0f - in[j+1] * 2.0f;
	out[get_global_id(0)] = tmp / sqrt( 10.0f );
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
	out[get_global_id(0)] = tmp / sqrt( 42.0f );
        break;
    }
}

__kernel void run_qpsk( __global const uint *in, __global real2_t *out)
{
   uint j;
   float x0,x1;
   
   x0 = (float)in[get_global_id(0) * 2];
   x1 = (float)in[get_global_id(0) * 2 + 1];
   
   /* signal constellation mapping */
   out[get_global_id(0)] = (real2_t)( (1.0f - 2.0f * x0) / sqrt( 2.0f ) , (1.0f - 2.0f * x1) / sqrt( 2.0f ) ) ;

}


__kernel void run_qam16( __global const uint *in, __global real2_t *out)
{
   uint j;
   float x0,x1,x2,x3;
   real2_t tmp;
   
   x0 = (float)in[get_global_id(0) * 4];
   x1 = (float)in[get_global_id(0) * 4 + 1];
   x2 = (float)in[get_global_id(0) * 4 + 2];
   x3 = (float)in[get_global_id(0) * 4 + 3];   
   
   /* signal constellation mapping */
   tmp.x = 3.0f - x2 * 2.0f;
   tmp.y = 3.0f - x3 * 2.0f;
   tmp.x *= 1.0f - x0 * 2.0f;
   tmp.y *= 1.0f - x1 * 2.0f;
   
   tmp /= sqrt( 10.0f );
   
   out[get_global_id(0)] = tmp;

}

__kernel void run_qam64( __global const uint *in, __global real2_t *out)
{
   uint j;
   float x0,x1,x2,x3,x4,x5;
   real2_t tmp;
   
   x0 = (float)in[get_global_id(0) * 6];
   x1 = (float)in[get_global_id(0) * 6 + 1];
   x2 = (float)in[get_global_id(0) * 6 + 2];
   x3 = (float)in[get_global_id(0) * 6 + 3];   
   x4 = (float)in[get_global_id(0) * 6 + 4];
   x5 = (float)in[get_global_id(0) * 6 + 5];  
   
   /* signal constellation mapping */
   tmp.x = 3.0f -x4 * 2.0f;
   tmp.y = 3.0f - x5 * 2.0f;
   tmp.x *= 1.0f - x2 * 2.0f;
   tmp.y *= 1.0f - x3 * 2.0f;
   tmp.x += 4.0f;
   tmp.y += 4.0f;
   tmp.x *= 1.0f - x0 * 2.0f;
   tmp.y *= 1.0f -x1 * 2.0f;
   
   tmp /= sqrt( 42.0f );
   
   out[get_global_id(0)] = tmp;

}
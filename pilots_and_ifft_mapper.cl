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

/*
 input real2_t
 output real2_t
 make sure that tpsbit=1 if (symbol == 0)
 *pilots contain information what to do on any carrier
 */
#if 0
__kernel void run( __global const real2_t *in,  __global real2_t *out, const uint *pilots, const uint tpsbit)
{
	uint i;
	real2_t *in_ptr = in;
        uint generator = 2047;   
        uint pbrsbit, temp;

	for(i = 0; i < get_global_size(0); i++)
	{
		/* pilot pbrs generator, reinit every ofdm symbol */
        	pbrsbit = generator >> 10;
        	temp = ((generator >> 10)&1)^((generator >> 8)&1); /* polynomial x^11 + x^2 + 1 */
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
					*(out+i) = (real2_t)((1 - 2 * pbrsbit) * tpsbit, 0);
			break;
			case 2:	/* continualpilot */
					*(out+i) = (real2_t)((1 - 2 * pbrsbit) * 4.0 / 3.0 , 0);
			break;
			case 3:	/* scatteredpilot */
					*(out+i) = (real2_t)((1 - 2 * pbrsbit) * 4.0 / 3.0 , 0);
			break;
		}
	}
}
#endif

__kernel void fill_continual( __global const real2_t *in,  __global real2_t *out,  __global const uint *pilots,  __global const uint *pbrsbits)
{
	uint carrier = pilots[get_global_id(0)];
	
	/* continualpilot */
	
	out[carrier] = (real2_t)((1 - 2 * pbrsbits[carrier]) * 4.0 / 3.0 , 0);
}

__kernel void fill_tps( __global const real2_t *in,  __global real2_t *out,  __global const uint *pilots,  __global const uint *pbrsbits, const uint tpsbit)
{
	uint carrier = pilots[get_global_id(0)];

	/* tpspilot */
	
	out[carrier] = (real2_t)((1 - 2 * pbrsbits[carrier]) * tpsbit, 0);
}

__kernel void fill_scattered( __global const real2_t *in,  __global real2_t *out,  __global const uint *pilots,  __global const uint *pbrsbits)
{
	uint carrier = pilots[get_global_id(0)];

	/* scatteredpilot */
	
	out[carrier] = (real2_t)((1 - 2 * pbrsbits[carrier]) * 4.0 / 3.0 , 0);
}

__kernel void fill_data( __global const real2_t *in,  __global real2_t *out,  __global const uint *pilots)
{
	uint carrier = pilots[get_global_id(0)];
	
	out[carrier] = in[get_global_id(0)];
}

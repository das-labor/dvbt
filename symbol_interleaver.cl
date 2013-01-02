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
  symbol interleaver: permutation function is inverted for odd odfm symbols
 2k mode:
  input/output is 1512 float2
  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )
  shift_reg has size 10 bits
  R -> R' mapping
  R'i bit positions 9 8 7 6 5 4 3 2 1 0
  Ri  bit positions 0 7 5 1 8 2 6 9 3 4
 */
__kernel void run2K_A( __global uint2 *in, __global uint2 *out, const uint frame)
{

#define ACTIVE_CARRIERS 1512
#define OFDM_MODE 2048

uint i,rs,r,rs_xor,q;
rs_xor = r = rs = q = 0;
for(i=0;i<OFDM_MODE;i++){
if(i<2)
	rs=0;
if(i==2)
	rs=1;
if(i>2){
	rs_xor = (rs & 1) ^ ((rs>>3) & 1);
	rs >>= 1;
	rs |= rs_xor<<9;
}
r  = (rs & 0x00000001)<<4;
r |= (rs & 0x00000002)<<2;
r |= (rs & 0x00000004)<<7;
r |= (rs & 0x00000008)<<3;
r |= (rs & 0x00000010)>>2;
r |= (rs & 0x00000020)<<3;
r |= (rs & 0x00000040)>>5;
r |= (rs & 0x00000080)>>2;
r |= (rs & 0x00000100)>>1;
r |= (rs & 0x00000200)>>9;
r |= (i  & 0x00000001)<<10;
if(r < ACTIVE_CARRIERS){
	if(frame & 1)
out[r+get_global_id(0)*ACTIVE_CARRIERS]=in[q+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	else
out[q+get_global_id(0)*ACTIVE_CARRIERS]=in[r+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	q+=1;
}
}

#undef ACTIVE_CARRIERS
#undef OFDM_MODE

}

/*
  8k mode:
  input/output is 6048 float2
  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )
  shift_reg has size 12 bits
  R -> R' mapping
  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0
  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7

 each workgroup processes work_dim*2 items
 */
__kernel void run8K_A( __global uint2 *in, __global uint2 *out, const uint frame)
{

#define ACTIVE_CARRIERS 6048
#define OFDM_MODE 8192

uint i,rs,r,rs_xor,q;
rs_xor = r = rs = q = 0;
for(i=0;i<OFDM_MODE;i++){
if(i<2)
	rs=0;
if(i==2)
	rs=1;
if(i>2){
	rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1);
	rs >>= 1;
	rs |= rs_xor<<11;
}
r = (rs & 0x00000001)<<7;
r |= (rs & 0x00000002)<<0;
r |= (rs & 0x00000004)<<2;
r |= (rs & 0x00000008)>>1;
r |= (rs & 0x00000010)<<5;
r |= (rs & 0x00000020)<<1;
r |= (rs & 0x00000040)<<2;
r |= (rs & 0x00000080)<<3;
r |= (rs & 0x00000100)>>8;
r |= (rs & 0x00000200)>>6;
r |= (rs & 0x00000400)<<1;
r |= (rs & 0x00000800)>>6;
r |= (i & 0x00000001)<<12;
if(r < ACTIVE_CARRIERS){
	if(frame & 1)
out[r+get_global_id(0)*ACTIVE_CARRIERS]=in[q+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	else
out[q+get_global_id(0)*ACTIVE_CARRIERS]=in[r+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	q+=1;
}
}

#undef ACTIVE_CARRIERS
#undef OFDM_MODE

}

/*
  symbol interleaver: permutation function is inverted for odd odfm symbols
 2k mode:
  input/output is 1512 float2
  R' = shift_reg = (XOR(shift_reg:0,shift_reg:3)<< 9 | shift_reg>>1 )
  shift_reg has size 10 bits
  R -> R' mapping
  R'i bit positions 9 8 7 6 5 4 3 2 1 0
  Ri  bit positions 0 7 5 1 8 2 6 9 3 4
 */
__kernel void run2K_B( __global uint2 *in, __global uint2 *out, const uint frame)
{

#define ACTIVE_CARRIERS 1512
#define OFDM_MODE 2048

uint i,rs,r,rs_xor,q;
event_t eventA[ACTIVE_CARRIERS];
local uint2 buffer[ACTIVE_CARRIERS];
for(i=0;i<ACTIVE_CARRIERS;i++)
	eventA[i] = async_work_group_copy(&buffer[i],in+get_global_id(0)*ACTIVE_CARRIERS+i,sizeof(uint2),0);
rs_xor = r = rs = q = 0;
for(i=0;i<OFDM_MODE;i++){
if(i<2)
	rs=0;
if(i==2)
	rs=1;
if(i>2){
	rs_xor = (rs & 1) ^ ((rs>>3) & 1);
	rs >>= 1;
	rs |= rs_xor<<9;
}
r  = (rs & 0x00000001)<<4;
r |= (rs & 0x00000002)<<2;
r |= (rs & 0x00000004)<<7;
r |= (rs & 0x00000008)<<3;
r |= (rs & 0x00000010)>>2;
r |= (rs & 0x00000020)<<3;
r |= (rs & 0x00000040)>>5;
r |= (rs & 0x00000080)>>2;
r |= (rs & 0x00000100)>>1;
r |= (rs & 0x00000200)>>9;
r |= (i  & 0x00000001)<<10;
if(r < ACTIVE_CARRIERS){
	if(frame & 1){
	wait_group_events(1,&eventA[q]);
	eventA[q] = async_work_group_copy(out +r+get_global_id(0)*ACTIVE_CARRIERS,&buffer[q],sizeof(uint2),0);
	}
	else
{
	wait_group_events(1,&eventA[r]);
	eventA[r] = async_work_group_copy(out+q+get_global_id(0)*ACTIVE_CARRIERS,&buffer[r],sizeof(uint2),0);
}
	q+=1;
}
}
wait_group_events(ACTIVE_CARRIERS,&eventA[0]);

#undef ACTIVE_CARRIERS
#undef OFDM_MODE

}

/*
  8k mode:
  input/output is 6048 float2
  R' = shift_reg = (XOR(shift_reg:0,shift_reg:1,shift_reg:4,shift_reg:6)<< 11 | shift_reg>>1 )
  shift_reg has size 12 bits
  R -> R' mapping
  R'i bit positions 11 10 9 8 7 6 5 4 3 2 1 0
  Ri  bit positions 5 11 3 0 10 8 6 9 2 4 1 7

 each workgroup processes work_dim*2 items
 */
__kernel void run8K_B( __global uint2 *in, __global uint2 *out, const uint frame)
{

#define ACTIVE_CARRIERS 6048
#define OFDM_MODE 8192

uint i,rs,r,rs_xor,q;
rs_xor = r = rs = q = 0;
for(i=0;i<OFDM_MODE;i++){
if(i<2)
	rs=0;
if(i==2)
	rs=1;
if(i>2){
	rs_xor = (rs & 1) ^ ((rs>>1) & 1) ^ ((rs>>4) & 1) ^ ((rs>>6) & 1);
	rs >>= 1;
	rs |= rs_xor<<11;
}
r = (rs & 0x00000001)<<7;
r |= (rs & 0x00000002)<<0;
r |= (rs & 0x00000004)<<2;
r |= (rs & 0x00000008)>>1;
r |= (rs & 0x00000010)<<5;
r |= (rs & 0x00000020)<<1;
r |= (rs & 0x00000040)<<2;
r |= (rs & 0x00000080)<<3;
r |= (rs & 0x00000100)>>8;
r |= (rs & 0x00000200)>>6;
r |= (rs & 0x00000400)<<1;
r |= (rs & 0x00000800)>>6;
r |= (i & 0x00000001)<<12;
if(r < ACTIVE_CARRIERS){
	if(frame & 1)
out[r+get_global_id(0)*ACTIVE_CARRIERS]=in[q+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	else
out[q+get_global_id(0)*ACTIVE_CARRIERS]=in[r+get_global_id(0)*ACTIVE_CARRIERS]; /* buffer_out[r]=buffer_in[q]; */
	q+=1;
}
}

#undef ACTIVE_CARRIERS
#undef OFDM_MODE

}

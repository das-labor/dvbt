/* input mpeg-ts packets, each packet has 188bytes
   numpy converts to input data stream to this format
   where uint is 0xAaBbCcDd
   0: Dd
   1: Cc
   2: Bb
   3: Aa
   ...

the output has reverse alignment
where uint is 0xAaBbCcDd
   0: Aa
   1: Bb
   2: Cc
   3: Dd
   ...

This is needed for inner-coding, as the uint can be shifted bitwise left

*/

__kernel void run( __global uint *in, __global uint *out)
{
   uint workingreg[64];
   ulong rs_shift_reg[4];
   int b,o,p,i;
   int pbrs_index = get_global_id(0);
   int dimN = pbrs_index*47;
/*
   const uint sync_byte[8] = {0x000000b8,0x00000047,0x00000047,0x00000047,0x00000047,0x00000047,0x00000047,0x00000047};

   for(i=0;i<47;i++)
      workingreg[dimN+i] = in[dimN+i] ^ pbrs[dimN+i];

      workingreg[0] = ((workingreg[0]&0xffffff00)|sync_byte[pbrs_index]);
*/
   switch(pbrs_index)
   {
      case 0:
         workingreg[0] = in[dimN+0] ^ 0x3408f600;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x000000b8);
         workingreg[1] = in[dimN+1] ^ 0x93a3b830;
         workingreg[2] = in[dimN+2] ^ 0x73b768c9;
         workingreg[3] = in[dimN+3] ^ 0xf5aa29b3;
         workingreg[4] = in[dimN+4] ^ 0x88043cfe;
         workingreg[5] = in[dimN+5] ^ 0xa15a301b;
         workingreg[6] = in[dimN+6] ^ 0x9ac0c4df;
         workingreg[7] = in[dimN+7] ^ 0xc20b5f83;
         workingreg[8] = in[dimN+8] ^ 0x2b938c38;
         workingreg[9] = in[dimN+9] ^ 0x1b7efb6a;
         workingreg[10] = in[dimN+10] ^ 0xdc195a04;
         workingreg[11] = in[dimN+11] ^ 0xb4fac954;
         workingreg[12] = in[dimN+12] ^ 0x9141b81f;
         workingreg[13] = in[dimN+13] ^ 0x5e1f6585;
         workingreg[14] = in[dimN+14] ^ 0x9d88c543;
         workingreg[15] = in[dimN+15] ^ 0xa7ab4e33;
         workingreg[16] = in[dimN+16] ^ 0xe014d0f9;
         workingreg[17] = in[dimN+17] ^ 0x861d417a;
         workingreg[18] = in[dimN+18] ^ 0x7dae154d;
         workingreg[19] = in[dimN+19] ^ 0x295e0ce5;
         workingreg[20] = in[dimN+20] ^ 0x3b9af4c4;
         workingreg[21] = in[dimN+21] ^ 0x58cb9b5c;
         workingreg[22] = in[dimN+22] ^ 0xe998d3bb;
         workingreg[23] = in[dimN+23] ^ 0x30ed7752;
         workingreg[24] = in[dimN+24] ^ 0xc767a16e;
         workingreg[25] = in[dimN+25] ^ 0x68e39350;
         workingreg[26] = in[dimN+26] ^ 0x25bb714b;
         workingreg[27] = in[dimN+27] ^ 0xcf5edd9a;
         workingreg[28] = in[dimN+28] ^ 0xc397a0c6;
         workingreg[29] = in[dimN+29] ^ 0x3a238b70;
         workingreg[30] = in[dimN+30] ^ 0x47bf9eca;
         workingreg[31] = in[dimN+31] ^ 0x66099183;
         workingreg[32] = in[dimN+32] ^ 0xfbb35437;
         workingreg[33] = in[dimN+33] ^ 0x54f019a8;
         workingreg[34] = in[dimN+34] ^ 0x12c4f821;
         workingreg[35] = in[dimN+35] ^ 0x63516f98;
         workingreg[36] = in[dimN+36] ^ 0xb15348e7;
         workingreg[37] = in[dimN+37] ^ 0xd975a4e9;
         workingreg[38] = in[dimN+38] ^ 0xf78ad63c;
         workingreg[39] = in[dimN+39] ^ 0xaf84323e;
         workingreg[40] = in[dimN+40] ^ 0x4d58e21b;
         workingreg[41] = in[dimN+41] ^ 0xeae5acd1;
         workingreg[42] = in[dimN+42] ^ 0x0cc97d5c;
         workingreg[43] = in[dimN+43] ^ 0xf9b42bb6;
         workingreg[44] = in[dimN+44] ^ 0x7d9c15ba;
         workingreg[45] = in[dimN+45] ^ 0x21b60f49;
         workingreg[46] = in[dimN+46] ^ 0x9dbac5b4;
         break;
      case 1:
         workingreg[0] = in[dimN+0] ^ 0xaf434d00;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0x4634e189;
         workingreg[2] = in[dimN+2] ^ 0x719597b9;
         workingreg[3] = in[dimN+3] ^ 0xd202277f;
         workingreg[4] = in[dimN+4] ^ 0x6826ec0e;
         workingreg[5] = in[dimN+5] ^ 0x2eff72d5;
         workingreg[6] = in[dimN+6] ^ 0x580ee402;
         workingreg[7] = in[dimN+7] ^ 0xe2dcd025;
         workingreg[8] = in[dimN+8] ^ 0xa7bd4eca;
         workingreg[9] = in[dimN+9] ^ 0xe62cd18d;
         workingreg[10] = in[dimN+10] ^ 0xf57d56ea;
         workingreg[11] = in[dimN+11] ^ 0x84283e0c;
         workingreg[12] = in[dimN+12] ^ 0x5c2a1af3;
         workingreg[13] = in[dimN+13] ^ 0xbc0ccafd;
         workingreg[14] = in[dimN+14] ^ 0x32f9882b;
         workingreg[15] = in[dimN+15] ^ 0xe977ac16;
         workingreg[16] = in[dimN+16] ^ 0x37a17630;
         workingreg[17] = in[dimN+17] ^ 0xa397b0c6;
         workingreg[18] = in[dimN+18] ^ 0xba24cb71;
         workingreg[19] = in[dimN+19] ^ 0x46d99edb;
         workingreg[20] = in[dimN+20] ^ 0x76f196d7;
         workingreg[21] = in[dimN+21] ^ 0xbad23427;
         workingreg[22] = in[dimN+22] ^ 0x45619eef;
         workingreg[23] = in[dimN+23] ^ 0x41919f47;
         workingreg[24] = in[dimN+24] ^ 0x13518767;
         workingreg[25] = in[dimN+25] ^ 0x715568e6;
         workingreg[26] = in[dimN+26] ^ 0xd80224ff;
         workingreg[27] = in[dimN+27] ^ 0xe026d00e;
         workingreg[28] = in[dimN+28] ^ 0x8ef542d6;
         workingreg[29] = in[dimN+29] ^ 0xdb8e243d;
         workingreg[30] = in[dimN+30] ^ 0xded6da26;
         workingreg[31] = in[dimN+31] ^ 0x9436c6f6;
         workingreg[32] = in[dimN+32] ^ 0x19b37bb7;
         workingreg[33] = in[dimN+33] ^ 0xfcfd55aa;
         workingreg[34] = in[dimN+34] ^ 0x3028080c;
         workingreg[35] = in[dimN+35] ^ 0xcc23a2f0;
         workingreg[36] = in[dimN+36] ^ 0xffb3aac8;
         workingreg[37] = in[dimN+37] ^ 0x04f001a8;
         workingreg[38] = in[dimN+38] ^ 0x52c01820;
         workingreg[39] = in[dimN+39] ^ 0x6204ef81;
         workingreg[40] = in[dimN+40] ^ 0xa9574c19;
         workingreg[41] = in[dimN+41] ^ 0x3824f4f1;
         workingreg[42] = in[dimN+42] ^ 0x6ed392d8;
         workingreg[43] = in[dimN+43] ^ 0x557b66eb;
         workingreg[44] = in[dimN+44] ^ 0x0558fe1b;
         workingreg[45] = in[dimN+45] ^ 0x4ae01cd0;
         workingreg[46] = in[dimN+46] ^ 0x8d85bd41;
         break;
      case 2:
         workingreg[0] = in[dimN+0] ^ 0xe54e2e00;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0xccd55da6;
         workingreg[2] = in[dimN+2] ^ 0xfc0baafc;
         workingreg[3] = in[dimN+3] ^ 0x33900838;
         workingreg[4] = in[dimN+4] ^ 0xfb43ab60;
         workingreg[5] = in[dimN+5] ^ 0x56301988;
         workingreg[6] = in[dimN+6] ^ 0x30c4f7a1;
         workingreg[7] = in[dimN+7] ^ 0xcb53a398;
         workingreg[8] = in[dimN+8] ^ 0x9173b8e8;
         workingreg[9] = in[dimN+9] ^ 0x56f76629;
         workingreg[10] = in[dimN+10] ^ 0x3ba8f433;
         workingreg[11] = in[dimN+11] ^ 0x502398f0;
         workingreg[12] = in[dimN+12] ^ 0x4fb8e2cb;
         workingreg[13] = in[dimN+13] ^ 0xc765a191;
         workingreg[14] = in[dimN+14] ^ 0x68cb935c;
         workingreg[15] = in[dimN+15] ^ 0x299b73bb;
         workingreg[16] = in[dimN+16] ^ 0x30def75a;
         workingreg[17] = in[dimN+17] ^ 0xcf9ba2c4;
         workingreg[18] = in[dimN+18] ^ 0xc8d3a358;
         workingreg[19] = in[dimN+19] ^ 0xad73b2e8;
         workingreg[20] = in[dimN+20] ^ 0x66f4ee29;
         workingreg[21] = in[dimN+21] ^ 0xfb975439;
         workingreg[22] = in[dimN+22] ^ 0x5a201b70;
         workingreg[23] = in[dimN+23] ^ 0xc784dec1;
         workingreg[24] = in[dimN+24] ^ 0x6d5f921a;
         workingreg[25] = in[dimN+25] ^ 0x6b8b6cc3;
         workingreg[26] = in[dimN+26] ^ 0x1f9b7a3b;
         workingreg[27] = in[dimN+27] ^ 0x88dd435a;
         workingreg[28] = in[dimN+28] ^ 0xafae32cd;
         workingreg[29] = in[dimN+29] ^ 0x4150e0e7;
         workingreg[30] = in[dimN+30] ^ 0x194584e1;
         workingreg[31] = in[dimN+31] ^ 0xff45559e;
         workingreg[32] = in[dimN+32] ^ 0x0748019c;
         workingreg[33] = in[dimN+33] ^ 0x65a011b0;
         workingreg[34] = in[dimN+34] ^ 0xcb875cc1;
         workingreg[35] = in[dimN+35] ^ 0x9d63ba10;
         workingreg[36] = in[dimN+36] ^ 0xa1b74f49;
         workingreg[37] = in[dimN+37] ^ 0x9da4c5b1;
         workingreg[38] = in[dimN+38] ^ 0xaadb4cdb;
         workingreg[39] = in[dimN+39] ^ 0x06d4fed9;
         workingreg[40] = in[dimN+40] ^ 0x741016f8;
         workingreg[41] = in[dimN+41] ^ 0x97463961;
         workingreg[42] = in[dimN+42] ^ 0x27737197;
         workingreg[43] = in[dimN+43] ^ 0xeefed22a;
         workingreg[44] = in[dimN+44] ^ 0x58156406;
         workingreg[45] = in[dimN+45] ^ 0xe600d17f;
         workingreg[46] = in[dimN+46] ^ 0xf80d5402;
         break;
      case 3:
         workingreg[0] = in[dimN+0] ^ 0x62e81000;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0xae274d71;
         workingreg[2] = in[dimN+2] ^ 0x56e4e6d1;
         workingreg[3] = in[dimN+3] ^ 0x3cd4f559;
         workingreg[4] = in[dimN+4] ^ 0x3c138af8;
         workingreg[5] = in[dimN+5] ^ 0x377f896a;
         workingreg[6] = in[dimN+6] ^ 0xac0fb202;
         workingreg[7] = in[dimN+7] ^ 0x72c4e821;
         workingreg[8] = in[dimN+8] ^ 0xe3562f99;
         workingreg[9] = in[dimN+9] ^ 0xb03548f6;
         workingreg[10] = in[dimN+10] ^ 0xc98da3bd;
         workingreg[11] = in[dimN+11] ^ 0xb6ebb62c;
         workingreg[12] = in[dimN+12] ^ 0xbe15b579;
         workingreg[13] = in[dimN+13] ^ 0x1e0d857d;
         workingreg[14] = in[dimN+14] ^ 0x9ae5442e;
         workingreg[15] = in[dimN+15] ^ 0xcccf5d5d;
         workingreg[16] = in[dimN+16] ^ 0xf8c3aba0;
         workingreg[17] = in[dimN+17] ^ 0x6a301388;
         workingreg[18] = in[dimN+18] ^ 0x00c77fa1;
         workingreg[19] = in[dimN+19] ^ 0x0b6c0392;
         workingreg[20] = in[dimN+20] ^ 0x9b703b68;
         workingreg[21] = in[dimN+21] ^ 0xdecb5a23;
         workingreg[22] = in[dimN+22] ^ 0x9192c7b8;
         workingreg[23] = in[dimN+23] ^ 0x5363676f;
         workingreg[24] = in[dimN+24] ^ 0x79b8eb4b;
         workingreg[25] = in[dimN+25] ^ 0x7f661591;
         workingreg[26] = in[dimN+26] ^ 0x08fe0355;
         workingreg[27] = in[dimN+27] ^ 0xa0183004;
         workingreg[28] = in[dimN+28] ^ 0x84e8c153;
         workingreg[29] = in[dimN+29] ^ 0x562a1973;
         workingreg[30] = in[dimN+30] ^ 0x340cf6fd;
         workingreg[31] = in[dimN+31] ^ 0x92f3b828;
         workingreg[32] = in[dimN+32] ^ 0x6af76c29;
         workingreg[33] = in[dimN+33] ^ 0x0bab7c33;
         workingreg[34] = in[dimN+34] ^ 0x901c38fa;
         workingreg[35] = in[dimN+35] ^ 0x45bb614b;
         workingreg[36] = in[dimN+36] ^ 0x4f599d9b;
         workingreg[37] = in[dimN+37] ^ 0xc2f1a0d7;
         workingreg[38] = in[dimN+38] ^ 0x2adb8c24;
         workingreg[39] = in[dimN+39] ^ 0x06defeda;
         workingreg[40] = in[dimN+40] ^ 0x779816c4;
         workingreg[41] = in[dimN+41] ^ 0xa8e63351;
         workingreg[42] = in[dimN+42] ^ 0x24f0f157;
         workingreg[43] = in[dimN+43] ^ 0xd2c2d820;
         workingreg[44] = in[dimN+44] ^ 0x6226ef8e;
         workingreg[45] = in[dimN+45] ^ 0xa6ff4ed5;
         workingreg[46] = in[dimN+46] ^ 0xf804d401;
         break;
      case 4:
         workingreg[0] = in[dimN+0] ^ 0x615c1000;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0x9bb744c9;
         workingreg[2] = in[dimN+2] ^ 0xd5a759b1;
         workingreg[3] = in[dimN+3] ^ 0x0ae2fcd0;
         workingreg[4] = in[dimN+4] ^ 0x8da83d4c;
         workingreg[5] = in[dimN+5] ^ 0xe82a2cf3;
         workingreg[6] = in[dimN+6] ^ 0x2c0572fe;
         workingreg[7] = in[dimN+7] ^ 0x7146e81e;
         workingreg[8] = in[dimN+8] ^ 0xdf7e2595;
         workingreg[9] = in[dimN+9] ^ 0x8c16c206;
         workingreg[10] = in[dimN+10] ^ 0xf6322977;
         workingreg[11] = in[dimN+11] ^ 0xb0e437ae;
         workingreg[12] = in[dimN+12] ^ 0xc4d9a15b;
         workingreg[13] = in[dimN+13] ^ 0x5efb9ad4;
         workingreg[14] = in[dimN+14] ^ 0x9958c41b;
         workingreg[15] = in[dimN+15] ^ 0xfaeb54d3;
         workingreg[16] = in[dimN+16] ^ 0x4e101d78;
         workingreg[17] = in[dimN+17] ^ 0xdf45a561;
         workingreg[18] = in[dimN+18] ^ 0x874ac19c;
         workingreg[19] = in[dimN+19] ^ 0x658211bf;
         workingreg[20] = in[dimN+20] ^ 0xc42f5e0d;
         workingreg[21] = in[dimN+21] ^ 0x5d439ae0;
         workingreg[22] = in[dimN+22] ^ 0xae38cd8b;
         workingreg[23] = in[dimN+23] ^ 0x5368e793;
         workingreg[24] = in[dimN+24] ^ 0x7a24eb71;
         workingreg[25] = in[dimN+25] ^ 0x46d61ed9;
         workingreg[26] = in[dimN+26] ^ 0x743d96f5;
         workingreg[27] = in[dimN+27] ^ 0x9a223b8f;
         workingreg[28] = in[dimN+28] ^ 0xc7a35ecf;
         workingreg[29] = in[dimN+29] ^ 0x63b390c8;
         workingreg[30] = in[dimN+30] ^ 0xb4fb49ab;
         workingreg[31] = in[dimN+31] ^ 0x9155b819;
         workingreg[32] = in[dimN+32] ^ 0x580f64fd;
         workingreg[33] = in[dimN+33] ^ 0xe2c8d023;
         workingreg[34] = in[dimN+34] ^ 0xa1ad4fb2;
         workingreg[35] = in[dimN+35] ^ 0x996cc4ed;
         workingreg[36] = in[dimN+36] ^ 0xf37b576b;
         workingreg[37] = in[dimN+37] ^ 0xfd502a18;
         workingreg[38] = in[dimN+38] ^ 0x294c0ce2;
         workingreg[39] = in[dimN+39] ^ 0x3cf2f5a8;
         workingreg[40] = in[dimN+40] ^ 0x32eb882c;
         workingreg[41] = in[dimN+41] ^ 0xee1fad7a;
         workingreg[42] = in[dimN+42] ^ 0x5d816540;
         workingreg[43] = in[dimN+43] ^ 0xa410ce07;
         workingreg[44] = in[dimN+44] ^ 0xd748d963;
         workingreg[45] = in[dimN+45] ^ 0x25aef1b2;
         workingreg[46] = in[dimN+46] ^ 0xc95adce4;
         break;
      case 5:
         workingreg[0] = in[dimN+0] ^ 0xbac7b400;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0x43659f91;
         workingreg[2] = in[dimN+2] ^ 0x38c18b5f;
         workingreg[3] = in[dimN+3] ^ 0x6a179386;
         workingreg[4] = in[dimN+4] ^ 0x0e2b7d73;
         workingreg[5] = in[dimN+5] ^ 0xd41c26fa;
         workingreg[6] = in[dimN+6] ^ 0x15bef94a;
         workingreg[7] = in[dimN+7] ^ 0x0e197d84;
         workingreg[8] = in[dimN+8] ^ 0xdcf42556;
         workingreg[9] = in[dimN+9] ^ 0xb39ec83a;
         workingreg[10] = in[dimN+10] ^ 0xf991ab47;
         workingreg[11] = in[dimN+11] ^ 0x73581764;
         workingreg[12] = in[dimN+12] ^ 0xf2e628d1;
         workingreg[13] = in[dimN+13] ^ 0xecf42d56;
         workingreg[14] = in[dimN+14] ^ 0x739d683a;
         workingreg[15] = in[dimN+15] ^ 0xf9a22b4f;
         workingreg[16] = in[dimN+16] ^ 0x7ba414ce;
         workingreg[17] = in[dimN+17] ^ 0x52d618d9;
         workingreg[18] = in[dimN+18] ^ 0x643ceef5;
         workingreg[19] = in[dimN+19] ^ 0xda375b89;
         workingreg[20] = in[dimN+20] ^ 0xc1a2dfb0;
         workingreg[21] = in[dimN+21] ^ 0x1ba784ce;
         workingreg[22] = in[dimN+22] ^ 0xd2ed58d2;
         workingreg[23] = in[dimN+23] ^ 0x6f6aed6c;
         workingreg[24] = in[dimN+24] ^ 0x4a0f637d;
         workingreg[25] = in[dimN+25] ^ 0x8ac9bc23;
         workingreg[26] = in[dimN+26] ^ 0x81be3fb5;
         workingreg[27] = in[dimN+27] ^ 0x1e120587;
         workingreg[28] = in[dimN+28] ^ 0x9f69456c;
         workingreg[29] = in[dimN+29] ^ 0x8a3f4375;
         workingreg[30] = in[dimN+30] ^ 0x82063f81;
         workingreg[31] = in[dimN+31] ^ 0x29720c17;
         workingreg[32] = in[dimN+32] ^ 0x36eaf62c;
         workingreg[33] = in[dimN+33] ^ 0xbe0bb57c;
         workingreg[34] = in[dimN+34] ^ 0x1b958439;
         workingreg[35] = in[dimN+35] ^ 0xda055b7e;
         workingreg[36] = in[dimN+36] ^ 0xc94adc1c;
         workingreg[37] = in[dimN+37] ^ 0xbd87b5be;
         workingreg[38] = in[dimN+38] ^ 0x25658e11;
         workingreg[39] = in[dimN+39] ^ 0xc0c6df5e;
         workingreg[40] = in[dimN+40] ^ 0x0b778396;
         workingreg[41] = in[dimN+41] ^ 0x9fac3a32;
         workingreg[42] = in[dimN+42] ^ 0x817b40eb;
         workingreg[43] = in[dimN+43] ^ 0x15560619;
         workingreg[44] = in[dimN+44] ^ 0x08397cf4;
         workingreg[45] = in[dimN+45] ^ 0xab743396;
         workingreg[46] = in[dimN+46] ^ 0x1f98fa3b;
         break;
      case 6:
         workingreg[0] = in[dimN+0] ^ 0x88e14300;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0xa59e3145;
         workingreg[2] = in[dimN+2] ^ 0xc190df47;
         workingreg[3] = in[dimN+3] ^ 0x134f8762;
         workingreg[4] = in[dimN+4] ^ 0x74cd69a2;
         workingreg[5] = in[dimN+5] ^ 0x98e23baf;
         workingreg[6] = in[dimN+6] ^ 0xe5a3514f;
         workingreg[7] = in[dimN+7] ^ 0xcbb15cc8;
         workingreg[8] = in[dimN+8] ^ 0x94dbb9a4;
         workingreg[9] = in[dimN+9] ^ 0x1ed77ad9;
         workingreg[10] = in[dimN+10] ^ 0x942d46f2;
         workingreg[11] = in[dimN+11] ^ 0x1d6f7aed;
         workingreg[12] = in[dimN+12] ^ 0xa34d4f62;
         workingreg[13] = in[dimN+13] ^ 0xb4ecc9ad;
         workingreg[14] = in[dimN+14] ^ 0x9779b96b;
         workingreg[15] = in[dimN+15] ^ 0x2d7f7215;
         workingreg[16] = in[dimN+16] ^ 0x640eee02;
         workingreg[17] = in[dimN+17] ^ 0xd2df5825;
         workingreg[18] = in[dimN+18] ^ 0x6782eec0;
         workingreg[19] = in[dimN+19] ^ 0xec2f520d;
         workingreg[20] = in[dimN+20] ^ 0x7d416ae0;
         workingreg[21] = in[dimN+21] ^ 0x2e120d87;
         workingreg[22] = in[dimN+22] ^ 0x5f6ae56c;
         workingreg[23] = in[dimN+23] ^ 0x8a0cc37d;
         workingreg[24] = in[dimN+24] ^ 0x8afa3c2b;
         workingreg[25] = in[dimN+25] ^ 0x89423c1f;
         workingreg[26] = in[dimN+26] ^ 0xbe22358f;
         workingreg[27] = in[dimN+27] ^ 0x17a186cf;
         workingreg[28] = in[dimN+28] ^ 0x239570c6;
         workingreg[29] = in[dimN+29] ^ 0xba06cb7e;
         workingreg[30] = in[dimN+30] ^ 0x49719c17;
         workingreg[31] = in[dimN+31] ^ 0xb6d1b627;
         workingreg[32] = in[dimN+32] ^ 0xb55db6e5;
         workingreg[33] = in[dimN+33] ^ 0x8badbccd;
         workingreg[34] = in[dimN+34] ^ 0x916e38ed;
         workingreg[35] = in[dimN+35] ^ 0x53536767;
         workingreg[36] = in[dimN+36] ^ 0x7178e8eb;
         workingreg[37] = in[dimN+37] ^ 0xd5662611;
         workingreg[38] = in[dimN+38] ^ 0x00f6ff56;
         workingreg[39] = in[dimN+39] ^ 0x03b80034;
         workingreg[40] = in[dimN+40] ^ 0x37600990;
         workingreg[41] = in[dimN+41] ^ 0xa983b340;
         workingreg[42] = in[dimN+42] ^ 0x3434f609;
         workingreg[43] = in[dimN+43] ^ 0x9993bbb8;
         workingreg[44] = in[dimN+44] ^ 0xf3775769;
         workingreg[45] = in[dimN+45] ^ 0xffa02a30;
         workingreg[46] = in[dimN+46] ^ 0x038c00c2;
         break;
      case 7:
         workingreg[0] = in[dimN+0] ^ 0x3ef00a00;
         workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
         workingreg[1] = in[dimN+1] ^ 0x1ac38420;
         workingreg[2] = in[dimN+2] ^ 0xc23d5f8a;
         workingreg[3] = in[dimN+3] ^ 0x222b8f8c;
         workingreg[4] = in[dimN+4] ^ 0xa41ecefa;
         workingreg[5] = in[dimN+5] ^ 0xd590d947;
         workingreg[6] = in[dimN+6] ^ 0x034eff62;
         workingreg[7] = in[dimN+7] ^ 0x34d809a4;
         workingreg[8] = in[dimN+8] ^ 0x9ee3bad0;
         workingreg[9] = in[dimN+9] ^ 0x9db74549;
         workingreg[10] = in[dimN+10] ^ 0xada74db1;
         workingreg[11] = in[dimN+11] ^ 0x6ae4ecd1;
         workingreg[12] = in[dimN+12] ^ 0x0cd77d59;
         workingreg[13] = in[dimN+13] ^ 0xfc2c2af2;
         workingreg[14] = in[dimN+14] ^ 0x3d7c0aea;
         workingreg[15] = in[dimN+15] ^ 0x24338e08;
         workingreg[16] = in[dimN+16] ^ 0xd8fedbaa;
         workingreg[17] = in[dimN+17] ^ 0xe016d006;
         workingreg[18] = in[dimN+18] ^ 0x86354176;
         workingreg[19] = in[dimN+19] ^ 0x718e17bd;
         workingreg[20] = in[dimN+20] ^ 0xd6de2625;
         workingreg[21] = in[dimN+21] ^ 0x3796f6c6;
         workingreg[22] = in[dimN+22] ^ 0xaa3bb374;
         workingreg[23] = in[dimN+23] ^ 0x0354ff99;
         workingreg[24] = in[dimN+24] ^ 0x301008f8;
         workingreg[25] = in[dimN+25] ^ 0xc743a160;
         workingreg[26] = in[dimN+26] ^ 0x66339188;
         workingreg[27] = in[dimN+27] ^ 0xf0fb57ab;
         workingreg[28] = in[dimN+28] ^ 0xc1502018;
         workingreg[29] = in[dimN+29] ^ 0x194f84e2;
         workingreg[30] = in[dimN+30] ^ 0xfccd55a2;
         workingreg[31] = in[dimN+31] ^ 0x38e80bac;
         workingreg[32] = in[dimN+32] ^ 0x66239170;
         workingreg[33] = in[dimN+33] ^ 0xf7bb56cb;
         workingreg[34] = in[dimN+34] ^ 0xa7503198;
         workingreg[35] = in[dimN+35] ^ 0xe148d0e3;
         workingreg[36] = in[dimN+36] ^ 0x9dad45b2;
         workingreg[37] = in[dimN+37] ^ 0xa96f4ced;
         workingreg[38] = in[dimN+38] ^ 0x3344f761;
         workingreg[39] = in[dimN+39] ^ 0xf753a998;
         workingreg[40] = in[dimN+40] ^ 0xa17030e8;
         workingreg[41] = in[dimN+41] ^ 0x96c8c623;
         workingreg[42] = in[dimN+42] ^ 0x31ab77b3;
         workingreg[43] = in[dimN+43] ^ 0xd81fa4fa;
         workingreg[44] = in[dimN+44] ^ 0xe582d140;
         workingreg[45] = in[dimN+45] ^ 0xc4255e0e;
         workingreg[46] = in[dimN+46] ^ 0x5ecb9adc;
         break;

   }


   /* fill with zeros */
   workingreg[47] = 0;
   workingreg[48] = 0;
   workingreg[49] = 0;
   workingreg[50] = 0;
   workingreg[51] = 0;
   workingreg[52] = 0;
   workingreg[53] = 0;
   workingreg[54] = 0;
   workingreg[55] = 0;
   workingreg[56] = 0;
   workingreg[57] = 0;
   workingreg[58] = 0;
   workingreg[59] = 0;
   workingreg[60] = 0;
   workingreg[61] = 0;
   workingreg[62] = 0;
   workingreg[63] = 0;

   rs_shift_reg[2] = 0;
   rs_shift_reg[3] = 0;

   o = 0;
   /* do a rs(255,236,8) reed-solomon encoding */
   for(i = 0; i < 255; i++)
   {
      b = (workingreg[i / 4]>>((i%4)*8))&0x000000ff;
      b ^= o;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0xa34129e56232243bULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0x5b8252d7c4644876ULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0xb619a4b395c890ecULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0x7132557b378d3dc5ULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0xe264aaf66e077a97ULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0xd9c849f1dc0ef433ULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0xaf8d92ffa51cf566ULL);
      b >>= 1;
      rs_shift_reg[0] ^= ((ulong)(b & 0x01)* 0x430739e35738f7ccULL);
      b >>= 1;
      b = (workingreg[i / 4]>>((i%4)*8))&0x000000ff;
      b ^= o;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0x3b0d68bd44d11e08ULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0x761ad06788bf3c10ULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0xec34bdce0d637820ULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0xc56867811ac6f040ULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0x97d0ce1f3491fd80ULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0x33bd813e683fe71dULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0x66671f7cd07ed33aULL);
      b >>= 1;
      rs_shift_reg[1] ^= ((ulong)(b & 0x01)* 0xccce3ef8bdfcbb74ULL);
      b >>= 1;
      o = (rs_shift_reg[3]&0xff00000000000000ULL)>>56;
      p = (rs_shift_reg[2]&0xff00000000000000ULL)>>56;
      rs_shift_reg[2] <<= 8;
      rs_shift_reg[3] <<= 8;
      rs_shift_reg[3] |= p;
      rs_shift_reg[2] ^= rs_shift_reg[0];
      rs_shift_reg[3] ^= rs_shift_reg[1];
   }

   /* convert back to uint32 */
   workingreg[47] = (rs_shift_reg[2]&0x00000000ffffffffULL);
   workingreg[48] = (rs_shift_reg[2]&0xffffffff00000000ULL)>>32;
   workingreg[49] = (rs_shift_reg[3]&0x00000000ffffffffULL);
   workingreg[50] = (rs_shift_reg[3]&0xffffffff00000000ULL)>>32;

   dimN = pbrs_index*51;
   out[dimN+0] = (((workingreg[0]>>0)&0x000000ff)<<24)|(((workingreg[2]>>24)&0x000000ff)<<16)|(((workingreg[0]>>8)&0x000000ff)<<8)|((workingreg[5]>>16)&0x000000ff);
   out[dimN+1] = (((workingreg[3]>>0)&0x000000ff)<<24)|(((workingreg[0]>>16)&0x000000ff)<<16)|(((workingreg[8]>>8)&0x000000ff)<<8)|((workingreg[5]>>24)&0x000000ff);
   out[dimN+2] = (((workingreg[3]>>8)&0x000000ff)<<24)|(((workingreg[0]>>24)&0x000000ff)<<16)|(((workingreg[11]>>0)&0x000000ff)<<8)|((workingreg[8]>>16)&0x000000ff);
   out[dimN+3] = (((workingreg[6]>>0)&0x000000ff)<<24)|(((workingreg[3]>>16)&0x000000ff)<<16)|(((workingreg[1]>>0)&0x000000ff)<<8)|((workingreg[13]>>24)&0x000000ff);
   out[dimN+4] = (((workingreg[11]>>8)&0x000000ff)<<24)|(((workingreg[8]>>24)&0x000000ff)<<16)|(((workingreg[6]>>8)&0x000000ff)<<8)|((workingreg[3]>>24)&0x000000ff);
   out[dimN+5] = (((workingreg[1]>>8)&0x000000ff)<<24)|(((workingreg[16]>>16)&0x000000ff)<<16)|(((workingreg[14]>>0)&0x000000ff)<<8)|((workingreg[11]>>16)&0x000000ff);
   out[dimN+6] = (((workingreg[9]>>0)&0x000000ff)<<24)|(((workingreg[6]>>16)&0x000000ff)<<16)|(((workingreg[4]>>0)&0x000000ff)<<8)|((workingreg[1]>>16)&0x000000ff);
   out[dimN+7] = (((workingreg[19]>>8)&0x000000ff)<<24)|(((workingreg[16]>>24)&0x000000ff)<<16)|(((workingreg[14]>>8)&0x000000ff)<<8)|((workingreg[11]>>24)&0x000000ff);
   out[dimN+8] = (((workingreg[9]>>8)&0x000000ff)<<24)|(((workingreg[6]>>24)&0x000000ff)<<16)|(((workingreg[4]>>8)&0x000000ff)<<8)|((workingreg[1]>>24)&0x000000ff);
   out[dimN+9] = (((workingreg[22]>>0)&0x000000ff)<<24)|(((workingreg[19]>>16)&0x000000ff)<<16)|(((workingreg[17]>>0)&0x000000ff)<<8)|((workingreg[14]>>16)&0x000000ff);
   out[dimN+10] = (((workingreg[12]>>0)&0x000000ff)<<24)|(((workingreg[9]>>16)&0x000000ff)<<16)|(((workingreg[7]>>0)&0x000000ff)<<8)|((workingreg[4]>>16)&0x000000ff);
   out[dimN+11] = (((workingreg[2]>>0)&0x000000ff)<<24)|(((workingreg[24]>>24)&0x000000ff)<<16)|(((workingreg[22]>>8)&0x000000ff)<<8)|((workingreg[19]>>24)&0x000000ff);
   out[dimN+12] = (((workingreg[17]>>8)&0x000000ff)<<24)|(((workingreg[14]>>24)&0x000000ff)<<16)|(((workingreg[12]>>8)&0x000000ff)<<8)|((workingreg[9]>>24)&0x000000ff);
   out[dimN+13] = (((workingreg[7]>>8)&0x000000ff)<<24)|(((workingreg[4]>>24)&0x000000ff)<<16)|(((workingreg[2]>>8)&0x000000ff)<<8)|((workingreg[27]>>16)&0x000000ff);
   out[dimN+14] = (((workingreg[25]>>0)&0x000000ff)<<24)|(((workingreg[22]>>16)&0x000000ff)<<16)|(((workingreg[20]>>0)&0x000000ff)<<8)|((workingreg[17]>>16)&0x000000ff);
   out[dimN+15] = (((workingreg[15]>>0)&0x000000ff)<<24)|(((workingreg[12]>>16)&0x000000ff)<<16)|(((workingreg[10]>>0)&0x000000ff)<<8)|((workingreg[7]>>16)&0x000000ff);
   out[dimN+16] = (((workingreg[5]>>0)&0x000000ff)<<24)|(((workingreg[2]>>16)&0x000000ff)<<16)|(((workingreg[30]>>8)&0x000000ff)<<8)|((workingreg[27]>>24)&0x000000ff);
   out[dimN+17] = (((workingreg[25]>>8)&0x000000ff)<<24)|(((workingreg[22]>>24)&0x000000ff)<<16)|(((workingreg[20]>>8)&0x000000ff)<<8)|((workingreg[17]>>24)&0x000000ff);
   out[dimN+18] = (((workingreg[15]>>8)&0x000000ff)<<24)|(((workingreg[12]>>24)&0x000000ff)<<16)|(((workingreg[10]>>8)&0x000000ff)<<8)|((workingreg[7]>>24)&0x000000ff);
   out[dimN+19] = (((workingreg[5]>>8)&0x000000ff)<<24)|(((workingreg[33]>>0)&0x000000ff)<<16)|(((workingreg[30]>>16)&0x000000ff)<<8)|((workingreg[28]>>0)&0x000000ff);
   out[dimN+20] = (((workingreg[25]>>16)&0x000000ff)<<24)|(((workingreg[23]>>0)&0x000000ff)<<16)|(((workingreg[20]>>16)&0x000000ff)<<8)|((workingreg[18]>>0)&0x000000ff);
   out[dimN+21] = (((workingreg[15]>>16)&0x000000ff)<<24)|(((workingreg[13]>>0)&0x000000ff)<<16)|(((workingreg[10]>>16)&0x000000ff)<<8)|((workingreg[8]>>0)&0x000000ff);
   out[dimN+22] = (((workingreg[35]>>24)&0x000000ff)<<24)|(((workingreg[33]>>8)&0x000000ff)<<16)|(((workingreg[30]>>24)&0x000000ff)<<8)|((workingreg[28]>>8)&0x000000ff);
   out[dimN+23] = (((workingreg[25]>>24)&0x000000ff)<<24)|(((workingreg[23]>>8)&0x000000ff)<<16)|(((workingreg[20]>>24)&0x000000ff)<<8)|((workingreg[18]>>8)&0x000000ff);
   out[dimN+24] = (((workingreg[15]>>24)&0x000000ff)<<24)|(((workingreg[13]>>8)&0x000000ff)<<16)|(((workingreg[10]>>24)&0x000000ff)<<8)|((workingreg[38]>>16)&0x000000ff);
   out[dimN+25] = (((workingreg[36]>>0)&0x000000ff)<<24)|(((workingreg[33]>>16)&0x000000ff)<<16)|(((workingreg[31]>>0)&0x000000ff)<<8)|((workingreg[28]>>16)&0x000000ff);
   out[dimN+26] = (((workingreg[26]>>0)&0x000000ff)<<24)|(((workingreg[23]>>16)&0x000000ff)<<16)|(((workingreg[21]>>0)&0x000000ff)<<8)|((workingreg[18]>>16)&0x000000ff);
   out[dimN+27] = (((workingreg[16]>>0)&0x000000ff)<<24)|(((workingreg[13]>>16)&0x000000ff)<<16)|(((workingreg[41]>>8)&0x000000ff)<<8)|((workingreg[38]>>24)&0x000000ff);
   out[dimN+28] = (((workingreg[36]>>8)&0x000000ff)<<24)|(((workingreg[33]>>24)&0x000000ff)<<16)|(((workingreg[31]>>8)&0x000000ff)<<8)|((workingreg[28]>>24)&0x000000ff);
   out[dimN+29] = (((workingreg[26]>>8)&0x000000ff)<<24)|(((workingreg[23]>>24)&0x000000ff)<<16)|(((workingreg[21]>>8)&0x000000ff)<<8)|((workingreg[18]>>24)&0x000000ff);
   out[dimN+30] = (((workingreg[16]>>8)&0x000000ff)<<24)|(((workingreg[44]>>0)&0x000000ff)<<16)|(((workingreg[41]>>16)&0x000000ff)<<8)|((workingreg[39]>>0)&0x000000ff);
   out[dimN+31] = (((workingreg[36]>>16)&0x000000ff)<<24)|(((workingreg[34]>>0)&0x000000ff)<<16)|(((workingreg[31]>>16)&0x000000ff)<<8)|((workingreg[29]>>0)&0x000000ff);
   out[dimN+32] = (((workingreg[26]>>16)&0x000000ff)<<24)|(((workingreg[24]>>0)&0x000000ff)<<16)|(((workingreg[21]>>16)&0x000000ff)<<8)|((workingreg[19]>>0)&0x000000ff);
   out[dimN+33] = (((workingreg[46]>>24)&0x000000ff)<<24)|(((workingreg[44]>>8)&0x000000ff)<<16)|(((workingreg[41]>>24)&0x000000ff)<<8)|((workingreg[39]>>8)&0x000000ff);
   out[dimN+34] = (((workingreg[36]>>24)&0x000000ff)<<24)|(((workingreg[34]>>8)&0x000000ff)<<16)|(((workingreg[31]>>24)&0x000000ff)<<8)|((workingreg[29]>>8)&0x000000ff);
   out[dimN+35] = (((workingreg[26]>>24)&0x000000ff)<<24)|(((workingreg[24]>>8)&0x000000ff)<<16)|(((workingreg[21]>>24)&0x000000ff)<<8)|((workingreg[49]>>16)&0x000000ff);
   out[dimN+36] = (((workingreg[47]>>0)&0x000000ff)<<24)|(((workingreg[44]>>16)&0x000000ff)<<16)|(((workingreg[42]>>0)&0x000000ff)<<8)|((workingreg[39]>>16)&0x000000ff);
   out[dimN+37] = (((workingreg[37]>>0)&0x000000ff)<<24)|(((workingreg[34]>>16)&0x000000ff)<<16)|(((workingreg[32]>>0)&0x000000ff)<<8)|((workingreg[29]>>16)&0x000000ff);
   out[dimN+38] = (((workingreg[27]>>0)&0x000000ff)<<24)|(((workingreg[24]>>16)&0x000000ff)<<16)|(((workingreg[49]>>24)&0x000000ff)<<8)|((workingreg[47]>>8)&0x000000ff);
   out[dimN+39] = (((workingreg[44]>>24)&0x000000ff)<<24)|(((workingreg[42]>>8)&0x000000ff)<<16)|(((workingreg[39]>>24)&0x000000ff)<<8)|((workingreg[37]>>8)&0x000000ff);
   out[dimN+40] = (((workingreg[34]>>24)&0x000000ff)<<24)|(((workingreg[32]>>8)&0x000000ff)<<16)|(((workingreg[29]>>24)&0x000000ff)<<8)|((workingreg[27]>>8)&0x000000ff);
   out[dimN+41] = (((workingreg[50]>>0)&0x000000ff)<<24)|(((workingreg[47]>>16)&0x000000ff)<<16)|(((workingreg[45]>>0)&0x000000ff)<<8)|((workingreg[42]>>16)&0x000000ff);
   out[dimN+42] = (((workingreg[40]>>0)&0x000000ff)<<24)|(((workingreg[37]>>16)&0x000000ff)<<16)|(((workingreg[35]>>0)&0x000000ff)<<8)|((workingreg[32]>>16)&0x000000ff);
   out[dimN+43] = (((workingreg[30]>>0)&0x000000ff)<<24)|(((workingreg[50]>>8)&0x000000ff)<<16)|(((workingreg[47]>>24)&0x000000ff)<<8)|((workingreg[45]>>8)&0x000000ff);
   out[dimN+44] = (((workingreg[42]>>24)&0x000000ff)<<24)|(((workingreg[40]>>8)&0x000000ff)<<16)|(((workingreg[37]>>24)&0x000000ff)<<8)|((workingreg[35]>>8)&0x000000ff);
   out[dimN+45] = (((workingreg[32]>>24)&0x000000ff)<<24)|(((workingreg[50]>>16)&0x000000ff)<<16)|(((workingreg[48]>>0)&0x000000ff)<<8)|((workingreg[45]>>16)&0x000000ff);
   out[dimN+46] = (((workingreg[43]>>0)&0x000000ff)<<24)|(((workingreg[40]>>16)&0x000000ff)<<16)|(((workingreg[38]>>0)&0x000000ff)<<8)|((workingreg[35]>>16)&0x000000ff);
   out[dimN+47] = (((workingreg[50]>>24)&0x000000ff)<<24)|(((workingreg[48]>>8)&0x000000ff)<<16)|(((workingreg[45]>>24)&0x000000ff)<<8)|((workingreg[43]>>8)&0x000000ff);
   out[dimN+48] = (((workingreg[40]>>24)&0x000000ff)<<24)|(((workingreg[38]>>8)&0x000000ff)<<16)|(((workingreg[48]>>16)&0x000000ff)<<8)|((workingreg[46]>>0)&0x000000ff);
   out[dimN+49] = (((workingreg[43]>>16)&0x000000ff)<<24)|(((workingreg[41]>>0)&0x000000ff)<<16)|(((workingreg[48]>>24)&0x000000ff)<<8)|((workingreg[46]>>8)&0x000000ff);
   out[dimN+50] = (((workingreg[43]>>24)&0x000000ff)<<24)|(((workingreg[49]>>0)&0x000000ff)<<16)|(((workingreg[46]>>16)&0x000000ff)<<8)|((workingreg[49]>>8)&0x000000ff);



}


/* Appendix
 x^8 + x^4 + x^3 + x + 1 == 0x1d
uint8_t gmul(uint8_t a, uint8_t b) {
        uint8_t p = 0;
        uint8_t counter;
        uint8_t hi_bit_set;
        for (counter = 0; counter < 8; counter++) {
                if (b & 1) 
                        p ^= a;
                hi_bit_set = (a & 0x80);
                a <<= 1;
                if (hi_bit_set) 
                        a ^= 0x1b; 
                b >>= 1;
        }
        return p;
}

*/

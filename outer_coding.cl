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
   pbrs encoder, reed-solomon encoder
   threadcount: T multiple of 8 (8,16,24,..) 
   data in    : 188 bytes * T (47 uints) little endian
   data out    : 204 bytes * T (51 uints) little endian
*/

__kernel void run_pbrs_rs( __global uint *in, __global uint *out)
{

uint workingreg[51];
int pbrs_index = get_global_id(0);
int dimN = pbrs_index*47;

uint16 wreg;
uint tmp;
uint shadow;
int i;

/*
   pbrs encoder:
    this function takes a uint ( 4-bytes) and xors it with the output of the pbrs
    the first byte of one packet is a sync byte ( 0xb8 or 0x47 ) and is not xor'd
    the pbrs is reinitialized on every 8th packet (after 1504 bytes)
*/

switch(pbrs_index%8)
{
	case 0:
		workingreg[0] = in[dimN+0] ^ 0x08F60300;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x000000b8);
		workingreg[1] = in[dimN+1] ^ 0xA3B83034;
		workingreg[2] = in[dimN+2] ^ 0xB768C993;
		workingreg[3] = in[dimN+3] ^ 0xAA29B373;
		workingreg[4] = in[dimN+4] ^ 0x043CFEF5;
		workingreg[5] = in[dimN+5] ^ 0x5A301B88;
		workingreg[6] = in[dimN+6] ^ 0xC0C4DFA1;
		workingreg[7] = in[dimN+7] ^ 0x0B5F839A;
		workingreg[8] = in[dimN+8] ^ 0x938C38C2;
		workingreg[9] = in[dimN+9] ^ 0x7EFB6A2B;
		workingreg[10] = in[dimN+10] ^ 0x195A041B;
		workingreg[11] = in[dimN+11] ^ 0xFAC954DC;
		workingreg[12] = in[dimN+12] ^ 0x41B81FB4;
		workingreg[13] = in[dimN+13] ^ 0x1F658591;
		workingreg[14] = in[dimN+14] ^ 0x88C5435E;
		workingreg[15] = in[dimN+15] ^ 0xAB4E339D;
		workingreg[16] = in[dimN+16] ^ 0x14D0F9A7;
		workingreg[17] = in[dimN+17] ^ 0x1D417AE0;
		workingreg[18] = in[dimN+18] ^ 0xAE154D86;
		workingreg[19] = in[dimN+19] ^ 0x5E0CE57D;
		workingreg[20] = in[dimN+20] ^ 0x9AF4C429;
		workingreg[21] = in[dimN+21] ^ 0xCB9B5C3B;
		workingreg[22] = in[dimN+22] ^ 0x98D3BB58;
		workingreg[23] = in[dimN+23] ^ 0xED7752E9;
		workingreg[24] = in[dimN+24] ^ 0x67A16E30;
		workingreg[25] = in[dimN+25] ^ 0xE39350C7;
		workingreg[26] = in[dimN+26] ^ 0xBB714B68;
		workingreg[27] = in[dimN+27] ^ 0x5EDD9A25;
		workingreg[28] = in[dimN+28] ^ 0x97A0C6CF;
		workingreg[29] = in[dimN+29] ^ 0x238B70C3;
		workingreg[30] = in[dimN+30] ^ 0xBF9ECA3A;
		workingreg[31] = in[dimN+31] ^ 0x09918347;
		workingreg[32] = in[dimN+32] ^ 0xB3543766;
		workingreg[33] = in[dimN+33] ^ 0xF019A8FB;
		workingreg[34] = in[dimN+34] ^ 0xC4F82154;
		workingreg[35] = in[dimN+35] ^ 0x516F9812;
		workingreg[36] = in[dimN+36] ^ 0x5348E763;
		workingreg[37] = in[dimN+37] ^ 0x75A4E9B1;
		workingreg[38] = in[dimN+38] ^ 0x8AD63CD9;
		workingreg[39] = in[dimN+39] ^ 0x84323EF7;
		workingreg[40] = in[dimN+40] ^ 0x58E21BAF;
		workingreg[41] = in[dimN+41] ^ 0xE5ACD14D;
		workingreg[42] = in[dimN+42] ^ 0xC97D5CEA;
		workingreg[43] = in[dimN+43] ^ 0xB42BB60C;
		workingreg[44] = in[dimN+44] ^ 0x9C15BAF9;
		workingreg[45] = in[dimN+45] ^ 0xB60F497D;
		workingreg[46] = in[dimN+46] ^ 0xBAC5B421;
		break;
	case 1:
		workingreg[0] = in[dimN+0] ^ 0x434D9F00;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0x34E189AF;
		workingreg[2] = in[dimN+2] ^ 0x9597B946;
		workingreg[3] = in[dimN+3] ^ 0x02277F71;
		workingreg[4] = in[dimN+4] ^ 0x26EC0ED2;
		workingreg[5] = in[dimN+5] ^ 0xFF72D568;
		workingreg[6] = in[dimN+6] ^ 0x0EE4022E;
		workingreg[7] = in[dimN+7] ^ 0xDCD02558;
		workingreg[8] = in[dimN+8] ^ 0xBD4ECAE2;
		workingreg[9] = in[dimN+9] ^ 0x2CD18DA7;
		workingreg[10] = in[dimN+10] ^ 0x7D56EAE6;
		workingreg[11] = in[dimN+11] ^ 0x283E0CF5;
		workingreg[12] = in[dimN+12] ^ 0x2A1AF384;
		workingreg[13] = in[dimN+13] ^ 0x0CCAFD5C;
		workingreg[14] = in[dimN+14] ^ 0xF9882BBC;
		workingreg[15] = in[dimN+15] ^ 0x77AC1632;
		workingreg[16] = in[dimN+16] ^ 0xA17630E9;
		workingreg[17] = in[dimN+17] ^ 0x97B0C637;
		workingreg[18] = in[dimN+18] ^ 0x24CB71A3;
		workingreg[19] = in[dimN+19] ^ 0xD99EDBBA;
		workingreg[20] = in[dimN+20] ^ 0xF196D746;
		workingreg[21] = in[dimN+21] ^ 0xD2342776;
		workingreg[22] = in[dimN+22] ^ 0x619EEFBA;
		workingreg[23] = in[dimN+23] ^ 0x919F4745;
		workingreg[24] = in[dimN+24] ^ 0x51876741;
		workingreg[25] = in[dimN+25] ^ 0x5568E613;
		workingreg[26] = in[dimN+26] ^ 0x0224FF71;
		workingreg[27] = in[dimN+27] ^ 0x26D00ED8;
		workingreg[28] = in[dimN+28] ^ 0xF542D6E0;
		workingreg[29] = in[dimN+29] ^ 0x8E243D8E;
		workingreg[30] = in[dimN+30] ^ 0xD6DA26DB;
		workingreg[31] = in[dimN+31] ^ 0x36C6F6DE;
		workingreg[32] = in[dimN+32] ^ 0xB37BB794;
		workingreg[33] = in[dimN+33] ^ 0xFD55AA19;
		workingreg[34] = in[dimN+34] ^ 0x28080CFC;
		workingreg[35] = in[dimN+35] ^ 0x23A2F030;
		workingreg[36] = in[dimN+36] ^ 0xB3AAC8CC;
		workingreg[37] = in[dimN+37] ^ 0xF001A8FF;
		workingreg[38] = in[dimN+38] ^ 0xC0182004;
		workingreg[39] = in[dimN+39] ^ 0x04EF8152;
		workingreg[40] = in[dimN+40] ^ 0x574C1962;
		workingreg[41] = in[dimN+41] ^ 0x24F4F1A9;
		workingreg[42] = in[dimN+42] ^ 0xD392D838;
		workingreg[43] = in[dimN+43] ^ 0x7B66EB6E;
		workingreg[44] = in[dimN+44] ^ 0x58FE1B55;
		workingreg[45] = in[dimN+45] ^ 0xE01CD005;
		workingreg[46] = in[dimN+46] ^ 0x85BD414A;
		break;
	case 2:
		workingreg[0] = in[dimN+0] ^ 0x4E2E1D00;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0xD55DA6E5;
		workingreg[2] = in[dimN+2] ^ 0x0BAAFCCC;
		workingreg[3] = in[dimN+3] ^ 0x900838FC;
		workingreg[4] = in[dimN+4] ^ 0x43AB6033;
		workingreg[5] = in[dimN+5] ^ 0x301988FB;
		workingreg[6] = in[dimN+6] ^ 0xC4F7A156;
		workingreg[7] = in[dimN+7] ^ 0x53A39830;
		workingreg[8] = in[dimN+8] ^ 0x73B8E8CB;
		workingreg[9] = in[dimN+9] ^ 0xF7662991;
		workingreg[10] = in[dimN+10] ^ 0xA8F43356;
		workingreg[11] = in[dimN+11] ^ 0x2398F03B;
		workingreg[12] = in[dimN+12] ^ 0xB8E2CB50;
		workingreg[13] = in[dimN+13] ^ 0x65A1914F;
		workingreg[14] = in[dimN+14] ^ 0xCB935CC7;
		workingreg[15] = in[dimN+15] ^ 0x9B73BB68;
		workingreg[16] = in[dimN+16] ^ 0xDEF75A29;
		workingreg[17] = in[dimN+17] ^ 0x9BA2C430;
		workingreg[18] = in[dimN+18] ^ 0xD3A358CF;
		workingreg[19] = in[dimN+19] ^ 0x73B2E8C8;
		workingreg[20] = in[dimN+20] ^ 0xF4EE29AD;
		workingreg[21] = in[dimN+21] ^ 0x97543966;
		workingreg[22] = in[dimN+22] ^ 0x201B70FB;
		workingreg[23] = in[dimN+23] ^ 0x84DEC15A;
		workingreg[24] = in[dimN+24] ^ 0x5F921AC7;
		workingreg[25] = in[dimN+25] ^ 0x8B6CC36D;
		workingreg[26] = in[dimN+26] ^ 0x9B7A3B6B;
		workingreg[27] = in[dimN+27] ^ 0xDD435A1F;
		workingreg[28] = in[dimN+28] ^ 0xAE32CD88;
		workingreg[29] = in[dimN+29] ^ 0x50E0E7AF;
		workingreg[30] = in[dimN+30] ^ 0x4584E141;
		workingreg[31] = in[dimN+31] ^ 0x45559E19;
		workingreg[32] = in[dimN+32] ^ 0x48019CFF;
		workingreg[33] = in[dimN+33] ^ 0xA011B007;
		workingreg[34] = in[dimN+34] ^ 0x875CC165;
		workingreg[35] = in[dimN+35] ^ 0x63BA10CB;
		workingreg[36] = in[dimN+36] ^ 0xB74F499D;
		workingreg[37] = in[dimN+37] ^ 0xA4C5B1A1;
		workingreg[38] = in[dimN+38] ^ 0xDB4CDB9D;
		workingreg[39] = in[dimN+39] ^ 0xD4FED9AA;
		workingreg[40] = in[dimN+40] ^ 0x1016F806;
		workingreg[41] = in[dimN+41] ^ 0x46396174;
		workingreg[42] = in[dimN+42] ^ 0x73719797;
		workingreg[43] = in[dimN+43] ^ 0xFED22A27;
		workingreg[44] = in[dimN+44] ^ 0x156406EE;
		workingreg[45] = in[dimN+45] ^ 0x00D17F58;
		workingreg[46] = in[dimN+46] ^ 0x0D5402E6;
		break;
	case 3:
		workingreg[0] = in[dimN+0] ^ 0xE8102C00;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0x274D7162;
		workingreg[2] = in[dimN+2] ^ 0xE4E6D1AE;
		workingreg[3] = in[dimN+3] ^ 0xD4F55956;
		workingreg[4] = in[dimN+4] ^ 0x138AF83C;
		workingreg[5] = in[dimN+5] ^ 0x7F896A3C;
		workingreg[6] = in[dimN+6] ^ 0x0FB20237;
		workingreg[7] = in[dimN+7] ^ 0xC4E821AC;
		workingreg[8] = in[dimN+8] ^ 0x562F9972;
		workingreg[9] = in[dimN+9] ^ 0x3548F6E3;
		workingreg[10] = in[dimN+10] ^ 0x8DA3BDB0;
		workingreg[11] = in[dimN+11] ^ 0xEBB62CC9;
		workingreg[12] = in[dimN+12] ^ 0x15B579B6;
		workingreg[13] = in[dimN+13] ^ 0x0D857DBE;
		workingreg[14] = in[dimN+14] ^ 0xE5442E1E;
		workingreg[15] = in[dimN+15] ^ 0xCF5D5D9A;
		workingreg[16] = in[dimN+16] ^ 0xC3ABA0CC;
		workingreg[17] = in[dimN+17] ^ 0x301388F8;
		workingreg[18] = in[dimN+18] ^ 0xC77FA16A;
		workingreg[19] = in[dimN+19] ^ 0x6C039200;
		workingreg[20] = in[dimN+20] ^ 0x703B680B;
		workingreg[21] = in[dimN+21] ^ 0xCB5A239B;
		workingreg[22] = in[dimN+22] ^ 0x92C7B8DE;
		workingreg[23] = in[dimN+23] ^ 0x63676F91;
		workingreg[24] = in[dimN+24] ^ 0xB8EB4B53;
		workingreg[25] = in[dimN+25] ^ 0x66159179;
		workingreg[26] = in[dimN+26] ^ 0xFE03557F;
		workingreg[27] = in[dimN+27] ^ 0x18300408;
		workingreg[28] = in[dimN+28] ^ 0xE8C153A0;
		workingreg[29] = in[dimN+29] ^ 0x2A197384;
		workingreg[30] = in[dimN+30] ^ 0x0CF6FD56;
		workingreg[31] = in[dimN+31] ^ 0xF3B82834;
		workingreg[32] = in[dimN+32] ^ 0xF76C2992;
		workingreg[33] = in[dimN+33] ^ 0xAB7C336A;
		workingreg[34] = in[dimN+34] ^ 0x1C38FA0B;
		workingreg[35] = in[dimN+35] ^ 0xBB614B90;
		workingreg[36] = in[dimN+36] ^ 0x599D9B45;
		workingreg[37] = in[dimN+37] ^ 0xF1A0D74F;
		workingreg[38] = in[dimN+38] ^ 0xDB8C24C2;
		workingreg[39] = in[dimN+39] ^ 0xDEFEDA2A;
		workingreg[40] = in[dimN+40] ^ 0x9816C406;
		workingreg[41] = in[dimN+41] ^ 0xE6335177;
		workingreg[42] = in[dimN+42] ^ 0xF0F157A8;
		workingreg[43] = in[dimN+43] ^ 0xC2D82024;
		workingreg[44] = in[dimN+44] ^ 0x26EF8ED2;
		workingreg[45] = in[dimN+45] ^ 0xFF4ED562;
		workingreg[46] = in[dimN+46] ^ 0x04D401A6;
		break;
	case 4:
		workingreg[0] = in[dimN+0] ^ 0x5C101A00;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0xB744C961;
		workingreg[2] = in[dimN+2] ^ 0xA759B19B;
		workingreg[3] = in[dimN+3] ^ 0xE2FCD0D5;
		workingreg[4] = in[dimN+4] ^ 0xA83D4C0A;
		workingreg[5] = in[dimN+5] ^ 0x2A2CF38D;
		workingreg[6] = in[dimN+6] ^ 0x0572FEE8;
		workingreg[7] = in[dimN+7] ^ 0x46E81E2C;
		workingreg[8] = in[dimN+8] ^ 0x7E259571;
		workingreg[9] = in[dimN+9] ^ 0x16C206DF;
		workingreg[10] = in[dimN+10] ^ 0x3229778C;
		workingreg[11] = in[dimN+11] ^ 0xE437AEF6;
		workingreg[12] = in[dimN+12] ^ 0xD9A15BB0;
		workingreg[13] = in[dimN+13] ^ 0xFB9AD4C4;
		workingreg[14] = in[dimN+14] ^ 0x58C41B5E;
		workingreg[15] = in[dimN+15] ^ 0xEB54D399;
		workingreg[16] = in[dimN+16] ^ 0x101D78FA;
		workingreg[17] = in[dimN+17] ^ 0x45A5614E;
		workingreg[18] = in[dimN+18] ^ 0x4AC19CDF;
		workingreg[19] = in[dimN+19] ^ 0x8211BF87;
		workingreg[20] = in[dimN+20] ^ 0x2F5E0D65;
		workingreg[21] = in[dimN+21] ^ 0x439AE0C4;
		workingreg[22] = in[dimN+22] ^ 0x38CD8B5D;
		workingreg[23] = in[dimN+23] ^ 0x68E793AE;
		workingreg[24] = in[dimN+24] ^ 0x24EB7153;
		workingreg[25] = in[dimN+25] ^ 0xD61ED97A;
		workingreg[26] = in[dimN+26] ^ 0x3D96F546;
		workingreg[27] = in[dimN+27] ^ 0x223B8F74;
		workingreg[28] = in[dimN+28] ^ 0xA35ECF9A;
		workingreg[29] = in[dimN+29] ^ 0xB390C8C7;
		workingreg[30] = in[dimN+30] ^ 0xFB49AB63;
		workingreg[31] = in[dimN+31] ^ 0x55B819B4;
		workingreg[32] = in[dimN+32] ^ 0x0F64FD91;
		workingreg[33] = in[dimN+33] ^ 0xC8D02358;
		workingreg[34] = in[dimN+34] ^ 0xAD4FB2E2;
		workingreg[35] = in[dimN+35] ^ 0x6CC4EDA1;
		workingreg[36] = in[dimN+36] ^ 0x7B576B99;
		workingreg[37] = in[dimN+37] ^ 0x502A18F3;
		workingreg[38] = in[dimN+38] ^ 0x4C0CE2FD;
		workingreg[39] = in[dimN+39] ^ 0xF2F5A829;
		workingreg[40] = in[dimN+40] ^ 0xEB882C3C;
		workingreg[41] = in[dimN+41] ^ 0x1FAD7A32;
		workingreg[42] = in[dimN+42] ^ 0x816540EE;
		workingreg[43] = in[dimN+43] ^ 0x10CE075D;
		workingreg[44] = in[dimN+44] ^ 0x48D963A4;
		workingreg[45] = in[dimN+45] ^ 0xAEF1B2D7;
		workingreg[46] = in[dimN+46] ^ 0x5ADCE425;
		break;
	case 5:
		workingreg[0] = in[dimN+0] ^ 0xC7B4DE00;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0x659F91BA;
		workingreg[2] = in[dimN+2] ^ 0xC18B5F43;
		workingreg[3] = in[dimN+3] ^ 0x17938638;
		workingreg[4] = in[dimN+4] ^ 0x2B7D736A;
		workingreg[5] = in[dimN+5] ^ 0x1C26FA0E;
		workingreg[6] = in[dimN+6] ^ 0xBEF94AD4;
		workingreg[7] = in[dimN+7] ^ 0x197D8415;
		workingreg[8] = in[dimN+8] ^ 0xF425560E;
		workingreg[9] = in[dimN+9] ^ 0x9EC83ADC;
		workingreg[10] = in[dimN+10] ^ 0x91AB47B3;
		workingreg[11] = in[dimN+11] ^ 0x581764F9;
		workingreg[12] = in[dimN+12] ^ 0xE628D173;
		workingreg[13] = in[dimN+13] ^ 0xF42D56F2;
		workingreg[14] = in[dimN+14] ^ 0x9D683AEC;
		workingreg[15] = in[dimN+15] ^ 0xA22B4F73;
		workingreg[16] = in[dimN+16] ^ 0xA414CEF9;
		workingreg[17] = in[dimN+17] ^ 0xD618D97B;
		workingreg[18] = in[dimN+18] ^ 0x3CEEF552;
		workingreg[19] = in[dimN+19] ^ 0x375B8964;
		workingreg[20] = in[dimN+20] ^ 0xA2DFB0DA;
		workingreg[21] = in[dimN+21] ^ 0xA784CEC1;
		workingreg[22] = in[dimN+22] ^ 0xED58D21B;
		workingreg[23] = in[dimN+23] ^ 0x6AED6CD2;
		workingreg[24] = in[dimN+24] ^ 0x0F637D6F;
		workingreg[25] = in[dimN+25] ^ 0xC9BC234A;
		workingreg[26] = in[dimN+26] ^ 0xBE3FB58A;
		workingreg[27] = in[dimN+27] ^ 0x12058781;
		workingreg[28] = in[dimN+28] ^ 0x69456C1E;
		workingreg[29] = in[dimN+29] ^ 0x3F43759F;
		workingreg[30] = in[dimN+30] ^ 0x063F818A;
		workingreg[31] = in[dimN+31] ^ 0x720C1782;
		workingreg[32] = in[dimN+32] ^ 0xEAF62C29;
		workingreg[33] = in[dimN+33] ^ 0x0BB57C36;
		workingreg[34] = in[dimN+34] ^ 0x958439BE;
		workingreg[35] = in[dimN+35] ^ 0x055B7E1B;
		workingreg[36] = in[dimN+36] ^ 0x4ADC1CDA;
		workingreg[37] = in[dimN+37] ^ 0x87B5BEC9;
		workingreg[38] = in[dimN+38] ^ 0x658E11BD;
		workingreg[39] = in[dimN+39] ^ 0xC6DF5E25;
		workingreg[40] = in[dimN+40] ^ 0x778396C0;
		workingreg[41] = in[dimN+41] ^ 0xAC3A320B;
		workingreg[42] = in[dimN+42] ^ 0x7B40EB9F;
		workingreg[43] = in[dimN+43] ^ 0x56061981;
		workingreg[44] = in[dimN+44] ^ 0x397CF415;
		workingreg[45] = in[dimN+45] ^ 0x74339608;
		workingreg[46] = in[dimN+46] ^ 0x98FA3BAB;
		break;
	case 6:
		workingreg[0] = in[dimN+0] ^ 0xE1435000;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0x9E314588;
		workingreg[2] = in[dimN+2] ^ 0x90DF47A5;
		workingreg[3] = in[dimN+3] ^ 0x4F8762C1;
		workingreg[4] = in[dimN+4] ^ 0xCD69A213;
		workingreg[5] = in[dimN+5] ^ 0xE23BAF74;
		workingreg[6] = in[dimN+6] ^ 0xA3514F98;
		workingreg[7] = in[dimN+7] ^ 0xB15CC8E5;
		workingreg[8] = in[dimN+8] ^ 0xDBB9A4CB;
		workingreg[9] = in[dimN+9] ^ 0xD77AD994;
		workingreg[10] = in[dimN+10] ^ 0x2D46F21E;
		workingreg[11] = in[dimN+11] ^ 0x6F7AED94;
		workingreg[12] = in[dimN+12] ^ 0x4D4F621D;
		workingreg[13] = in[dimN+13] ^ 0xECC9ADA3;
		workingreg[14] = in[dimN+14] ^ 0x79B96BB4;
		workingreg[15] = in[dimN+15] ^ 0x7F721597;
		workingreg[16] = in[dimN+16] ^ 0x0EEE022D;
		workingreg[17] = in[dimN+17] ^ 0xDF582564;
		workingreg[18] = in[dimN+18] ^ 0x82EEC0D2;
		workingreg[19] = in[dimN+19] ^ 0x2F520D67;
		workingreg[20] = in[dimN+20] ^ 0x416AE0EC;
		workingreg[21] = in[dimN+21] ^ 0x120D877D;
		workingreg[22] = in[dimN+22] ^ 0x6AE56C2E;
		workingreg[23] = in[dimN+23] ^ 0x0CC37D5F;
		workingreg[24] = in[dimN+24] ^ 0xFA3C2B8A;
		workingreg[25] = in[dimN+25] ^ 0x423C1F8A;
		workingreg[26] = in[dimN+26] ^ 0x22358F89;
		workingreg[27] = in[dimN+27] ^ 0xA186CFBE;
		workingreg[28] = in[dimN+28] ^ 0x9570C617;
		workingreg[29] = in[dimN+29] ^ 0x06CB7E23;
		workingreg[30] = in[dimN+30] ^ 0x719C17BA;
		workingreg[31] = in[dimN+31] ^ 0xD1B62749;
		workingreg[32] = in[dimN+32] ^ 0x5DB6E5B6;
		workingreg[33] = in[dimN+33] ^ 0xADBCCDB5;
		workingreg[34] = in[dimN+34] ^ 0x6E38ED8B;
		workingreg[35] = in[dimN+35] ^ 0x53676791;
		workingreg[36] = in[dimN+36] ^ 0x78E8EB53;
		workingreg[37] = in[dimN+37] ^ 0x66261171;
		workingreg[38] = in[dimN+38] ^ 0xF6FF56D5;
		workingreg[39] = in[dimN+39] ^ 0xB8003400;
		workingreg[40] = in[dimN+40] ^ 0x60099003;
		workingreg[41] = in[dimN+41] ^ 0x83B34037;
		workingreg[42] = in[dimN+42] ^ 0x34F609A9;
		workingreg[43] = in[dimN+43] ^ 0x93BBB834;
		workingreg[44] = in[dimN+44] ^ 0x77576999;
		workingreg[45] = in[dimN+45] ^ 0xA02A30F3;
		workingreg[46] = in[dimN+46] ^ 0x8C00C2FF;
		break;
	case 7:
		workingreg[0] = in[dimN+0] ^ 0xF00A2800;
		workingreg[0] = ((workingreg[0]&0xffffff00)|0x00000047);
		workingreg[1] = in[dimN+1] ^ 0xC384203E;
		workingreg[2] = in[dimN+2] ^ 0x3D5F8A1A;
		workingreg[3] = in[dimN+3] ^ 0x2B8F8CC2;
		workingreg[4] = in[dimN+4] ^ 0x1ECEFA22;
		workingreg[5] = in[dimN+5] ^ 0x90D947A4;
		workingreg[6] = in[dimN+6] ^ 0x4EFF62D5;
		workingreg[7] = in[dimN+7] ^ 0xD809A403;
		workingreg[8] = in[dimN+8] ^ 0xE3BAD034;
		workingreg[9] = in[dimN+9] ^ 0xB745499E;
		workingreg[10] = in[dimN+10] ^ 0xA74DB19D;
		workingreg[11] = in[dimN+11] ^ 0xE4ECD1AD;
		workingreg[12] = in[dimN+12] ^ 0xD77D596A;
		workingreg[13] = in[dimN+13] ^ 0x2C2AF20C;
		workingreg[14] = in[dimN+14] ^ 0x7C0AEAFC;
		workingreg[15] = in[dimN+15] ^ 0x338E083D;
		workingreg[16] = in[dimN+16] ^ 0xFEDBAA24;
		workingreg[17] = in[dimN+17] ^ 0x16D006D8;
		workingreg[18] = in[dimN+18] ^ 0x354176E0;
		workingreg[19] = in[dimN+19] ^ 0x8E17BD86;
		workingreg[20] = in[dimN+20] ^ 0xDE262571;
		workingreg[21] = in[dimN+21] ^ 0x96F6C6D6;
		workingreg[22] = in[dimN+22] ^ 0x3BB37437;
		workingreg[23] = in[dimN+23] ^ 0x54FF99AA;
		workingreg[24] = in[dimN+24] ^ 0x1008F803;
		workingreg[25] = in[dimN+25] ^ 0x43A16030;
		workingreg[26] = in[dimN+26] ^ 0x339188C7;
		workingreg[27] = in[dimN+27] ^ 0xFB57AB66;
		workingreg[28] = in[dimN+28] ^ 0x502018F0;
		workingreg[29] = in[dimN+29] ^ 0x4F84E2C1;
		workingreg[30] = in[dimN+30] ^ 0xCD55A219;
		workingreg[31] = in[dimN+31] ^ 0xE80BACFC;
		workingreg[32] = in[dimN+32] ^ 0x23917038;
		workingreg[33] = in[dimN+33] ^ 0xBB56CB66;
		workingreg[34] = in[dimN+34] ^ 0x503198F7;
		workingreg[35] = in[dimN+35] ^ 0x48D0E3A7;
		workingreg[36] = in[dimN+36] ^ 0xAD45B2E1;
		workingreg[37] = in[dimN+37] ^ 0x6F4CED9D;
		workingreg[38] = in[dimN+38] ^ 0x44F761A9;
		workingreg[39] = in[dimN+39] ^ 0x53A99833;
		workingreg[40] = in[dimN+40] ^ 0x7030E8F7;
		workingreg[41] = in[dimN+41] ^ 0xC8C623A1;
		workingreg[42] = in[dimN+42] ^ 0xAB77B396;
		workingreg[43] = in[dimN+43] ^ 0x1FA4FA31;
		workingreg[44] = in[dimN+44] ^ 0x82D140D8;
		workingreg[45] = in[dimN+45] ^ 0x255E0EE5;
		workingreg[46] = in[dimN+46] ^ 0xCB9ADCC4;
		break;
}


/* 
   reed-solomon encoder (204,188,t=8)
    input: 188 bytes workingreg[0..47]
    output: 204 bytes workingreg[0..51]
    one thread per loop 
*/

/* load data into wreg */
shadow = (workingreg[0]>>0)&0x000000ff;
wreg.s0 = (workingreg[0]>>8)&0x000000ff;
wreg.s1 = (workingreg[0]>>16)&0x000000ff;
wreg.s2 = (workingreg[0]>>24)&0x000000ff;
wreg.s3 = (workingreg[1]>>0)&0x000000ff;
wreg.s4 = (workingreg[1]>>8)&0x000000ff;
wreg.s5 = (workingreg[1]>>16)&0x000000ff;
wreg.s6 = (workingreg[1]>>24)&0x000000ff;
wreg.s7 = (workingreg[2]>>0)&0x000000ff;
wreg.s8 = (workingreg[2]>>8)&0x000000ff;
wreg.s9 = (workingreg[2]>>16)&0x000000ff;
wreg.sa = (workingreg[2]>>24)&0x000000ff;
wreg.sb = (workingreg[3]>>0)&0x000000ff;
wreg.sc = (workingreg[3]>>8)&0x000000ff;
wreg.sd = (workingreg[3]>>16)&0x000000ff;
wreg.se = (workingreg[3]>>24)&0x000000ff;
wreg.sf = (workingreg[4]>>0)&0x000000ff;
for(i = 0; i < 172; i++)
{
	/* load new byte into wreg.sf */
	wreg.sf = workingreg[(i+16)>>2];
	wreg.sf >>=((i+16)&0x00000003)<<3;
	wreg.sf &=0x000000ff;

	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(59,13,104,189,68,209,30,8,163,65,41,229,98,50,36,59));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(118,26,208,103,136,191,60,16,91,130,82,215,196,100,72,118));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(236,52,189,206,13,99,120,32,182,25,164,179,149,200,144,236));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(197,104,103,129,26,198,240,64,113,50,85,123,55,141,61,197));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(151,208,206,31,52,145,253,128,226,100,170,246,110,7,122,151));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(51,189,129,62,104,63,231,29,217,200,73,241,220,14,244,51));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(102,103,31,124,208,126,211,58,175,141,146,255,165,28,245,102));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(204,206,62,248,189,252,187,116,67,7,57,227,87,56,247,204));
	shadow >>=1;
	/* shadow .s0 */
	shadow = wreg.s0;

	/* shift all bytes left */
	wreg.s0 = wreg.s1;
	wreg.s1 = wreg.s2;
	wreg.s2 = wreg.s3;
	wreg.s3 = wreg.s4;
	wreg.s4 = wreg.s5;
	wreg.s5 = wreg.s6;
	wreg.s6 = wreg.s7;
	wreg.s7 = wreg.s8;
	wreg.s8 = wreg.s9;
	wreg.s9 = wreg.sa;
	wreg.sa = wreg.sb;
	wreg.sb = wreg.sc;
	wreg.sc = wreg.sd;
	wreg.sd = wreg.se;
	wreg.se = wreg.sf;

}

for(i = 0; i < 15; i++)
{
	/* load new byte into wreg.sf */
	wreg.sf=0;

	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(59,13,104,189,68,209,30,8,163,65,41,229,98,50,36,59));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(118,26,208,103,136,191,60,16,91,130,82,215,196,100,72,118));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(236,52,189,206,13,99,120,32,182,25,164,179,149,200,144,236));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(197,104,103,129,26,198,240,64,113,50,85,123,55,141,61,197));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(151,208,206,31,52,145,253,128,226,100,170,246,110,7,122,151));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(51,189,129,62,104,63,231,29,217,200,73,241,220,14,244,51));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(102,103,31,124,208,126,211,58,175,141,146,255,165,28,245,102));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(204,206,62,248,189,252,187,116,67,7,57,227,87,56,247,204));
	shadow >>=1;

	/* shadow .s0 */
	shadow = wreg.s0;

	/* shift all bytes left */
	wreg.s0 = wreg.s1;
	wreg.s1 = wreg.s2;
	wreg.s2 = wreg.s3;
	wreg.s3 = wreg.s4;
	wreg.s4 = wreg.s5;
	wreg.s5 = wreg.s6;
	wreg.s6 = wreg.s7;
	wreg.s7 = wreg.s8;
	wreg.s8 = wreg.s9;
	wreg.s9 = wreg.sa;
	wreg.sa = wreg.sb;
	wreg.sb = wreg.sc;
	wreg.sc = wreg.sd;
	wreg.sd = wreg.se;
	wreg.se = wreg.sf;

}
	/* load new byte into wreg.sf */
	wreg.sf=0;

	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(59,13,104,189,68,209,30,8,163,65,41,229,98,50,36,59));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(118,26,208,103,136,191,60,16,91,130,82,215,196,100,72,118));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(236,52,189,206,13,99,120,32,182,25,164,179,149,200,144,236));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(197,104,103,129,26,198,240,64,113,50,85,123,55,141,61,197));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(151,208,206,31,52,145,253,128,226,100,170,246,110,7,122,151));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(51,189,129,62,104,63,231,29,217,200,73,241,220,14,244,51));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(102,103,31,124,208,126,211,58,175,141,146,255,165,28,245,102));
	shadow >>=1;
	tmp= 0x00000000 - (shadow & 0x00000001);
	wreg ^= (tmp & (uint16)(204,206,62,248,189,252,187,116,67,7,57,227,87,56,247,204));
	shadow >>=1;

	/* dont shift left */

/* convert back to uint32 */
workingreg[47] = (wreg.s3<<24)|(wreg.s2<<16)|(wreg.s1<<8)|wreg.s0;
workingreg[48] = (wreg.s7<<24)|(wreg.s6<<16)|(wreg.s5<<8)|wreg.s4;
workingreg[49] = (wreg.sb<<24)|(wreg.sa<<16)|(wreg.s9<<8)|wreg.s8;
workingreg[50] = (wreg.sf<<24)|(wreg.se<<16)|(wreg.sd<<8)|wreg.sc;

/* back to global memory, prepare for outer interleaver */
for(i=0;i<51;i++)
   out[11*17 + i + pbrs_index*51] = workingreg[i];

}

/* 
   convolutional interleaver
   threadcount: 3
   data in    : 204 bytes * T (51 uints) little endian
   data out   : 204 bytes * T (51 uints) big endian + 4 bytes 
   fifos      : buffer size (1+2+3+4+5+6+7+8+9+10+11) * 17 byte, init with zero upon startup, leave untouched between kernel calls

*/


__kernel void run_oi_A( __global uint *in, __global uint *out )
{
 uint tmp;
 switch(get_global_id(0)%3)
 {
  case 0:
   tmp = (in[11*17-0+get_global_id(0)]&0x000000ff)|(in[11*17-17+get_global_id(0)]&0x0000ff00)|(in[11*17-17*2+get_global_id(0)]&0x00ff0000)|(in[11*17-17*3+get_global_id(0)]&0xff000000);
   out[4+get_global_id(0)] = tmp;
   break;
  case 1:
   tmp = (in[11*17-17*4+get_global_id(0)]&0x000000ff)|(in[11*17-17*5+get_global_id(0)]&0x0000ff00)|(in[11*17-17*6+get_global_id(0)]&0x00ff0000)|(in[11*17-17*7+get_global_id(0)]&0xff000000);
   out[4+get_global_id(0)] = tmp;
   break;
  case 2:
   tmp = (in[11*17-17*8+get_global_id(0)]&0x000000ff)|(in[11*17-17*9+get_global_id(0)]&0x0000ff00)|(in[11*17-17*10+get_global_id(0)]&0x00ff0000)|(in[11*17-17*11+get_global_id(0)]&0xff000000);
   out[4+get_global_id(0)] = tmp;
   break;
 }
}


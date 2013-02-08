// this is a modified FFT example from
// http://www.bealto.com/gpu-fft2_opencl-1.html
// BEALTO di Eric Bainville
// Mail info@bealto.com
// 
// example: radix-2 IFFT N=32
// fftswaprealimag x [Threadcount = 32]
// fftRadix2Kernel x, y , 1 [Threadcount = 16]
// fftRadix2Kernel y, x , 2 [Threadcount = 16]
// fftRadix2Kernel x, y , 4 [Threadcount = 16]
// fftRadix2Kernel y, x , 8 [Threadcount = 16]
// fftRadix2Kernel x, y , 16 [Threadcount = 16]
// fftswaprealimag y [Threadcount = 32]

#ifndef CONFIG_USE_DOUBLE
#define CONFIG_USE_DOUBLE 0
#endif

#if CONFIG_USE_DOUBLE

#if defined(cl_khr_fp64)  // Khronos extension available?
#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#elif defined(cl_amd_fp64)  // AMD extension available?
#pragma OPENCL EXTENSION cl_amd_fp64 : enable
#endif

// double
typedef double real_t;
typedef double2 real2_t;
#define FFT_PI 3.14159265358979323846
#define FFT_SQRT_1_2 0.70710678118654752440

#else

// float
typedef float real_t;
typedef float2 real2_t;
#define FFT_PI       3.14159265359f
#define FFT_SQRT_1_2 0.707106781187f

#endif

// Return A*B
real2_t mul(real2_t a,real2_t b)
{
#if USE_MAD
  return (real2_t)(mad(a.x,b.x,-a.y*b.y),mad(a.x,b.y,a.y*b.x)); // mad
#else
  return (real2_t)(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x); // no mad
#endif
}

// Return A * exp(K*ALPHA*i)
real2_t twiddle(real2_t a,int k,real_t alpha)
{
  real_t cs,sn;
  sn = sincos((real_t)k*alpha,&cs);
  return mul(a,(real2_t)(cs,sn));
}

// In-place DFT-2, output is (a,b). Arguments must be variables.
#define DFT2(a,b) { real2_t tmp = a - b; a += b; b = tmp; }

// Compute T x DFT-2.
// T is the number of threads.
// N = 2*T is the size of input vectors.
// X[N], Y[N]
// P is the length of input sub-sequences: 1,2,4,...,T.
// Each DFT-2 has input (X[I],X[I+T]), I=0..T-1,
// and output Y[J],Y|J+P], J = I with one 0 bit inserted at postion P. */
__kernel void fftRadix2Kernel(__global const real2_t * x,__global real2_t * y,int p)
{
  int t = get_global_size(0); // thread count
  int i = get_global_id(0);   // thread index
  int k = i&(p-1);            // index in input sequence, in 0..P-1
  int j = ((i-k)<<1) + k;     // output index
  real_t alpha = -FFT_PI*(real_t)k/(real_t)p;
  
  // Read and twiddle input
  x += i;
  real2_t u0 = x[0];
  real2_t u1 = twiddle(x[t],1,alpha);

  // In-place DFT-2
  DFT2(u0,u1);

  // Write output
  y += j;
  y[0] = u0/2; // divide by two for inverse
  y[p] = u1/2;
}

// swap real and imag part
__kernel void fftswaprealimag(__global real2_t *x)
{
  int i = get_global_id(0);   // thread index

  x[i] = (real2_t)(x[i].y, x[i].x);
}

'''

Scratch area for developing / testing kernels

'''

import numpy as np
import gfuncs as gf
from time import time
from matplotlib.pyplot import plot
import pycuda.gpuarray as gpuarray
import gfuncs.kernels as kn; reload(kn)
from pycuda.compiler import SourceModule


# params
sz = 10;
data1 = np.arange(sz, dtype=numpy.float32)
data2 = np.arange(sz, dtype=numpy.float32)

# call
s=time()

dA1 = gpuarray.to_gpu(data1.astype(np.float32))
dA2 = gpuarray.to_gpu(data2.astype(np.float32))
dM1 = gpuarray.sum(dA1)/len(data1)
dM2 = gpuarray.sum(dA2)/len(data1)
	
covar = kn.kCOVAR(dA1, dA2, dM1, dM2).get()/len(data1)

e=time()
device_time = e-s
print 'device time: %f' % (e-s)

# serial test
# s=time()
# hA2 = std(data1)
# e=time()
# host_time = e-s
# 
# print 'host time: %f' % (host_time)
# print 'GPU speedup: %f' % (host_time/device_time)
# print 'diff: %f' % (hA1 - hA2)

# gf.gCOVAR(data1, data2)
# gf.gCORREL(data1, data2)



## CUSTOM KERNELS ###

# ----------------------------------------------------------
# short/long moving average crossover

kMAcross_mod = SourceModule("""
	__device__ float getMA(float *dS, float *dW, int idx)
	{
		int i = 0;
		float csum = 0;
		float R = 0;

		if(idx < dW[0])
		{
			R = 0;
		}
		else
		{
			for(i = 0; i < dW[0]; i++)
			{
				csum = csum + dS[idx - i];
			}
			R = csum / dW[0];
		}
		return R;
	}
	__global__ void kMAcross(float *dS, float *dR, float *dSW, float *dLW)
	{
		int idx = blockIdx.x*blockDim.x*blockDim.y+threadIdx.y*blockDim.y+ threadIdx.x;
		dR[idx] = getMA(dS, dSW, idx) > getMA(dS, dLW, idx);
	}
	""")

kMAcross = kMAcross_mod.get_function("kMAcross")

#----------------------------------------------------------
# relative strength index

kRSI_mod = SourceModule("""
	__global__ void kRSI(float *dS, float *dR, float *dW, float *dA)
	{
		int idx = blockIdx.x*blockDim.x*blockDim.y+threadIdx.y*blockDim.y+ threadIdx.x;

		int W = (int)dW[0];
		float A = (float)dA[0];
		const int maxW = 28;

		if(idx < W-1)
		{
			int i;
			float total = 0.0;
			for(i = 0; i <= idx; i++)
			{
				total = total + dS[i];
			}
			dR[idx] = (float)total/(idx+1);
		}
		else
		{
			if(W <= 1)
			{
				dR[idx] = dS[idx];
			}
			else
			{
				int i, j, k;
				float delta[maxW-1];
				float upchange[maxW-1];
				float downchange[maxW-1];
				float upema[maxW-1];
				float downema[maxW-1];

				// compute daily change
				for(i = 1; i <= W-1; i++)
				{
					delta[i-1] = dS[idx-W+i+1] - dS[idx-W+i];
				}

				// compute upchange and downchange
				for(j = 0; j < W-1; j++)
				{
					if(delta[j] >= 0)
					{
						upchange[j] = delta[j];
						downchange[j] = 0;
					} 
					else if(delta[j] < 0)
					{
						upchange[j] = 0;
						downchange[j] = abs(delta[j]);
					}
				}

				// compute ema of upchange and downchange
				upema[0] = upchange[0];
				downema[0] = downchange[0];

				for(k = 1; k < W-1; k++)
				{
					upema[k] = A * upchange[k] + (1 - A) * upema[k-1];
					downema[k] = A * downchange[k] + (1 - A) * downema[k-1];
				}

				dR[idx] = 100.0 - (100.0 / (1.0 + (float)upema[W-2] / downema[W-2]));
			}
		}
	}
	""")

# get the kernel
kRSI = kRSI_mod.get_function("kRSI")
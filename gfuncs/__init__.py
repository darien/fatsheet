'''

Python functions that wrap CUDA kernels via pycuda.  
Variables named d* reside on the device (GPU memory) and those named h* are host (CPU) variables.

'''

import numpy as np
import pycuda.gpuarray as gpuarray
import gfuncs.kernels as kn; reload(kn)

# takes n-dimensional array
# uses pycuda sum function
def gSUM(data1):
	dA = gpuarray.to_gpu(data1.astype(np.float32))
	hR = np.float64(gpuarray.sum(dA).get())
	return hR

# takes a one-dimensional array
def gSTDEV(data1):
	dA = gpuarray.to_gpu(data1.astype(np.float32))
	dM = gpuarray.sum(dA)/len(data1)

	hR = kn.kSTDEV(dA, dM).get()
	stdev = np.float64((hR/(len(data1)-1))**.5)
	
	return stdev

# takes two one-dimensional arrays
def gCOVAR(data1, data2):
	dA1 = gpuarray.to_gpu(data1.astype(np.float32))
	dA2 = gpuarray.to_gpu(data2.astype(np.float32))
	dM1 = gpuarray.sum(dA1)/len(data1)
	dM2 = gpuarray.sum(dA2)/len(data1)
		
	covar = np.float64(kn.kCOVAR(dA1, dA2, dM1, dM2).get()/len(data1))
	
	return covar
		
# takes two one-dimensional arrays
def gCORREL(data1, data2):
	dA1 = gpuarray.to_gpu(data1.astype(np.float32))
	dA2 = gpuarray.to_gpu(data2.astype(np.float32))
	dM1 = gpuarray.sum(dA1)/len(data1)
	dM2 = gpuarray.sum(dA2)/len(data1)
	
	correl = np.float64(kn.kCOVAR(dA1, dA2, dM1, dM2).get() / \
	(kn.kSTDEV(dA1, dM1).get() * kn.kSTDEV(dA2, dM2).get())**.5)
	
	return correl
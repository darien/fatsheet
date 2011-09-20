import numpy as np
import gfuncs as gf
from time import time
from matplotlib.pyplot import plot
import pycuda.gpuarray as gpuarray
import gfuncs.kernels as kn; reload(kn)

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
'''

Kernel definitions.  Fatsheet relies heavily on predefined pycuda kernels, but some custom kernels can be found in kernel_dev.py.

'''

import numpy as np
import pycuda.autoinit
from pycuda.reduction import ReductionKernel
from pycuda.compiler import SourceModule

#----------------------------------------------------------
# standard deviation

kSTDEV = ReductionKernel(\
	np.float32, \
	neutral="0", \
	reduce_expr="a+b", \
	map_expr="(dA[i]-dM[0])*(dA[i]-dM[0])", \
	arguments="float *dA, float *dM" \
	)
	
#----------------------------------------------------------
# covariance

kCOVAR = ReductionKernel(\
	np.float32, \
	neutral="0", \
	reduce_expr="a+b", \
	map_expr="(dA1[i]-dM1[0]) * (dA2[i]-dM2[0])", \
	arguments="float *dA1, float *dA2, float *dM1, float *dM2" \
	)
	
#----------------------------------------------------------
# correlation

# none needed, uses COVAR and STDEV

#----------------------------------------------------------
# test kernel

kTEST = ReductionKernel(\
	np.float32, \
	neutral="0", \
	reduce_expr="a+b", \
	map_expr="dA[i]+0", \
	arguments="float *dA" \
	)

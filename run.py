'''

This file can be executed from a terminal window to run the demo.  A few things to note:

-- Fatsheet runs faster than the regular spreadsheet compiler only when the dataset is huge, i.e. more than a ~100k cells per vector.  With this size dataset, the speedup conferred by GPU execution is only about 50% (on my machine).  With insanely huge datasets, the speedup can top 1000%.  Essentially, the advantage of processing a dataset on the GPU has to completely offset the cost of writing the dataset to the GPU across PCIe.  This bottleneck is compounded when a spreadsheet formula has multiple different functions, each requiring a different dataset to be sent to the GPU.  

-- The output of Fatsheet may be inaccurate compared to CPU results depending on the GPU you use to run the demo.  Many GPUs only support 32-bit precision calculations, while most CPUs can support up to 64-bit precision.  On my machine, this error ends up around 0.0000000004194103 for the correlation example.

'''

from xmlparse import odsSheet
from topology import Tree
import numpy as np
from time import time

# reads spreadsheet XML into pythonic data container
odsheet = odsSheet('data/correl_test.xml')

# Compiles spreadsheet data into dependency tree
t = Tree(odsheet)

# run correlation using fatsheet (executes on GPU)
sGPU = time()
t.run()
GPU_correl = t.getResults()[t.schedule[0][0]]
eGPU = time()

# GPU test results
GPU_time = eGPU - sGPU
print("GPU time: %s" % (GPU_time))
print("GPU correlation: %.16f" % (GPU_correl))

# run correlation using numpy built-in function (executes on CPU)
sCPU = time()
CPU_correl = np.corrcoef(t.sheetobj.data[0,:,0], t.sheetobj.data[0,:,1])[0][1]
eCPU = time()

# CPU test results
CPU_time = eCPU - sCPU
print("CPU time: %s" % (CPU_time))
print("CPU correlation: %.16f" % (CPU_correl))

# error between GPU / CPU calculations
print("GPU / CPU error: %.16f" % (GPU_correl - CPU_correl))
print("GPU Speedup: %.16f" % (CPU_time / GPU_time))





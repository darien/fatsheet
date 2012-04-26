'''

All of the classes here convert spreadsheet formulas into execable python strings via the "transform" method.  Each execable string calls a GPU-accelerated function from the gfuncs module.

'''

import re
import lexer.regexes as rx
import lexer.refuncs as rf
import gfuncs as gf

# Replace single cell references with equivalent slice index
class CellRef:
	def __init__(self):
		self.formula = ''
		self.ref_rx = re.compile(r'(?<![A-Z]\(\[)Sheet[0-9]+\.[A-Z]+[0-9]+(?=\])')
	
	def transform(self, formula, objstr):
		self.formula = formula

		# replace all single cell refs with equivalent data reference strings
		refs = self.ref_rx.findall(self.formula)
		for ref in refs:
			dataref = rf.cellref2dataref(ref, objstr)
			self.formula = re.sub(re.escape('['+ref+']'), dataref, self.formula)
		
		return self.formula

# class CellRange:
# 	def __init__(self):
# 		self.formula = ''
# 		self.rng_rx = re.compile(\
# 		r'Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+(?=\])')
# 
# 	def transform(self, formula, objstr):
# 		self.formula = formula
# 
# 		# replace all terminal arguments with equivalent data range string
# 		rngs = self.rng_rx.findall(self.formula)
# 		for rng in rngs:
# 			# ods clips explicit ranges to first cell in range
# 			firstref = rx.minref.findall(rng)[0]
# 			dataref = rf.cellref2dataref(firstref, objstr)
# 			self.formula = re.sub(re.escape('['+rng+']'), dataref, self.formula)
# 	
# 		return self.formula

# Base class for functions that take a data range, e.g. 
# SUM[Sheet1.A1:Sheet1.A10]
class RangeFunction(object):
	def __init__(self):
		self.formula = ''
		self.funcname = ''
		self.gfuncname = ''
		self.f_rx = ''
		self.args_rx = ''
		
	def transform(self, formula, objstr):
		self.formula = formula

		# replace all spreadsheet function calls with equivalent python function
		self.formula = re.sub(re.escape(self.funcname), self.gfuncname, self.formula)

		funcalls = self.f_rx.findall(self.formula)
		for funcall in funcalls:
			cellrng = self.args_rx.findall(funcall)[0]
			datarng = rf.cellrng2datarng(cellrng, objstr)
			newcall = re.sub(re.escape(cellrng), datarng, funcall)
			self.formula = re.sub(re.escape(funcall), newcall, self.formula)

		return self.formula

# Base class for functions that take a list of data ranges, e.g.
# CORREL([Sheet1.A1:Sheet1.A10], [Sheet1.B1:Sheet1.B10])
class RangeListFunction(RangeFunction):
	def __init__(self):
		super(RangeFunction, self).__init__()
		
	def transform(self, formula, objstr):
		self.formula = formula

		# replace all spreadsheet function calls with equivalent python function
		self.formula = re.sub(re.escape(self.funcname), self.gfuncname, self.formula)

		funcalls = self.f_rx.findall(self.formula)
		for funcall in funcalls:
			rnglist = self.args_rx.findall(funcall)[0]
			datalist = rf.rnglist2datalist(rnglist, objstr)
			newcall = re.sub(re.escape(rnglist), datalist, funcall)
			self.formula = re.sub(re.escape(funcall), newcall, self.formula)

		return self.formula
			
# Subclasses for specific spreadsheet functions

# sum
class SUM(RangeListFunction):
	def __init__(self):
		super(SUM, self).__init__()
		self.formula = ''
		self.funcname = 'SUM'
		self.gfuncname = 'gf.gSUM'
		self.f_rx = re.compile(\
		r'SUM\(.*\)')
		self.args_rx = re.compile(r'(?<=SUM\().*(?=\))')
		
	def transform(self, formula, objstr):
		return super(SUM, self).transform(formula, objstr)

# standard deviation
class STDEV(RangeListFunction):
	def __init__(self):
		super(STDEV, self).__init__()
		self.formula = ''
		self.funcname = 'STDEV'
		self.gfuncname = 'gf.gSTDEV'
		self.f_rx = re.compile(\
		r'STDEV\(\[Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+\]\)')
		self.args_rx = re.compile(r'(?<=STDEV\().*(?=\))')
		
	def transform(self, formula, objstr):
		return super(STDEV, self).transform(formula, objstr)

# covariance
class COVAR(RangeListFunction):
	def __init__(self):
		super(COVAR, self).__init__()
		self.formula = ''
		self.funcname = 'COVAR'
		self.gfuncname = 'gf.gCOVAR'
		self.f_rx = re.compile(\
		r'COVAR\(\[Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+\]; \[Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+\]\)')
		self.args_rx = re.compile(r'(?<=COVAR\().*(?=\))')
		
	def transform(self, formula, objstr):
		return super(COVAR, self).transform(formula, objstr)

# correlation
class CORREL(RangeListFunction):
	def __init__(self):
		super(CORREL, self).__init__()
		self.formula = ''
		self.funcname = 'CORREL'
		self.gfuncname = 'gf.gCORREL'
		self.f_rx = re.compile(\
		r'CORREL\(\[Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+\]; \[Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+\]\)')
		self.args_rx = re.compile(r'(?<=CORREL\().*(?=\))')
		
	def transform(self, formula, objstr):
		return super(CORREL, self).transform(formula, objstr)
				
# make sure to add new classes here
translators = [SUM(), STDEV(), COVAR(), CORREL(), CellRef()]
				
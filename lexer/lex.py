import re
import lexer.regexes as rx
import lexer.refuncs as rf
import gfuncs as gf

# 1) NakedRef and NakedRange transform refs/ranges into calls to sheetobj.data
# 2) RangeFunction and RangeListFunction handle functions that take data ranges 
# and lists of data ranges
# 3) Subclasses for each function

## 1) direct replacement classes
# replaces '[Sheet1.A1]' with 'objstr[0, 0, 0]' when NOT part of a function call

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

# replaces '[Sheet1.A1:Sheet1.A10]' with 'objstr[0, 1, 0]' when NOT part of a function call
class CellRange:
	def __init__(self):
		self.formula = ''
		self.rng_rx = re.compile(\
		r'(?<![A-Z]\(\[)Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+(?=\])')

	def transform(self, formula, objstr):
		self.formula = formula

		# replace all terminal arguments with equivalent data range string
		rngs = self.rng_rx.findall(self.formula)
		for rng in rngs:
			# ods clips explicit ranges to first cell in range
			firstref = rx.minref.findall(rng)[0]
			dataref = rf.cellref2dataref(firstref, objstr)
			self.formula = re.sub(re.escape('['+rng+']'), dataref, self.formula)
	
		return self.formula
		
# 2) base classes for functions
# range functions take data ranges as arguments
class RangeFunction(object):
	def __init__(self):
		self.formula = ''
		self.funcname = ''
		self.gfuncname = ''
		self.f_rx = ''
		self.args_rx = ''
		
	def transform(self, formula, objstr):
		self.formula = formula

		# replace all funcalls with equivalent python function
		self.formula = re.sub(re.escape(self.funcname), self.gfuncname, self.formula)

		funcalls = self.f_rx.findall(self.formula)
		for funcall in funcalls:
			cellrng = self.args_rx.findall(funcall)[0]
			datarng = rf.cellrng2datarng(cellrng, objstr)
			newcall = re.sub(re.escape(cellrng), datarng, funcall)
			self.formula = re.sub(re.escape(funcall), newcall, self.formula)

		return self.formula

# rangelist functions take a list of ranges
class RangeListFunction(RangeFunction):
	def __init__(self):
		super(RangeFunction, self).__init__()
		
	def transform(self, formula, objstr):
		self.formula = formula

		# replace all funcalls with equivalent python function
		self.formula = re.sub(re.escape(self.funcname), self.gfuncname, self.formula)

		funcalls = self.f_rx.findall(self.formula)
		for funcall in funcalls:
			rnglist = self.args_rx.findall(funcall)[0]
			datalist = rf.rnglist2datalist(rnglist, objstr)
			newcall = re.sub(re.escape(rnglist), datalist, funcall)
			self.formula = re.sub(re.escape(funcall), newcall, self.formula)

		return self.formula
			
# 3) subclasses for functions
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
				
lexers = [CellRef(), CellRange(), SUM(), STDEV(), COVAR(), CORREL()]
				
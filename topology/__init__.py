import lexalyzer.refuncs as rf
import lexalyzer.lex as lx
import topology.sorting as ts
import gfuncs as gf

class Leaf:
	def __init__(self, ref, sheetobj):
		self.ref = ref
		self.sheetobj = sheetobj
		self.formula = sheetobj.formulas[self.ref]
		self.dataref = rf.cellref2dataref(self.ref, 'self.sheetobj.data')
		self.output = []
			
		# tranform lexical elements into execable strings
		for lxr in lx.lexers:
			self.formula = lxr.transform(self.formula, 'self.sheetobj.data')
		
		# get cell output and update sheetobj.data
		exec 'self.output = ' + self.formula
		exec self.dataref + '= self.output'
		
class Tree:
	def __init__(self, sheetobj):
		self.sheetobj = sheetobj 
		self.schedule = ts.topsort(sheetobj.formulas)
		self.branches = []
		
		self.output = {}
		
	# populate branches with leaf processes
	def run(self):
		for slot in self.schedule:
			self.branches.append([])
			for el in slot:
				lf = Leaf(el, self.sheetobj)
				self.branches[-1].append(lf)
	
	# get leaf output
	def getOutput(self):
		for branch in self.branches:
			for leaf in branch:
				self.output[leaf.ref] = leaf.output
				
		return self.output

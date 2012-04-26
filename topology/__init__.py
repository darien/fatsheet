'''

This module is used to convert spreadsheet data from a python container into a data structure ("Tree" class) that reflects the different dependencies between cell formulas.  A Tree object represents the spreadsheet as a whole and has different branches that are sequentially dependent.  Each branch has a set of Leaf objects, each of which represents a different formula to be executed.  Formulas within branches are mutually independent.  A given formula may include any number of different spreadsheet functions, each of which can be converted to an equivalent GPU-accelerated function.  

When a Tree object is run, it populates itself with Leaf objects based on the interdependencies between formulas in the spreadsheet.  On creation, a Leaf object converts its formula to a python string containing GPU-accelerated function calls that take spreadhseet data as arguments.  When the Tree object output is queried, all cell data is returned, just like the ODS compiler itself (except presumably way faster).

'''

import lexer.refuncs as rf
import lexer.lexclasses as lx
import topology.sorting as ts
import gfuncs as gf

# "Leaf" class represents a single spreadsheet formula and the data that formula processes.
# A given formula could have any number of spreadsheet functions, Leaf replaces those functions with GPU-accelerated equivalents
class Leaf:
	def __init__(self, ref, sheetobj):
		self.ref = ref
		self.sheetobj = sheetobj
		self.formula = sheetobj.formulas[self.ref]
		self.dataref = rf.cellref2dataref(self.ref, 'self.sheetobj.data')
		self.output = []
			
		# tranform lexical elements into execable strings
		for trnsltr in lx.translators:
			self.formula = trnsltr.transform(self.formula, 'self.sheetobj.data')
			
		# get cell output and update sheetobj.data
		exec 'self.output = ' + self.formula
		exec self.dataref + '= self.output'

# "Tree" class is the new spreadsheet compiler, capable of sorting the spreadsheet formulas and executing them in the proper order using Leaf objects.
class Tree:
	
	def __init__(self, sheetobj):
		self.sheetobj = sheetobj 						# holds spreadsheet data
		self.schedule = ts.topsort(sheetobj.formulas) 	# execution schedule
		self.branches = []		# each branch corresponds to a slot in schedule
		
		self.output = {}		# holds result of spreadsheet compilation, ~ to ODS
		self.results = {}		# holds just the formula results
		
	# populate branches with leaf processes
	def run(self):
		for slot in self.schedule:
			self.branches.append([])
			for el in slot:
				lf = Leaf(el, self.sheetobj)
				self.branches[-1].append(lf)
	
	# get entire compiled spreadsheet, mimics behavior of ODS.
	# could have this function write spreadsheet output back to spreadsheet.
	def getOutput(self):
		for branch in self.branches:
			for leaf in branch:
				self.output[leaf.ref] = leaf.output
				
		return self.output
	
	# only gets the results of final formula calculations.  Omits input and intermediate data.
	def getResults(self):
		for leaf in self.branches[-1]:
			self.results[leaf.ref] = leaf.output
		
		return self.results
		

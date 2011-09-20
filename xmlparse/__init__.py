from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import re
import lexalyzer.regexes as rx
import lexalyzer.refuncs as rf
import numpy as np

class odsxmlHandler(ContentHandler):
	
	def __init__(self):
		self.formulas = {}		# hash: ref: formula
		self.conRefs = []		# list of refs to constants
		self.data = []		# list array of raw data
		
		self.formFlag = 0
		self.numFlag = 0
		
		self.curTable = 0
		self.curRow = 0
		self.curCol = 0
		
		self.maxTable = 0
		self.maxRow = 0
		self.maxCol = 0
		
		self.curRef = ''
		
	def getRef(self):
		self.curRef = 'Sheet' + \
		str(self.curTable+1) + '.' + \
		str(rx.cols[self.curCol+1]) + \
		str(self.curRow+1)
				
	def startElement(self, name, attr):
		if name == 'Table':
			self.data.append([])
			
		elif name == 'Row':
			self.data[self.curTable].append([])
			
		elif name == 'Cell':
			self.data[self.curTable][self.curRow].append(0)
			newForm = attr.get('ss:Formula')
			if newForm is not None:
				self.getRef()
				self.formulas[self.curRef] = newForm[4:].decode('string_escape')
				self.formFlag = 1
			
		elif name == 'Data':
			dType = attr.get('ss:Type')
			if dType == 'Number':
				self.numFlag = 1
				
	def endElement(self, name):
		if name == 'Table':
			self.curTable += 1
			self.curRow = 0
			self.curCol = 0
			
		elif name == 'Row':
			self.curRow += 1
			self.curCol = 0
			
		elif name == 'Cell':
			self.curCol += 1
			
		if self.curTable > self.maxTable: self.maxTable = self.curTable
		if self.curRow > self.maxRow: self.maxRow = self.curRow
		if self.curCol > self.maxCol: self.maxCol = self.curCol
		
	def characters(self, ch):
		# only record constants -- not spreadsheet-generated formula results
		if self.numFlag and not self.formFlag:			
			number = float(ch.decode('string_escape'))
			self.data[self.curTable][self.curRow][self.curCol] = number
			
			self.getRef()
			self.conRefs.append(self.curRef)
			
		self.formFlag = 0
		self.numFlag = 0
			
	def endDocument(self):
		# fix formulas to have complete cell references
		for ref in self.formulas:
			self.formulas[ref] = rf.fixOmissions(ref, self.formulas[ref])
			
		# append zeros to make list array rectangular
		for sheet in self.data:
			for i in np.arange(0, self.maxRow - len(sheet)):
				sheet.append([0 for j in np.arange(0, self.maxCol)])
		
			for row in sheet:
				for k in np.arange(0, self.maxCol - len(row)):
					row.append(0)
			
		# cast to array
		self.data = np.array(self.data)
			
		print 'done'

# calls odsxmlHandler with filename
class odsSheet:
	def __init__(self, filename):
		self.filename = filename
		
		self.parser = make_parser()
		self.handler = odsxmlHandler()
		self.parser.setContentHandler(self.handler)
		self.parser.parse(open(self.filename))
		
		self.formulas = self.handler.formulas
		self.conRefs = self.handler.conRefs
		self.data = self.handler.data
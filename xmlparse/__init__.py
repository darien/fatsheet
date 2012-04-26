'''

This module is used to read XML-formatted spreadsheets and to convert the resident data and formulas into a pythonic data structure.  Currently the only supported XML format is that output by an Open Document Spreadsheet (ODS) saved as an MS Excel 2003 XML file.  

-- Could add handlers for other XML formats 
-- Could also add support for converting .ods and .xls files into XML before parsing. 

'''

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import lexer.refuncs as rf
import lexer.regexes as rx
import numpy as np

# This class is responsible for parsing xml generated from an OpenDocument spreadsheet.  
class odsxmlHandler(ContentHandler):
	
	def __init__(self):
		self.formulas = {}		# hash: ref: formula
		self.conRefs = []		# list of references to constants
		self.data = []			# list array of constant (input) data
		
		self.formFlag = 0		# flag set when cell contains a formula
		self.numFlag = 0		# flag set when cell contains a number
		
		self.curTable = 0		# current table index
		self.curRow = 0			# current row index
		self.curCol = 0			# current column index
		
		self.maxTable = 0		# record max table/row/col sizes
		self.maxRow = 0
		self.maxCol = 0
		
		self.curRef = ''		# stores the reference to the current cell being read
	
	# updates curRef with the reference of the cell currently being read (as a string)
	def getRef(self):
		self.curRef = 'Sheet' + \
		str(self.curTable+1) + '.' + \
		str(rx.cols[self.curCol+1]) + \
		str(self.curRow+1)
	
	# this function is called for every opening xml tag
	def startElement(self, name, attr):
		
		# adds a new sheet to 'data'
		if name == 'Table':
			self.data.append([])
		
		# adds a new row to current table
		elif name == 'Row':
			self.data[self.curTable].append([])
		
		# adds a new value (default 0) to the current row
		elif name == 'Cell':
			self.data[self.curTable][self.curRow].append(0)
			newForm = attr.get('ss:Formula')
			if newForm is not None:
				self.getRef()
				
				# store formula in hash table with current reference as key
				self.formulas[self.curRef] = newForm[4:].decode('string_escape')
				self.formFlag = 1
		
		# when a number is encountered set the numFlag 	
		elif name == 'Data':
			dType = attr.get('ss:Type')
			if dType == 'Number':
				self.numFlag = 1
	
	# this function is called for every closing xml tag
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
		
		# keep track of max number of tables/rows/columns for array allocation later on
		if self.curTable > self.maxTable: self.maxTable = self.curTable
		if self.curRow > self.maxRow: self.maxRow = self.curRow
		if self.curCol > self.maxCol: self.maxCol = self.curCol
	
	# this function is called every time characters are encountered within a cell
	def characters(self, ch):
		
		# only record constants -- not spreadsheet-generated formula results
		if self.numFlag and not self.formFlag:
			number = float(ch.decode('string_escape'))
			self.data[self.curTable][self.curRow][self.curCol] = number
			
			
			self.getRef()						# update current reference
			self.conRefs.append(self.curRef)	# append reference to list of constant values
			
		self.formFlag = 0		# reset flags
		self.numFlag = 0

	# this function is called at the end of the xml document, do postprocessing here
	def endDocument(self):
		
		# ODS omits redundant references, like: [Sheet1.A1:.A10]
		# here, fix formulas to have explicit cell references, like: [Sheet1.A1:Sheet1.A10]
		for ref in self.formulas:
			self.formulas[ref] = rf.fixOmissions(ref, self.formulas[ref])
			
		# rectangularize list to cast to array
		for sheet in self.data:
			for i in np.arange(0, self.maxRow - len(sheet)):
				sheet.append([0 for j in np.arange(0, self.maxCol)])
		
			for row in sheet:
				for k in np.arange(0, self.maxCol - len(row)):
					row.append(0)
			
		# cast to array
		self.data = np.array(self.data)
			
		print('done')

# calls odsxmlHandler with filename
class odsSheet:
	def __init__(self, filename):
		self.filename = filename
		
		# this stuff does all the parsing
		self.parser = make_parser()
		self.handler = odsxmlHandler()
		self.parser.setContentHandler(self.handler)
		self.parser.parse(open(self.filename))
		
		# all data in spreadsheet is abstracted to these containers
		self.formulas = self.handler.formulas
		self.conRefs = self.handler.conRefs
		self.data = self.handler.data
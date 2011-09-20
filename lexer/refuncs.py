import lexer.regexes as rx
import re

# replaces omitted redundncies
def fixOmissions(ref, formula):
	
	# converts [Sheet1.A1:.A10] --> [Sheet1.A1:Sheet1.A10]
	nakedsheets = rx.nakedsheet.findall(formula)
	for ns in nakedsheets:
		r_sheetref = rx.sheetref.findall(ns)[0]
		formula = re.sub(ns, ns+r_sheetref, formula)

	# actual cell sheetref
	f_sheetref = rx.sheetref.findall(ref)[0]
	
	# converts [A1:A10] --> [Sheet1.A1:.A10]
	nakedmins = rx.nakedmin.findall(formula)
	for nmn in nakedmins:
		formula = re.sub(nmn[1:], f_sheetref+nmn[1:], formula)
	
	# converts [Sheet1.A1:.A10] --> [Sheet1.A1:Sheet1.A10]
	nakedmaxs = rx.nakedmax.findall(formula)
	for nmx in nakedmaxs:
		formula = re.sub(nmx[:-1], nmx[0]+f_sheetref+nmx[1:-1], formula)

	# converts [.A1.] --> [Sheet1.A1]
	nakedrefs = rx.nakedref.findall(formula)
	for nrf in nakedrefs:
		formula = re.sub(nrf[1:-1], f_sheetref+nrf[1:-1], formula)
		
	return formula
	
	
## functions for converting various cell references to equivalent slice indices
# convert cellref: [Sheet1.A1] --> objstr[0, 0, 0]	
def cellref2dataref(ref, objstr):
	
	# get ref elements
	sheet = str(int(rx.sheetnum.findall(ref)[0]) - 1)
	
	col = str([i-1 for i, a in enumerate(rx.cols) \
	if a == rx.colchar.findall(ref)[0]][0])
	
	row = str(int(rx.rownum.findall(ref)[0]) - 1)
	
	# make dataref string
	dataref = objstr+'['+sheet+','+row+','+col+']'	
	
	return dataref
	
# convert cell range: [Sheet1.A1:Sheet1.A10] --> objstr[0, 0:10, 0]
def cellrng2datarng(rng, objstr):
	
	# ensure correct format
	# rng = rx.cellrange.findall(rng)[0]
	
	# get range lims	
	shmin = str(int(rx.sheetmin.findall(rng)[0]) - 1)
	shmax = str(int(rx.sheetmax.findall(rng)[0]))	# no -1 to enforce inclusion of max

	colims = rx.colchar.findall(rng)
	
	colmin = str([i-1 for i, char in enumerate(rx.cols) \
	if char == colims[0]][0])

	colmax = str([i for i, char in enumerate(rx.cols) \
	if char == colims[1]][0])
	
	rowmin = str(int(rx.rowmin.findall(rng)[0]) - 1)
	rowmax = str(int(rx.rowmax.findall(rng)[0])) 
	
	# make datarng string	
	datarng = objstr+'[' \
	+shmin+':'+shmax+',' \
	+rowmin+':'+rowmax+',' \
	+colmin+':'+colmax+']'
		
	return datarng
	
# converts list of cell ranges: Sheet1.A1:Sheet1.A10; Sheet2.A1:Sheet2.A10 -->
# objstr[0:0, 0:10, 0:0], objstr[1:1, 0:10, 0;0]
def rnglist2datalist(rnglist, objstr):
	cellrngs = rx.cellrange.findall(rnglist)
	datalist = ''
	for rng in cellrngs:
		datalist += cellrng2datarng(rng, objstr) + ','
		
	return datalist[:-1]
	
	
	
	
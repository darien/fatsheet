from xmlparse import odsSheet
from topology import Tree, Leaf
from lexalyzer.lex import lexers as lx
import lexalyzer.refuncs as rf; reload(rf)
import lexalyzer.regexes as rx; reload(rx)
import re

odsheet = odsSheet('data/sample.xml')

t = Tree(odsheet)
t.run()
t.getOutput()

# import xmlutils.ods.refuncs as rf; reload(rf)
# import xmlutils.ods.lex as lx; reload(lx)
# import topology.sorting as ts
# 
# objstr = 'odsheet.data'
# 
# frm = '[Sheet1.A9:Sheet1.A18]+[Sheet2.A9:Sheet2.A18]'	
# # tranform lexical elements into execable strings
# lxr = lx.lexers[1]
# # frm = lxr.transform(frm, 'odsheet.data')
# rngs = lxr.rng_rx.findall(frm)
# for rng in rngs:
# 	cellranges = rf.getCellRanges(rng)
# 	rngstr = rf.makeRangeStr(cellranges[0], objstr)
# 	frm = re.sub(re.escape('['+rng+']'), rngstr, frm)
# 
# # exec formula
# exec 'output = ' + frm
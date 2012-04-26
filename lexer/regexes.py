'''

Various regexes

'''


import re

# doesn't support > Z; e.g. 'AA'
cols = '!ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# for finding naked refs: [.A1], [Sheet1.A1:.A10], etc
nakedref = re.compile(r'\[\.[A-Z]+[0-9]+\]')
nakedmin = re.compile(r'\[\.[A-Z]+[0-9]+:')
nakedmax = re.compile(r':\.[A-Z]+[0-9]+\]')
nakedsheet = re.compile(r'Sheet[0-9]+\.[A-Z]+[0-9]+:')

# get sheet from ref
sheetref = re.compile(r'Sheet[0-9]+')

# 1) find complete cellranges
cellrange = \
re.compile(r'(?<=\[)Sheet[0-9]+\.[A-Z]+[0-9]+:Sheet[0-9]+\.[A-Z]+[0-9]+(?=\])')

# 2) find elements within cellranges
sheetmin = re.compile(r'(?<!:Sheet)[0-9]+(?=\.)')
sheetmax = re.compile(r'(?<=:Sheet)[0-9]+(?=\.)')
# use colchar[0] and colchar[1] for colmin, colmax
rowmin = re.compile(r'(?<=\.[A-Z])[0-9]+(?=:Sheet)')
rowmax = re.compile(r'(?<=\.[A-Z])[0-9]+$')


# 1) find single ref 
cellref = re.compile(r'(?<=\[)Sheet[0-9]+\.[A-Z]+[0-9]+(?=\])')

# 2) find elements within ref
sheetnum = re.compile(r'(?<=Sheet)[0-9]+(?=\.[A-Z])')
colchar = re.compile(r'(?<=[0-9]\.)[A-Z]+(?=[0-9])')
rownum = re.compile(r'(?<=[A-Z])[0-9]+$')

# find cellrange minref
minref = re.compile(r'Sheet[0-9]+\.[A-Z]+[0-9]+(?=:Sheet)')

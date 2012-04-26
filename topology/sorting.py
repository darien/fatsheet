'''

These function are used to sort spreadsheet cells based on their dependencies on other cells.

'''


import lexer.regexes as rx

# Topsort sorts formula references (i.e. spreadsheet cell references) into an execution schedule.  Each slot (row) in schedule includes formula references that depend on a previous slot.  Formula refs within a given slot are independent of one another and could be executed simultaneously (on different GPUs or different CPU threads)

def topsort(formulas):

	refs = formulas.keys()
	schedule = []
	
	# loop until all formulas are scheduled
	while len(refs) > 0:
		
		# check each formula
		for ref in refs:
			frm = formulas[ref]
			frmDep = 0			# flag indicating that formula depends on something in refs

			# check whether formula depends on any formulas remaining in refs
			# want to schedule formulas that depend only on already-scheduled formulas
			for othref in refs:
				if dependsOn(frm, othref): frmDep = 1

			# formula is independent, place in appropriate slot of schedule
			if not frmDep:
				schedDep = 0
				
				# if schedule is empty, just append current ref
				if len(schedule) == 0: 
					schedule.append([ref])
				
				# otherwise, either include within last slot or append a new slot
				else:
					
					# check refs in last slot of schedule
					for schedref in schedule[-1]:
						
						# checks if formula depends on any already-scheduled refs in last slot
						if dependsOn(formulas[ref], schedref):
							schedDep = 1
					# formula is independent of other formulas in last slot, add to that slot
					if not schedDep:
						schedule[-1].append(ref)
					# fomula depends on a formula within last slot, add new slot
					else:
						schedule.append([ref])
				
				# formula corresponding to ref is scheduled, remove ref
				refs.remove(ref)

	return schedule

# Utility function that determines whether a given formula depends on a specific reference
def dependsOn(frm, ref):
	
	if ref == []:
		depFlag = 0
	else:
		# get address elements of ref
		r_sheet = int(rx.sheetnum.findall(ref)[0])
		r_col = rx.colchar.findall(ref)[0]
		r_row = int(rx.rownum.findall(ref)[0])
	
		# check for individual refs
		depFlag = 0
		if ref in frm:
			depFlag = 1
	
		# get all data ranges in formula
		crs = rx.cellrange.findall(frm)
		
		# check each one to see if any formula ranges depend on reference
		for cr in crs:
			
			# get address elements of current cell range
			f_shmin = int(rx.sheetmin.findall(cr)[0])
			f_shmax = int(rx.sheetmax.findall(cr)[0])
			
			f_cmin = rx.colchar.findall(cr)[0]
			f_cmax = rx.colchar.findall(cr)[1]
			
			f_rmin = int(rx.rowmin.findall(cr)[0])
			f_rmax = int(rx.rowmax.findall(cr)[0])
			
			# determine whether elements of the reference fall within the range of the formula 
			if f_shmin <= r_sheet <= f_shmax and \
				f_cmin <= r_col <= f_cmax and \
				f_rmin <= r_row <= f_rmax:
				depFlag = 1
		
		return depFlag
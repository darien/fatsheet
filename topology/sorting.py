import lexalyzer.regexes as rx

# topological sort
def topsort(formulas):

	refs = formulas.keys()
	schedule = []
	
	while len(refs) > 0:
		# check each formula for various dependencies
		for ref in refs:
			frm = formulas[ref]
			frmDep = 0

			# check whether ref depends on any unscheduled formulas
			for othref in refs:
				if dependsOn(frm, othref): frmDep = 1

			# schedule independent jobs for parallel execution
			if not frmDep:
				schedDep = 0
				if len(schedule) == 0: schedule.append([ref])
				else:
					for schedref in schedule[-1]:
						if dependsOn(formulas[ref], schedref):
							schedDep = 1
					if not schedDep:
						schedule[-1].append(ref)
					else:
						schedule.append([ref])
				refs.remove(ref)

	return schedule

# determines whether formula depends on reference
def dependsOn(frm, ref):
	
	if ref == []:
		depFlag = 0
	else:
		# get address elements of ref
		r_sheet = int(rx.sheetnum.findall(ref)[0])
		r_col = rx.colchar.findall(ref)[0]
		r_row = int(rx.rownum.findall(ref)[0])
	
		# check ind. refs
		depFlag = 0
		if ref in frm:
			depFlag = 1
	
		# check all ranges in formula
		crs = rx.cellrange.findall(frm)
		for cr in crs:
			# get address elements of current cell range
			f_shmin = int(rx.sheetmin.findall(cr)[0])
			f_shmax = int(rx.sheetmax.findall(cr)[0])
			
			f_cmin = rx.colchar.findall(cr)[0]
			f_cmax = rx.colchar.findall(cr)[1]
			
			f_rmin = int(rx.rowmin.findall(cr)[0])
			f_rmax = int(rx.rowmax.findall(cr)[0])
	
			if f_shmin <= r_sheet <= f_shmax and \
				f_cmin <= r_col <= f_cmax and \
				f_rmin <= r_row <= f_rmax:
				depFlag = 1
		
		return depFlag
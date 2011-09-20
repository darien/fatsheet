# step through formula, comparing to all function RE's
# when one is found, append it to a list and extract arguments / function name
	# will need a class for each function that extracts correct args, turns into
	# data ranges (data[1,2,3];data[5,6,7], etc)
# get correpsonding GPU function, evaluate with data range string
# store results in another list
# create new string with listed results, exec for results
# ex:
# SUM([a:c]) + CORREL([w1:100;w2:100])
# locate SUM, turn [a:c] into data[1:3]
# eval sum, store results in results[0]
# create new string: results[0] + '+ ...(other non function elements)
# what about this: 

# STDEV(SUM([Sheet1.A1:Sheet1.A10]) + COVAR([Sheet2.A1:A100; Sheet2.B1:B100]))
# gSTDEV(gSUM(data[0:0, 0:9, 0:0]) + gCOVAR(data[1, 0:99, 0]; data[1, 0:99, 1]))


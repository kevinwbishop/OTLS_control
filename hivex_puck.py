import numpy as np

def well(well_number, experiment_dict):

	row = np.ceil(well_number/3) #indexing starts at 1
	column = well_number - 3*(row - 1) #indexing starts at 1

	## Experimental coordinates for well #1, i.e. the top left well
	experiment_dict.xMin = -12.7 # mm
	experiment_dict.xMax = -8.75  # mm
	experiment_dict.yMin = 4.2  # mm
	experiment_dict.yMax = 8.00 # mm
	experiment_dict.zMin = 0.41  # mm
	experiment_dict.zMax = 0.41 + 0.60 # mm

	## Calculate position
	experiment_dict.yMin -= 8*(column - 1) # mm
	experiment_dict.yMax -= 8*(column - 1) # mm

	experiment_dict.xMin += 8*(row - 1)
	experiment_dict.xMax += 8*(row - 1)

	return experiment_dict
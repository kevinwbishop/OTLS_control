#!/usr/bin/python

import lsmfx
from lsmfx import experiment
from lsmfx import camera
from lsmfx import daq
from lsmfx import laser
from lsmfx import wheel
from lsmfx import etl
from lsmfx import stage


# NEW VERSION

um_per_px = 0.3846 # microns        0.43 for water, 0.3846 for ECi

# CAMERA PARAMETERS
camera.number = 0
camera.sampling = um_per_px
camera.expTime = 10.0 # ms
camera.Y = 256
camera.X = 2048
camera.shutterMode = 'top middle bottom middle'
camera.triggerMode = 'auto sequence'
camera.acquireMode = 'external'
camera.compressionMode = 1
camera.quantSigma = {'405': 1.0, '488': 1.0, '561': 1.0, '638': 1.0}

# ROI PARAMETERS
experiment.drive = 'K'
experiment.fname = 'AFM030B_2mW' # specimen names
experiment.overlap = 30 # number of px overlap in Y and Z between tiles
experiment.xMin = -3.8 # mm
experiment.xMax = -0.6 # mm
experiment.yMin = -0.7 # mm
experiment.yMax = 2.5 # mm
experiment.zMin = -0.03 # mm
experiment.zMax = 1.50 # mm
experiment.xWidth = um_per_px # um
experiment.yWidth = (camera.X - experiment.overlap) * um_per_px / 1000 # mm
experiment.zWidth = (camera.Y/1.4142 - experiment.overlap) * um_per_px / 1000 # mm
experiment.wavelengths = {'488': 2.0, '638': 2.0}		# set experiment wavelenths here
experiment.attenuations = {'405': 1000.0, '488': 1000.0, '561': 1000.0, '638': 1000.0}
experiment.theta = 45.0 # light sheet angle


# VOLTAGE PARAMETERS
daq.rate = 4e5 # Hz
daq.board = 'Dev3'
daq.num_channels = 32 # AO channels
daq.names_to_channels = {'xgalvo': 0,
						 'ygalvo': 1,
						 'camera2_ex': 2,
						 'camera2_aq': 3, 
						 'camera0_ex': 4,
						 'camera0_aq': 5,
						 'etl': 6,
						 'daq_active': 7,	#adjusting behavior of this!
						 '405': 8, 
						 '488': 9,
						 '561': 11,
						 '638': 12}
daq.xamplitude = {'405': 0.1400, '488': 0.3000, '561': 0.1400, '638': 0.3000}
daq.xoffset =    {'405': -0.040, '488': 1.1750, '561': -0.040, '638': 1.1750} # Volts
daq.yamplitude = {'405': 0.0017, '488': 0.0195, '561': 0.0200, '638': 0.0195} # Volts
daq.yoffset =    {'405': 0.1200, '488': 0.0650, '561': 0.0575, '638': 0.0650} # Volts
daq.eamplitude = {'405': 0.0000, '488': 0.0000, '561': 0.0000, '638': 0.0000} # Volts
daq.eoffset =    {'405': 2.6300, '488': 2.5000, '561': 2.5850, '638': 2.5000} # Volts

'''
water 5/11/22
daq.xamplitude = {'405': 0.1400, '488': 0.1400, '561': 0.1400, '638': 0.3000}
daq.xoffset =    {'405': -0.040, '488': -0.040, '561': -0.040, '638': 1.1800} # Volts
daq.yamplitude = {'405': 0.0017, '488': 0.0017, '561': 0.0017, '638': 0.0200} # Volts
daq.yoffset =    {'405': 0.1200, '488': 0.1300, '561': 0.1310, '638': 0.0660} # Volts
daq.eamplitude = {'405': 0.0000, '488': 0.0000, '561': 0.0000, '638': 0.0000} # Volts
daq.eoffset =    {'405': 2.6300, '488': 2.5600, '561': 2.5850, '638': 2.5050} # Volts
'''

# LASER PARAMETERS
laser.port = 'COM4'
laser.rate = 9600
laser.names_to_channels = {'405': 4,
						   '488': 3,
						   '561': 1,
						   '638': 2}

laser.max_powers = {'405': 50.0,
					'488': 50.0,
					'561': 50.0,
					'638': 50.0}

# FILTER WHEEL PARAMETERS
wheel.port = 'COM6'
wheel.rate = 115200
wheel.names_to_channels = {'405': 1,
						   '488': 2,
						   '561': 3,
						   '638': 4,
						   '660': 5,
						   'none': 6}

# ETL PARAMETERS
etl.port = 'COM5'

# XYZ STAGE PARAMETERS
stage.port = 'COM3'
stage.rate = 115200

############ BEGIN SCANNING ##############

lsmfx.scan3D(experiment, camera, daq, laser, wheel, etl, stage)
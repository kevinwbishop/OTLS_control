#!/usr/bin/python

import scope
from scope import experiment
from scope import camera
from scope import daq
from scope import laser
from scope import wheel
from scope import etl
from scope import stage

############# SCAN PARAMETERS #############

experiment.drive = 'C'
experiment.fname = 'code_test' # specimen names
experiment.xMin = -1.0 # mm
experiment.xMax = 0.0 # mm
experiment.yMin = -1.0 # mm
experiment.yMax = 0.0 # mm
experiment.zMin = 0 # mm
experiment.zMax = 0.15 # mm
experiment.xWidth = 2.14 # microns
experiment.yWidth = 3.0 # mm
experiment.zWidth = 0.15 # mm
experiment.wavelengths = {'488': 20.0, '561': 20.0, '638': 20.0}
experiment.attenuations = {'488': 1000.0, '561': 1000.0, '638': 1000.0}
experiment.theta = 45.0 # light sheet angle

# CAMERA PARAMETERS
camera.number = 0
camera.sampling = 2.10 # pix 2 micron sampling on camera
camera.expTime = 4.99 # ms
camera.Y = 128
camera.X = 1536
camera.shutterMode = 'top middle bottom middle'
camera.triggerMode = 'auto sequence'
camera.acquireMode = 'external'
camera.compressionMode = 1
camera.quantSigma = {'488': 1.0, '561': 1.0, '638': 1.0}

# VOLTAGE PARAMETERS
daq.rate = 4e5 # Hz
daq.board = 'Dev2'
daq.num_channels = 32 # AO channels
daq.names_to_channels = {'xgalvo': 0,
						 'ygalvo': 1,
						 'camera2_ex': 2,
						 'camera2_aq': 3, 
						 'camera0_ex': 4,
						 'camera0_aq': 5,
						 'etl': 6,
						 'stage': 7,
						 '405': 8, 
						 '488': 9,
						 '561': 11,
						 '638': 12}
daq.xamplitude = {'405': 1.700, '488': 1.700, '561': 1.700, '638': 1.700} # Volts
daq.xoffset =    {'405': -0.06, '488': -0.06, '561': -0.05, '638': -0.06} # Volts
daq.yamplitude = {'405': 0.020, '488': 0.010, '561': 0.010, '638': 0.010} # Volts
daq.yoffset =    {'405': 0.125, '488': -0.02, '561': -0.08, '638': -0.10} # Volts
daq.eamplitude = {'405': 0.000, '488': 0.000, '561': 0.000, '638': 0.000} # Volts
daq.eoffset =    {'405': 2.635, '488': 2.480, '561': 2.480, '638': 2.500} # Volts

# LASER PARAMETERS
laser.port = 'COM15'
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
wheel.port = 'COM8'
wheel.rate = 115200
wheel.names_to_channels = {'405': 1,
						   '488': 2,
						   '561': 3,
						   '638': 4,
						   '660': 5,
						   'none': 6}

# ETL PARAMETERS
etl.port = 'COM14'

# XYZ STAGE PARAMETERS
stage.port = 'COM13'
stage.rate = 9600

############ BEGIN SCANNING ##############

scope.scan3D(experiment, camera, daq, laser, wheel, etl, stage)
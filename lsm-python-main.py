#!/usr/bin/python

import lsmfx
import json

'''
I don't think we need these
from lsmfx import experiment
from lsmfx import camera
from lsmfx import daq
from lsmfx import laser
from lsmfx import wheel
from lsmfx import etl
from lsmfx import stage
'''

# Code stucture:
# import dicts from static params
# set user-defined paramters
# compute any remaining paramters
# pass dicts to class constructors
# pass objects to scan3D

um_per_px = 0.3846  # microns        0.43 for water, 0.3846 for ECi

# import static parameters
with open('static_params.json', 'r') as read_file:
    static_params = json.load(read_file)

camera_dict = static_params['camera']
experiment_dict = static_params['experiment']
daq_dict = static_params['daq']
laser_dict = static_params['laser']
wheel_dict = static_params['wheel']
etl_dict = static_params['etl']
stage_dict = static_params['stage']

# Set user-defined paramters

# CAMERA PARAMETERS
camera_dict['expTime'] = 10.0  # ms
camera_dict['quantSigma'] = {'405': 0.0, '488': 0.0, '561': 0.0, '638': 0.0}

# FILE PARAMETERS
experiment_dict['drive'] = 'E'
experiment_dict['fname'] = 'code_testing'  # specimen names

# ROI PARAMETERS
experiment_dict['xMin'] = 0.5  # mm
experiment_dict['xMax'] = 1.0  # mm
experiment_dict['yMin'] = 0.0  # mm
experiment_dict['yMax'] = 1.5  # mm
experiment_dict['zMin'] = 0.0  # mm
experiment_dict['zMax'] = 0.2  # mm

# set experiment wavelenths here, power in mW
experiment_dict['wavelengths'] = {'405': 1.0,
                                  '488': 1.0,
                                  '561': 1.0,
                                  '638': 1.0}


experiment_dict['attenuations'] = {'405': 1.4,
                                   '488': 1.4,
                                   '561': 1.4,
                                   '638': 1.4}


# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax and econst should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': 0.0000,
                    '488': 0.0000,
                    '561': 0.0000,
                    '638': 0.0000}

daq_dict['xmax'] = {'405': 2.3650,
                    '488': 2.3650,
                    '561': 2.3650,
                    '638': 2.3650}

daq_dict['xpp'] = {'405': 0.6000,
                   '488': 0.6000,
                   '561': 0.6000,
                   '638': 0.6000}

# Y Galvo
daq_dict['ymin'] = {'405': -2.000,
                    '488': -2.000,
                    '561': -2.000,
                    '638': -2.000}

# >>>>>>>  Adjust ymax  <<<<<<<
daq_dict['ymax'] = {'405': 2.1250,
                    '488': 2.1300,
                    '561': 2.1360,
                    '638': 2.1350}

daq_dict['ypp'] = {'405': 0.0400,
                   '488': 0.0400,
                   '561': 0.0400,
                   '638': 0.0400}

# ETL
# >>>>>>>  Adjust econst  <<<<<<<
daq_dict['econst'] = {'405': 2.6300,
                      '488': 2.5000,
                      '561': 2.5100,
                      '638': 2.5100}

# compute remaining parameters
camera_dict['sampling'] = um_per_px

experiment_dict['xWidth'] = um_per_px  # um
experiment_dict['yWidth'] = \
    (camera_dict['X'] - experiment_dict['overlap']) * um_per_px / 1000  # mm
experiment_dict['zWidth'] = \
    (camera_dict['Y'] / 1.4142 - experiment_dict['overlap']) * \
    um_per_px / 1000  # mm

# construct objects
cameraObj = lsmfx.camera(camera_dict)
experimentObj = lsmfx.experiment(experiment_dict)
daqObj = lsmfx.daq(daq_dict)
laserObj = lsmfx.laser(laser_dict)
wheelObj = lsmfx.wheel(wheel_dict)
etlObj = lsmfx.etl(etl_dict)
stageObj = lsmfx.stage(stage_dict)

print('potato')

# Begin scanning
lsmfx.scan3D(experimentObj, cameraObj, daqObj, laserObj, wheelObj, etlObj,
             stageObj)

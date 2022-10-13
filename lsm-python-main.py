#!/usr/bin/python

#New code adapter for OTLS 4 NODO

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

um_per_px = 0.197  # microns        0.43 for water, 0.3846 for ECi

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
camera_dict['expTime'] = 5.0  # ms
camera_dict['quantSigma'] = {'405': 1.0, '488': 1.0, '561': 1.0, '638': 1.0}

# FILE PARAMETERS
experiment_dict['drive'] = 'A'
experiment_dict['fname'] = 'Nanostring_BM-uncleared-sybr-gold_1mW-5ms-2'  # specimen names

# ROI PARAMETERS

experiment_dict['xMin'] = -2.41  # mm
experiment_dict['xMax'] = -2.21  # mm
experiment_dict['yMin'] = 7.56  # mm
experiment_dict['yMax'] = 8.02  # mm
experiment_dict['zMin'] = -8.67  # mm
experiment_dict['zMax'] = -8.59  # mm

'''
experiment_dict['xMin'] = -2.41  # mm
experiment_dict['xMax'] = 0.11  # mm
experiment_dict['yMin'] = 7.26  # mm
experiment_dict['yMax'] = 8.02  # mm
experiment_dict['zMin'] = -8.67  # mm
experiment_dict['zMax'] = -8.59  # mm
'''

# set experiment wavelenths here, power in mW
experiment_dict['wavelengths'] = {'488': 5.0}


experiment_dict['attenuations'] = {'405': 1.4,
                                   '488': 1.4,
                                   '561': 1.4,
                                   '638': 1.4}


# all daq amplitudes are in Volts
daq_dict['xamplitude'] = {'405': 0.1400,
                          '488': 0.1400,
                          '561': 0.1400,
                          '638': 0.1400}

daq_dict['xoffset'] = {'405': -0.042,
                       '488': -0.042,
                       '561': -0.042,
                       '638': -0.042}

daq_dict['yamplitude'] = {'405': 0.00325,
                          '488': 0.00325,
                          '561': 0.00325,
                          '638': 0.00325}

daq_dict['yoffset'] = {'405': 0.0875,
                       '488': 0.0890,
                       '561': 0.0875,
                       '638': 0.0875}

daq_dict['eamplitude'] = {'405': 0.0000,
                          '488': 0.0000,
                          '561': 0.0000,
                          '638': 0.0000}

daq_dict['eoffset'] = {'405': 2.6300,
                       '488': 2.5000,
                       '561': 2.5850,
                       '638': 2.5200}

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

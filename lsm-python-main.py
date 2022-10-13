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
experiment_dict['wavelengths'] = {'561': 1.0}


experiment_dict['attenuations'] = {'405': 1.4,
                                   '488': 1.4,
                                   '561': 1.4,
                                   '638': 1.4}


# all daq amplitudes are in Volts
daq_dict['xamplitude'] = {'405': 0.3000,
                          '488': 0.3000,
                          '561': 0.3000,
                          '638': 0.3000}

daq_dict['xoffset'] = {'405': 1.1825,
                       '488': 1.1825,
                       '561': 1.1825,
                       '638': 1.1825}

daq_dict['yamplitude'] = {'405': 0.0200,
                          '488': 0.0200,
                          '561': 0.0200,
                          '638': 0.0200}

daq_dict['yoffset'] = {'405': 0.0625,
                       '488': 0.0650,
                       '561': 0.0680,
                       '638': 0.0675}

daq_dict['eamplitude'] = {'405': 0.0000,
                          '488': 0.0000,
                          '561': 0.0000,
                          '638': 0.0000}

daq_dict['eoffset'] = {'405': 2.6300,
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

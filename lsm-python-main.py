import lsmfx
import json

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


# ------ Set user-defined paramters ------ #

# CAMERA PARAMETERS
camera_dict['expTime'] = 10.0  # ms

# B3D compression. 0.0 = off, 1.0 = standard compression
camera_dict['quantSigma'] = {'405': 1.0,
                             '488': 1.0,
                             '561': 1.0,
                             '638': 1.0}

# FILE PARAMETERS
experiment_dict['drive'] = 'A'
experiment_dict['fname'] = 'OTLS4_ECi_beads_11-22-22_24mV_Ypp_2447mV_Ymax_2531mV_ETL'  # file name

# ROI PARAMETERS
experiment_dict['xMin'] = -0.2  # mm
experiment_dict['xMax'] = 0.2  # mm
experiment_dict['yMin'] = -0.4  # mm
experiment_dict['yMax'] = 0.4  # mm
experiment_dict['zMin'] = 0.1  # mm
experiment_dict['zMax'] = 0.15  # mm

# Uncomment this line to force no filter on 638 channel (i.e. reflective beads)
# otherwise leave this line commented out
wheel_dict['names_to_channels']['638'] = 6

# set experiment wavelenths here, power in mW
experiment_dict['wavelengths'] = {'638': 2.0}

experiment_dict['attenuations'] = {'405': 1.4,
                                   '488': 1.4,
                                   '561': 1.4,
                                   '638': 1000}


# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': -5.0620,
                    '488': -5.0620,
                    '561': -5.0620,
                    '638': -5.0500}

daq_dict['xmax'] = {'405': 5.0000,
                    '488': 5.0000,
                    '561': 5.0000,
                    '638': 5.0000}

daq_dict['xpp'] = {'405': 0.6000,
                   '488': 0.6000,
                   '561': 0.6000,
                   '638': 1.2000}

# Y Galvo
daq_dict['ymin'] = {'405': -2.000,
                    '488': -2.000,
                    '561': -2.000,
                    '638': -2.000}

# >>>>>>>  Adjust ymax  <<<<<<<
daq_dict['ymax'] = {'405': 2.1740,
                    '488': 2.1780,
                    '561': 2.1880,
                    '638': 2.4470}

daq_dict['ypp'] = {'405': 0.0075,
                   '488': 0.008,
                   '561': 0.008,
                   '638': 0.024}

# ETL
# >>>>>>>  Do NOT adjust  <<<<<<<
daq_dict['econst'] = {'405': 2.5480,
                      '488': 2.5180,
                      '561': 2.5230,
                      '638': 2.5310}


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

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
camera_dict['freq'] = 17 # Hz, 17 is the max. Use caution when changing
camera_dict['slitSize'] = 50   # number of lines exposed at once in rolling shutter

# B3D compression. 0.0 = off, 1.0 = standard compression
camera_dict['quantSigma'] = {'405': 1.0,
                             '488': 1.0,
                             '561': 1.0,
                             '638': 1.0}

# FILE PARAMETERS
experiment_dict['drive'] = 'E'
experiment_dict['fname'] = 'ECi-beads_sweep_q-tilt_12-15-23'  # file name

# ROI PARAMETERS
experiment_dict['xMin'] = -0.5  # mm
experiment_dict['xMax'] = 0.5  # mm
experiment_dict['yMin'] = -0.77  # mm
experiment_dict['yMax'] = 0.0  # mm
experiment_dict['zMin'] = 0.0  # mm
experiment_dict['zMax'] = 0.25  # mm

################## IMPORTANT!!##################
# set experiment wavelengths here, current in mA
################################################

experiment_dict['wavelengths'] = {'638': 103.0}

experiment_dict['attenuations'] = {'405': 6, # This value should be 2x greater than the max depth in z
                                   '488': 6,
                                   '561': 1000,
                                   '638': 1000}

daq_dict['p'] = {'405': 1.0,
                 '488': 1.0,
                 '561': 1.0,
                 '638': 1.0
                 #'638': 0.92
                 }

daq_dict['q'] = {'405': 2.29,
                 '488': 2.29,
                 '561': 2.447,
                 '638': 2.5935}

daq_dict['Qamp']= {'405': 0.0,
                   '488': 0.0,
                   '561': 0.0,
                   '638': -0.0035}

daq_dict['VCamplitude'] = {'405': 0.5,
                           '488': 0.5,
                           '561': 0.5,
                           '638': 0.5}

daq_dict['VCoffset'] = {'405': -1.65,
                        '488': -1.1,
                        '561': -1.85,
                        '638': -2.15}

daq_dict['Tamplitude'] = 3.3

#daq_dict['Tdelay'] = 0
daq_dict['Tdelay'] = 20

daq_dict['Tduration'] = 1


'''
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
daq_dict['ymax'] = {'405': 2.1250,
                    '488': 2.1100,
                    '561': 2.1070,
                    '638': 2.1050}

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
'''

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

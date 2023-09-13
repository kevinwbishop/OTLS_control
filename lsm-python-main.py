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
experiment_dict['fname'] = 'ECi_beads_1024_slit_50_Tdelay_20_VCamp_5_VCoff_-1400_17Hz_120mA'  # file name

# ROI PARAMETERS
experiment_dict['xMin'] = -0.4  # mm
experiment_dict['xMax'] = 0.4  # mm
experiment_dict['yMin'] = -0.4  # mm
experiment_dict['yMax'] = 0.4  # mm
experiment_dict['zMin'] = 0.15  # mm
experiment_dict['zMax'] = 0.45  # mm

################## IMPORTANT!!##################
# set experiment wavelengths here, current in mA
################################################

experiment_dict['wavelengths'] = {#'561': 2050.0,
                                  '638': 110.0}

experiment_dict['attenuations'] = {'405': 6, # This value should be 2x greater than the max depth in z
                                   '488': 6,
                                   '561': 6,
                                   '638': 6}

daq_dict['p'] = {'405': 0.92,
                 '488': 0.92,
                 '561': 1.0,
                 '638': 1.0}

daq_dict['q'] = {'405': 2.29,
                 '488': 2.29,
                 '561': 2.580,
                 '638': 2.597}

daq_dict['VCamplitude'] = {'405': 1.15,
                           '488': 1.15,
                           '561': 0.5,
                           '638': 0.5}

daq_dict['VCoffset'] = {'405': -1.65,
                        '488': -1.65,
                        '561': -1.3,
                        '638': -1.4}

daq_dict['Tamplitude'] = 3.3

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

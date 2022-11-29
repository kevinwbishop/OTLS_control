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

# pixel sampling: ~0.43 for water, 0.3846 for ECi
um_per_px = 0.3846  # microns

# FILE PARAMETERS
experiment_dict['drive'] = 'E'
experiment_dict['fname'] = '16-092G_CK8_0.4-0.5mW_10ms'  # file name

# ROI PARAMETERS
experiment_dict['xMin'] = -3.0  # mm
experiment_dict['xMax'] = 2.0  # mm
experiment_dict['yMin'] = -6.8  # mm
experiment_dict['yMax'] = -1.8  # mm
experiment_dict['zMin'] = -1.6  # mm
experiment_dict['zMax'] = -1.4  # mm

# IMPORTANT!!
# set experiment wavelenths here, current in mA
experiment_dict['wavelengths'] = {'488': 0.4, '561':0.5, '638': 0.5}


experiment_dict['attenuations'] = {'405': 1.5,
                                   '488': 1.5,
                                   '561': 1.5,
                                   '638': 1.5}


# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax and econst should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': 0.0000,
                    '488': 0.0000,
                    '561': 0.0000,
                    '638': 0.0000}

daq_dict['xmax'] = {'405': 2.3700,
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
                    '488': 2.1100,
                    '561': 2.1070,
                    '638': 2.1050}

daq_dict['ypp'] = {'405': 0.0400,
                   '488': 0.0400,
                   '561': 0.0400,
                   '638': 0.0400}

# ETL
# >>>>>>>  Adjust econst  <<<<<<<
daq_dict['econst'] = {'405': 2.6300,
                      '488': 2.4900,
                      '561': 2.5000,
                      '638': 2.5200}


# ------ Automatically compute remaining parameters  ------ #
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

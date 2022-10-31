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
camera_dict['quantSigma'] = {'405': 1,
                             '488': 1,
                             '561': 1,
                             '638': 1}

# pixel sampling: ~0.43 for water, 0.3846 for ECi
um_per_px = 0.3846  # microns

# FILE PARAMETERS
experiment_dict['drive'] = 'E'
experiment_dict['fname'] = 'code_testing'#'wholekidney_LEL_Dy649_1mW_RSA_TxRed_4mW_30ms__ROI2_1x1x4_atten10'  # file name

# ROI PARAMETERS
experiment_dict['xMin'] = -0.5  # mm
experiment_dict['xMax'] = 0.5  # mm
experiment_dict['yMin'] = -0.5  # mm
experiment_dict['yMax'] = 0.5  # mm
experiment_dict['zMin'] = 0.0 # mm
experiment_dict['zMax'] = 0.4  # mm

# set experiment wavelenths here, power in mW
experiment_dict['wavelengths'] = {'638': 1}


experiment_dict['attenuations'] = {'405': 100,
                                   '488': 100,
                                   '561': 10,
                                   '638': 10}


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
                    '561': 2.1100,
                    '638': 2.1050}

daq_dict['ypp'] = {'405': 0.0400,
                   '488': 0.0400,
                   '561': 0.0400,
                   '638': 0.0400}

# ETL
# >>>>>>>  Adjust econst  <<<<<<<
daq_dict['econst'] = {'405': 2.6300,
                      '488': 2.5000,
                      '561': 2.5000,
                      '638': 2.5200}


# ------ Automatically compute remaining parameters  ------ #
camera_dict['sampling'] = um_per_px

experiment_dict['xWidth'] = um_per_px  # um
experiment_dict['yWidth'] = \
    (camera_dict['X'] - experiment_dict['overlapY']) * um_per_px / 1000  # mm
experiment_dict['zWidth'] = \
    (camera_dict['Y'] / 1.4142 - experiment_dict['overlapZ']) * \
    um_per_px / 1000  # mm

# construct objects
cameraObj = lsmfx.camera(camera_dict)
experimentObj = lsmfx.experiment(experiment_dict)
daqObj = lsmfx.daq(daq_dict)
laserObj = lsmfx.laser(laser_dict)
wheelObj = lsmfx.wheel(wheel_dict)
etlObj = lsmfx.etl(etl_dict)
stageObj = lsmfx.stage(stage_dict)


# Begin scanning
lsmfx.scan3D(experimentObj, cameraObj, daqObj, laserObj, wheelObj, etlObj,
             stageObj)

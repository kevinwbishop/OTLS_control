import lsmfx
import json
import numpy as np

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
image_wells = static_params['image_wells'] ## Default option for this is "no"


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
experiment_dict['fname'] = 'LB_OTLS4_NODO_1-15-23'  # file name

# ## If imaging on hivex puck with pre-defined well positions, indicate which wells to image below.
## If not, just comment out the three lines below
image_wells['option'] = 'yes'
image_wells['well_numbers'] = [1,9] ## This must be in brackets even if only imaging 1 well
image_wells['well_ids'] = 'AA3','CC1'  # (Optional) append the ID of each tissue to the filename for each well, if doing multiple wells


# # # ROI PARAMETERS
# experiment_dict['xMin'] = -4.26 # mm
# experiment_dict['xMax'] = -3.35  # mm
# experiment_dict['yMin'] = 5.06  # mm
# experiment_dict['yMax'] = 5.50 # mm
# experiment_dict['zMin'] = 0.41  # mm
# experiment_dict['zMax'] = 0.91  # mm


# Uncomment this line to force no filter on 638 channel (i.e. reflective beads)
# otherwise leave this line commented out
# wheel_dict['names_to_channels']['638'] = 6
# wheel_dict['names_to_channels']['488'] = 6

################## IMPORTANT!!##################
# set experiment wavelenths here, current in mA
################################################

experiment_dict['wavelengths'] = {'638': 115.00, '561': 1800.00} ##Lab convention for H&E analog: ch0 = TOPRO, ch1 = eosin

experiment_dict['attenuations'] = {'405': 1000, # This value should be 2x greater than the max depth in z
                                   '488': 1000, 
                                   '561': 1000,
                                   '638': 1000}



# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax & ETL should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': -5.3350,
                    '488': -5.3350,
                    '561': -5.3350,
                    '638': -5.3350}

daq_dict['xmax'] = {'405': 5.0000,
                    '488': 5.0000,
                    '561': 5.0000,
                    '638': 5.0000}

daq_dict['xpp'] = {'405': 0.9500,
                   '488': 0.9500,
                   '561': 0.9500,
                   '638': 0.9500}

# Y Galvo
daq_dict['ymin'] = {'405': -2.000,
                    '488': -2.000,
                    '561': -2.000,
                    '638': -2.000}

# >>>>>>>  Adjust ymax  <<<<<<<
daq_dict['ymax'] = {'405': 2.44,
                    '488': 2.44,
                    '561': 2.440,
                    '638': 2.435}

daq_dict['ypp'] = {'405': 0.019,
                   '488': 0.019,
                   '561': 0.019,
                   '638': 0.019}

# ETL
# >>>>>>>  Adjust ETL  <<<<<<<
daq_dict['econst'] = {'405': 2.2500,
                      '488': 2.3000,
                      '561': 2.3750,
                      '638': 2.5500}


# construct objects
cameraObj = lsmfx.camera(camera_dict)
experimentObj = lsmfx.experiment(experiment_dict)
daqObj = lsmfx.daq(daq_dict)
laserObj = lsmfx.laser(laser_dict)
wheelObj = lsmfx.wheel(wheel_dict)
etlObj = lsmfx.etl(etl_dict)
stageObj = lsmfx.stage(stage_dict)


# Begin scanning
lsmfx.scan3D(experimentObj, cameraObj, daqObj, laserObj, wheelObj, etlObj, stageObj, image_wells)
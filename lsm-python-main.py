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
experiment_dict['fname'] = 'OTLS4_NODO_5-8-23'  # file name

# ## If imaging on hivex puck with pre-defined well positions, indicate which wells to image below.
## If not, just comment out the three lines below
image_wells['option'] = 'yes'
image_wells['well_numbers'] = [7] ## This must be in brackets even if only imaging 1 well
image_wells['well_ids'] = 'EAM047'  # (Optional) append the ID of each tissue to the filename for each well, if doing multiple wells


# # # ROI PARAMETERS
# experiment_dict['xMin'] = 1.54 # mm
# experiment_dict['xMax'] = 5.27  # mm
# experiment_dict['yMin'] = -5.22  # mm
# experiment_dict['yMax'] = -4.12 # mm
# experiment_dict['zMin'] = 0.03  # mm
# experiment_dict['zMax'] = 0.85  # mm

# Uncomment this line to force no filter on 638 channel (i.e. reflective beads)
# otherwise leave this line commented out
# wheel_dict['names_to_channels']['638'] = 6
# wheel_dict['names_to_channels']['488'] = 6

################## IMPORTANT!!##################
# set experiment wavelenths here, current in mA
################################################

experiment_dict['wavelengths'] = {'638':109.3, '561':1550} ##Lab convention for H&E analog: ch0 = TOPRO, ch1 = eosin

experiment_dict['attenuations'] = {'405': 1000, # This value should be 2x greater than the max depth in z
                                   '488': 1000, 
                                   '561': 3.5,
                                   '638': 0.40} 



# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax & ETL should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': -5.3350,
                    '488': -0.635,
                    '561': -0.635,
                    '638': -0.635}

daq_dict['xmax'] = {'405': 5.0000,
                    '488': .28,
                    '561': .28,
                    '638': .28}

daq_dict['xpp'] = {'405': 1.1, #0.9400,
                   '488': 1.1, #0.9400,
                   '561': 1.1, #0.9400,
                   '638': 1.1} #0.9400}

# Y Galvo
daq_dict['ymin'] = {'405': -2.000,
                    '488': .20,
                    '561': .20,
                    '638': .20}

# >>>>>>>  Adjust ymax  <<<<<<<
daq_dict['ymax'] = {'405': 2.44,
                    '488': .23,
                    '561': .270,
                    '638': .265}

daq_dict['ypp'] = {'405': 0.0198,
                   '488': 0.0198,
                   '561': 0.0198,
                   '638': 0.0198}

# ETL
# >>>>>>>  Adjust ETL  <<<<<<<
daq_dict['econst'] = {'405': 2.2500,
                      '488': 2.3500,
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
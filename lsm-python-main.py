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
experiment_dict['fname'] = 'LB_OTLS4_eosin_sample_2-6-23'  # file name

# ## If imaging on hivex puck with pre-defined well positions, indicate which wells to image below.
## If not, just comment out the two lines below
# image_wells['option'] = 'no'
# image_wells['well_numbers'] = [3]

# ROI PARAMETERS
experiment_dict['xMin'] = -5.07 # mm
experiment_dict['xMax'] = -3.07  # mm
experiment_dict['yMin'] = 5.4  # mm
experiment_dict['yMax'] = 10.3  # mm
experiment_dict['zMin'] = 0.19  # mm
experiment_dict['zMax'] = 0.28  # mm


# Uncomment this line to force no filter on 638 channel (i.e. reflective beads)
# otherwise leave this line commented out
# wheel_dict['names_to_channels']['638'] = 6
# wheel_dict['names_to_channels']['488'] = 6

################## IMPORTANT!!##################
# set experiment wavelenths here, current in mA
################################################

experiment_dict['wavelengths'] = {'561': 1550} ##Lab convention for H&E analog: ch0 = TOPRO, ch1 = eosin

experiment_dict['attenuations'] = {'405': 1000, # This value should be 2x greater than the max depth in z
                                   '488': 1000, ##To keep the power as constant as possible thru depth, maket hese values large
                                   '561': 15,
                                   '638': 1000}



# NEW: set DAQ parameters to match DAQExpress (values in volts)
# Only ymax & ETL should be adjusted for each sample. Remaining
# parameters should not be changed, but you should confirm they
# match those in DAQExpress

# X Galvo
daq_dict['xmin'] = {'405': -5.1500,
                    '488': -5.1500,
                    '561': -5.1500,
                    '638': -5.1500}

daq_dict['xmax'] = {'405': 5.0000,
                    '488': 5.0000,
                    '561': 5.0000,
                    '638': 5.0000}

daq_dict['xpp'] = {'405': 1.2000,
                   '488': 1.2000,
                   '561': 1.2000,
                   '638': 1.2000}

# Y Galvo
daq_dict['ymin'] = {'405': -2.000,
                    '488': -2.000,
                    '561': -2.000,
                    '638': -2.000}

# >>>>>>>  Adjust ymax  <<<<<<<
daq_dict['ymax'] = {'405': 2.3950,
                    '488': 2.4500, #4140,
                    '561': 2.4450,
                    '638': 2.4400}#110}

daq_dict['ypp'] = {'405': 0.024,
                   '488': 0.024,
                   '561': 0.024,
                   '638': 0.024}

# ETL
# >>>>>>>  Adjust ETL  <<<<<<<
daq_dict['econst'] = {'405': 3.0500,
                      '488': 2.4000,
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
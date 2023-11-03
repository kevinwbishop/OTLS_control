import json
import numpy as np
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR

# pixel sampling based on index: ~0.43 for water, ~0.373 for ECi
um_per_px = 0.376  # microns

static_params_write = {
    'camera': {
        'number': 0,  # int e.g. 0
        'Y': 1024,  # frame size in pixels
        'X': 2048,
        'sampling': um_per_px,
        'shutterMode': 'UNUSED',
        'triggerMode': 'external exposure start & software trigger',
        'acquireMode': 'auto',
        'compressionMode': 1,
        'B3Denv': '', # name of required conda env when B3D is active.
                      # e.g. 'image'. Leave as empty string to allow any env.
        'expFraction': 0.35 # 0 - 1.0. fraction of VC waveform for exposure
                            # 0.35 is the roughly linear part of a sine wave
    },
    'experiment': {
        'overlapZ': 30,
        'overlapY': 100,  # number of px overlap in Y and Z between tiles
        'theta': 50.0,  # light sheet angle in deg
        'xWidth': um_per_px
    },
    'daq': {
        'rate': 4e5,  # Hz
        'board': 'Dev2',  # board number e.g. 'Dev0'
        'num_channels': 32,  # AO channels
        'names_to_channels': {
            'xgalvo': 0,
            'ygalvo': 1,
            # 'camera2_ex': 2,
            # 'camera2_aq': 3,
            'camera0_ex': 4,
            'camera0_aq': 5,
            # 'etl': 6,
            'vc': 6,
            'trigger': 2,
            'daq_active': 7,
            '405': 8,
            '488': 9,
            '561': 11,
            '638': 3
            },
        'freq_max': 50,
		'Xmax': 10,
		'Xmin': -10,
		'Ymax': 10,
		'Ymin': -10,
		'VCmax': 5,
		'VCmin': -5,
		'Tmax': 3.3,
		'Tmin': 0
    },
    'laser': {
        'port': 'COM4',  # e.g. 'COM1'
        'rate': 9600,
        'names_to_channels': {
            '405': 4,
            '488': 3,
            '561': 1,
            '638': 2
            },
        'max_powers': {
            '405': 50.0,
            '488': 50.0,
            '561': 50.0,
            '638': 50.0
            },
        'skyra_system_name': 'OTLS5',
        'use_LUT': False,  # True or False
        'min_currents': {
            '405': 0.0,
            '488': 0.0,
            '561': 1165.0,
            '638': 0.0
        },
        'max_currents': {
            '405': 70.0,
            '488': 107.0,
            '561': 2500.0,
            '638': 167.0
        },

        'strobing': 'OFF'  # 'ON' or 'OFF'
    },
    'wheel': {
        'port': 'COM7',  # e.g. 'COM1'
        'rate': 115200,
        'names_to_channels': {
            '405': 1,
            '488': 2,
            '561': 3,
            '638': 4
            }
    },
    'etl': {
        'port': ''  # e.g. 'COM1'
        # The ETL port might not actually be used
    },
    'stage': {
        'model': 'tiger',  # must be 'tiger' or 'ms2000'
        'port': 'COM3',  # e.g. 'COM1'
        'rate': 115200  # 115200 for Tiger or 9600 for MS2000
    }
}

# Compute sampling parameters
static_params_write['experiment']['yWidth'] = \
    (static_params_write['camera']['X'] -
     static_params_write['experiment']['overlapY']) * um_per_px / 1000  # mm
static_params_write['experiment']['zWidth'] = \
    (static_params_write['camera']['Y'] * np.cos(np.deg2rad(static_params_write['experiment']['theta'])) -
     static_params_write['experiment']['overlapZ']) * um_per_px / 1000  # mm

filename = 'static_params.json'

# Make JSON writable
try:
    os.chmod(filename, S_IWUSR|S_IREAD)
except Exception: 
    pass

# Write JSON
with open(filename, 'w') as write_file:
    json.dump(static_params_write, write_file, indent=4)

# Make JSON read only
os.chmod(filename, S_IREAD|S_IRGRP|S_IROTH)

import json

# pixel sampling: ~0.43 for water, 0.3846 for ECi
um_per_px = 0.373  # microns

static_params_write = {
    'camera': {
        'number': 0,
        'Y': 256,  # frame size in pixels
        'X': 2048,
        'sampling': um_per_px,
        'shutterMode': 'top middle bottom middle',
        'triggerMode': 'auto sequence',
        'acquireMode': 'external',
        'compressionMode': 1,
        'B3Denv': ''  # name of required conda env when B3D is active.
                           # leave as empty string to allow any env.
    },
    'experiment': {
        'overlapZ': 30,
        'overlapY': 30,  # number of px overlap in Y and Z between tiles
        'theta': 45.0,  # light sheet angle in deg
        'xWidth': um_per_px
    },
    'daq': {
        'rate': 4e5,  # Hz
        'board': 'Dev2',
        'num_channels': 32,  # AO channels
        'names_to_channels': {
            'xgalvo': 0,
            'ygalvo': 1,
            'camera2_ex': 2,
            'camera2_aq': 3,
            'camera0_ex': 4,
            'camera0_aq': 5,
            'etl': 6,
            'daq_active': 7,  # adjusting behavior of this!
            '405': 8,
            '488': 9,
            '561': 11,
            '638': 12
            }
    },
    'laser': {
        'port': 'COM15',
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
        'skyra_system_name': 'OTLS 4',
        'use_LUT': False,
        'min_currents': {
            '405': 36.0,
            '488': 32.0,
            '561': 1400.0,
            '638': 109.0
        },
        'max_currents': {
            '405': 77.0,
            '488': 96.0,
            '561': 2630.0,
            '638': 177.0
        },

        'strobing': 'OFF'  # 'ON' or 'OFF'
    },
    'wheel': {
        'port': 'COM8',
        'rate': 115200,
        'names_to_channels': {
            '405': 1,
            '488': 2,
            '561': 3,
            '638': 4,
            '660': 5,
            'none': 6
            }
    },
    'etl': {
        'port': 'COM14'  # this might not actually be used
    },
    'stage': {
        'model': 'ms2000',  # must be 'tiger' or 'ms2000'
        'port': 'COM13',
        'rate': 9600
    }
}

# Compute sampling parameters
static_params_write['experiment']['yWidth'] = \
    (static_params_write['camera']['X'] - \
    static_params_write['experiment']['overlapY']) * um_per_px / 1000  # mm
static_params_write['experiment']['zWidth'] = \
    (static_params_write['camera']['Y'] / 1.4142 - \
    static_params_write['experiment']['overlapZ']) * um_per_px / 1000  # mm

# Write JSON
with open('static_params.json', 'w') as write_file:
    json.dump(static_params_write, write_file, indent=4)

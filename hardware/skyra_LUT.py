laser_LUT_write = {
    'ch1': {    # 561
        'current': [],
        'power': []
    },
    'ch2': {    # 638
        'current': [],
        'power': []
    },    
    'ch3': {    # 488
        'current': [1,2,3,4],
        'power': [0,20,50,100]
    },    
    'ch4': {    # 405
        'current': [],
        'power': []
    },
}

with open('skyra_LUT.json', 'w') as write_file:
    json.dump(laser_LUT_write, write_file)
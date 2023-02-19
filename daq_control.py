import numpy as np
import math
import json
import nidaqmx # uncomment while run
from nidaqmx import constants # uncomment while run
import numpy


class Daq(object):
    def __init__(self, ymax=2.4350, eoffset=2.5000):
        with open('static_params.json', 'r') as read_file:
            static_params = json.load(read_file)
        self.daq = static_params['daq']
        self.names_to_channels = self.daq['names_to_channels']
        self.num_channels = self.daq['num_channels']
        self.ymax = ymax
        self.eoffset = eoffset
        self.rate = self.daq['rate']
        self.ao_task = nidaqmx.Task("ao0") # uncomment while run
        self.samples = 2000 # rate * exptime / 1000 = 400000 * 5 / 1000 = 2000
        self.voltages = np.zeros((self.num_channels, self.samples))
        print('NI-Daq Initialized!')


    def start(self, wavelength):
        self.ao_task.stop() # uncomment while run
        self.voltages[4, :] = 5.0 # for test
        self.voltages[self.names_to_channels[wavelength], :] = 5.0 # uncomment while run
        self.ao_task.write(self.voltages) # uncomment while run
        self.ao_task.start() # uncomment while run
        print(str(wavelength) + ' galvo started!')


    def stop(self, wavelength):
        self.ao_task.stop() # uncomment while run
        self.voltages[4, :] = 0.0 # for test
        self.voltages[self.names_to_channels[wavelength], :] = 0.0 # option1-close one # uncomment while run
        self.ao_task.write(self.voltages) # option1-close one # uncomment while run

        self.ao_task.start() # uncomment while run
        print(str(wavelength) + ' galvo stopped!')


    def update(self):
        self.ao_task.stop() # uncomment while run
        self.ao_task.write(self.voltages) # uncomment while run
        self.ao_task.start() # uncomment while run
        print('Galvo updated!')


    def stop_all(self):
        self.ao_task.stop() # uncomment while run

        zero_voltage_array = numpy.zeros((self.daq['num_channels'], 2)) # option2-close all # uncomment while run
        self.ao_task.write(zero_voltage_array) # option2-close all # uncomment while run

        self.ao_task.start() # uncomment while run
        print('All channels stopped!')


    def adjust_ymax(self, ymax):
        self.ymax = ymax
    

    def adjust_eoffset(self, eoffset):
        self.eoffset = eoffset


    def create_voltages_galvo(self):
        xmax = 5.0000
        xmin = -5.1500
        xpp = 1.2000
        ymin = -2.0000
        ypp = 0.024
        xoffset = (xmax + xmin) / 2
        xamplitude = xpp / 2
        yoffset = (self.ymax + ymin) / 2
        yamplitude = ypp / 2

        # X Galvo
        time = np.linspace(0, 2 * math.pi, self.samples)
        xsamples = xamplitude * np.sin(time) + xoffset
        self.voltages[self.names_to_channels['xgalvo'], :] = xsamples

        # Y Galvo
        time = np.linspace(0, 2 * math.pi, self.samples)
        ysamples = yamplitude * np.sin(time) + yoffset
        self.voltages[self.names_to_channels['ygalvo'], :] = ysamples
        print('NI-Daq created voltages: X & Y Galvo!')


    def create_voltages_lasers(self):
        # Lasers
        self.voltages[4, :] = 0.0 # for test
        self.voltages[self.names_to_channels['405'], :] = 0.0
        self.voltages[self.names_to_channels['488'], :] = 0.0
        self.voltages[self.names_to_channels['561'], :] = 0.0
        self.voltages[self.names_to_channels['638'], :] = 0.0
        print('NI-Daq created voltages: lasers!')


    def create_voltages_etl(self):
        # ETL
        self.voltages[self.names_to_channels['etl'], :] = self.eoffset
        print('NI-Daq created voltages: ETL!')


    def create_voltages_daq(self):
        # NI
        self.voltages[self.names_to_channels['daq_active'], :] = 3.0
        print('NI-Daq created voltages: daq!')


    def create_ao_channels(self):
        # Create ao channels
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao0') # uncomment while run
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao1')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao2')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao3')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao4')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao5')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao6')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao7')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao8')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao9')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao10')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao11')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao12')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao13')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao14')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao15')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao16')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao17')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao18')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao19')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao20')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao21')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao22')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao23')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao24')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao25')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao26')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao27')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao28')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao29')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao30')
        self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + self.daq['board'] + '/ao31')

        self.ao_task.timing.cfg_samp_clk_timing(rate = self.rate, sample_mode = constants.AcquisitionType.CONTINUOUS, samps_per_chan= self.samples)

        print('NI-DAQ activated ' + str(self.num_channels) + ' ao channels!')
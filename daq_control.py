import numpy as np
import math
import json
import nidaqmx # uncomment while run
from nidaqmx import constants # uncomment while run
import numpy
import scipy
import scipy.interpolate


class Daq(object):
    def __init__(self, camera, ymax=2.4350, eoffset=2.5000):
        with open('static_params.json', 'r') as read_file:
            static_params = json.load(read_file)
        self.daq = static_params['daq']
        self.daq['xmin'] = {'488': -.635, '561': -.635, '638': -.635}
        self.daq['xmax'] = {'488': 0.28,'561': 0.28,'638': 0.28}
        self.daq['xpp'] = {'488': 1.1,'561': 1.1,'638': 1.1}
        self.daq['ymin'] = {'488':  0.20,'561': 0.20,'638': 0.20}
        self.daq['ymax'] = {'488':0.23,'561': 0.255,'638': 0.255}
        self.daq['ypp'] = {'488': 0.0198,'561': 0.0198,'638': 0.0198}
        self.daq['econst'] = {'488': 2.35, '561': 2.37500, '638': 2.5500}
        self.names_to_channels = self.daq['names_to_channels']
        self.num_channels = self.daq['num_channels']
        self.ymax = ymax
        self.eoffset = eoffset
        self.rate = self.daq['rate']
        self.ao_task = nidaqmx.Task("ao0") # uncomment while run
        self.samples = 4000 # rate * exptime / 1000 = 400000 * 5 / 1000 = 2000
        self.voltages = np.zeros((self.num_channels, self.samples))
        self.expTime = 10
        # self.wave_key = wave_key
        print('NI-Daq Initialized!')

    def get_original_sawtooth(self):
        # convert max / min / peak-to-peak (DAQExpress convention)
        # to offset / amplitude
        wave_key = '638'
        xoffset = (self.daq['xmax'][wave_key] + self.daq['xmin'][wave_key]) / 2
        xamplitude = self.daq['xpp'][wave_key] / 2
        xmin = xoffset - xamplitude
        xmax = xoffset + xamplitude
        fov_V = .63 + .28
        yoffset = (self.daq['ymax'][wave_key] + self.daq['ymin'][wave_key]) / 2
        yamplitude = self.daq['ypp'][wave_key] / 2
        ymin = yoffset - yamplitude
        ymax = yoffset + yamplitude
        eoffset = self.daq['econst'][wave_key]

        rate = self.daq['rate']
        samples = int(rate*self.expTime/1e3)  # number of samples for DAQ. 
        samples_halfcycle = samples/2
        halfcycle = samples_halfcycle/rate ## Length of a cycle, seconds

        n = np.arange(samples_halfcycle) # Indices of all samples in one cycle
        x = xmin + n*(xmax - xmin)/(halfcycle*rate) ## Equation for x position (in units of V)
        y = ymin + n*(ymax - ymin)/(halfcycle*rate)
        dt = halfcycle/len(n) ## Number of seconds each sample gets 
        dwell_time = dt*np.ones(len(n))

        time = np.zeros((len(n)))
        for el in range(1, len(n)):
            time[el] = time[el - 1] + dwell_time[el]
            
        return time, x, xmin, xmax, y, ymin, ymax, n

    def get_custom_waveform(self, time, x, xmin, xmax, y, ymin, ymax, n, dwell_time_new):
        time_new = np.zeros((len(n)))
        for el in range(1, len(n)):
            time_new[el] = time_new[el - 1] + dwell_time_new[el]
        total_time_el = np.cumsum(dwell_time_new)
        total_time_el -= np.min(total_time_el)

        x_ = x
        y_ = y
        if total_time_el[-1] < time[-1]:
            total_time_el = np.append(total_time_el, time[-1])
            x_ = np.append(x, xmax)
            y_ = np.append(y, ymax)
            
        interp = scipy.interpolate.interp1d(total_time_el, x_)
        interpY = scipy.interpolate.interp1d(total_time_el, y_)

        x_new = interp(time)
        y_new = interpY(time)

        x_new = np.append(x_new, np.flip(x_new))
        y_new = np.append(y_new, np.flip(y_new))
        
        return x_new, y_new


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
        # self.ymax = ymax
        self.daq['ymax']['638'] = ymax
        time, x, wavexmin, wavexmax, y, waveymin, waveymax, nn = self.get_original_sawtooth()
        dwell_time_new = np.load('C://Users//AERB//Desktop//Lindsey//troubleshooting//dwell_time_new_v3.npy')
        x_new, y_new = self.get_custom_waveform(time, x, wavexmin, wavexmax, y, waveymin, waveymax, nn, dwell_time_new)
        self.voltages[self.names_to_channels['xgalvo'], :] = x_new
        self.voltages[self.names_to_channels['ygalvo'], :] = y_new
    

    def adjust_eoffset(self, eoffset):
        self.eoffset = eoffset


    def create_voltages_galvo(self):
        ## Custom waveform
        time, x, wavexmin, wavexmax, y, waveymin, waveymax, nn = self.get_original_sawtooth()
        dwell_time_new = np.load('C://Users//AERB//Desktop//Lindsey//troubleshooting//dwell_time_new_v3.npy')
        x_new, y_new = self.get_custom_waveform(time, x, wavexmin, wavexmax, y, waveymin, waveymax, nn, dwell_time_new)
        self.voltages[self.names_to_channels['xgalvo'], :] = x_new
        self.voltages[self.names_to_channels['ygalvo'], :] = y_new


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
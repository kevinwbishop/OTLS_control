#!/usr/bin/python
#
# Adam Glaser 07/19
#

import nidaqmx
from nidaqmx import stream_writers
from nidaqmx import constants
import numpy as np
from nidaqmx.types import CtrTime
import threading
import time
import math
import matplotlib.pyplot as plt
from scipy import signal

class waveformGenerator(object):

	def __init__(self, daq, camera):

		samples = int(daq.rate*camera.expTime) # number of samples for DAQ

		self.ao_task = nidaqmx.Task("ao0")
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao0')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao1')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao2')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao3')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao4')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao5')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao6')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao7')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao8')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao9')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao10')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao11')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao12')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao13')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao14')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao15')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao16')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao17')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao18')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao19')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao20')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao21')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao22')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao23')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao24')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao25')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao26')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao27')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao28')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao29')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao30')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/Dev2/ao31')

		self.ao_task.timing.cfg_samp_clk_timing(rate = daq.rate, active_edge = nidaqmx.constants.Edge.RISING, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan = samples)
		self.ao_task.triggers.start_trigger.retriggerable = True
		self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/Dev2/PFI0', trigger_edge = nidaqmx.constants.Slope.RISING)

		self.counter_task = nidaqmx.Task("counter0")
		self.counter_loop = self.counter_task.ci_channels.add_ci_count_edges_chan('/Dev2/ctr0', edge = nidaqmx.constants.Edge.RISING)
		self.counter_loop.ci_count_edges_term = '/Dev2/PFI0'

		# for c in range(voltages.shape[0]):
		# 	plt.plot(voltages[c, :])
		# plt.legend(loc='upper right')
		# plt.show()
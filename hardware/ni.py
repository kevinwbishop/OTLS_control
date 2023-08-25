#!/usr/bin/python
#
# Adam Glaser 07/19
# Edited by Kevin Bishop 5/22 (replaced explicit definition of Dev2 w/ daq.board)
#

import nidaqmx
from nidaqmx import stream_writers
from nidaqmx import constants
import numpy as np
from nidaqmx.types import CtrTime
import threading
import time
import math
import numpy
import matplotlib.pyplot as plt
from scipy import signal

class waveformGenerator(object):

	def __init__(self, daq, camera, session, triggered = True):

		self.samples = int(session.nFrames*daq.rate*camera.expTime/1000) # number of samples for DAQ

		self.ao_task = nidaqmx.Task("ao0")

		'''		
		# new stuff
		omit=[5,7]
		all_chans = [i for i in range(32)]
		use_chans = list(set(all_chans) - set(omit))
		use_chans = [str(x) for x in use_chans]''

		for j in use_chans:
			self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao' + j)

		'''
		#OLD VERSION
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao0')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao1')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao2')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao3')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao4')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao5')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao6')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao7')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao8')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao9')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao10')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao11')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao12')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao13')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao14')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao15')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao16')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao17')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao18')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao19')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao20')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao21')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao22')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao23')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao24')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao25')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao26')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao27')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao28')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao29')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao30')
		self.ao_task.ao_channels.add_ao_voltage_chan(physical_channel = '/' + daq.board + '/ao31')

		self.ao_task.timing.cfg_samp_clk_timing(rate = daq.rate, active_edge = nidaqmx.constants.Edge.RISING, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan = self.samples)
		
		if triggered:
			print('arming trigger')
			self.ao_task.triggers.start_trigger.retriggerable = True
			self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/' + daq.board + '/PFI0', trigger_edge = nidaqmx.constants.Slope.RISING)
		else:
			self.ao_task.triggers.start_trigger.disable_start_trig()

		'''
		self.counter_task = nidaqmx.Task("counter0")
		self.counter_loop = self.counter_task.ci_channels.add_ci_count_edges_chan('/' + daq.board + '/ctr0', edge = nidaqmx.constants.Edge.RISING)
		self.counter_loop.ci_count_edges_term = '/' + daq.board + '/PFI0'
		'''

		# for c in range(voltages.shape[0]):
		# 	plt.plot(voltages[c, :])
		# plt.legend(loc='upper right')
		# plt.show()


	# Function writes zeros to all active channels of the NIDAQ
	# It disables triggering functions above, writes zeros, then renables them
	# This causes the code to crash if used at the start of the imaging loop (maybe it must be used after a normal write?)
	# It's okay if used at the end of the imaging loop
	# It also throws a warning which can be safely ignored:
	# 	Warning 200010 occurred.
	# 	Finite acquisition or generation has been stopped before the requested number of samples were acquired or generated.
  	# 	error_buffer.value.decode("utf-8"), error_code))

	def write_zeros(self, daq):
		zero_voltage_array = numpy.zeros((daq.num_channels, 2)) # create zero voltages array
		self.ao_task.triggers.start_trigger.retriggerable = False
		self.ao_task.triggers.start_trigger.disable_start_trig()
		self.ao_task.write(zero_voltage_array)
		self.ao_task.start()
		self.ao_task.stop()
		self.ao_task.triggers.start_trigger.retriggerable = True
		self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/' + daq.board + '/PFI0', trigger_edge = nidaqmx.constants.Slope.RISING)

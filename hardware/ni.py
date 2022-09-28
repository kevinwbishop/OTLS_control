#!/usr/bin/python
"""
Adam Glaser 07/19
Edited by Kevin Bishop 5/22 (replaced explicit definition of Dev2 w/ daq.board)
Edited by Gan 09/22: enforced linting and added doc strings. Deleted imported
packages that are unused. Deleted codes that are commented out.
"""
import nidaqmx
import numpy


class waveformGenerator(object):
	"""
	Generate waveform using NI card.
	"""

	def __init__(self, daq, camera, triggered=True):

		self.samples = int(daq.rate*camera.expTime)  # number of samples for DAQ

		self.ao_task = nidaqmx.Task("ao0")

		# OLD VERSION
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
			self.ao_task.triggers.start_trigger.retriggerable = True
			self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/' + daq.board + '/PFI0', trigger_edge = nidaqmx.constants.Slope.RISING)
		else:
			self.ao_task.triggers.start_trigger.disable_start_trig()

	def write_zeros(self, daq):
		"""
		Function writes zeros to all active channels of the NIDAQ
	    
		It disables triggering functions above, writes zeros, then renables them
	    This causes the code to crash if used at the start of the imaging loop (maybe it must be used after a normal write?)
	    It's okay if used at the end of the imaging loop
	    It also throws a warning which can be safely ignored:
		Warning 200010 occurred.
		Finite acquisition or generation has been stopped before the requested number of samples were acquired or generated.
  		error_buffer.value.decode("utf-8"), error_code))
		"""
		zero_voltage_array = numpy.zeros((daq.num_channels, 2)) # create zero voltages array
		self.ao_task.triggers.start_trigger.retriggerable = False
		self.ao_task.triggers.start_trigger.disable_start_trig()
		self.ao_task.write(zero_voltage_array)
		self.ao_task.start()
		self.ao_task.stop()
		self.ao_task.triggers.start_trigger.retriggerable = True
		self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source = '/' + daq.board + '/PFI0', trigger_edge = nidaqmx.constants.Slope.RISING)

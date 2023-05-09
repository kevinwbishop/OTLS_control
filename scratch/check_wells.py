#!/usr/bin/python

"""
OTLS 4 code for checking that well positions are correct for imaging session

"""
import numpy as np
import json
import math
import hardware.ni as ni
import hivex_puck as puck
import scan3D_image_wells


class check_wells:
	"""
	"""

	def __init__(self, well_number):
		# import static parameters
		with open('static_params.json', 'r') as read_file:
			static_params = json.load(read_file)

		experiment = static_params['experiment']
		self.well_number = well_number
		## Grab imaging coordinates
		self.xWidth = experiment['xWidth']
		self.yWidth = experiment['yWidth']
		self.zWidth = experiment['zWidth']
		self.overlapY = experiment['overlapY']
		self.overlapZ = experiment['overlapZ']
		self = puck.well(well_number, self) ## Imaging coordinates of well

		self.xLength = self.xMax - self.xMin  # mm
		self.yLength = round((self.yMax - self.yMin) / self.yWidth) * self.yWidth  # mm
		self.zLength = round((self.zMax - self.zMin) / self.zWidth) * self.zWidth  # mm
		self.xOff = self.xMax - self.xLength/2
		self.yOff = self.yMax - self.yLength/2
		self.zOff = self.zMin
		self.nFrames = int(np.floor(self.xLength/(self.xWidth/1000.0)))
		self.yTiles = int(round(self.yLength/self.yWidth))
		self.zTiles = int(round(self.zLength/self.zWidth))

		# xyzStage, initialPos = stage.initialize(stageobj, well_number)

	def initialize_stage(self):

		# import static parameters
		with open('static_params.json', 'r') as read_file:
			static_params = json.load(read_file)

		stage_dict = static_params['stage']
		self.port = stage_dict['port']
		self.rate = stage_dict['rate']
		self.model = stage_dict['model']

		# Should check the velocity and acceration, I think this
		# really shouldn't be part of the init since it's set to different
		# values in various places
		self.settings = {'backlash': 0.0,
			'velocity': 1.0, 'acceleration': 100}
		self.axes = ('X', 'Y', 'Z')

		if self.model == 'tiger':
			print('initializing stage: Tiger')
			import hardware.tiger as tiger
			xyzStage = tiger.TIGER(baudrate=self.rate, port=self.port)
			xyzStage.setPLCPreset(6, 52)

		elif self.model == 'ms2000':
			print('initializing stage: MS2000')
			import hardware.ms2000 as ms2000
			xyzStage = ms2000.MS2000(baudrate=self.rate, port=self.port)
			xyzStage.setTTL('Y', 3)

		else:
			raise Exception('invalid stage type!')

		initialPos = xyzStage.getPosition()
		xyzStage.setScanF(1)
		for ax in self.axes:
			xyzStage.setBacklash(ax, self.settings['backlash'])
			xyzStage.setVelocity(ax, self.settings['velocity'])
			xyzStage.setAcceleration(ax, self.settings['acceleration'])
		print('stage initialized', initialPos)

		return xyzStage

	def go_to_well(self, xyzStage):
		print('Moving stage to well ' + str(self.well_number))
		xyzStage.goAbsolute('X', self.xOff, False)
		xyzStage.goAbsolute('Y', self.yOff, False)
		xyzStage.goAbsolute('Z', self.zOff, False) ## Bottom surface of well
		# print(self.xOff, self.yOff, self.zOff) ## Middle of well at surface of Z.

# The MIT License
#
# Copyright (c) 2020 Adam Glaser, University of Washington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

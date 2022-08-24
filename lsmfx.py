#!/usr/bin/python
"""
LSM scanning code

# Adam Glaser 07/19
# Edited by Kevin Bishop 5/22

"""
import wave
import numpy
import math
import h5py
# import tifffile
import warnings
import os.path
import shutil
import skimage.transform
import pco
# import hardware.pco as pco
import hardware.tiger as tiger
# import hardware.ms2000 as ms2000
import hardware.ni as ni
import hardware.fw102c as fw102c
import hardware.skyra as skyra
from hardware.opto import Opto
from scipy.ndimage import gaussian_filter1d
import time as timer
# import matplotlib.pyplot as plt

class experiment(object):
	def __init__(self, drive = [], 
					   fname = [], 
					   xMin = [], 
					   xMax = [], 
					   yMin = [], 
					   yMax = [], 
					   zMin = [], 
					   zMax = [], 
					   xWidth = [], 
					   yWidth = [], 
					   zWidth = [], 
					   wavelengths = [], 
					   powers = [], 
					   attenuations = [], 
					   theta = [], 
					   overlap = []):
		self.drive = drive
		self.fname = fname
		self.xMin = xMin
		self.xMax = xMax
		self.yMin = yMin
		self.yMax = yMax
		self.zMin = zMin
		self.zMax = zMax
		self.xWidth = xWidth
		self.yWidth = yWidth
		self.zWidth = zWidth
		self.wavelengths = wavelengths
		self.powers = powers
		self.attenuations = attenuations
		self.theta = theta
		self.overlap = overlap

class scan(object):
	def __init__(self, xLength = [], yLength = [], zLength = [], xOff = [], yOff = [], zOff = [], nFrames = [], nWavelengths = [], yTiles = [], zTiles = [], scanSpeed = [], chunkSize1 = [], chunkSize2 = [], chunkSize3  = [], blockSize = []):
		self.xLength = xLength
		self.yLength = yLength
		self.zLength = zLength
		self.xOff = xOff
		self.yOff = yOff
		self.zOff = zOff
		self.nFrames = nFrames
		self.nWavelengths = nWavelengths
		self.yTiles = yTiles
		self.zTiles = zTiles
		self.scanSpeed = scanSpeed
		self.chunkSize1 = chunkSize1
		self.chunkSize2 = chunkSize2
		self.chunkSize3 = chunkSize3
		self.blockSize = blockSize

class camera(object):
	def __init__(self, number = [], X = [], Y = [], sampling = [], expTime = [], triggerMode = [], acquireMode = []):
		self.number = number
		self.X = X
		self.Y = Y	
		self.sampling = sampling
		self.expTime = expTime
		self.triggerMode = triggerMode
		self.acquireMode = acquireMode

class daq(object):
	def __init__(self, rate = [], name = [], board = [], num_channels = [], names_to_channels = []):
		self.rate = rate
		self.board = board
		self.name = name
		self.num_channels = num_channels	
		self.names_to_channels = names_to_channels

class laser(object):
	def __init__(self,  port = [], rate = [], names_to_channels = []):
		self.port = port
		self.rate = rate
		self.names_to_channels = names_to_channels

class etl(object):
	def __init__(self, port = []):
		self.port = port

class wheel(object):
	def __init__(self, port = [], rate = [], names_to_channels = []):
		self.port = port
		self.rate = rate
		self.names_to_channels = names_to_channels

class stage(object):
	def __init__(self, port = [], rate = []):
		self.port = port
		self.rate = rate

def scan3D(experiment, camera, daq, laser, wheel, etl, stage):

	######### ROUND SCAN DIMENSIONS ###########

	scan.xLength = experiment.xMax - experiment.xMin # mm
	scan.yLength = round((experiment.yMax - experiment.yMin)/experiment.yWidth)*experiment.yWidth # mm
	scan.zLength = round((experiment.zMax - experiment.zMin)/experiment.zWidth)*experiment.zWidth # mm
	scan.xOff = experiment.xMax - (scan.xLength)/2
	scan.yOff = experiment.yMax - scan.yLength/2
	scan.zOff = experiment.zMin
	scan.nFrames = int(numpy.floor(scan.xLength/(experiment.xWidth/1000.0)))
	scan.nWavelengths = len(experiment.wavelengths)
	scan.yTiles = int(round(scan.yLength/experiment.yWidth))
	scan.zTiles = int(round(scan.zLength/experiment.zWidth))
	scan.scanSpeed = experiment.xWidth/(1.0/(1.0/((camera.expTime+10.0e-3)/1000.0))*1000.0)
	scan.chunkSize1 = 256
	if scan.chunkSize1 >= scan.nFrames/8:
		scan.chunkSize1 = numpy.floor(scan.nFrames/8)
	scan.chunkSize2 = 16
	if scan.chunkSize2 >= camera.Y/8:
		scan.chunkSize2 = numpy.floor(camera.Y/8)
	scan.chunkSize3 = 256
	if scan.chunkSize3 >= camera.X/8:
		scan.chunkSize3 = numpy.floor(camera.X/8)
	scan.blockSize = int(2*scan.chunkSize1)

	########## SETUP DATA DIRECTORY ###########

	#if os.path.exists(experiment.drive + ':\\' + experiment.fname):
		#shutil.rmtree(experiment.drive + ':\\' + experiment.fname, ignore_errors = True)
	os.makedirs(experiment.drive + ':\\' + experiment.fname)
	dest = experiment.drive + ':\\' + experiment.fname + '\\data.h5'

	############# CONNECT XYZ STAGE #############
	
	xyzStage = tiger.TIGER(baudrate = stage.rate, port = stage.port)
	initialPos = xyzStage.getPosition()
	#xyzStage.setTTL("Y",3)	#old command for MS2000
	#print('setting TTL')
	xyzStage.setPLCPreset(6,52)	#new command for Tiger
	#print('set TTL')
	xyzStage.setScanF(1)
	xyzStage.setBacklash("X",0)
	xyzStage.setBacklash("Y",0)
	xyzStage.setBacklash("Z",0)
	xyzStage.setVelocity("X", 1.0)
	xyzStage.setVelocity("Y", 1.0)
	xyzStage.setVelocity("Z", 0.1)
	xyzStage.setAcceleration("X",100)
	xyzStage.setAcceleration("Y",100)
	xyzStage.setAcceleration("Z",100)
	print(xyzStage)

	########## INITIALIZE H5 FILE #############

	h5init(dest, camera, scan, experiment)
	write_xml(experiment = experiment, camera = camera, scan = scan)

	############### CONNECT NIDAQ ###############

	waveformGenerator = ni.waveformGenerator(daq = daq, camera = camera, triggered = True)
	#waveformGenerator.write_zeros(daq = daq)

	
	############# CONNECT LASER #############
	
	#according to the manual, you should wait for 2min after setting laser 1 (561) to mod mode for power to stabalize. Consider adding this in
	#ch is channel number of laser
	skyraLaser = skyra.Skyra(baudrate = laser.rate, port = laser.port)
	for ch in list(laser.names_to_channels):
		skyraLaser.setModulationOn(laser.names_to_channels[ch])
		skyraLaser.setDigitalModulation(laser.names_to_channels[ch],1)
		skyraLaser.setAnalogModulation(laser.names_to_channels[ch],0)	#new, to ensure analog mod is not active
	for ch in list(experiment.wavelengths):
		#skyraLaser.setModulationHighCurrent(laser.names_to_channels[ch], experiment.wavelengths[ch]/laser.max_powers[ch])
		skyraLaser.setModulationHighCurrent(laser.names_to_channels[ch], experiment.wavelengths[ch])
		skyraLaser.turnOn(laser.names_to_channels[ch])
	for ch in list(experiment.wavelengths):
		skyraLaser.setModulationLowCurrent(laser.names_to_channels[ch], 0)
	print(skyraLaser)

	############ CONNECT FILTER WHEEL ###########

	fWheel = fw102c.FW102C(baudrate = wheel.rate, port = wheel.port)
	print(fWheel)

	############ CONNECT TUNBALE LENS ###########

	etl = Opto(port = etl.port)
	etl.connect()
	etl.mode('analog')
	print(etl)



	############## CONNECT CAMERA ##############

	#print('making cam')
	cam = pco.Camera(camera_number=camera.number)
	#print(cam)
	
	cam.configuration = {'exposure time': camera.expTime*1.0e-3,
                 'roi': (1, 1023-round(camera.Y/2), 2060, 1026+round(camera.Y/2)),
                 'trigger': camera.triggerMode,
                 'acquire': camera.acquireMode,
                 'pixel rate': 272250000}
	#print('configured cam')
	cam.record(number_of_images = scan.nFrames, mode = 'sequence non blocking')
	# possibly change mode to ring buffer??
	#print('made record') 

	######## IMAGING LOOP #########

	ring_buffer = numpy.zeros((scan.blockSize, camera.Y, camera.X), dtype = 'uint16')

	#print('made ring buffer')
	tile = 0
	previous_tile_time = 0
	previous_ram = 0
	
	start_time = timer.time()

	#print('made timer')

	xPos = scan.xLength/2.0 - scan.xOff

	for j in range(scan.zTiles):

		zPos = j*experiment.zWidth + scan.zOff
		xyzStage.setVelocity('Z', 0.1)
		xyzStage.goAbsolute('Z', zPos, False)

		#print('sent Z')

		for k in range(scan.yTiles):

			yPos = scan.yOff-scan.yLength/2.0+k*experiment.yWidth+experiment.yWidth/2.0
			xyzStage.setVelocity('Y', 1.0)
			xyzStage.goAbsolute('Y', yPos, False)

			#print('sent Y')

			for ch in range(scan.nWavelengths):
				# ch is order of wavelenghts in main (NOT necessarily Skyra channel number)

				xyzStage.setVelocity('X', 1.0)
				xPos = scan.xLength/2.0 - scan.xOff
				xyzStage.goAbsolute('X', -xPos, False)

				#print('sent X')

				############# CHANGE FILTER ############

				fWheel.setPosition(wheel.names_to_channels[list(experiment.wavelengths)[ch]])
				
				#print('set filter')

				############## START SCAN ##############

				#skyraLaser.setModulationHighCurrent(laser.names_to_channels[list(experiment.wavelengths)[ch]], experiment.wavelengths[list(experiment.wavelengths)[ch]]/laser.max_powers[list(experiment.wavelengths)[ch]]/numpy.exp(-j*experiment.zWidth/experiment.attenuations[list(experiment.wavelengths)[ch]]))
				skyraLaser.setModulationHighCurrent(laser.names_to_channels[list(experiment.wavelengths)[ch]], \
					experiment.wavelengths[list(experiment.wavelengths)[ch]] / \
					numpy.exp(-j*experiment.zWidth/experiment.attenuations[list(experiment.wavelengths)[ch]]))
				
				#print('set laser')
				voltages, rep_time = write_voltages(daq = daq, laser=laser, camera = camera, experiment = experiment, scan = scan, ch = ch)
				#print('writing voltages')
				waveformGenerator.ao_task.write(voltages)

				print('Starting tile ' + str((tile)*scan.nWavelengths+ch+1) + '/' + str(scan.nWavelengths*scan.zTiles*scan.yTiles))
				print('y position: ' + str(yPos) + ' mm')
				print('z position: ' + str(zPos) + ' mm')
				tile_start_time = timer.time()

				xyzStage.setScanR(-xPos, -xPos + scan.xLength)
				xyzStage.setScanV(yPos)

				response = xyzStage.getMotorStatus()
				while response[0] == 'B':
					response = xyzStage.getMotorStatus()

				xyzStage.setVelocity('X', scan.scanSpeed)
				xyzStage.setVelocity('Y', scan.scanSpeed)
				xyzStage.setVelocity('Z', scan.scanSpeed)

				waveformGenerator.ao_task.start()
				cam.start()
				xyzStage.scan(False)
				skyraLaser.turnOn(laser.names_to_channels[list(experiment.wavelengths)[ch]])

				########## START IMAGING LOOP ##########

				num_acquired = 0
				num_acquired_counter = 0
				num_acquired_previous = 0

				# while num_acquired < scan.nFrames: #original version. for some reason code frequently (but not always)
				# gets stuck on cam.wait_for_next_image(num_acquired), like cam is a frame or two ahead of code
				while num_acquired < scan.nFrames - 100:

					cam.wait_for_next_image(num_acquired)

					if num_acquired_counter == int(scan.blockSize):
						print('Saving frames: ' + str(num_acquired_previous) + ' - ' + str(num_acquired))
						print('Tile: ' + str(tile))
						h5write(dest, ring_buffer, tile + scan.zTiles*scan.yTiles*ch, num_acquired_previous, num_acquired)
						num_acquired_counter = 0
						num_acquired_previous = num_acquired
						temp = cam.image(num_acquired)[0]
						#ring_buffer[num_acquired_counter] = numpy.fliplr(temp[2:camera.Y+2, 1024-int(camera.X/2):1024-int(camera.X/2)+camera.X])
						ring_buffer[num_acquired_counter] = temp[2:camera.Y+2, 1024-int(camera.X/2):1024-int(camera.X/2)+camera.X]

					else:

						temp = cam.image(num_acquired)[0]
						#ring_buffer[num_acquired_counter] = numpy.fliplr(temp[2:camera.Y+2, 1024-int(camera.X/2):1024-int(camera.X/2)+camera.X])
						ring_buffer[num_acquired_counter] = temp[2:camera.Y+2, 1024-int(camera.X/2):1024-int(camera.X/2)+camera.X]

					if num_acquired == scan.nFrames-1:
						print('Saving frames: ' + str(num_acquired_previous) + ' - ' + str(scan.nFrames))
						h5write(dest, ring_buffer[0:num_acquired_counter+1], tile + scan.zTiles*scan.yTiles*ch, num_acquired_previous, scan.nFrames)

					num_acquired += 1
					num_acquired_counter += 1

				waveformGenerator.ao_task.stop()
				waveformGenerator.write_zeros(daq = daq)
				# For some reason this write_zeros works but the above doesn't?
				# laser stops and starts appropriately with this one active and the top write_zeros() commented out

				skyraLaser.turnOff(list(experiment.wavelengths)[ch])
				cam.stop()

				tile_end_time = timer.time()
				tile_time = tile_end_time - tile_start_time
				print('Tile time: ' + str(round((tile_time/60), 3)) + " min")
				tiles_remaining = scan.nWavelengths*scan.zTiles*scan.yTiles - (tile*scan.nWavelengths+ch+1) 
				if tiles_remaining != 0:
					print('Estimated time remaining: ' + str(round((tile_time*tiles_remaining/3600), 3)) + " hrs")

			tile += 1

	end_time = timer.time()

	print("Total time = " + str(round((end_time - start_time)/3600, 3)) + " hrs")
	
	response = xyzStage.getMotorStatus()
	while response[0] == 'B':
		response = xyzStage.getMotorStatus()

	cam.close()
	etl.close(soft_close=True)
	# waveformGenerator.counter_task.close()
	waveformGenerator.ao_task.close()
	xyzStage.shutDown()

def write_voltages(daq, laser, camera, experiment, scan, ch):

	n2c = daq.names_to_channels

	samples = int(daq.rate*camera.expTime/1e3) # number of samples for DAQ
	
	line_time = 9.76/1.0e6 # seconds, constant for pco.edge camera
	roll_time = line_time*camera.Y/2.0 # chip rolling time in seconds
	roll_samples = int(numpy.floor(roll_time*daq.rate)) # rolling samples

	on_time = camera.expTime/1e3 - roll_time # ON time for strobing laser
	on_samples = int(numpy.floor(on_time*daq.rate)) # ON samples

	galvo_time = 365/1.0e6 # galvo delay time
	galvo_samples = int(numpy.floor(galvo_time*daq.rate))

	buffer_time = 50/1.0e6
	buffer_samples = int(numpy.floor(buffer_time*daq.rate))

	voltages = numpy.zeros((daq.num_channels, samples)) # create voltages array

	# X Galvo scanning:
	period_samples = numpy.linspace(0, 2*math.pi, on_samples+2*buffer_samples)
	snap_back = numpy.linspace(daq.xoffset[list(experiment.wavelengths)[ch]]+daq.xamplitude[list(experiment.wavelengths)[ch]], daq.xoffset[list(experiment.wavelengths)[ch]]-daq.xamplitude[list(experiment.wavelengths)[ch]], samples-on_samples-2*buffer_samples)
	voltages[n2c['xgalvo'],:] = daq.xoffset[list(experiment.wavelengths)[ch]]
	voltages[n2c['xgalvo'], roll_samples-galvo_samples-buffer_samples:roll_samples+on_samples-galvo_samples+buffer_samples] = -2*(daq.xamplitude[list(experiment.wavelengths)[ch]]/math.pi)*numpy.arctan(1.0/(numpy.tan(period_samples/2.0)))+daq.xoffset[list(experiment.wavelengths)[ch]]
	voltages[n2c['xgalvo'], roll_samples+on_samples-galvo_samples+buffer_samples:samples] = snap_back[0:samples-(roll_samples+on_samples-galvo_samples+buffer_samples)]
	voltages[n2c['xgalvo'], 0:roll_samples-galvo_samples-buffer_samples] = snap_back[samples-(roll_samples+on_samples-galvo_samples+buffer_samples):samples]

	# Y Galvo scanning:
	period_samples = numpy.linspace(0, 2*math.pi, on_samples+2*buffer_samples)
	snap_back = numpy.linspace(daq.yoffset[list(experiment.wavelengths)[ch]]+daq.yamplitude[list(experiment.wavelengths)[ch]], daq.yoffset[list(experiment.wavelengths)[ch]]-daq.yamplitude[list(experiment.wavelengths)[ch]], samples-on_samples-2*buffer_samples)
	voltages[n2c['ygalvo'],:] = daq.yoffset[list(experiment.wavelengths)[ch]]
	voltages[n2c['ygalvo'], roll_samples-galvo_samples-buffer_samples:roll_samples+on_samples-galvo_samples+buffer_samples] = -2*(daq.yamplitude[list(experiment.wavelengths)[ch]]/math.pi)*numpy.arctan(1.0/(numpy.tan(period_samples/2.0)))+daq.yoffset[list(experiment.wavelengths)[ch]]
	voltages[n2c['ygalvo'], roll_samples+on_samples-galvo_samples+buffer_samples:samples] = snap_back[0:samples-(roll_samples+on_samples-galvo_samples+buffer_samples)]
	voltages[n2c['ygalvo'], 0:roll_samples-galvo_samples-buffer_samples] = snap_back[samples-(roll_samples+on_samples-galvo_samples+buffer_samples):samples]
	
	# Laser modulation:
	voltages[n2c[list(experiment.wavelengths)[ch]], roll_samples+50:roll_samples+on_samples-50] = 5.0
	voltages[n2c[list(experiment.wavelengths)[ch]],0] = 0.0
	voltages[n2c[list(experiment.wavelengths)[ch]],-1] = 0.0

    # ETL scanning:
	voltages[n2c['etl'], :] = daq.eoffset[list(experiment.wavelengths)[ch]]

	# NI playing:
	voltages[n2c['daq_active'], :] = 3.0


	# for c in range(12):
	# 	plt.plot(voltages[c, :])
	# 	plt.legend(loc='upper right')
	# plt.show()

	# Check final voltages for sanity
	# Assert that voltages are safe
	assert (1.0/(1.0/on_time)) <= 800.0
	assert numpy.max(voltages[n2c['xgalvo'],:]) <= 5.0
	assert numpy.min(voltages[n2c['xgalvo'],:]) >= -5.0
	assert numpy.max(voltages[n2c['ygalvo'],:]) <= 5.0
	assert numpy.min(voltages[n2c['ygalvo'],:]) >= -5.0
	assert numpy.max(voltages[n2c['etl'],:]) <= 5.0
	assert numpy.min(voltages[n2c['etl'],:]) >= 0.0
	assert numpy.max(voltages[n2c['daq_active'],:]) <= 5.0
	assert numpy.min(voltages[n2c['daq_active'],:]) >= 0.0
	assert numpy.max(voltages[n2c[list(experiment.wavelengths)[ch]],:]) <= 5.0
	assert numpy.min(voltages[n2c[list(experiment.wavelengths)[ch]],:]) >= 0.0

	return voltages, (camera.expTime/1e3-2*roll_time)*1000

def zero_voltages(daq, camera):
	samples = int(daq.rate*camera.expTime/1e3) # number of samples for DAQ
	voltages = numpy.zeros((daq.num_channels, 2)) # create voltages array
	return voltages


def h5init(dest, camera, scan, experiment):

	f = h5py.File(dest,'a')

	res_list = [1,2,4,8]

	res_np = numpy.zeros((len(res_list), 3), dtype = 'float64')

	res_np[:,0] = res_list
	res_np[:,1] = res_list
	res_np[:,2] = res_list

	subdiv_np = numpy.zeros((len(res_list), 3), dtype = 'uint32')

	subdiv_np[:, 0] = scan.chunkSize1
	subdiv_np[:, 1] = scan.chunkSize2
	subdiv_np[:, 2] = scan.chunkSize3

	tgroup = f.create_group('/t00000')

	tile = 0

	for j in range(scan.zTiles):

		for k in range(scan.yTiles):

			for ch in range(scan.nWavelengths):

				idx = tile + scan.zTiles*scan.yTiles*ch

				sgroup = f.create_group('/s' + str(idx).zfill(2))
				resolutions = f.require_dataset('/s' + str(idx).zfill(2) + '/resolutions', 
												chunks = (res_np.shape), 
												dtype = 'float64', 
												shape = (res_np.shape), 
												data = res_np)

				subdivisions = f.require_dataset('/s' + str(idx).zfill(2) + '/subdivisions', 
												 chunks = (res_np.shape), 
												 dtype = 'uint32', 
												 shape = (subdiv_np.shape), 
												 data = subdiv_np)

				for z in range(len(res_list)-1, -1, -1):

					res = res_list[z]

					resgroup = f.create_group('/t00000/s' + str(idx).zfill(2) + '/' + str(z))

					if camera.quantSigma[list(experiment.wavelengths)[ch]] == 0:

						data = f.require_dataset('/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells', 
												 chunks = (scan.chunkSize1, 
												 		   scan.chunkSize2, 
												 		   scan.chunkSize3), 
												 dtype = 'int16', 
												 shape = numpy.ceil(numpy.divide([scan.nFrames, 
												 								  camera.Y, 
												 								  camera.X],
												 								  res)))	
					else:	
						data = f.require_dataset('/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells', 
												 chunks = (scan.chunkSize1, 
												 		   scan.chunkSize2, 
												 		   scan.chunkSize3), 
												 dtype = 'int16', 
												 shape = numpy.ceil(numpy.divide([scan.nFrames, 
												 								  camera.Y, 
												 								  camera.X],
												 								  res)), 
												 compression = 32016, 
												 compression_opts = (round(camera.quantSigma[list(experiment.wavelengths)[ch]]*1000), 
												 				     camera.compressionMode, 
												 				     round(2.1845*1000), 
												 				     0, 
												 				     round(1.5*1000))
												 )	

			tile += 1

	f.close()

def h5write(dest, img_3d, idx, ind1, ind2):

	f = h5py.File(dest,'a')

	res_list = [1,2,4,8]

	for z in range(len(res_list)):
		res = res_list[z]
		if res > 1:
			img_3d = skimage.transform.downscale_local_mean(img_3d, (2, 2, 2)).astype('uint16')

		if ind1 == 0:
			ind1_r = ind1
		else:
			ind1_r = numpy.ceil((ind1 + 1)/res - 1)

		data = f['/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells']	
		data[int(ind1_r):int(ind1_r+img_3d.shape[0])] = img_3d.astype('int16')
	
	f.close()

def write_xml(experiment, camera, scan):
	
	print("Writing BigDataViewer XML file...")

	c = scan.nWavelengths # number of channels
	tx = scan.yTiles # number of lateral x tiles
	ty = scan.zTiles # number of vertical y tiles
	t = tx*ty # total tiles

	ox = experiment.yWidth*1000 # offset along x in um
	oy = experiment.zWidth*1000 # offset along y in um

	sx = camera.sampling # effective pixel size in x direction
	sy = camera.sampling*numpy.cos(experiment.theta*numpy.pi/180.0) # effective pixel size in y direction
	sz = experiment.xWidth # effective pixel size in z direction (scan direction)

	scale_x = sx/sy # normalized scaling in x
	scale_y = sy/sy # normalized scaling in y
	scale_z = sz/sy # normalized scaning in z

	shear = -numpy.tan(experiment.theta*numpy.pi/180.0)*sy/sz # shearing based on theta and y/z pixel sizes

	f = open(experiment.drive + ':\\' + experiment.fname + '\\data.xml', 'w')
	f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	f.write('<SpimData version="0.2">\n')
	f.write('\t<BasePath type="relative">.</BasePath>\n')
	f.write('\t<SequenceDescription>\n')
	f.write('\t\t<ImageLoader format="bdv.hdf5">\n')
	f.write('\t\t\t<hdf5 type="relative">data.h5</hdf5>\n')
	f.write('\t\t</ImageLoader>\n')
	f.write('\t\t<ViewSetups>\n')

	for i in range (0, c):
		for j in range(0, t):
			ind = j+i*t
			if ind <= scan.yTiles*scan.zTiles*scan.nWavelengths:
				f.write('\t\t\t<ViewSetup>\n')
				f.write('\t\t\t\t<id>' + str(t*i+j) + '</id>\n')
				f.write('\t\t\t\t<name>' + str(t*i+j) + '</name>\n')
				f.write('\t\t\t\t<size>' + str(camera.X) + ' ' + str(camera.Y) + ' ' + str(scan.nFrames) + '</size>\n')
				f.write('\t\t\t\t<voxelSize>\n')
				f.write('\t\t\t\t\t<unit>um</unit>\n')
				f.write('\t\t\t\t\t<size>' + str(sx) + ' ' + str(sy) + ' ' + str(sz) + '</size>\n')
				f.write('\t\t\t\t</voxelSize>\n')
				f.write('\t\t\t\t<attributes>\n')
				f.write('\t\t\t\t\t<illumination>0</illumination>\n')
				f.write('\t\t\t\t\t<channel>' + str(i) + '</channel>\n')
				f.write('\t\t\t\t\t<tile>' + str(j) + '</tile>\n')
				f.write('\t\t\t\t\t<angle>0</angle>\n')
				f.write('\t\t\t\t</attributes>\n')
				f.write('\t\t\t</ViewSetup>\n')

	f.write('\t\t\t<Attributes name="illumination">\n')
	f.write('\t\t\t\t<Illumination>\n')
	f.write('\t\t\t\t\t<id>0</id>\n')
	f.write('\t\t\t\t\t<name>0</name>\n')
	f.write('\t\t\t\t</Illumination>\n')
	f.write('\t\t\t</Attributes>\n')
	f.write('\t\t\t<Attributes name="channel">\n')

	for i in range(0, c):
		ind = i
		if ind <= scan.nWavelengths:
			f.write('\t\t\t\t<Channel>\n')
			f.write('\t\t\t\t\t<id>' + str(i) + '</id>\n')
			f.write('\t\t\t\t\t<name>' + str(i) + '</name>\n')
			f.write('\t\t\t\t</Channel>\n')

	f.write('\t\t\t</Attributes>\n')
	f.write('\t\t\t<Attributes name="tile">\n')

	for i in range(0, t):
		ind = i
		if ind <= scan.yTiles*scan.zTiles:
			f.write('\t\t\t\t<Tile>\n')
			f.write('\t\t\t\t\t<id>' + str(i) + '</id>\n')
			f.write('\t\t\t\t\t<name>' + str(i) + '</name>\n')
			f.write('\t\t\t\t</Tile>\n')

	f.write('\t\t\t</Attributes>\n')
	f.write('\t\t\t<Attributes name="angle">\n')
	f.write('\t\t\t\t<Illumination>\n')
	f.write('\t\t\t\t\t<id>0</id>\n')
	f.write('\t\t\t\t\t<name>0</name>\n')
	f.write('\t\t\t\t</Illumination>\n')
	f.write('\t\t\t</Attributes>\n')
	f.write('\t\t</ViewSetups>\n')
	f.write('\t\t<Timepoints type="pattern">\n')
	f.write('\t\t\t<integerpattern>0</integerpattern>')
	f.write('\t\t</Timepoints>\n')
	f.write('\t\t<MissingViews />\n')
	f.write('\t</SequenceDescription>\n')

	f.write('\t<ViewRegistrations>\n')

	for i in range(0, c):
		for j in range(0, ty):
			for k in range(0, tx):

				ind = i*ty*tx + j*tx + k

				if ind <= scan.yTiles*scan.zTiles*scan.nWavelengths:

					shiftx = scale_x*(ox/sx)*k # shift tile in x, unit pixels
					shifty = -scale_y*(oy/sy)*j # shift tile in y, unit pixels

					f.write('\t\t<ViewRegistration timepoint="0" setup="' + str(ind) + '">\n')

					# affine matrix for translation of tiles into correct positions
					f.write('\t\t\t<ViewTransform type="affine">\n')
					f.write('\t\t\t\t<Name>Overlap</Name>\n')
					f.write('\t\t\t\t<affine>1.0 0.0 0.0 ' + str(shiftx) + ' 0.0 1.0 0.0 ' + str(shifty) + ' 0.0 0.0 1.0 0.0</affine>\n')
					f.write('\t\t\t</ViewTransform>\n')

					# affine matrix for scaling of tiles in orthogonal XYZ directions, accounting for theta and inter-frame spacing
					f.write('\t\t\t<ViewTransform type="affine">\n')
					f.write('\t\t\t\t<Name>Scale</Name>\n')
					f.write('\t\t\t\t<affine>' + str(scale_x) + ' 0.0 0.0 0.0 0.0 ' + str(scale_y) + ' 0.0 0.0 0.0 0.0 ' + str(scale_z) + ' 0.0</affine>\n')
					f.write('\t\t\t</ViewTransform>\n')

					# affine matrix for shearing of data within each tile
					f.write('\t\t\t<ViewTransform type="affine">\n')
					f.write('\t\t\t\t<Name>Deskew</Name>\n')
					f.write('\t\t\t\t<affine>1.0 0.0 0.0 0.0 0.0 1.0 ' + str(0.0) + ' 0.0 0.0 ' + str(shear) + ' 1.0 0.0</affine>\n')
					f.write('\t\t\t</ViewTransform>\n')

					f.write('\t\t</ViewRegistration>\n')

	f.write('\t</ViewRegistrations>\n')
	f.write('\t<ViewInterestPoints />\n')
	f.write('\t<BoundingBoxes />\n')
	f.write('\t<PointSpreadFunctions />\n')
	f.write('\t<StitchingResults />\n')
	f.write('\t<IntensityAdjustments />\n')
	f.write('</SpimData>')
	f.close()

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

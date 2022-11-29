#!/usr/bin/python

"""
LSM scanning code

# Adam Glaser 07/19
# Edited by Kevin Bishop 5/22
# Edited by Rob Serafin 9/22

"""
import numpy as np
import math
import h5py
import os.path
import skimage.transform
import pco
# Tiger or MS2000 are imported below based on stage model param
import hardware.ni as ni
import hardware.fw102c as fw102c
import hardware.skyra as skyra
from hardware.opto import Opto
import time as timer


class experiment(object):
    """
    A descriptive sentence

    Parameters
    ----------

    drive

    fname

    xMin

    xMax

    yMin

    YMax

    zMin

    zMax

    wavelengths

    powers

    attenuations

    theta

    overlap
    """

    def __init__(self,
                 experiment_dict):

        self.drive = experiment_dict['drive']
        self.fname = experiment_dict['fname']
        self.xMin = experiment_dict['xMin']
        self.xMax = experiment_dict['xMax']
        self.yMin = experiment_dict['yMin']
        self.yMax = experiment_dict['yMax']
        self.zMin = experiment_dict['zMin']
        self.zMax = experiment_dict['zMax']
        self.xWidth = experiment_dict['xWidth']
        self.yWidth = experiment_dict['yWidth']
        self.zWidth = experiment_dict['zWidth']
        self.wavelengths = experiment_dict['wavelengths']
        # self.powers = powers
        self.attenuations = experiment_dict['attenuations']
        self.theta = experiment_dict['theta']
        self.overlap = experiment_dict['overlap']


class scan(object):
    def __init__(self, experiment, camera):

        self.xLength = experiment.xMax - experiment.xMin  # mm
        self.yLength = round((experiment.yMax - experiment.yMin) /
                             experiment.yWidth) * experiment.yWidth  # mm
        self.zLength = round((experiment.zMax - experiment.zMin) /
                             experiment.zWidth) * experiment.zWidth  # mm
        self.xOff = experiment.xMax - self.xLength/2
        self.yOff = experiment.yMax - self.yLength/2
        self.zOff = experiment.zMin
        self.nFrames = int(np.floor(self.xLength/(experiment.xWidth/1000.0)))
        self.nWavelengths = len(experiment.wavelengths)
        self.yTiles = int(round(self.yLength/experiment.yWidth))
        self.zTiles = int(round(self.zLength/experiment.zWidth))

        # setup scan speed and chunk sizes
        self.scanSpeed = self.setScanSpeed(experiment.xWidth, camera.expTime)
        self.chunkSize1 = 256
        if self.chunkSize1 >= self.nFrames/8:
            self.chunkSize1 = np.floor(self.nFrames/8)

        self.chunkSize2 = 16

        if self.chunkSize2 >= camera.Y/8:
            self.chunkSize2 = np.floor(camera.Y/8)

        self.chunkSize3 = 256
        if self.chunkSize3 >= camera.X/8:
            self.chunkSize3 = np.floor(camera.X/8)

        self.blockSize = int(2*self.chunkSize1)

    def setScanSpeed(self, xWidth, expTime):

        speed = xWidth/(1.0/(1.0/((expTime + 10.0e-3)/1000.0))*1000.0)
        return speed


# TODO: Change name to camera_settings
class camera(object):
    def __init__(self,
                 camera_dict):
        self.number = camera_dict['number']
        self.X = camera_dict['X']
        self.Y = camera_dict['Y']
        self.sampling = camera_dict['sampling']
        self.expTime = camera_dict['expTime']
        self.triggerMode = camera_dict['triggerMode']
        self.acquireMode = camera_dict['acquireMode']
        self.shutterMode = camera_dict['shutterMode']
        self.compressionMode = camera_dict['compressionMode']
        self.B3Denv = camera_dict['B3Denv']
        self.quantSigma = camera_dict['quantSigma']


class daq(object):
    def __init__(self,
                 daq_dict):

        self.rate = daq_dict['rate']
        self.board = daq_dict['board']
        # self.name = daq_dict['name']
        self.num_channels = daq_dict['num_channels']
        self.names_to_channels = daq_dict['names_to_channels']

        self.xmin = daq_dict['xmin']
        self.xmax = daq_dict['xmax']
        self.xpp = daq_dict['xpp']
        self.ymin = daq_dict['ymin']
        self.ymax = daq_dict['ymax']
        self.ypp = daq_dict['ypp']
        self.econst = daq_dict['econst']


class laser(object):
    def __init__(self,
                 laser_dict):

        self.port = laser_dict['port']
        self.rate = laser_dict['rate']
        self.names_to_channels = laser_dict['names_to_channels']
        self.max_powers = laser_dict['max_powers']
        self.skyra_system_name = laser_dict['skyra_system_name']
        self.use_LUT = laser_dict['use_LUT']
        self.min_currents = laser_dict['min_currents']
        self.max_currents = laser_dict['max_currents']
        self.strobing = laser_dict['strobing']

    def initialize(self, experiment, scan):

        print('initializing laser')
        print('using laser parameters use_LUT=' + str(self.use_LUT) +
              ' system_name=' + self.skyra_system_name)
        input('If this is NOT correct, press CTRL+C to exit and avoid damage' +
              ' to the laser. If this correct, press Enter to continue.')

        min_currents_sk_num = {}
        max_currents_sk_num = {}

        for ch in experiment.wavelengths:  # ch is wavelength as a string
            min_currents_sk_num[self.names_to_channels[ch]] = \
                self.min_currents[ch]
            max_currents_sk_num[self.names_to_channels[ch]] = \
                self.max_currents[ch]

        skyraLaser = skyra.Skyra(baudrate=self.rate,
                                 port=self.port)
        skyraLaser.setMinCurrents(min_currents_sk_num)
        skyraLaser.setMaxCurrents(max_currents_sk_num)
        skyraLaser.setUseLUT(self.use_LUT)
        skyraLaser.importLUT()

        for ch in list(self.names_to_channels):
            skyraLaser.setModulationOn(self.names_to_channels[ch])
            skyraLaser.setDigitalModulation(self.names_to_channels[ch], 1)

            #  new, to ensure analog mod is not active
            skyraLaser.setAnalogModulation(self.names_to_channels[ch], 0)
        for ch in list(experiment.wavelengths):
            skyraLaser.setModulationHighCurrent(self.names_to_channels[ch],
                                                experiment.wavelengths[ch])
            skyraLaser.turnOn(self.names_to_channels[ch])
        for ch in list(experiment.wavelengths):
            skyraLaser.setModulationLowCurrent(self.names_to_channels[ch], 0)
            highest_power = experiment.wavelengths[ch] / \
                np.exp(-scan.zTiles * experiment.zWidth /
                       experiment.attenuations[ch])
            if skyraLaser.use_LUT:
                maxPower = skyraLaser.LUT['ch' + str(self.names_to_channels[ch])]['power'][-1]
            else:
                maxPower = self.max_powers[ch]
            if highest_power > maxPower:
                raise Exception('Power will be out of range at final Z ' +
                                'position. Adjust power or attenuation.\n')

        print('finished initializing laser')
        return skyraLaser


class etl(object):
    def __init__(self,
                 etl_dict):
        self.port = etl_dict['port']


class wheel(object):
    def __init__(self,
                 wheel_dict):
        self.port = wheel_dict['port']
        self.rate = wheel_dict['rate']
        self.names_to_channels = wheel_dict['names_to_channels']


class stage(object):
    def __init__(self,
                 stage_dict):
        self.port = stage_dict['port']
        self.rate = stage_dict['rate']
        self.model = stage_dict['model']

        # Should check the velocity and acceration, I think this
        # really shouldn't be part of the init since it's set to different
        # values in various places
        self.settings = {'backlash': 0.0,
                         'velocity': 1.0,
                         'acceleration': 100
                         }
        self.axes = ('X', 'Y', 'Z')

    def initialize(self):

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
        return xyzStage, initialPos


# TODO: break apart into smaller pieces:
# initialize hardware
# scan tiles

def scan3D(experiment, camera, daq, laser, wheel, etl, stage):

    # ROUND SCAN DIMENSIONS & SETUP IMAGING SESSION
    session = scan(experiment, camera)

    print('made session')
    # SETUP DATA DIRECTORY
    os.makedirs(experiment.drive + ':\\' + experiment.fname)
    dest = experiment.drive + ':\\' + experiment.fname + '\\data.h5'

    #  CONNECT XYZ STAGE
    xyzStage, initialPos = stage.initialize()
    print(xyzStage)

    #  INITIALIZE H5 FILE
    h5init(dest, camera, session, experiment)
    write_xml(experiment=experiment, camera=camera, scan=session)

    # CONNECT NIDAQ
    waveformGenerator = ni.waveformGenerator(daq=daq,
                                             camera=camera,
                                             triggered=True)

    # CONNECT LASER

    # according to the manual, you should wait for 2min after setting
    # laser 1 (561) to mod mode for power to stabalize. Consider adding this in
    # TODO: disentangle laser and experiment attributes
    skyraLaser = laser.initialize(experiment, session)
    print(skyraLaser)

    # CONNECT FILTER WHEEL

    fWheel = fw102c.FW102C(baudrate=wheel.rate, port=wheel.port)
    print(fWheel)

    # CONNECT TUNBALE LENS

    etl = Opto(port=etl.port)
    etl.connect()
    etl.mode('analog')
    print(etl)

    # CONNECT CAMERA
    # TODO: setup separate hardware initialization method within camera

    cam = pco.Camera(camera_number=camera.number)

    cam.configuration = {'exposure time': camera.expTime*1.0e-3,
                         'roi': (1,
                                 1023-round(camera.Y/2),
                                 2060,
                                 1026+round(camera.Y/2)),
                         'trigger': camera.triggerMode,
                         'acquire': camera.acquireMode,
                         'pixel rate': 272250000}

    cam.record(number_of_images=session.nFrames, mode='sequence non blocking')
    # possibly change mode to ring buffer??

    # IMAGING LOOP

    ring_buffer = np.zeros((session.blockSize,
                           camera.Y,
                           camera.X),
                           dtype=np.uint16)

    # print('made ring buffer')
    tile = 0
    previous_tile_time = 0
    previous_ram = 0

    start_time = timer.time()

    xPos = session.xLength/2.0 - session.xOff

    for j in range(session.zTiles):

        zPos = j*experiment.zWidth + session.zOff
        xyzStage.setVelocity('Z', 0.1)
        xyzStage.goAbsolute('Z', zPos, False)

        for k in range(session.yTiles):

            yPos = session.yOff - session.yLength / 2.0 + \
                k*experiment.yWidth + experiment.yWidth / 2.0

            xyzStage.setVelocity('Y', 1.0)
            xyzStage.goAbsolute('Y', yPos, False)

            for ch in range(session.nWavelengths):

                wave_str = list(experiment.wavelengths)[ch]
                # wave_str is wavelength in nm as a string, e.g. '488'

                # ch is order of wavelenghts in main (an integer 0 -> X)
                #   (NOT necessarily Skyra channel number)

                xyzStage.setVelocity('X', 1.0)
                xPos = session.xLength/2.0 - session.xOff
                xyzStage.goAbsolute('X', -xPos, False)

                # CHANGE FILTER

                fWheel.setPosition(wheel.names_to_channels[wave_str])

                # START SCAN

                skyraLaser.setModulationHighCurrent(
                    laser.names_to_channels[wave_str],
                    experiment.wavelengths[wave_str] /
                    np.exp(-j*experiment.zWidth /
                           experiment.attenuations[wave_str])
                    )

                voltages, rep_time = write_voltages(daq=daq,
                                                    laser=laser,
                                                    camera=camera,
                                                    experiment=experiment,
                                                    ch=ch)

                waveformGenerator.ao_task.write(voltages)

                print('Starting tile ' + str((tile)*session.nWavelengths+ch+1),
                      '/',
                      str(session.nWavelengths*session.zTiles*session.yTiles))
                print('y position: ' + str(yPos) + ' mm')
                print('z position: ' + str(zPos) + ' mm')
                tile_start_time = timer.time()

                xyzStage.setScanR(-xPos, -xPos + session.xLength)
                xyzStage.setScanV(yPos)

                response = xyzStage.getMotorStatus()
                while response[0] == 'B':
                    response = xyzStage.getMotorStatus()

                xyzStage.setVelocity('X', session.scanSpeed)
                xyzStage.setVelocity('Y', session.scanSpeed)
                xyzStage.setVelocity('Z', session.scanSpeed)

                waveformGenerator.ao_task.start()
                cam.start()
                xyzStage.scan(False)
                skyraLaser.turnOn(laser.names_to_channels[
                    list(experiment.wavelengths)[ch]])

                # START IMAGING LOOP

                num_acquired = 0
                num_acquired_counter = 0
                num_acquired_previous = 0

                # while num_acquired < scan.nFrames: #original version.
                # for some reason code frequently (but not always)
                # gets stuck on cam.wait_for_next_image(num_acquired),
                # like cam is a frame or two ahead of code
                while num_acquired < session.nFrames - 100:

                    # print('you\'ve got an image!', num_acquired, 'of',
                    #       session.nFrames, 'total')
                    cam.wait_for_next_image(num_acquired)

                    if num_acquired_counter == int(session.blockSize):
                        print('Saving frames: ',
                              str(num_acquired_previous),
                              ' - ',
                              str(num_acquired))
                        print('Tile: ' + str(tile))
                        h5write(dest,
                                ring_buffer,
                                tile + session.zTiles*session.yTiles*ch,
                                num_acquired_previous, num_acquired)
                        num_acquired_counter = 0
                        num_acquired_previous = num_acquired
                        temp = cam.image(num_acquired)[0]

                        ring_buffer[num_acquired_counter] = \
                            temp[2:camera.Y + 2, 1024 - int(camera.X / 2):1024
                                 - int(camera.X / 2) + camera.X]

                    else:

                        temp = cam.image(num_acquired)[0]

                        ring_buffer[num_acquired_counter] = \
                            temp[2:camera.Y + 2, 1024 - int(camera.X / 2):1024
                                 - int(camera.X / 2) + camera.X]

                    if num_acquired == session.nFrames-1:
                        print('Saving frames: ',
                              str(num_acquired_previous),
                              ' - ',
                              str(session.nFrames))

                        h5write(dest,
                                ring_buffer[0:num_acquired_counter+1],
                                tile + session.zTiles*session.yTiles*ch,
                                num_acquired_previous,
                                session.nFrames)

                    num_acquired += 1
                    num_acquired_counter += 1

                waveformGenerator.ao_task.stop()
                waveformGenerator.write_zeros(daq=daq)
                # For some reason this write_zeros works but the above doesn't?
                # laser stops and starts appropriately with this one active
                # and the top write_zeros() commented out

                # skyraLaser.turnOff(list(experiment.wavelengths)[ch]) # old code, which is a wrong command
                skyraLaser.turnOff(laser.names_to_channels[list(experiment.wavelengths)[ch]])
                cam.stop()

                tile_end_time = timer.time()
                tile_time = tile_end_time - tile_start_time
                print('Tile time: ' + str(round((tile_time/60), 3)) + " min")
                tiles_remaining = session.nWavelengths * session.zTiles * \
                    session.yTiles - (tile * session.nWavelengths + ch + 1)

                if tiles_remaining != 0:
                    print('Estimated time remaining: ',
                          str(round((tile_time*tiles_remaining/3600), 3)),
                          " hrs")

            tile += 1

    end_time = timer.time()

    print("Total time = ",
          str(round((end_time - start_time)/3600, 3)),
          " hrs")

    response = xyzStage.getMotorStatus()
    while response[0] == 'B':
        response = xyzStage.getMotorStatus()

    cam.close()
    etl.close(soft_close=True)
    # waveformGenerator.counter_task.close()
    waveformGenerator.ao_task.close()
    xyzStage.shutDown()


def write_voltages(daq,
                   laser,
                   camera,
                   experiment,
                   ch):

    print('writing voltages')
    n2c = daq.names_to_channels
    wave_key = list(experiment.wavelengths)[ch]  # wavelength as a string

    # convert max / min / peak-to-peak (DAQExpress convention)
    # to offset / amplitude
    xoffset = (daq.xmax[wave_key] + daq.xmin[wave_key]) / 2
    xamplitude = daq.xpp[wave_key] / 2
    yoffset = (daq.ymax[wave_key] + daq.ymin[wave_key]) / 2
    yamplitude = daq.ypp[wave_key] / 2
    eoffset = daq.econst[wave_key]

    samples = int(daq.rate*camera.expTime/1e3)  # number of samples for DAQ

    line_time = 9.76/1.0e6  # seconds, constant for pco.edge camera
    roll_time = line_time*camera.Y/2.0  # chip rolling time in seconds
    roll_samples = int(np.floor(roll_time*daq.rate))  # rolling samples

    on_time = camera.expTime/1e3 - roll_time  # ON time for strobing laser
    on_samples = int(np.floor(on_time*daq.rate))  # ON samples

    galvo_time = 365/1.0e6  # galvo delay time
    galvo_samples = int(np.floor(galvo_time*daq.rate))

    buffer_time = 50/1.0e6
    buffer_samples = int(np.floor(buffer_time*daq.rate))

    voltages = np.zeros((daq.num_channels, samples))  # create voltages array

    # X Galvo scanning:
    period_samples = np.linspace(0,
                                 2 * math.pi, on_samples + 2 * buffer_samples)
    snap_back = np.linspace(xoffset + xamplitude,
                            xoffset - xamplitude,
                            samples - on_samples - 2 * buffer_samples)
    voltages[n2c['xgalvo'], :] = xoffset
    voltages[n2c['xgalvo'],
             roll_samples - galvo_samples - buffer_samples:
             roll_samples + on_samples - galvo_samples + buffer_samples] = \
        -2 * (xamplitude / math.pi) * \
        np.arctan(1.0 / (np.tan(period_samples / 2.0))) + xoffset
    voltages[n2c['xgalvo'],
             roll_samples + on_samples - galvo_samples + buffer_samples:
             samples] = \
        snap_back[0:samples - (roll_samples + on_samples - galvo_samples +
                  buffer_samples)]
    voltages[n2c['xgalvo'],
             0:roll_samples - galvo_samples - buffer_samples] = \
        snap_back[samples - (roll_samples + on_samples - galvo_samples +
                  buffer_samples):samples]

    # Y Galvo scanning:
    period_samples = np.linspace(0,
                                 2 * math.pi, on_samples + 2 * buffer_samples)
    snap_back = np.linspace(yoffset + yamplitude,
                            yoffset - yamplitude,
                            samples - on_samples - 2 * buffer_samples)
    voltages[n2c['ygalvo'], :] = yoffset
    voltages[n2c['ygalvo'],
             roll_samples - galvo_samples - buffer_samples:
             roll_samples + on_samples-galvo_samples + buffer_samples] = \
        -2 * (yamplitude / math.pi) * \
        np.arctan(1.0 / (np.tan(period_samples / 2.0))) + yoffset
    voltages[n2c['ygalvo'],
             roll_samples + on_samples - galvo_samples + buffer_samples:
             samples] = \
        snap_back[0:samples - (roll_samples + on_samples - galvo_samples +
                  buffer_samples)]
    voltages[n2c['ygalvo'],
             0:roll_samples - galvo_samples - buffer_samples] = \
        snap_back[samples - (roll_samples + on_samples - galvo_samples +
                  buffer_samples):samples]

    # Laser modulation:
    if laser.strobing == 'ON':
        voltages[n2c[wave_key],
                 roll_samples + 50:roll_samples + on_samples - 50] = 5.0
        voltages[n2c[wave_key], 0] = 0.0
        voltages[n2c[wave_key], -1] = 0.0
    elif laser.strobing == 'OFF':
        voltages[n2c[wave_key], :] = 5.0
    else:
        raise Exception('laser.strobing invalid, must be \'ON\' or \'OFF\'')

    # ETL scanning:
    voltages[n2c['etl'], :] = eoffset

    # NI playing:
    voltages[n2c['daq_active'], :] = 3.0

    # for c in range(12):
    # 	plt.plot(voltages[c, :])
    # 	plt.legend(loc='upper right')
    # plt.show()

    # Check final voltages for sanity
    # Assert that voltages are safe
    assert (1.0/(1.0/on_time)) <= 800.0
    assert np.max(voltages[n2c['xgalvo'], :]) <= 5.0
    assert np.min(voltages[n2c['xgalvo'], :]) >= -5.0
    assert np.max(voltages[n2c['ygalvo'], :]) <= 5.0
    assert np.min(voltages[n2c['ygalvo'], :]) >= -5.0
    assert np.max(voltages[n2c['etl'], :]) <= 5.0
    assert np.min(voltages[n2c['etl'], :]) >= 0.0
    assert np.max(voltages[n2c['daq_active'], :]) <= 5.0
    assert np.min(voltages[n2c['daq_active'], :]) >= 0.0
    assert np.max(voltages[n2c[wave_key], :]) <= 5.0
    assert np.min(voltages[n2c[wave_key], :]) >= 0.0

    print('wrote voltages')

    return voltages, (camera.expTime/1e3-2*roll_time)*1000


def zero_voltages(daq, camera):
    # samples = int(daq.rate*camera.expTime/1e3)  # number of samples for DAQ
    voltages = np.zeros((daq.num_channels, 2))  # create voltages array
    return voltages


def h5init(dest, camera, scan, experiment):

    f = h5py.File(dest, 'a')

    res_list = [1, 2, 4, 8]

    res_np = np.zeros((len(res_list), 3), dtype='float64')

    res_np[:, 0] = res_list
    res_np[:, 1] = res_list
    res_np[:, 2] = res_list

    subdiv_np = np.zeros((len(res_list), 3), dtype='uint32')

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
                                                chunks=(res_np.shape),
                                                dtype='float64',
                                                shape=(res_np.shape),
                                                data=res_np)

                subdivisions = f.require_dataset('/s' + str(idx).zfill(2) + '/subdivisions',
                                                 chunks=(res_np.shape),
                                                 dtype='uint32',
                                                 shape=(subdiv_np.shape),
                                                 data=subdiv_np)

                for z in range(len(res_list)-1, -1, -1):

                    res = res_list[z]

                    resgroup = f.create_group('/t00000/s' + str(idx).zfill(2) + '/' + str(z))

                    if camera.quantSigma[list(experiment.wavelengths)[ch]] == 0:

                        data = f.require_dataset('/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells', 
                                                 chunks=(scan.chunkSize1,
                                                         scan.chunkSize2,
                                                         scan.chunkSize3),
                                                 dtype='int16',
                                                 shape=np.ceil(np.divide([scan.nFrames,
                                                                          camera.Y,
                                                                          camera.X],
                                                                          res)
                                                                          )
                                                                          )
                    else:
                        if ((camera.B3Denv != '') and
                            (camera.B3Denv != os.environ['CONDA_DEFAULT_ENV'])
                            ):
                            print('Warning: B3D is active but the ' +
                                  'current conda environment is: ' +
                                  os.environ['CONDA_DEFAULT_ENV'])
                            print('Press CTRL + C to exit and run \'conda' +
                                  ' activate ' + camera.B3Denv + '\' before ' +
                                  'running lsm-python-main.py')
                            input('Press Enter to override this warning' +
                                  ' and continue anyways')

                        data = f.require_dataset('/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells',
                                chunks=(scan.chunkSize1,
                                        scan.chunkSize2,
                                        scan.chunkSize3),
                                dtype='int16',
                                shape=np.ceil(np.divide([scan.nFrames,
                                                        camera.Y,
                                                        camera.X],
                                                        res)),
                                compression=32016,
                                compression_opts=(round(camera.quantSigma[list(experiment.wavelengths)[ch]]*1000),
                                                    camera.compressionMode,
                                                    round(2.1845*1000),
                                                    0, 
                                                    round(1.5*1000))
                                                 )

            tile += 1

    f.close()


def h5write(dest, img_3d, idx, ind1, ind2):

    f = h5py.File(dest, 'a')

    res_list = [1, 2, 4, 8]

    for z in range(len(res_list)):
        res = res_list[z]
        if res > 1:
            img_3d = skimage.transform.downscale_local_mean(img_3d,
                                                            (2, 2, 2)
                                                            ).astype('uint16')

        if ind1 == 0:
            ind1_r = ind1
        else:
            ind1_r = np.ceil((ind1 + 1)/res - 1)

        data = f['/t00000/s' + str(idx).zfill(2) + '/' + str(z) + '/cells']
        data[int(ind1_r):int(ind1_r+img_3d.shape[0])] = img_3d.astype('int16')

    f.close()


def write_xml(experiment, camera, scan):

    print("Writing BigDataViewer XML file...")

    c = scan.nWavelengths  # number of channels
    tx = scan.yTiles  # number of lateral x tiles
    ty = scan.zTiles  # number of vertical y tiles
    t = tx*ty  # total tiles

    ox = experiment.yWidth*1000  # offset along x in um
    oy = experiment.zWidth*1000  # offset along y in um

    sx = camera.sampling  # effective pixel size in x direction

    # effective pixel size in y direction
    sy = camera.sampling*np.cos(experiment.theta*np.pi/180.0)

    # effective pixel size in z direction (scan direction)
    sz = experiment.xWidth

    scale_x = sx/sy  # normalized scaling in x
    scale_y = sy/sy  # normalized scaling in y
    scale_z = sz/sy  # normalized scaning in z

    # shearing based on theta and y/z pixel sizes
    shear = -np.tan(experiment.theta*np.pi/180.0)*sy/sz

    f = open(experiment.drive + ':\\' + experiment.fname + '\\data.xml', 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<SpimData version="0.2">\n')
    f.write('\t<BasePath type="relative">.</BasePath>\n')
    f.write('\t<SequenceDescription>\n')
    f.write('\t\t<ImageLoader format="bdv.hdf5">\n')
    f.write('\t\t\t<hdf5 type="relative">data.h5</hdf5>\n')
    f.write('\t\t</ImageLoader>\n')
    f.write('\t\t<ViewSetups>\n')

    for i in range(0, c):
        for j in range(0, t):
            ind = j+i*t
            if ind <= scan.yTiles*scan.zTiles*scan.nWavelengths:
                f.write('\t\t\t<ViewSetup>\n')
                f.write('\t\t\t\t<id>' + str(t*i+j) + '</id>\n')
                f.write('\t\t\t\t<name>' + str(t*i+j) + '</name>\n')
                f.write('\t\t\t\t<size>' + str(camera.X) + ' ' + str(camera.Y)
                        + ' ' + str(scan.nFrames) + '</size>\n')
                f.write('\t\t\t\t<voxelSize>\n')
                f.write('\t\t\t\t\t<unit>um</unit>\n')
                f.write('\t\t\t\t\t<size>' + str(sx) + ' ' + str(sy) + ' '
                        + str(sz) + '</size>\n')
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

                    shiftx = scale_x*(ox/sx)*k  # shift tile in x, unit pixels
                    shifty = -scale_y*(oy/sy)*j  # shift tile in y, unit pixels

                    f.write('\t\t<ViewRegistration timepoint="0" setup="'
                            + str(ind) + '">\n')

                    # affine matrix for translation of
                    # tiles into correct positions
                    f.write('\t\t\t<ViewTransform type="affine">\n')
                    f.write('\t\t\t\t<Name>Overlap</Name>\n')
                    f.write('\t\t\t\t<affine>1.0 0.0 0.0 ' + str(shiftx)
                            + ' 0.0 1.0 0.0 ' + str(shifty)
                            + ' 0.0 0.0 1.0 0.0</affine>\n')
                    f.write('\t\t\t</ViewTransform>\n')

                    # affine matrix for scaling of tiles in orthogonal
                    # XYZ directions, accounting for theta and
                    # inter-frame spacing
                    f.write('\t\t\t<ViewTransform type="affine">\n')
                    f.write('\t\t\t\t<Name>Scale</Name>\n')
                    f.write('\t\t\t\t<affine>' + str(scale_x)
                            + ' 0.0 0.0 0.0 0.0 ' + str(scale_y)
                            + ' 0.0 0.0 0.0 0.0 ' + str(scale_z)
                            + ' 0.0</affine>\n')
                    f.write('\t\t\t</ViewTransform>\n')

                    # affine matrix for shearing of data within each tile
                    f.write('\t\t\t<ViewTransform type="affine">\n')
                    f.write('\t\t\t\t<Name>Deskew</Name>\n')
                    f.write('\t\t\t\t<affine>1.0 0.0 0.0 0.0 0.0 1.0 '
                            + str(0.0) + ' 0.0 0.0 ' + str(shear)
                            + ' 1.0 0.0</affine>\n')
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

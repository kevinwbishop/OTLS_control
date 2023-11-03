import pco
import lsmfx

# This could be cleaned up, probably lots of this is not needed

print('Configuring camera')
um_per_px = 0.376

camera_dict = {
    'number': 0,  # int e.g. 0
    'Y': 2044,  # frame size in pixels - 2044 max Y
    'X': 2048,
    'sampling': um_per_px,
    'shutterMode': 'top middle bottom middle',  ### NOT ACTUALLY USED
    'triggerMode': 'external exposure start & software trigger', # previously 'auto sequence'
    #'triggerMode': 'auto sequence', # previously 'auto sequence'
    'acquireMode': 'auto', # previously 'external'
    'compressionMode': 1,
    'B3Denv': '',   # name of required conda env when B3D is active.
                    # e.g. 'image'. Leave as empty string to allow any env.
    'freq': 17.0,   # Hz, 17 is the max. Use caution when changing
    'slitSize': 20, #not used here!!
    'quantSigma': {'405': 1.0,
                   '488': 1.0,
                   '561': 1.0,
                   '638': 1.0},
    'expFraction': 0.35
}

camera = lsmfx.camera(camera_dict)


pco_cam = pco.Camera(camera_number=camera.number)


pco_cam.configuration = {'exposure time': 10*1.0e-3, # converting ms (camera.expTime) to sec (pco_cam.configuration{'exposure time})
                        'roi': (1,
                                1023-round(camera.Y/2),
                                2060,
                                1026+round(camera.Y/2)),
                        'trigger': camera.triggerMode,
                        'acquire': camera.acquireMode,
                        'pixel rate': 272250000}         # 95333333 (slow scan) or 272250000 (fast scan) - default is slow scan.
                                                        # Documentation says you should use slow scan for lightsheet mode, not sure why (doesn't seem to make a difference)


# commands to set light-sheet mode

freq = 10    #Hz slow scan, max is ~4Hz. Fast scan, max is 10Hz
#line_time = (0.35*1/freq)/camera.Y   #sec
line_time = 20e-6

# parameter='on': turns on light-sheet mode
# line_time=20e-6: sets time before going to next line in sec.
#   Min values: 17 µs @ 286 MHz (fast scan), 40 µs @ 95.3 MHz (slow scan), Max value: 100ms
pco_cam.sdk.set_cmos_line_timing(parameter='on', line_time=line_time)

# lines_exposure=10: number of lines to expose at once
# lines_delay=0: default is zero, not clear what this does yet
pco_cam.sdk.set_cmos_line_exposure_delay(lines_exposure=50,lines_delay=0)

# interface='edge': reverses readout direction. Seems like setting to 'edge' is a requirement
# format='top bottom': tells camera to read whole frame top to bottom (as opposed to simultaneously reading two ROIs)
pco_cam.sdk.set_interface_output_format(interface='edge',format='top bottom')

# Note on set_interface_output_format from SDK manual:
# For all cameras with Camera Link interface it is recommended to use PCO_SetTransferParameter function instead of this 
# function, because the driver layer must be informed about any changes in readout format to successfully rearrange the 
# image data.


print(pco_cam.sdk.get_cmos_line_exposure_delay())
print(pco_cam.sdk.get_cmos_line_timing())
print(pco_cam.sdk.get_interface_output_format(interface='edge'))
print('Configuration complete')
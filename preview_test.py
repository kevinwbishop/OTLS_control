import pco
import lsmfx
import numpy as np
from PIL import Image
import scipy
import json
import cv2
import threading
import sys

#%matplotlib notebook
import matplotlib.pyplot as plt

## note: you can run the PCO cam in external trigger if you start a record (but not light sheet)

class preview(object):

    def __init__(self):
        # CAMERA PARAMETERS
        um_per_px = 0.376  # microns (0.43 for water, 0.376 for ECi)

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
            'B3Denv': '',  # name of required conda env when B3D is active.
                            # e.g. 'image'. Leave as empty string to allow any env.
            'expTime': 10.0, # in ms, minimum is 0.1ms (100,000ns)
            'slitSize': 20, #not used here!!
            'quantSigma': {'405': 1.0,
                        '488': 1.0,
                        '561': 1.0,
                        '638': 1.0}
        }

        self.camera = lsmfx.camera(camera_dict)
        self.pco_cam = pco.Camera(camera_number=self.camera.number)

        self.pco_cam.configuration = {'exposure time': 10*1.0e-3, # converting ms (camera.expTime) to sec (pco_cam.configuration{'exposure time})
                                      'roi': (1,
                                              1023-round(self.camera.Y/2),
                                              2060,
                                              1026+round(self.camera.Y/2)),
                                      'trigger': self.camera.triggerMode,
                                      'acquire': self.camera.acquireMode,
                                      'pixel rate': 272250000}         # 95333333 (slow scan) or 272250000 (fast scan) - default is slow scan.
                                                                    # Documentation says you should use slow scan for lightsheet mode, not sure why (doesn't seem to make a difference)


        # commands to set light-sheet mode

        freq = 10    #Hz slow scan, max is ~4Hz. Fast scan, max is 10Hz
        #line_time = (0.35*1/freq)/self.camera.Y   #sec
        line_time = 20e-6

        # parameter='on': turns on light-sheet mode
        # line_time=20e-6: sets time before going to next line in sec.
        #   Min values: 17 µs @ 286 MHz (fast scan), 40 µs @ 95.3 MHz (slow scan), Max value: 100ms
        self.pco_cam.sdk.set_cmos_line_timing(parameter='on', line_time=line_time)

        # lines_exposure=10: number of lines to expose at once
        # lines_delay=0: default is zero, not clear what this does yet
        self.pco_cam.sdk.set_cmos_line_exposure_delay(lines_exposure=50,lines_delay=0)

        # interface='edge': reverses readout direction. Seems like setting to 'edge' is a requirement
        # format='top bottom': tells camera to read whole frame top to bottom (as opposed to simultaneously reading two ROIs)
        self.pco_cam.sdk.set_interface_output_format(interface='edge',format='top bottom')

        # Note on set_interface_output_format from SDK manual:
        # For all cameras with Camera Link interface it is recommended to use PCO_SetTransferParameter function instead of this 
        # function, because the driver layer must be informed about any changes in readout format to successfully rearrange the 
        # image data.


        print(self.pco_cam.sdk.get_cmos_line_exposure_delay())
        print(self.pco_cam.sdk.get_cmos_line_timing())
        print(self.pco_cam.sdk.get_interface_output_format(interface='edge'))

        self.stop_event = threading.Event()
        self.preview_thread = threading.Thread(target=self.open_preview, args=())
        self.preview_thread.daemon = True
        self.preview_thread.start()
        print('Starting preview')
        #self._stop = threading.Event() 




    # fig, ax = plt.subplots()

    def open_preview(self):
        buffer_size = 25

        self.pco_cam.record(number_of_images=buffer_size, mode='ring buffer')
        self.pco_cam.start()

        win_size = cv2.WINDOW_NORMAL        # WINDOW_NORMAL or WINDOW_AUTOSIZE
        win_ratio = cv2.WINDOW_KEEPRATIO    # WINDOW_FREERATIO or WINDOW_KEEPRATIO
        win_GUI = cv2.WINDOW_GUI_EXPANDED     # WINDOW_GUI_NORMAL or WINDOW_GUI_EXPANDED
        win_settings = win_size | win_ratio | win_GUI
        print("{:08b}".format(win_settings))

        cv2.namedWindow('Live Preview', win_settings)
        cv2.setMouseCallback('Live Preview',self.get_pix_val)
        self.mouse_posX = 0
        self.mouse_posY = 0
        
        num_acquired = 0

        print('starting image loop')
        while not self.stop_event.is_set():
            self.pco_cam.wait_for_next_image(num_acquired)
            image = self.pco_cam.image(0)[0][2:self.camera.Y + 2,
                                                  1024 - int(self.camera.X / 2):1024
                                                  - int(self.camera.X / 2) + self.camera.X]
            # print('You\'ve got an image!', num_acquired + 1, end='\r')
            #     ax.imshow(image,'gray',interpolation='nearest',vmin=win_min,vmax=win_max)
            #     fig.show()


            image_norm = cv2.normalize(image,None,0,2**16,cv2.NORM_MINMAX)

            image_norm = self._rescale(image)

            # text = 'Hi there'
            # cv2.putText(image_norm,
            #             text,
            #             (50,50),
            #             fontFace = cv2.FONT_HERSHEY_COMPLEX,
            #             fontScale = 1.5,
            #             color = (0,0,0),
            #             lineType = cv2.LINE_AA)
            cv2.imshow('Live Preview', image_norm)
            cv2.waitKey(1)

            x = self.mouse_posX
            y = self.mouse_posY

            out_string = ('X: ' + str(x) + 
                        ' Y: ' + str(y) +
                        ' Val: ' + str(image[x,y]))
            
            cv2.setWindowTitle('Live Preview', out_string)


            #out_string = out_string.ljust(70)
            #print(out_string, end='\r')
            #cv2.resizeWindow('custom window', 200, 200)

            num_acquired += 1
            

    
    def close_preview(self):
        print('Closing preview')
        self.stop_event.set()   # end thread running preview
        cv2.destroyAllWindows()
        self.pco_cam.stop()
        self.pco_cam.close()

    def get_pix_val(self,event,x,y,flags,param):

        # This works BUT only updates when the mouse moves (not w/ each frame)
        # Need to check that coordiantes are not flipped etc.

        # TODO: figure out how to only update pix val when mouse is within the window
        if event == cv2.EVENT_MOUSEMOVE:
            # out_string = ('X: ' + str(x) + ' Y: ' + str(y) +
            #               ' Val: ' + str(self.image[x,y]))
            # out_string = out_string.ljust(70)
            # print(out_string, end='\r')
            self.mouse_posX = x
            self.mouse_posY = y

    def set_range(self,min,max):
        self.min = min
        self.max = max
        self.auto_range = False
        return
    
    def arange_peak(self):
        self.min = 0
        self.max = self.image.max()
        self.auto_range = False
        return

    def arange_con(self):
        return


    def _rescale(self,image,min,max):
        im_scaled = image
        im_scaled[im_scaled < min] = min
        im_scaled[im_scaled > max] = max

        alpha = int(2**16/(max-min))
        im_scaled -= min
        im_scaled *= alpha

        return im_scaled
            

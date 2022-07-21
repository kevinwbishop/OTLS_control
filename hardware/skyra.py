#!/usr/bin/env python
"""
Cobolt Skyra control.

# Adam Glaser 07/19

# Made max min currents a variable, but still hardcoded in set max/min. Note these values change
  with the specific laser as they are factory calibrated - KB 2022

"""
import hardware.RS232 as RS232


class Skyra(RS232.RS232):
    """
    Encapsulates communication with a Cobolt Skyra that is connected via RS-232.
    """
    def __init__(self, **kwds):

        # min and max of linear range for current control, in order by laser #
        self.minCurrents = [1180.0,
                            101.0,
                            32.0,
                            37.0]

        self.maxCurrents = [2610.0,
                            169.0,
                            99.0,
                            78.0]

        try:
            # open port
            super().__init__(**kwds)

        except Exception:
            print("Failed to connect to the Cobolt Skyra!")

    def turnOn(self, wavelength):
        """
        Turn laser ON.
        """
        self.sendCommand(str(wavelength) + "l1")
        self.waitResponse() 

    def turnOff(self, wavelength):
        """
        Turn laser OFF.
        """
        self.sendCommand(str(wavelength) + "l0")
        self.waitResponse() 

    def setPower(self, wavelength, power):
        """
        Set the laser power.
        """
        power = power/1000 # convert to W
        self.sendCommand(str(wavelength) + "p " + str(power))
        self.waitResponse() 

    def setModulationOn(self, wavelength):
        """
        Set the modulation mode ON.
        """
        self.sendCommand(str(wavelength) + "em")
        self.waitResponse()       

    def setDigitalModulation(self, wavelength, mode):
        """
        Set the modulation mode ON.
        """
        self.sendCommand(str(wavelength) + "sdmes " + str(mode))
        self.waitResponse()       

    def setAnalogModulation(self, wavelength, mode):
        """
        Set the modulation mode ON.
        """
        self.sendCommand(str(wavelength) + "sames " + str(mode))
        self.waitResponse()  

    def getModulationHighCurrent(self, wavelength):
        """
        Set the modulation high current in mA.
        """

        response = self.commWithResp(str(wavelength) + "gmc?")
        self.waitResponse() 
        response = float(response[0:len(response)-5])
        return response 

    def getModulationLowCurrent(self, wavelength):
        """
        Set the modulation high current in mA.
        """

        response = self.commWithResp(str(wavelength) + "glth?")
        self.waitResponse()
        response = float(response[0:len(response)-5])
        return response

    def setModulationHighCurrent(self, wavelength, power):
        """
        Set the modulation high current in mA.
        """
        waveMin = self.minCurrents[wavelength-1]
        waveMax = self.maxCurrents[wavelength-1]

        current =  waveMin + power*(waveMax - waveMin)

        assert current <= waveMax
        assert current > self.getModulationLowCurrent(wavelength)

        # These max values are intentionally hardcoded in two places for redundancy, they must be changed here and in init
        if wavelength == 1:
            assert current <= 2610.0
        if wavelength == 2:
            assert current <= 169.0
        if wavelength == 3:
            assert current <= 99.0
        if wavelength == 4:
            assert current <= 78.0

        assert current >= 0.0

        print('Setting high current for wavelength ' + str(wavelength) + ' to ' + str(current) + 'mA')

        self.sendCommand(str(wavelength) + "smc " + str(current)) 
        self.waitResponse() 

    def setModulationLowCurrent(self, wavelength, power):
        """
        Set the modulation low current in mA.
        """

        # These max values are intentionally hardcoded in two places for redundancy, they must be changed here and in init
        if wavelength == 1:
            current = 780.0 + power*(self.maxCurrents[0]-780.0)
            assert current <= 2610.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 2:
            current = 0.0 + power*(self.maxCurrents[1])
            assert current <= 169.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 3:
            current = 0.0 + power*(self.maxCurrents[2])
            assert current <= 99.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 4:
            current = 0.0 + power*(self.maxCurrents[3])
            assert current <= 78.0
            assert current < self.getModulationHighCurrent(1)

        assert current >= 0.0

        print('Setting low current for wavelength ' + str(wavelength) + ' to ' + str(current) + 'mA')

        self.sendCommand(str(wavelength) + "slth " + str(current))  
        self.waitResponse() 
        
if (__name__ == "__main__"):
    laser = skyra()
    laser.shutDown()

#
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
#
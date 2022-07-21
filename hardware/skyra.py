#!/usr/bin/env python
"""
Cobolt Skyra control.

# Adam Glaser 07/19

"""
import hardware.RS232 as RS232


class Skyra(RS232.RS232):
    """
    Encapsulates communication with a Cobolt Skyra that is connected via RS-232.
    """
    def __init__(self, **kwds):
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

        if wavelength == 1:
            current = 1400.0 + power*(2630.0-1400.0)
            assert current <= 2630.0
            assert current > self.getModulationLowCurrent(1)
        if wavelength == 2:
            current = 109.0 + power*(177.0 - 109.0)
            assert current <= 177.0
            assert current > self.getModulationLowCurrent(2)
        if wavelength == 3:
            current = 32.0 + power*(96.0 - 32.0)
            assert current <= 96.0
            assert current > self.getModulationLowCurrent(3)
        if wavelength == 4:
            current = 36.0 + power*(77.0 - 36.0)
            assert current <= 77.0
            assert current > self.getModulationLowCurrent(4)

        assert current >= 0.0

        self.sendCommand(str(wavelength) + "smc " + str(current)) 
        self.waitResponse() 

    def setModulationLowCurrent(self, wavelength, power):
        """
        Set the modulation low current in mA.
        """

        if wavelength == 1:
            current = 780.0 + power*(2630.0-780.0)
            assert current <= 2630.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 2:
            current = 0.0 + power*(177.0)
            assert current <= 177.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 3:
            current = 0.0 + power*(96.0)
            assert current <= 96.0
            assert current < self.getModulationHighCurrent(1)
        if wavelength == 4:
            current = 0.0 + power*(77.0)
            assert current <= 77.0
            assert current < self.getModulationHighCurrent(1)

        assert current >= 0.0

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
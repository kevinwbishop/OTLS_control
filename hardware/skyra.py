#!/usr/bin/env python
"""
Cobolt Skyra control.

# Adam Glaser 07/19
# updated by Kevin Bishop 10/22

For all functions, wavelength should be specified as Skyra number:
    1: 561
    2: 638
    3: 488
    4: 405

"""

# TODO Update skyra_LUT.py so that it properly generates a LUT, or add
# instructions to generate such a table in MATLAB

import hardware.RS232 as RS232
import json
from scipy import interpolate


class Skyra(RS232.RS232):
    """
    Encapsulates communication with a Cobolt Skyra that is connected
    via RS-232.
    """
    def __init__(self, **kwds):

        # min and max of linear range for current control, in order by laser #
        self.minCurrents = min_currents
        self.maxCurrents = max_currents
        self.use_LUT = use_LUT

        try:
            # open port
            super().__init__(**kwds)

        except Exception:
            print("Failed to connect to the Cobolt Skyra!")

        # import LUT
        with open('skyra_LUT.json', 'r') as read_file:
            self.LUT = json.load(read_file)

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

        wavelength: Skyra channel number (1-4)
        power: power in mW
        """
        power = power/1000  # convert to W
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
        Set digital modulation mode.
        """
        self.sendCommand(str(wavelength) + "sdmes " + str(mode))
        self.waitResponse()

    def setAnalogModulation(self, wavelength, mode):
        """
        Set analog modulation mode.
        """
        self.sendCommand(str(wavelength) + "sames " + str(mode))
        self.waitResponse()

    def getModulationHighCurrent(self, wavelength):
        """
        Get the modulation high current in mA.
        """

        response = self.commWithResp(str(wavelength) + "gmc?")
        self.waitResponse()
        response = float(response[0:len(response)-5])
        return response

    def getModulationLowCurrent(self, wavelength):
        """
        Get the modulation low current in mA.
        """

        response = self.commWithResp(str(wavelength) + "glth?")
        self.waitResponse()
        response = float(response[0:len(response)-5])
        return response

    def setModulationHighCurrent(self, wavelength, power):
        """
        Set the modulation high current in mA.
        power is power in mW (note - previous version used power as
        fraction of max power)
        """

        # waveMin = self.minCurrents[wavelength]

        # current =  waveMin + power*(waveMax - waveMin)
        current = self.power2current(wavelength, power)
        waveMax = self.maxCurrents[wavelength]
        assert current <= waveMax
        assert current > self.getModulationLowCurrent(wavelength)
        assert current >= 0.0

        print('Setting high current for wavelength ' + str(wavelength) +
              ' to ' + str(current) + 'mA')

        self.sendCommand(str(wavelength) + "smc " + str(current))
        self.waitResponse()

    def setModulationLowCurrent(self, wavelength, power):
        """
        Set the modulation low current in mA.
        Power is in mW
        """
        current = self.power2current(wavelength, power)
        waveMax = self.maxCurrents[wavelength]
        assert current <= waveMax
        assert current < self.getModulationHighCurrent(wavelength)
        assert current >= 0.0

        print('Setting low current for wavelength ' + str(wavelength) +
              ' to ' + str(current) + 'mA')

        self.sendCommand(str(wavelength) + "slth " + str(current))
        self.waitResponse()

    def power2current(self, wavelength, power):
        """
        converts power in mW to current in mA using LUT for a given wavelength
        """

        min_interp = self.LUT['ch' + str(wavelength)]['power'][0]
        max_interp = self.LUT['ch' + str(wavelength)]['power'][-1]

        set_power = power / \
            self.LUT['ch' + str(wavelength)]['measurement_factor']

        if set_power == 0:
            current = self.LUT['ch' + str(wavelength)]['zero_current']
        elif set_power >= min_interp and set_power <= max_interp:
            interp_func = interpolate.interp1d(
                self.LUT['ch' + str(wavelength)]['power'],
                self.LUT['ch' + str(wavelength)]['current'])
            current = interp_func(set_power).item()
        else:
            raise Exception('Specified power out of range')
        return current


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
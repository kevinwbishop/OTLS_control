#!/usr/bin/python
#
# @file
"""
RS232 interface to a Applied Scientific Instrumentation MS2000 stage.

Hazen 3/09
Adam Glaser 07/19
Kevin Bishop 2/22 - changed to be for Tiger controller instead.
Added set acceleration on 5/6/22 -KB
Renamed variables to refer to mm and not um (code is correct,
    but names/comments weren't) on 5/9/22 -KB
Gan Gao 09/22: enforced linting and added doc strings.
"""

import hardware.RS232 as RS232


class TIGER(RS232.RS232):
    """
    Applied Scientific Instrumentation Tiger RS232 interface class.
    """
    def __init__(self, **kwds):
        """
        Connect to the Tiger stage at the specified port.

        Parameters:
        port: The RS-232 port name (e.g. "COM1").
        wait_time (Optional): How long (in seconds) for a response from
        the stage.
        """

        self.mm_to_unit = 10000  # 10000 means "10000 units = 1mm"
        self.unit_to_mm = 1.0/self.mm_to_unit
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        try:
            # open port
            super().__init__(**kwds)
        except Exception:
            print("ASI Stage is not connected? Stage is not on?")

    def getCD(self):
        """
        Returns the date and time the current firmware were compiled.
        """
        response = self.commWithResp("CD")
        return response

    def getBU(self):
        """
        Returns various build configuration options, the firmware modules
        in the build, and the build name.
        """
        response = self.commWithResp("BU X")
        return response

    def getMotorStatus(self):
        """
        Return True/False if the stage is moving.
        """
        response = self.commWithResp("/")
        return response

    def goAbsolute(self, axis, pos, bwait):
        """
        Move to an absolute coordinate.

        Parameters:
        axis: X, Y, or Z.
        pos: absolute position coordinates in mm.
        bwait (bool): If true, execute this movement command until
        there are no motors running from a serial command.
        """
        p = pos * self.mm_to_unit
        p = round(p)
        self.commWithResp("M " + axis + "=" + str(p))
        if bwait == True:
            response = self.getMotorStatus()
            while response[0] == 'B':
                response = self.getMotorStatus()

    def goRelative(self, axis, pos, bwait):
        """
        Move to a relative coordinate.

        Parameters:
        axis: X, Y, or Z.
        pos: Amount to move the stage in mm.
        bwait (bool): If true, execute this movement command until
        there are no motors running from a serial command.
        """
        p = pos * self.mm_to_unit
        p = round(p)
        self.commWithResp("R " + axis + "=" + str(p))
        if bwait is True:
            response = self.getMotorStatus()
            while response[0] == 'B':
                response = self.getMotorStatus()

    def getPosition(self):
        """
        Return [stage x (mm), stage y (mm), stage z (mm)]
        """
        try:
            [self.x, self.y, self.z] = self.commWithResp("W X Y Z").split(" ")[1:4]
            self.x = float(self.x)*self.unit_to_mm # convert to mm
            self.y = float(self.y)*self.unit_to_mm # convert to mm
            self.z = float(self.z)*self.unit_to_mm # convert to mm
        except Exception:
            print("Stage Error")
        return [self.x, self.y, self.z]

    def setBacklash(self, axis, backlash):
        """
        Set the amount of distance in millimeters to travel to
        absorb the backlash in the axis' gearing.

        Parameters:
        axis: X, Y, or Z.
        backlash: Distance to travel in millimeters. 0 (off).
        """
        self.commWithResp("B " + axis + "=" + str(backlash))

    def scan(self, bwait):
        """
        Activate stage scan.

        Parameters:
        bwait (bool): If true, execute scanning until
        there are no motors running from a serial command.
        """
        self.commWithResp("SCAN")
        if bwait is True:
            response = self.getMotorStatus()
            while response[0] == 'B':
                response = self.getMotorStatus()

    def setScanF(self, x):
        """
        Sets up scanning pattern.

        Parameters:
        x: 0 for RASTER scans or 1 for SERPENTINE scans.
        """
        self.commWithResp("SCAN F=" + str(x))

    def setScanR(self, x, y):
        """
        Sets up raster scan start and stop positions.

        Parameters:
        x: Start position.
        y: Stop position.
        """
        x = round(x, 3)
        y = round(y, 3)
        self.commWithResp("SCANR X=" + str(x) + " Y=" + str(y))

    def setScanV(self, x):
        """
        Set up the slow-scan (vertical) start and stop positions.

        Parameters:
        x: z position.
        """
        x = round(x, 3)
        #may need to adjust F number, it is the extra settling time in ms
        self.commWithResp("SCANV X=" + str(x) + "Y=" + str(x) + " Z=1 F=10")

    def setTTL(self, card, axis, ttl):
        """
        Set TTL input (IN0) and output (OUT0) port.

        Parameters:
        card: card number (1, 2, 3, etc.)
        axis: X, Y, or Z.
        ttl: 0 (off) or 1 (on).
        """
        self.commWithResp(str(card) + "TTL " + axis + "=" + str(ttl))

    def setPLCPreset(self, card, preset):
        """
        Set the configuration flags as https://asiimaging.com/docs/commands/customa.

        Parameters:
        card: card number (1, 2, 3, etc.)
        preset: preset PLC code - use 52 for stage SYNC access on BNC 3.
        """
        self.commWithResp(str(card) + "CCA X=" + str(preset))

    def setAcceleration(self, axis, accel):
        """
        Set the amount of time in milliseconds that it takes
        an axis motor speed to go from stopped to the set speed.
        It is also the duration of the deceleration time at the
        end of the move.

        Parameters:
        axis: X, Y, or Z.
        accel: Acceleration time to reach velocity in ms.
        """
        self.commWithResp("AC " + axis + "=" + str(accel))
      
    def setVelocity(self, axis, vel):
        """
        Set the speed at which the stage will move
        during the middle of a commanded move.

        Parameters:
        axis: X, Y, or Z.
        vel: Maximum velocity to move in mm/s.
        """
        vel = round(vel, 5)
        self.commWithResp("S " + axis + "=" + str(vel))

    def zero(self):
        """
        Set the current stage position as the stage zero.
        """
        self.commWithResp("Z")

#
# The MIT License
#
# Copyright (c) 2014 Zhuang Lab, Harvard University
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

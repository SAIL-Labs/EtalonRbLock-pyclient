from .. import erlBase
from math import isnan


class PID(erlBase):
    def __init__(self, kp=0, ki=0, kd=0, starttime=0):
        erlBase.__init__(self)

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

        self.prevtm = starttime
        self.prev_err = 0
        self.prev_input = 0

        self.firstTime = True

        self.maxout = 1.0
        self.minout = 0.2
        self.output = 0

    def update(self, input, setpoint, mesurmentTime):
        if isnan(input+setpoint+mesurmentTime):
            return self.output

        error = input - setpoint

        dt = 1/20 #mesurmentTime - self.prevtm  # get delta t
        # de = error - self.prev_err          # get delta error

        self.Cp = self.kp * error
        self.Ci += error * self.ki

        if self.Ci > self.maxout:
            self.Ci = self.maxout
        elif self.Ci < self.minout:
            self.Ci = self.minout

        self.Cd = 0
        if dt > 0:  # no div by zero
            self.Cd = (input - self.prev_input) * self.kd  # derivative term

        self.prevtm = mesurmentTime  # save curret time for next iter
        self.prev_err = error
        self.prev_input = input  # save t-1 error

        change = self.Cp + self.Ci - self.Cd
        self.output = change

        if self.output > self.maxout:
            self.output = self.maxout
        elif self.output < self.minout:
            self.output = self.minout

        #self.logger.debug("dP {}, dI {}, dD {}, total change {} : Output {}".format(
        #    self.Cp, self.Ci, self.Cd, change, self.output))
        return self.output

    def setKpid(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        # self.Cp = 0
        # self.Ci = 0
        # self.Cd = 0

    def setMax(self, maxoutvalue):
        self.maxout = maxoutvalue

    def setMin(self, minoutvalue):
        self.minout = minoutvalue

from .. import erlBase
from math import isnan


class PID(erlBase):
    def __init__(self, kp=0, Ti=0, Td=0, startvalue=0, starttime=0):
        erlBase.__init__(self)

        self.kp = kp
        self.Ti = Ti
        self.Td = Td

        self.Cp = 0
        self.Ci = 0
        self.Cd = 0
        self.Co = startvalue

        self.prevtm = starttime
        self.prev_err = 0
        self.prev_input = 0
        self.error_int = 0

        self.firstTime = True

        self.maxout = 1.0
        self.minout = 0.2
        self.output = 0

        self.TransferCount = 0

    def update(self, input, setpoint, mesurmentTime):


        if isnan(input+setpoint+mesurmentTime):
            return self.output

        self.TransferCount += 1

        error = input - setpoint

        dt = mesurmentTime - self.prevtm  # get delta t
        # de = error - self.prev_err          # get delta error

        self.Cp = self.kp * error

        self.error_int+=error

        self.Ci = 0
        if self.Ti > 0:
            self.Ci = self.error_int * self.kp / self.Ti

        # if self.Ci + self.Co > self.maxout:
        #     self.Ci = self.maxout
        # elif self.Ci + self.Co < self.minout:
        #     self.Ci = self.minout

        if self.TransferCount > 400 and self.Ti > 0:
            self.Co = self.Ci + self.Co
            self.Ci = 0
            self.int_error = 0
            self.TransferCount = 0

        self.Cd = 0
        if dt > 0:  # no div by zero
            self.Cd = (input - self.prev_input) * self.Td * self.kp  # derivative term

        self.output = self.Co + self.Cp + self.Ci - self.Cd

        if self.output > self.maxout:
            self.output = self.maxout
        elif self.output < self.minout:
            self.output = self.minout

        self.prevtm = mesurmentTime  # save curret time for next iter
        self.prev_err = error
        self.prev_input = input  # save t-1 error

        self.logger.debug(" TfC {},dP {}, dI {}, dD {}, Co {} : Output {}".format(self.TransferCount,
             self.Cp, self.Ci, self.Cd, self.Co, self.output))
        return self.output

    def setKpid(self, kp, Ti, Td):
        self.Co = self.Ci + self.Co
        self.int_error = 0
        self.TransferCount = 0

        self.kp = kp
        self.Ti = Ti
        self.Td = Td

        # self.Cp = 0
        # self.Ci = 0
        # self.Cd = 0

    def setMax(self, maxoutvalue):
        self.maxout = maxoutvalue

    def setMin(self, minoutvalue):
        self.minout = minoutvalue

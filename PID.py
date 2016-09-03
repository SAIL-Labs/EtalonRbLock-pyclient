class PID:
    def __init__(self,kp=0.001,ki=0,kd=0,starttime=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

        self.prevtm = starttime
        self.prev_err = 0

    def update(self,error,mesurmentTime):
        dt = mesurmentTime - self.prevtm    # get delta t
        de = error - self.prev_err          # get delta error

        self.Cp = self.kp * error
        self.Ci += error * dt
        self.Cd = 0
        if dt > 0:                          # no div by zero
            self.Cd = de / dt               # derivative term

        self.prevtm = mesurmentTime         # save curret time for next iter
        self.prev_err = error               # save t-1 error
        return self.Cp + (self.ki * self.Ci) + (self.kd * self.Cd)

    def setKpid(self,kp,ki,kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
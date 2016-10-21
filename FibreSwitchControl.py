import serial

class FibreSwitchs:
    def __init__(self,port="/dev/ttyUSB0",baud=115200):
        self.ser = serial.Serial(port,baud)
        self.ser.write(b'0,1;/n')
        line=self.ser.readline()
        self.status=int(line[2:3].decode("utf-8"))

    def setStateOne(self):
        self.ser.write(b'0,0;/n')
        line=self.ser.readline()
        self.status=int(line[2:3].decode("utf-8"))

    def setStateTwo(self):
        self.ser.write(b'0,1;/n')
        line=self.ser.readline()
        self.status=int(line[2:3].decode("utf-8"))

if __name__ == '__main__':
    fs = FibreSwitchs(port='/dev/tty.usbmodem142121')
    #fs.setSwitchState(100)
    #fs.setSwitchState(100)
    #fs.setSwitchState(True)

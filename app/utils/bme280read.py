#from .. import erlBase
import serial

class bme280(object):

    def __init__(self,port='/dev/ttyACM0'):
        #erlBase.__init__(self)
        self.ser = serial.Serial(port)
        self.port = port


    def getData(self):
        self.ser.write(b'1')
        line = self.ser.readline()
        self.temp=float(line.decode().rstrip('\r\n'))

        line = self.ser.readline()
        self.pressure = float(line.decode().rstrip('\r\n'))

        line = self.ser.readline()
        self.hum = float(line.decode().rstrip('\r\n'))

if __name__ == '__main__':
    tp=bme280()

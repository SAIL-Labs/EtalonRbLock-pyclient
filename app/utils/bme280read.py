#from .. import erlBase
import serial
import time

class bme280(object):
    temp=-90.0
    pressure=0
    hum=0

    def __init__(self,port='/dev/ttyUSB1'):
        #erlBase.__init__(self)
        self.ser = serial.Serial(port,baudrate=115200)
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

    t = time.time()
    for i in range(100):
        t = time.time()
        tp.getData()
        elapsed=time.time() - t
        print("{}, {}, {}, {}".format(1/elapsed, tp.temp, tp.pressure, tp.hum))


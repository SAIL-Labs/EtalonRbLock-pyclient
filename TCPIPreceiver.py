# updreceiver.py
import socket   #for sockets
#from array import array
import numpy as np

#from matplotlib import pyplot as plt

# RED_IP ="10.66.101.121"
# # "10.66.101.121"
class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class TCPIPreceiver(metaclass=Singleton):
    pass
    def __init__(self, PORT_A, PORT_B, PORT_ACK, AQUSITIONSIZE, RED_IP):
        self.PORT_A = PORT_A
        self.PORT_B = PORT_B
        self.PORT_ACK = PORT_ACK
        self.AQUSITIONSIZE = AQUSITIONSIZE
        self.RED_IP = RED_IP

        #self.sockA = self.setupSocket(self.PORT_A, 3*self.AQUSITIONSIZE)
        #self.sockB = self.setupSocket(self.PORT_B, 3*self.AQUSITIONSIZE)
        #self.sockAck = self.setupSocket(self.PORT_ACK, 1024)

        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.dataB = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.timetrigger = np.empty((1,1),dtype = '<u8')
        self.temp = np.empty((1,1),dtype = '<f')

    def recv_into(self,arr,port):
        s=self.setupSocket(port, 3 * self.AQUSITIONSIZE)

        view = memoryview(arr).cast('B')
        bytesrecv = 0

        while len(view):
            nrecv = s.recv_into(view)
            view = view[nrecv:]
            bytesrecv+=nrecv
            #print(bytesrecv)
        s.close()

        return bytesrecv

    def setupSocket(self,PORT,RCVBUFSIZE):
        # try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUFSIZE)
        s.connect((self.RED_IP, PORT))
            #s.bind(("", PORT))
            #s.settimeout(5.0)
        # except socket.error:
        #     print('Failed to create socket')
        #     raise ValueError('Failed to create socket:' + str(PORT))
        return s

    def sendAckResponse(self, msg):
        s=self.setupSocket(self.PORT_ACK, 1024)

        MESSAGE = "%s %f\n" % ('Ack', msg)
        s.send(str.encode(MESSAGE))
        s.close()
        #self.receiveDACData()

    def sendEndResponse(self):
        s = self.setupSocket(self.PORT_ACK, 1024)
        MESSAGE = "%s %f\n" % ('END', float(10.0))
        s.send(str.encode(MESSAGE))
        s.close()
        #self.receiveDACData()

    def receiveDACData(self):
        #print('receiveDACData 1')
        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')

        NumBytedataA = self.recv_into(self.dataA,self.PORT_A)

        #print('receiveDACData 2')
        self.dataB = np.empty((self.AQUSITIONSIZE),dtype='i2')

        NumBytedataB = self.recv_into(self.dataB,self.PORT_B)

        #print('receiveDACData 3')
        #dataAout=array('i',np.nditer(self.dataA,flags=['buffered']))
        #dataBout=array('i',np.nditer(self.dataB,flags=['buffered']))
        #dataBout=array.array('d',np.nditer(dataB))
        return (NumBytedataA,NumBytedataB)

    def recieveTrigerTimeAndTemp(self):
        s = self.setupSocket(self.PORT_ACK, 1024)
        ttrig = s.recv_into(self.timetrigger, )
        ttemp = s.recv_into(self.temp, 4)
        s.close()
        return (ttemp, ttrig)

    def doALL(self,tempset=8.00):
        self.sendAckResponse(tempset)
        self.receiveDACData()
        self.recieveTrigerTimeAndTemp()

if __name__ == "__main__":
    print("Nothing to do. Use in external script.")



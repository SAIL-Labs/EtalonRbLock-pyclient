# updreceiver.py
import socket   #for sockets
#from array import array
import numpy as np



#from matplotlib import pyplot as plt

# RED_UDP_IP ="10.66.101.121"
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


class updreceiver(metaclass=Singleton):
    pass
    def __init__(self, UDP_PORT_A, UDP_PORT_B, UDP_PORT_ACK, AQUSITIONSIZE, RED_UDP_IP):
        self.UDP_PORT_A = UDP_PORT_A
        self.UDP_PORT_B = UDP_PORT_B
        self.UDP_PORT_ACK = UDP_PORT_ACK
        self.AQUSITIONSIZE = AQUSITIONSIZE
        self.RED_UDP_IP = RED_UDP_IP

        self.sockA = self.setupSocket(self.UDP_PORT_A, 4*self.AQUSITIONSIZE)
        self.sockB = self.setupSocket(self.UDP_PORT_B, 4*self.AQUSITIONSIZE)
        self.sockAck = self.setupSocket(self.UDP_PORT_ACK, 1024*2)

        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.dataB = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.timetrigger = np.empty((1,1),dtype = '<u8')
        self.temp = np.empty((1,1),dtype = '<f')

    def recv_into(self,arr, source):
        view = memoryview(arr).cast('B')
        bytesrecv = 0

        while len(view):
            nrecv = source.recv_into(view)
            view = view[nrecv:]
            bytesrecv+=nrecv
        return bytesrecv

    def setupSocket(self,PORT,RCVBUFSIZE):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUFSIZE)
            s.bind(("", PORT))
            s.settimeout(10.0)

        except socket.error:
            print('Failed to create socket')
            raise ValueError('Failed to create socket:' + str(PORT))
        return s

    def sendAckResponse(self, msg):
        MESSAGE = "%s %f\n" % ('Ack', msg)
        self.sockAck.sendto(str.encode(MESSAGE), (self.RED_UDP_IP, self.UDP_PORT_ACK))
        #self.receiveDACData()

    def sendEndResponse(self):
        MESSAGE = "%s %f\n" % ('END', float(10.0))
        self.sockAck.sendto(str.encode(MESSAGE), (self.RED_UDP_IP, self.UDP_PORT_ACK))
        #self.receiveDACData()

    def receiveDACData(self):
        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')
        NumBytedataA = self.recv_into(self.dataA, self.sockA)

        self.dataB = np.empty((self.AQUSITIONSIZE),dtype='i2')
        NumBytedataB = self.recv_into(self.dataB, self.sockB)
        
        #dataAout=array('i',np.nditer(self.dataA,flags=['buffered']))
        #dataBout=array('i',np.nditer(self.dataB,flags=['buffered']))
        
        #dataBout=array.array('d',np.nditer(dataB))
        return (NumBytedataA,NumBytedataB)

    def recieveTrigerTimeAndTemp(self):
        ttrig = self.sockAck.recv_into(self.timetrigger, 8)
        ttemp = self.sockAck.recv_into(self.temp, 4)
        
        return (ttemp, ttrig)

    def doALL(self):
        self.sendAckResponse(8.0)
        self.receiveDACData()
        self.recieveTrigerTimeAndTemp()
        # self.sockA.flush()
        # self.sockB.flush()
        # self.sockAck.flush()

if __name__ == "__main__":
    print("Nothing to do. Use in external script.")



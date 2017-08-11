#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


from app import erlBase

class TCPIPreceiver(erlBase, metaclass=Singleton):
    """ TCPIPreceiver is an object that manages the TCP/IP communication with the RedPitaya
     based data acquisition.

        :param PORT_A: TCP/IP port that RP ADC 1 data (Etalon signal)
        :param PORT_B: TCP/IP port that RP ADC 1 data (Etalon signal)
        :param PORT_ACK: TCP/IP used for two comunications, sends continue (Ack), stop (end), and
         sets PID temp or direct drive current.
        :param AQUSITIONSIZE: Size of the data acquisition per trigger
        :param RED_IP: IP address of the RP. Must be on local network to handle bandwidth.
    """
    pass
    def __init__(self, PORT_A, PORT_B, PORT_ACK, AQUSITIONSIZE, RED_IP):
        """ TCPIPreceiver constructor

        Description above.
        """
        erlBase.__init__(self)

        self.PORT_A = PORT_A
        self.PORT_B = PORT_B
        self.PORT_ACK = PORT_ACK
        self.AQUSITIONSIZE = AQUSITIONSIZE
        self.RED_IP = RED_IP

        self.logger.info('Using Port A: %d, Port B: %d, Port Ack: %d with IP %s', PORT_A, PORT_B,PORT_ACK, RED_IP)

        #self.sockA = self.setupSocket(self.PORT_A, 3*self.AQUSITIONSIZE)
        #self.sockB = self.setupSocket(self.PORT_B, 3*self.AQUSITIONSIZE)
        #self.sockAck = self.setupSocket(self.PORT_ACK, 1024)

        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.dataB = np.empty((self.AQUSITIONSIZE), dtype='i2')
        self.timetrigger = np.empty((1,1),dtype = '<u8')
        self.temp = np.empty((1,1),dtype = '<f')
        self.tempexternal = np.empty((1, 1), dtype='<f')
        self.pressure = np.empty((1, 1), dtype='<f')
        self.humidity = np.empty((1, 1), dtype='<f')

    def recv_into(self,arr,port):
        """ Wrapper to connect to server and receive ADC data in numpy.ndarray "arr".

        Establishes connection with RP server.
        Done by looping over array using a memory view, and filling in chunks with socket.recv_into.

        :param arr: empty numpy.ndarray defined in constructor (np.empty((self.AQUSITIONSIZE), dtype='i2')).
        :param port: port to communicate on (with A or B, depending on channel wanted).
        :return: Number of bytes received (should be 2*AQUSITIONSIZE)
        """
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
        """ establishes a connection to RP server on specified port returning socket.

        :param PORT: TCP/IP communication port
        :param RCVBUFSIZE: TCP/IP communication buffer size.
        :return: socket connected to RP on port PORT.
        """
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
        """ sends message msg to RP server on communications port.

        :param msg: Message to send RP server.
        :return: nothing.
        """
        s=self.setupSocket(self.PORT_ACK, 1024)

        MESSAGE = "%s %f\n" % ('Ack', msg)
        s.send(str.encode(MESSAGE))
        s.close()
        #self.receiveDACData()

    def sendEndResponse(self):
        """ Send message "END" to RP server on communications port. Terminate RP server.

        :return: nothing.
        """
        s = self.setupSocket(self.PORT_ACK, 1024)
        MESSAGE = "%s %f\n" % ('END', float(10.0))
        s.send(str.encode(MESSAGE))
        s.close()
        #self.receiveDACData()

    def receiveDACData(self):
        """ receive ADC dat from the RP data

        :return: number of bytes received from both channels
        """
        #print('receiveDACData 1')
        self.dataA = np.empty((self.AQUSITIONSIZE), dtype='i2')

        NumBytedataA = self.recv_into(self.dataA,self.PORT_A)

        #print('receiveDACData 2')
        self.dataB = np.empty((self.AQUSITIONSIZE),dtype='i2')

        NumBytedataB = self.recv_into(self.dataB,self.PORT_B)

        return NumBytedataA, NumBytedataB

    def recieveTrigerTimeAndTemp(self):
        """ receive trigger time of data acquisition  and current Etalon temp on communication channel

        :return:  temperature and trigger time
        """
        s = self.setupSocket(self.PORT_ACK, 1024)
        ttrig = s.recv_into(self.timetrigger, )
        ttemp = s.recv_into(self.temp, 4)
        ttempexternal = s.recv_into(self.tempexternal, 4)
        tpressure = s.recv_into(self.pressure, 4)
        thumidity = s.recv_into(self.humidity, 4)

        s.close()
        return ttemp, ttrig,ttempexternal,tpressure,thumidity

    def doALL(self,tempset=8.00):
        """ execute sendAckResponse, receiveDACData and recieveTrigerTimeAndTemp in order.

        :param tempset: PID temp or direct drive current value as float
        :return:
        """
        #self.logger.debug('Temp Set is: {}'.format(tempset))
        self.sendAckResponse(tempset)  # get data from next trigger
        self.receiveDACData()  # receives the ADC data
        self.recieveTrigerTimeAndTemp()  # get trigger time and temp of acquisition.

if __name__ == "__main__":
    print("Nothing to do. Use in external script.")



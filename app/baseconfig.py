import os
import datetime
import socket
import numpy as np

class erblconfig:

    def __init__(self, *args, **kwargs):
        self.rpIP = socket.gethostbyname('redpitaya1.sail-laboratories.com')
        #self.rpIP = '192.168.1.100'
        self.localIP = getLocalInterfaceIp(self.rpIP)

        self.arduinoport = '/dev/ttyACM0'

        self.sos = np.asarray(
            [[5.80953794660816e-06, 1.16190758932163e-05, 5.80953794660816e-06, 1, -1.99516198526679,
              0.995185223418579],
             [0.00240740227660535, 0.00240740227660535, 0, 1, -0.995185195446789, 0]])

        self.samplescale_nm = 9.1604852488056226e-07  # nm per sample, 20hz, 20000 samples, DE_64, sweep amp 20, centre
        self.samplescale_nm = 1.0914981908744188e-06
        self.samplescale_ms = 0.4131877581547582

        self.decimation = 64
        self.aquisitionsize = 1280000 // self.decimation

        self.degperms = 1 / 8200
        self.delay = 1

        self.useExtPID = 0
        if self.useExtPID:
            self.MESetPointStart = 3.42  # Temp
        else:
            self.MESetPointStart = 0.52  # current

        self.baseDirectory = os.path.join(os.getcwd(),'data')
        os.makedirs(self.baseDirectory, exist_ok=True)
        self.image_directory = os.path.join(self.baseDirectory, 'specimages', datetime.date.today().isoformat())
        os.makedirs(self.image_directory, exist_ok=True)
        self.rbLockData_directory = os.path.join(self.baseDirectory, 'rbData', datetime.date.today().isoformat())
        os.makedirs(self.rbLockData_directory, exist_ok=True)


def getLocalInterfaceIp(rpIP='8.8.8.8'):

    localIP = ([l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                [(s.connect((rpIP, 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

    return localIP

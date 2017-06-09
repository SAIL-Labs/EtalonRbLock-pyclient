import sys
sys.path.append("..")

from app.comms.TCPIPreceiver import TCPIPreceiver
from app.utils.RBfitting import *
from app import erlBase
erlb=erlBase()

from matplotlib import pyplot as plt
from scipy import signal
from peakutils import plot as pkplot
import socket
import time


sos = np.asarray(
    [[5.80953794660816e-06, 1.16190758932163e-05, 5.80953794660816e-06, 1, -1.99516198526679, 0.995185223418579],
     [0.00240740227660535, 0.00240740227660535, 0, 1, -0.995185195446789, 0]])
rpIP = socket.gethostbyname('redpitaya1.sail-laboratories.com')

SHOULDPLOT_RB = 0
SHOULDPLOT_etalon = 0
if SHOULDPLOT_RB or SHOULDPLOT_etalon:
    plt.ion()
ur = TCPIPreceiver(12345, 12346, 12347, 20000, rpIP)
rbcentres = []
etaloncentres = []
scale = []

x = np.arange(20000)
ur.sendAckResponse(erlb.config.MESetPointStart)
time.sleep(0.2)
ur.receiveDACData()
ur.recieveTrigerTimeAndTemp()

# rbcentres = np.empty((6,1))
t = time.time()
#plt.clf()

for i in range(0, 1):
    erroroccured = False
    try:
        ur.doALL(erlb.config.MESetPointStart)
        # b=(ur.dataB-ur.dataB[320000])*-1.0

        # start = np.argmin(ur.dataB[0:230000])- 19000

        #start, finish = getRbWindow(ur.dataB)
        newRBcentre = fitRblines(x, ur.dataB)
        etalondata = ur.dataA #signal.sosfiltfilt(sos, ur.dataA)
        etaloncentre = fitEtalon(x, etalondata,100)

        #scale.append(fitwavelengthscale(newRBcentre))
        #rbcentres.append(newRBcentre)
        #etaloncentres.append(etaloncentre)


    except:
        erroroccured=True
        pass
elapsed = time.time() - t

print((i + 1) / elapsed)
#plt.plot(x,ur.dataB,newRBcentre,ur.dataB[(newRBcentre.astype(int))],'rx')
#print(fitwavelengthscale(newRBcentre))

#plt.plot(range(0, len(etaloncentres)), (etaloncentres), range(0, len(etaloncentres)),np.mean(rbcentres, axis=1))
#plt.plot(range(0, len(etaloncentres)), (etaloncentres - np.mean(rbcentres, axis=1)))

# del(ur)
#    errorsig = np.mean(rbcentres, axis=1) - etaloncentres
#    plt.clf()
#    plt.plot(etaloncentres - etaloncentres[0])
#    plt.plot(np.mean(rbcentres - rbcentres[0], axis=1))
#    # plt.plot(errorsig-errorsig[0])
#    plt.show()
# del ur
# centrestart=150000
#    a[ 2:21:2,:]
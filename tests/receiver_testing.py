from app.comms.TCPIPreceiver import TCPIPreceiver
from app.baseconfig import getLocalInterfaceIp
import socket
import time


rpIP=socket.gethostbyname('redpitaya1.sail-laboratories.com')
localIP=getLocalInterfaceIp(rpIP)
print(localIP)
print(rpIP)

aquisitionsize = 20000

ur = TCPIPreceiver(12345, 12346, 12347, aquisitionsize, rpIP)

ur.sendAckResponse(10)
time.sleep(1)
ur.receiveDACData()
ur.recieveTrigerTimeAndTemp()

# while (1):
#     t = time.time()
#     ur.sendAckResponse(10)
#     ur.receiveDACData()
#     ur.recieveTrigerTimeAndTemp()
#
#     elapsed = time.time() - t
#
#     print(1/elapsed)
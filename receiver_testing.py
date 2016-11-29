import updreceiver
import socket
import time


localIP=socket.gethostbyname(socket.gethostname()) #socket.getfqdn()
rpIP=socket.gethostbyname('redpitaya1.sail-laboratories.com')
print(localIP)
print(rpIP)

aquisitionsize = 150000

ur = updreceiver.updreceiver(12345, 12346, 12347, aquisitionsize, rpIP)

ur.sendAckResponse(10)
time.sleep(1)
ur.receiveDACData()
ur.recieveTrigerTimeAndTemp()

while (1):
    t = time.time()
    ur.sendAckResponse(10)
    ur.receiveDACData()
    ur.recieveTrigerTimeAndTemp()

    elapsed = time.time() - t

    print(1/elapsed)
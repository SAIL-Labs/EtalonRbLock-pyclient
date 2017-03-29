from app import erlBase
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import time
import socket


class getDataReceiverWorker(QtCore.QObject, erlBase):
    finished = pyqtSignal()
    dataReady = pyqtSignal(np.ndarray, np.ndarray, float, float, float)
    errorOccured = pyqtSignal()
    tempset = pyqtSignal(float)

    def __init__(self, ur, tempinit):
        QtCore.QObject.__init__(self)
        erlBase.__init__(self)
        self.ur = ur
        self.CurrentTemp = tempinit
        self._mutex = QtCore.QMutex()
        self.running = True

    @pyqtSlot()
    def dataRecvLoop(self):
        self.logger.debug("dataRecvLoop start\n")
        while self.running:
            try:
                #print(self.CurrentTemp)
                t = time.time()
                self.ur.doALL(self.CurrentTemp)
                elapsed = time.time() - t
                if self.ur.dataA.size == self.config.aquisitionsize and self.ur.dataB.size == self.config.aquisitionsize:
                    self.dataReady.emit(self.ur.dataA, self.ur.dataB, self.ur.timetrigger, self.ur.temp, elapsed)
                else:
                    self.logger.warning('skipped 393')
            except socket.timeout:
                self.logger.debug("sock timeout error\n")
                self.errorOccured.emit()
                break

        self.logger.debug("getDataReceiverWorker while loop ended")
        self.finished.emit()

    @pyqtSlot(float)
    def tempchangedinGUI(self, temp):
        self._mutex.lock()
        self.CurrentTemp = temp
        self._mutex.unlock()

    @pyqtSlot()
    def stop(self):
        self._mutex.lock()
        self.running=False
        self._mutex.unlock()
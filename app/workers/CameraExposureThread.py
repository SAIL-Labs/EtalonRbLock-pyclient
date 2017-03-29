from app import erlBase
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astropy.time import Time
import numpy as np
from ..utils import temppressure
import sys

from ..camera import Camera

class CameraExposureThread(QtCore.QThread,erlBase):
    dataReady = pyqtSignal(np.ndarray,Time, float, float, float)
    finished = pyqtSignal()

    def __init__(self, cam:Camera, continous:bool):
        QtCore.QThread.__init__(self)
        erlBase.__init__(self)
        self.cam = cam
        self._mutex = QtCore.QMutex()
        self.continous = continous
        self.temppressure=temppressure(self.config.arduinoport)

    def __del__(self):
        self.wait()

    def run(self):
        try:
            if self.continous:
                while self.continous:
                    self.logger.debug('Camera: Take Exposure Start')
                    tstart=Time.now()
                    self.temppressure.getData()
                    imdata = self.cam._cam.take_photo()
                    self.dataReady.emit(imdata, tstart, self.temppressure.temp, self.temppressure.pressure, self.temppressure.hum)
                    self.logger.debug('Camera: Take Exposure End')
                    time.sleep(2.0)
            else:
                self.logger.debug('Camera: Take Exposure Start')
                tstart = Time.now()
                self.temppressure.getData()
                imdata=self.cam._cam.take_photo()
                self.dataReady.emit(imdata,tstart, self.temppressure.temp, self.temppressure.pressure, self.temppressure.hum)
                self.logger.debug('Camera: Take Exposure End')

        except (ValueError, TypeError, RuntimeError) as err:
            self.logger.error("Camera: error({0}):".format(err))
            # raise err
            pass
        finally:
            self.logger.debug('Camera: Take Exposure Thread End')
            self.finished.emit()
            # self.terminate()

    @pyqtSlot()
    def stopContinous(self):
        self._mutex.lock()
        self.continous=False
        self._mutex.unlock()
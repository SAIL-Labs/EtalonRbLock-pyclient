from app import erlBase
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from scipy import signal
import numpy as np
import app.utils.RBfitting as fr



class fitdatathread(QtCore.QThread,erlBase):
    dataReady = pyqtSignal(float, np.ndarray, float)

    def __init__(self, dataA, dataB, trigtime):
        QtCore.QThread.__init__(self)
        erlBase.__init__(self)
        self.dataA = dataA
        self.dataB = dataB
        self.trigtime = trigtime

    def __del__(self):
        self.wait()

    def run(self):
        try:
            newRBcentre = fr.fitRblines(self.x, self.dataB)

            etalondata = signal.sosfiltfilt(self.config.sos, self.dataA)
            #etalondata=self.dataA
            etaloncentre = fr.fitEtalon(self.x, etalondata, 100)

            self.dataReady.emit(etaloncentre, newRBcentre, self.trigtime)
        except (ValueError, TypeError, RuntimeError) as err:
            self.logger.error("fit error({0}):".format(err))
            # raise err
            pass
        finally:
            pass
            # self.terminate()
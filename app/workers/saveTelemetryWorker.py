from app import erlBase
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import numpy as np
import app.utils.RBfitting as fr


class SaveTelemetryThread(QtCore.QThread, erlBase):

    def __init__(self, telemetry_file, data_to_save):
        QtCore.QThread.__init__(self)
        erlBase.__init__(self)

        self.filename = telemetry_file
        self.data = data_to_save

    def __del__(self):
        self.wait()

    def run(self):
        try:
            self.logger.info("Saving Data to {}".format(self.filename))
            with open(self.filename, 'a', encoding='utf-8') as file:
                for i in range(0, len(self.data)):
                    file.write(",".join(np.char.mod('%f', self.data[i, :])) + "\n")

        except (ValueError, TypeError, RuntimeError) as err:
            pass
        finally:
            pass


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:11:52 2016

@author: chrisbetters
"""

import itertools
import os
import subprocess
import sys
import time
from collections import deque

import numpy as np
import scipy.io
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from astropy.time import Time
from scipy.stats import binned_statistic

from app import erlBase
from app.RbMonitorUI import Ui_RbMoniter
from app.camera import Camera
from app.comms import TCPIPreceiver, remoteexecutor
from app.utils import PID, RingBuffer,temppressure
from app.workers import CameraExposureThread, fitdatathread, getDataReceiverWorker, SaveTelemetryThread


class RbMonitorProgram(QtWidgets.QMainWindow, Ui_RbMoniter, erlBase):

    rbcentres = RingBuffer(size=6)
    etaloncentres = RingBuffer()
    trigtimesfitted = RingBuffer()
    trigtimes = RingBuffer()
    temps = RingBuffer()
    looptimes = RingBuffer()
    trigtimescontrol = RingBuffer()
    controlvalues = RingBuffer()
    externaltemp = RingBuffer()
    pressure = RingBuffer()
    humidity = RingBuffer()


    DataReceiverThread = []
    dataReceivedWorker = []
    exposure_thread = []

    def __init__(self):
        super(RbMonitorProgram, self).__init__()
        erlBase.__init__(self)

        self.setupUi(self)
        # self.showMaximized()
        # uic.loadUi(os.path.join(bundle_dir, 'RbMoniter.ui'), self)
        self.cam = None

        self.lineEdit_rpIP.setText(str(self.config.rpIP))
        self.lineEdit_localIP.setText(str(self.config.localIP))

        self.ur = TCPIPreceiver(12345, 12346, 12347, self.config.aquisitionsize, self.config.rpIP)

        self.exec = remoteexecutor(self.config.rpIP)
        self.exec.startserver(self.config.localIP, self.config.useExtPID, self.config.aquisitionsize)

        if 'darwin' in sys.platform:
            self.logger.info('Running \'caffeinate\' on MacOSX to prevent the system from sleeping')
            subprocess.Popen('caffeinate')

        time.sleep(0.5)
        self.doubleSpinBox_mesetpoint.setValue(self.config.MESetPointStart)
        self.ur.sendAckResponse(self.config.MESetPointStart)
        time.sleep(1)
        self.ur.receiveDACData()
        self.ur.recieveTrigerTimeAndTemp()

        self.startbutton.clicked.connect(self.startDataReceiverThread)
        self.stopbutton.clicked.connect(self.stopUdpReceiverThread)
        self.pushButton_savedata.clicked.connect(self.saveTimeSeries)
        # self.pushButton_resetUDP.clicked.connect(self.restartRP)
        self.pushButton_clearData.clicked.connect(self.clearData)
        self.pushButton_connectCamera.clicked.connect(self.setupCamera)
        self.pushButton_cameraStartExposure.clicked.connect(self.take_exposure)

        self.plot_etalondata = self.pw_etalondata.plot()
        self.plot_rbdata = self.pw_rbdata.plot()
        self.DiagnosticRbPlot = self.pw_DiagnosticRbPlot.plot()
        self.DiagnosticEtalonPlot = self.pw_DiagnosticEtalonPlot.plot()
        self.EnvironmentTempPlot = self.pw_externalTemp.plot()
        self.EnvironmentPressurePlot = self.pw_externalPressure.plot()
        self.EnvironmentHumidityPlot = self.pw_externalHumidity.plot()

        self.pw_rawtimeseriesPlot = self.glw_rawtimeseries.addPlot()
        self.plot_rawtimeseries1 = self.pw_rawtimeseriesPlot.plot(pen=(0, 0, 200))
        self.plot_rawtimeseries2 = self.pw_rawtimeseriesPlot.plot(pen=(0, 128, 0))

        self.pw_velocitytimeseries = self.glw_velocitytimeseries.addPlot()
        self.plot_velocitytimeseries = self.pw_velocitytimeseries.plot()

        self.pw_temp = self.glw_tempandcontrol.addPlot(row=1, col=1)
        self.plot_temp = self.pw_temp.plot()
        self.pw_control = self.glw_tempandcontrol.addPlot(row=1, col=1)
        self.pw_control.showAxis('right')
        self.pw_control.hideAxis('left')
        self.pw_temp.showAxis('left')
        self.pw_temp.getAxis('right').setLabel('axis2', color='#0000ff')
        self.pw_control.setXLink(self.pw_temp)
        self.plot_control = self.pw_control.plot(pen=(0, 128, 0))

        self.pw_rawtimeseriesPlot.setXLink(self.pw_temp)
        self.pw_velocitytimeseries.setXLink(self.pw_temp)

        self.plot_etalondata.setDownsampling(method='peak', auto=True)
        self.plot_rbdata.setDownsampling(method='peak', auto=True)
        self.DiagnosticRbPlot.setDownsampling(method='peak', auto=True)
        self.DiagnosticEtalonPlot.setDownsampling(method='peak', auto=True)
        self.EnvironmentTempPlot.setDownsampling(method='peak', auto=True)
        self.EnvironmentPressurePlot.setDownsampling(method='peak', auto=True)
        self.EnvironmentHumidityPlot.setDownsampling(method='peak', auto=True)
        self.plot_rawtimeseries1.setDownsampling(method='peak', auto=True)
        self.plot_rawtimeseries2.setDownsampling(method='peak', auto=True)
        self.plot_velocitytimeseries.setDownsampling(method='peak', auto=True)
        self.plot_temp.setDownsampling(method='peak', auto=True)

        self.doubleSpinBox_P.valueChanged.connect(self.updatePIDparameters)
        self.doubleSpinBox_I.valueChanged.connect(self.updatePIDparameters)
        self.doubleSpinBox_D.valueChanged.connect(self.updatePIDparameters)

        self.pid = PID()
        self.pid.setKpid(self.doubleSpinBox_P.value(), self.doubleSpinBox_I.value(), self.doubleSpinBox_D.value())

        self.doubleSpinBox_mesetpoint_max.valueChanged.connect(self.doubleSpinBox_mesetpoint.setMaximum)
        self.doubleSpinBox_mesetpoint_max.valueChanged.connect(self.pid.setMax)
        self.doubleSpinBox_mesetpoint_min.valueChanged.connect(self.doubleSpinBox_mesetpoint.setMinimum)
        self.doubleSpinBox_mesetpoint_min.valueChanged.connect(self.pid.setMin)
        self.pushButton_resetPID.clicked.connect(self.resetPID)

        #self.temppressure = temppressure(self.config.arduinoport)

        if self.config.useExtPID:
            self.doubleSpinBox_mesetpoint_max.setValue(25)
            self.doubleSpinBox_mesetpoint_min.setValue(3)
        else:
            self.doubleSpinBox_mesetpoint_max.setValue(0.8)
            self.doubleSpinBox_mesetpoint_min.setValue(0)

        self.logger.info("Started.")

    def clearData(self):
        self.rbcentres.clear()
        self.etaloncentres.clear()
        self.trigtimes.clear()
        self.temps.clear()
        self.looptimes.clear()
        self.trigtimesfitted.clear()
        self.trigtimescontrol.clear()
        self.controlvalues.clear()
        self.externaltemp.clear()
        self.pressure.clear()
        self.humidity.clear()

        self.updatePIDparameters(0)

    def closeEvent(self, event):
        if self.stopbutton.isEnabled():
            event.ignore()
            return

        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               "Are you sure to quit?", QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.stopUdpReceiverThread()
                self.ur.sendEndResponse()
                self.logger.info("done\n")
            finally:
                event.accept()
        else:
            event.ignore()

    def startDataReceiverThread(self):
        self.DataReceiverThread = QtCore.QThread(self)
        self.DataReceiverThread.setTerminationEnabled(True)
        self.dataReceivedWorker = getDataReceiverWorker(self.ur, self.doubleSpinBox_mesetpoint.value())

        self.dataReceivedWorker.moveToThread(self.DataReceiverThread)
        # noinspection PyUnresolvedReferences
        self.DataReceiverThread.started.connect(self.dataReceivedWorker.dataRecvLoop)
        self.stopbutton.clicked.connect(self.stopClicked)
        self.doubleSpinBox_mesetpoint.valueChanged.connect(self.tempChanged)
        self.dataReceivedWorker.dataReady.connect(self.fitdata)

        self.dataReceivedWorker.finished.connect(self.DataReceiverThread.quit)
        self.dataReceivedWorker.dataReady.connect(self.plotData)
        # self.checkBox_fitting.stateChanged.connect(self.toggleFittingsConection)
        # if self.checkBox_fitting.isChecked():
        #    self.worker.dataReady.connect(self.fitdata)

        self.dataReceivedWorker.errorOccured.connect(self.restartRP)

        self.DataReceiverThread.start()

        self.startbutton.setEnabled(False)
        self.stopbutton.setEnabled(True)

    @pyqtSlot()
    def stopClicked(self):
        self.dataReceivedWorker.stop()

    @pyqtSlot(float)
    def tempChanged(self, temp):
        self.dataReceivedWorker.tempchangedinGUI(temp)

    def stopUdpReceiverThread(self):
        # QtWidgets.QApplication.processEvents()
        if hasattr(self, 'DataReceiverThread'):
            if self.DataReceiverThread.isRunning():
                self.DataReceiverThread.terminate()
                # while not self.UdpReceiverThread.isFinished():
                #    time.sleep(0.1)

            # self.UdpReceiverThread.terminate()
            self.startbutton.setEnabled(True)
            self.stopbutton.setEnabled(False)

    @pyqtSlot(np.ndarray, np.ndarray, tuple, name="plotData")
    def plotData(self, dataA, dataB, telemetry):
        self.trimdatadeques()

        (trigtime, temp, looptime, tempexternal, pressure, humidity) = telemetry

        self.trigtimes.append(trigtime)
        self.temps.append(temp)
        self.looptimes.append(looptime)
        self.externaltemp.append(tempexternal)
        self.pressure.append(pressure)
        self.humidity.append(humidity)

        QtWidgets.QApplication.processEvents()

        if not len(self.trigtimes) % 1:  # update every spinBox_update_rate.value() samples
            # print(trigtime,temp,1/looptime)
            if self.tabWidget_display.currentIndex() is 1:
                self.DiagnosticRbPlot.setData(y=dataB, x=self.x)
                self.DiagnosticEtalonPlot.setData(y=dataA, x=self.x)

            elif self.tabWidget_display.currentIndex() is 3:
                if len(self.trigtimes) > 1:
                    self.EnvironmentTempPlot.setData(y=self.externaltemp.data[-self.spinBox_plotwindowsize.value():],
                                                     x=(self.trigtimes.data[-self.spinBox_plotwindowsize.value():] -
                                                        self.trigtimes.data[0]) / 1000)

                    self.EnvironmentPressurePlot.setData(y=self.pressure.data[-self.spinBox_plotwindowsize.value():],
                                                             x=(self.trigtimes.data[-self.spinBox_plotwindowsize.value():] -
                                                                self.trigtimes.data[0]) / 1000)

                    self.EnvironmentHumidityPlot.setData(y=self.humidity.data[-self.spinBox_plotwindowsize.value():],
                                                             x=(self.trigtimes.data[-self.spinBox_plotwindowsize.value():] -
                                                                self.trigtimes.data[0]) / 1000)

            elif self.tabWidget_display.currentIndex() is 0:
                # t = time.time()
                #
                self.plot_etalondata.setData(y=dataA * self.config.samplescale_ms, x=self.x)
                self.plot_rbdata.setData(y=dataB * self.config.samplescale_ms, x=self.x)
                if len(self.trigtimes) > 1:
                    self.plot_temp.setData(y=self.temps.data[-self.spinBox_plotwindowsize.value():],
                                           x=(self.trigtimes.data[-self.spinBox_plotwindowsize.value():] -
                                              self.trigtimes.data[0]) / 1000)

                if len(self.trigtimes) > 1:
                    self.lcdNumber_dateRate.display(1000 / np.mean(np.diff(self.trigtimes.data[-100:])))
                    # self.lcdNumber_triggerCount.display(1 / np.mean(self.looptimes[-20:]))
                    self.lcdNumber_triggerCount.display(self.looptimes.totaldataadded)

                    self.lcdNumber_tempStd.display(1000 * np.std(self.temps.data[-100:]))

    # noinspection PyUnusedLocal
    @pyqtSlot(np.ndarray, np.ndarray, tuple)
    def fitdata(self, dataA, dataB, telemetry):
        (trigtime, temp, looptime, tempexternal, pressure, humidity) = telemetry
        if self.checkBox_fitting.isChecked():
            # t = time.time()
            if self.checkBox_fitting.isChecked() and (not dataA.max() < 500 or dataB.min() > -300):
                fittingwork = fitdatathread(dataA, dataB, trigtime)
                fittingwork.dataReady.connect(self.plotfitdata)
                fittingwork.start()
                fittingwork.wait()
            else:
                self.logger.debug(
                    'fitdata: Skipped with dataA.max {} and dataB.min {}'.format(dataA.max(), dataB.min()))
        if not self.config.useExtPID:  # not using external PID
            if self.radioButton_PIDUseTemp.isChecked() and len(self.temps) > 0:
                self.PIDaction((self.temps.data[-10:]).mean(), 3.44, trigtime, self.config.delay)

    def PIDaction(self, PIDinput, setPoint, trigtime, delay):
        if self.checkBox_PIDonoff.isChecked() and not len(self.trigtimes) % delay:
            if self.pid.firstTime:
                self.pid.prevtm = trigtime / 1000

                self.pid.firstTime = False
                self.pid.Ci = self.doubleSpinBox_mesetpoint.value()  # initial value, i.e. don't set current/temp ot
                # zero.
                newMESetPoint = self.doubleSpinBox_mesetpoint.value()  # initial value, i.e. don't set current ot zero.
            else:
                newMESetPoint = self.pid.update(PIDinput, setPoint, trigtime / 1000)

            self.doubleSpinBox_mesetpoint.setValue(newMESetPoint)
        else:
            pass

        if len(self.trigtimes) > 1:
            self.trigtimescontrol.append(trigtime)
            self.controlvalues.append(self.doubleSpinBox_mesetpoint.value())
            self.plot_control.setData(y=self.controlvalues.data[-self.spinBox_plotwindowsize.value():],
                                      x=(self.trigtimescontrol.data[-self.spinBox_plotwindowsize.value():]
                                         - self.trigtimes.data[0]) / 1000)

    # noinspection PyUnusedLocal
    def updatePIDparameters(self, new_value):
        self.pid.setKpid(self.doubleSpinBox_P.value(), self.doubleSpinBox_I.value(), self.doubleSpinBox_D.value())
        self.logger.debug("PID changed")

    def resetPID(self):
        self.pid = PID()
        self.pid.setKpid(self.doubleSpinBox_P.value(), self.doubleSpinBox_I.value(), self.doubleSpinBox_D.value())

    def trimdatadeques(self):
        savelength=4000
        mindatainbuffer=6000

        if not len(self.trigtimesfitted) % savelength and len(self.trigtimesfitted) > mindatainbuffer:
            rbcentres_out = []
            etaloncentres_out = []
            trigtimesfitted_out = []
            for i in range(savelength):
                rbcentres_out.append(self.rbcentres.popleft())
                etaloncentres_out.append(self.etaloncentres.popleft())
                trigtimesfitted_out.append(self.trigtimesfitted.popleft())

            dataout = np.column_stack((rbcentres_out, etaloncentres_out, trigtimesfitted_out))
            worker1 = SaveTelemetryThread(os.path.join(self.config.rbLockData_directory, 'data-RbEt.csv'), dataout)
            worker1.start()

        if not len(self.trigtimes) % savelength and len(self.trigtimes) > mindatainbuffer:
            looptimes_out = []
            temps_out = []
            trigtimes_out = []
            externaltemp_out = []
            pressure_out = []
            humidity_out = []
            for i in range(savelength):
                looptimes_out.append( self.looptimes.popleft())
                temps_out.append(self.temps.popleft())
                trigtimes_out.append(self.trigtimes.popleft())
                externaltemp_out.append(self.externaltemp.popleft())
                pressure_out.append(self.pressure.popleft())
                humidity_out.append(self.humidity.popleft())


            dataout = np.column_stack((trigtimes_out, looptimes_out, temps_out,externaltemp_out,pressure_out,humidity_out))
            worker2 = SaveTelemetryThread(os.path.join(self.config.rbLockData_directory, 'data-temp.csv'), dataout)
            worker2.start()

        if not len(self.trigtimescontrol) % savelength and len(self.trigtimescontrol) > mindatainbuffer:
            controlvalues_out = []
            trigtimescontrol_out = []
            for i in range(savelength):
                controlvalues_out.append(self.controlvalues.popleft())
                trigtimescontrol_out.append(self.trigtimescontrol.popleft())

            dataout = np.column_stack((trigtimescontrol_out, controlvalues_out))
            worker3 = SaveTelemetryThread(os.path.join(self.config.rbLockData_directory, 'data-control.csv'), dataout)
            worker3.start()

    def plotfitdata(self, etaloncentre, newRBcentre, trigtime):
        if 0: #len(self.rbcentres) > *6 and (abs(np.mean(newRBcentre) - np.mean(self.rbcentres.data[-20:],axis=1)) > 10):
            #                           or abs(etaloncentre - self.etaloncentres[-1]) > 500):
            print('335')
            return
        else:
            if len(self.rbcentres.data) > 20:
                if abs(np.mean(newRBcentre) - self.rbcentres.data[-20:].mean(axis=1).mean()) > 20:
                    self.logger.warning("bad rb value({0}):")
                    return

            self.etaloncentres.append(etaloncentre)
            self.rbcentres.append(newRBcentre)
            self.trigtimesfitted.append(trigtime)

            try:
                if len(self.trigtimesfitted) > 1:
                    plotimefitted = self.trigtimesfitted.data / 1000
                    # plotimefitted -= plotimefitted[0]
                    plotimefitted -= self.trigtimes.data[0] / 1000

                    # rbplotdata = savgol_filter(np.mean(np.asarray(self.rbcentres), axis=1),
                    #                         self.spinBox_smoothingWindow.value(), 3)

                    rbplotdata = np.mean(self.rbcentres.data, axis=1) * self.config.samplescale_ms

                    etalonplotdata = self.etaloncentres.data * self.config.samplescale_ms

                    error = -(etalonplotdata - rbplotdata)
                    # rbplotdata -= rbplotdata[0]
                    # etalonplotdata -= etalonplotdata[0]

                    delay = self.config.delay
                    if self.radioButton_PIDUseEtalon.isChecked():
                        self.PIDaction((error[-1:] * self.config.degperms).mean(), 0, trigtime, delay)

                    win = self.spinBox_plotwindowsize.value()
                    if self.checkBox_etalonsmoothing.isChecked():
                        smootherror, veltimes, binnumber = \
                            binned_statistic(plotimefitted[-win:], error[-win:],
                                             bins=np.arange(plotimefitted[-win:].min(), plotimefitted[-win:].max(),
                                                            self.doubleSpinBox_etalonbinsize.value()))
                        veltimes = veltimes[1:]
                    else:
                        smootherror = error[-win:]
                        veltimes = plotimefitted[-win:]

                    if not len(self.trigtimesfitted) % self.spinBox_updaterate.value():
                        self.plot_rawtimeseries1.setData(y=rbplotdata[-win:] - rbplotdata[-win:].mean(),
                                                         x=plotimefitted[-win:])
                        self.plot_rawtimeseries2.setData(y=etalonplotdata[-win:] - etalonplotdata[-win:].mean(),
                                                         x=plotimefitted[-win:])
                        self.plot_velocitytimeseries.setData(y=smootherror, x=veltimes)

                    if len(self.rbcentres) > 1 and not len(self.trigtimes) % self.spinBox_updaterate.value() * 4:
                        # self.lcdNumber_rbStd.display(sigma_clip(rbplotdata,sigma=4).std())
                        # self.lcdNumber_etalonStd.display(sigma_clip(etalonplotdata,sigma=4).std())
                        self.lcdNumber_rbStd.display(rbplotdata[-win:].std())
                        self.lcdNumber_etalonStd.display(smootherror.std())

                    if len(self.trigtimesfitted) > 1:
                        self.lcdNumber_fitrate.display(1000/np.mean(np.diff(self.trigtimesfitted.data[-100:])))

            except (IndexError, ValueError, TypeError, RuntimeError) as err:
                self.logger.warning("plot fit error({0}):".format(err))
                self.etaloncentres.pop()
                self.rbcentres.pop()
                self.trigtimesfitted.pop()

    def saveTimeSeries(self):
        scipy.io.savemat(os.path.join(self.config.rbLockData_directory, 'data.mat'),
                         mdict={'rbdata': self.rbcentres.data,
                                'etalondata': self.etaloncentres.data,
                                'trigtimes': self.trigtimes.data,
                                'temps': self.temps.data,
                                'looptimes': self.looptimes.data,
                                'trigtimesfitted': self.trigtimesfitted.data,
                                'rbraw': self.ur.dataB,
                                'etalonraw': self.ur.dataA
                                })

    @pyqtSlot()
    def restartRP(self):
        raise NotImplementedError

    def setupCamera(self):
        self.cam = Camera()
        self.pushButton_connectCamera.setDisabled(True)
        self.pushButton_DisconnectCamera.setEnabled(True)
        # self.pushButton_CoolerToggle.setEnabled(True)
        self.pushButton_CoolerToggle.setChecked(True)
        self.pushButton_cameraStartExposure.setEnabled(True)
        self.doubleSpinBox_ExposureTime.valueChanged.connect(self.setCamExposure)

    def take_exposure(self):
        self.exposure_thread = CameraExposureThread(self.cam, self.radioButton_continuousExposures.isChecked())
        self.exposure_thread.dataReady.connect(self.plotCCDimage)
        self.exposure_thread.finished.connect(self.exposure_thread.quit)

        if self.radioButton_continuousExposures.isChecked():
            self.pushButton_cameraStopExposure.setEnabled(True)
            self.pushButton_cameraStopExposure.clicked.connect(self.stopExposureClicked)

        self.exposure_thread.start()
        self.logger.debug('Camera: Take Exposure Thread Started')
        # self.exposure_thread.wait()

    @pyqtSlot()
    def stopExposureClicked(self):
        self.logger.debug('Camera: Take Exposure Continous Stopped')
        self.exposure_thread.stopContinous()
        self.pushButton_cameraStopExposure.setEnabled(False)

    @pyqtSlot(np.ndarray, Time,float, float, float)
    def plotCCDimage(self, imdata, time_start, temp, pressure, hum):
        self.logger.info("Image Data Received")
        self.pw_FullCCDImage.setImage(imdata)
        if self.checkBox_saveCameraFile.isChecked():
            basefilename = self.lineEdit_cameraFilename.text() or "test"
            filename = os.path.join(self.config.image_directory,
                                    basefilename + '-' + '{:f}'.format(time_start.mjd) + '.fit')
            self.cam.save_image_to_fits(imagetime=time_start, imdata=imdata, filename=filename,
                                        exposuretime=int(self.doubleSpinBox_ExposureTime.value()),
                                        temp=temp, pressure=pressure, hum=hum)

    @pyqtSlot(float)
    def setCamExposure(self, exposure_time):
        self.logger.debug('Camera: Exposure set to %d ms', int(exposure_time * 1000))
        self.cam.CCD_exposure = int(exposure_time * 1000)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RbMonitorProgram()
    win.show()
    win.raise_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

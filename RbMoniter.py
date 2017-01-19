#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:11:52 2016

@author: chrisbetters
"""

import itertools
import os
import socket
import subprocess
import sys
import time
from collections import deque

import PyQt5
import numpy as np
import scipy.io
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from scipy import signal
from scipy.stats import binned_statistic

import RBfitting as fr
import TCPIPreceiver
from PID import PID
from RbMoniterUI import Ui_RbMoniter
from remoteexecutor import remoteexecutor

from configVariables import *

if getattr(sys, 'frozen', False) or sys.platform == 'win32':
    # we are running in a bundle
    # noinspection PyProtectedMember
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    print(bundle_dir)
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    with open('RbMoniterUI.py', 'w') as fout:
        PyQt5.uic.compileUi(os.path.join(bundle_dir, 'RbMoniter.ui'), fout)
    print(bundle_dir)


localIP = socket.gethostbyname(socket.gethostname())  # socket.getfqdn()
rpIP = socket.gethostbyname('redpitaya1.sail-laboratories.com')

class RbMoniterProgram(QtWidgets.QMainWindow, Ui_RbMoniter):
    rbcentres = deque()
    etaloncentres = deque()
    trigtimesfitted = deque()

    trigtimes = deque()
    temps = deque()
    looptimes = deque()

    def __init__(self):
        super(RbMoniterProgram, self).__init__()
        self.setupUi(self)
        self.showMaximized()
        # uic.loadUi(os.path.join(bundle_dir, 'RbMoniter.ui'), self)

        self.lineEdit_rpIP.setText(str(rpIP))
        self.lineEdit_localIP.setText(str(localIP))

        self.ur = TCPIPreceiver.TCPIPreceiver(12345, 12346, 12347, aquisitionsize, rpIP)
        if sys.platform == 'win32':
            sshcmd = "\"C:\Program Files (x86)\PuTTY\plink.exe\" -pw notroot -ssh "
            subprocess.run(sshcmd + "root@" + rpIP + " killall UDPStreamer")

            self.exec = remoteexecutor(sshcmd + "-t " + "-t " + "root@" + rpIP + " ~/RpRbDAQ/UDPStreamer -i " + localIP + " -m " + "1 " + "-a " + str(aquisitionsize))
        else:
            subprocess.run(["ssh", "root@" + rpIP, "killall UDPStreamer"])
            sshcmd = ["ssh", "-t", "-t", "root@" + rpIP, "~/RpRbDAQ/UDPStreamer", "-i", localIP, "-m", "1","-a",str(aquisitionsize)]
            print(" ".join(sshcmd))
            self.exec = remoteexecutor(sshcmd)

        if 'darwin' in sys.platform:
            print('Running \'caffeinate\' on MacOSX to prevent the system from sleeping')
            subprocess.Popen('caffeinate')

        time.sleep(0.5)
        #self.ur.sendAckResponse(self.doubleSpinBox_tempsetpoint.value())
        self.doubleSpinBox_tempsetpoint.setValue(starttemp)
        self.ur.sendAckResponse(starttemp)
        #self.ur.sendAckResponse(0.55)
        time.sleep(0.5)
        self.ur.receiveDACData()
        self.ur.recieveTrigerTimeAndTemp()

        self.startbutton.clicked.connect(self.startUdpRecevierThread)
        self.stopbutton.clicked.connect(self.stopUdpRecevierThread)
        self.pushButton_savedata.clicked.connect(self.saveTimeSeries)
        # self.pushButton_resetUDP.clicked.connect(self.restartRP)
        self.pushButton_clearData.clicked.connect(self.clearData)

        self.plot_etalondata = self.pw_etalondata.plot()
        self.plot_rbdata = self.pw_rbdata.plot()
        self.DiagnosticRbPlot = self.pw_DiagnosticRbPlot.plot()
        self.DiagnosticEtalonPlot = self.pw_DiagnosticEtalonPlot.plot()
        self.plot_rawtimeseriesPlot = self.glw_rawtimeseries.addPlot()
        self.plot_rawtimeseries1 = self.plot_rawtimeseriesPlot.plot(pen=(0, 0, 200))
        self.plot_rawtimeseries2 = self.plot_rawtimeseriesPlot.plot(pen=(0, 128, 0))
        self.plot_velocitytimeseries = self.pw_velocitytimeseries.plot()
        self.plot_temp = self.pw_temp.plot()

        self.plot_etalondata.setDownsampling(method='peak', auto=True)
        self.plot_rbdata.setDownsampling(method='peak', auto=True)
        self.DiagnosticRbPlot.setDownsampling(method='peak', auto=True)
        self.DiagnosticEtalonPlot.setDownsampling(method='peak', auto=True)
        self.plot_rawtimeseries1.setDownsampling(method='peak', auto=True)
        self.plot_rawtimeseries2.setDownsampling(method='peak', auto=True)
        self.plot_velocitytimeseries.setDownsampling(method='peak', auto=True)
        self.plot_temp.setDownsampling(method='peak', auto=True)

        self.doubleSpinBox_P.valueChanged.connect(self.updatePIDparameters)
        self.doubleSpinBox_I.valueChanged.connect(self.updatePIDparameters)
        self.doubleSpinBox_D.valueChanged.connect(self.updatePIDparameters)
        self.pid = PID()
        self.pid.setKpid(self.doubleSpinBox_P.value(), self.doubleSpinBox_I.value(), self.doubleSpinBox_D.value())

        print("Started.")

    def clearData(self):
        self.rbcentres.clear()
        self.etaloncentres.clear()
        self.trigtimes.clear()
        self.temps.clear()
        self.looptimes.clear()
        self.trigtimesfitted.clear()
        self.pid=PID()
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
                self.stopUdpRecevierThread()
                self.ur.sendEndResponse()
                print("closing ssh\n")
                self.exec.close()
                subprocess.run(["ssh", "root@" + rpIP, "killall UDPStreamer"])
                print("done\n")
            finally:
                event.accept()
        else:
            event.ignore()

    def startUdpRecevierThread(self):
        self.UdpRecevierThread = QtCore.QThread(self)
        self.UdpRecevierThread.setTerminationEnabled(True)
        self.worker = getDataRecevierWorker(self.ur, self.doubleSpinBox_tempsetpoint.value())

        self.worker.moveToThread(self.UdpRecevierThread)
        self.UdpRecevierThread.started.connect(self.worker.dataRecvLoop)
        self.stopbutton.clicked.connect(self.stopClicked)
        self.doubleSpinBox_tempsetpoint.valueChanged.connect(self.tempChanged)
        self.worker.dataReady.connect(self.fitdata)

        self.worker.finished.connect(self.UdpRecevierThread.quit)
        self.worker.dataReady.connect(self.plotdata)
        # self.checkBox_fitting.stateChanged.connect(self.toggleFittingsConection)
        # if self.checkBox_fitting.isChecked():
        #    self.worker.dataReady.connect(self.fitdata)

        self.worker.errorOccured.connect(self.restartRP)

        self.UdpRecevierThread.start()

        self.startbutton.setEnabled(False)
        self.stopbutton.setEnabled(True)

    @pyqtSlot()
    def stopClicked(self):
        self.worker.stop()

    @pyqtSlot(float)
    def tempChanged(self,temp):
        self.worker.tempchangedinGUI(temp)

    # def toggleFittingsConection(self):
    #     if self.checkBox_fitting.isChecked():
    #         self.worker.dataReady.connect(self.fitdata, type=QtCore.Qt.UniqueConnection)
    #     else:
    #         while True:
    #             try:
    #                 self.worker.dataReady.disconnect(self.fitdata)
    #             except TypeError:
    #                 break

    def stopUdpRecevierThread(self):
        # QtWidgets.QApplication.processEvents()
        if (self.UdpRecevierThread.isRunning()):
            self.UdpRecevierThread.terminate()
            # while not self.UdpRecevierThread.isFinished():
            #    time.sleep(0.1)

        # self.UdpRecevierThread.terminate()
        self.startbutton.setEnabled(True)
        self.stopbutton.setEnabled(False)


    @pyqtSlot(np.ndarray, np.ndarray, float, float, float, name="plotdata")
    def plotdata(self, dataA, dataB, trigtime, temp, looptime):
        self.trigtimes.append(trigtime)
        self.temps.append(temp)
        self.looptimes.append(looptime)

        if not len(self.trigtimes) % 1:  # update every spinBox_updaterate.value() samples
            # print(trigtime,temp,1/looptime)
            if self.tabWidget.currentIndex():
                self.DiagnosticRbPlot.setData(y=dataB, x=x)
                self.DiagnosticEtalonPlot.setData(y=dataA, x=x)
            else:
                # t = time.time()
                #
                self.plot_etalondata.setData(y=dataA, x=x)
                self.plot_rbdata.setData(y=dataB, x=x)
                if (len(self.trigtimes) > 1):
                    self.plot_temp.setData(y=np.asarray(self.temps)[-self.spinBox_plotwindowsize.value():],
                                           x=(np.asarray(self.trigtimes)[-self.spinBox_plotwindowsize.value():] - self.trigtimes[0]) / 1000)
                    # start, finish = fr.getRbWindow(dataB[0:120000])

        # if not len(self.trigtimes) % 4:
        #     plotime = np.asarray(self.trigtimes) / 1000
        #     plotime -= plotime[0]
        #     self.plot_temp.setData(y=np.asarray(self.temps)[-self.spinBox_plotwindowsize.value():], x=plotime[-self.spinBox_plotwindowsize.value():])

        if (len(self.trigtimes) > 1):
            self.lcdNumber_dateRate.display(1 / np.mean(np.diff(list(
                itertools.islice(self.trigtimes, max([len(self.trigtimes) - 100, 0]),
                                 len(self.trigtimes)))) / 1000))
            # self.lcdNumber_triggerCount.display(1 / np.mean(self.looptimes[-20:]))
            self.lcdNumber_triggerCount.display(len(self.looptimes))



            # if not len(self.trigtimes) % 30:
            #    self.plot_rbdata.getViewBox().setXRange(start, finish)

    @pyqtSlot(np.ndarray, np.ndarray, float, float, float)
    def fitdata(self, dataA, dataB, trigtime, temp, looptime):
        if self.checkBox_fitting.isChecked():
            # t = time.time()
            if self.checkBox_fitting.isChecked() and (not dataA.max() < 1200 or dataB.min() > -300):
                fittingwork = fitdatathread(dataA, dataB, trigtime)
                fittingwork.dataReady.connect(self.plotfitdata)
                #fittingwork.dataReady.connect(self.PIDaction)
                fittingwork.start()
                fittingwork.wait()
            else:
                print('skipped 252')

    def PIDaction(self, averageEtalon, averageRb, trigtime,delay):

        if self.checkBox_PIDonoff.isChecked() and not len(self.trigtimes) % delay:
            if self.pid.firsttime:
                self.pid.prevtm = trigtime / 1000
                self.pid.setpoint = 0 #etaloncentre - np.mean(newRBcentre)
                self.pid.firsttime = False
            else:
                #averageEtalon=np.mean(np.diff(list(itertools.islice(self.etaloncentres, max([len(self.etaloncentres) - delay, 0]),len(self.etaloncentres)))))
                #averageRb = np.mean(np.diff(list(itertools.islice(self.rbcentres, max([len(self.etaloncentres) - delay, 0]),len(self.etaloncentres)))))

                error = self.pid.setpoint - (averageEtalon - averageRb).mean()/1000
                print(error)
                newtemp = self.pid.update(error, trigtime / 1000) + self.doubleSpinBox_tempsetpoint.value()
                self.doubleSpinBox_tempsetpoint.setValue(np.asscalar(newtemp))
                #self.tempChanged(newtemp)
        else:
            pass

    def updatePIDparameters(self, float):
        self.pid.setKpid(self.doubleSpinBox_P.value(), self.doubleSpinBox_I.value(), self.doubleSpinBox_D.value())

    def trimdatadeques(self):
        if not len(self.trigtimesfitted) % 8000 and len(self.trigtimesfitted) > 12000:
            with open('data-RbEt.csv', 'a', encoding='utf-8') as file:
                for i in range(0, 8000):
                    file.write("%f, %f, %f, %f, %f, " % tuple(self.rbcentres.popleft()) +
                               "%f, %f\n" % (self.etaloncentres.popleft(), self.trigtimesfitted.popleft()))

        if not len(self.trigtimes) % 8000 and len(self.trigtimes) > 12000:
            with open('data-temp.csv', 'a', encoding='utf-8') as file:
                for i in range(0, 8000):
                    file.write("%f, %f\n" % (self.trigtimes.popleft(), self.temps.popleft()))

    def plotfitdata(self, etaloncentre, newRBcentre, trigtime):
        if len(self.rbcentres) > 2 and (abs(np.mean(newRBcentre) - np.mean(self.rbcentres[-1])) > 500
                                        or abs(etaloncentre - self.etaloncentres[-1]) > 500):
            print('275')
            return
        else:
            self.etaloncentres.append(etaloncentre)
            self.rbcentres.append(newRBcentre)
            self.trigtimesfitted.append(trigtime)

        self.trimdatadeques()

        try:
            if len(self.trigtimesfitted) > 1:
                plotimefitted = np.asarray(self.trigtimesfitted) / 1000
                #plotimefitted -= plotimefitted[0]
                plotimefitted -= np.asarray(self.trigtimes[0]) / 1000

                # rbplotdata = savgol_filter(np.mean(np.asarray(self.rbcentres), axis=1),
                #                         self.spinBox_smoothingWindow.value(), 3)


                rbplotdata = np.mean(np.asarray(self.rbcentres), axis=1)

                etalonplotdata = np.asarray(self.etaloncentres)

                error = rbplotdata - etalonplotdata
                # rbplotdata -= rbplotdata[0]
                # etalonplotdata -= etalonplotdata[0]

                delay = 60
                self.PIDaction(etalonplotdata[-delay:], rbplotdata[-delay:], trigtime, delay)

                win=self.spinBox_plotwindowsize.value()
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
                    self.plot_rawtimeseries1.setData(y=rbplotdata[-win:] - rbplotdata[-win:].mean(), x=plotimefitted[-win:])
                    self.plot_rawtimeseries2.setData(y=etalonplotdata[-win:] - etalonplotdata[-win:].mean(), x=plotimefitted[-win:])
                    self.plot_velocitytimeseries.setData(y=smootherror, x=veltimes)

                if len(self.rbcentres) > 1 and not len(self.trigtimes) % self.spinBox_updaterate.value()*4:
                    # self.lcdNumber_rbStd.display(sigma_clip(rbplotdata,sigma=4).std())
                    # self.lcdNumber_etalonStd.display(sigma_clip(etalonplotdata,sigma=4).std())
                    self.lcdNumber_rbStd.display(fr.nm2ms(rbplotdata[-win:].std() * samplescale))
                    self.lcdNumber_etalonStd.display(fr.nm2ms(smootherror.std() * samplescale))

                if (len(self.trigtimesfitted) > 1):
                    self.lcdNumber_fitrate.display(1 / np.mean(np.diff(list(
                        itertools.islice(self.trigtimesfitted, max([len(self.trigtimesfitted) - 100, 0]),
                                         len(self.trigtimesfitted)))) / 1000))

        except IndexError:
            self.etaloncentres.pop()
            self.rbcentres.pop()
            self.trigtimesfitted.pop()

    def saveTimeSeries(self):
        scipy.io.savemat('data.mat',
                         mdict={'rbdata': self.rbcentres,
                                'etalondata': self.etaloncentres,
                                'trigtimes': self.trigtimes,
                                'temps': self.temps,
                                'looptimes': self.looptimes,
                                'trigtimesfitted': self.trigtimesfitted
                                })

    @pyqtSlot()
    def restartRP(self):

        self.stopUdpRecevierThread()

        del (self.ur)
        # self.ur=[]
        self.ur = TCPIPreceiver.TCPIPreceiver(12345, 12346, 12347, aquisitionsize, "10.66.101.121")
        if sys.platform == 'win32':
            sshcmd = "C:\Program Files (x86)\PuTTY\plink.exe -pw notroot -ssh"
        else:
            sshcmd = "ssh"

        subprocess.run(["ssh", "root@10.66.101.121", "killall UDPStreamer"])
        self.exec = remoteexecutor([sshcmd, "-t", "-t", "root@10.66.101.121", "~/RpRbDAQ/UDPStreamer"])

        self.startUdpRecevierThread()


class getDataRecevierWorker(QtCore.QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal(np.ndarray, np.ndarray, float, float, float)
    errorOccured = pyqtSignal()
    tempset = pyqtSignal(float)

    def __init__(self, ur, tempinit):
        QtCore.QObject.__init__(self)
        self.ur = ur
        self.CurrentTemp = tempinit
        self._mutex = QtCore.QMutex()
        self.running = True

    @pyqtSlot()
    def dataRecvLoop(self):
        print("dataRecvLoop start\n")
        while self.running:
            try:
                #print(self.CurrentTemp)
                t = time.time()
                self.ur.doALL(self.CurrentTemp)
                elapsed = time.time() - t
                if self.ur.dataA.size == aquisitionsize and self.ur.dataB.size == aquisitionsize:
                    self.dataReady.emit(self.ur.dataA, self.ur.dataB, self.ur.timetrigger, self.ur.temp, elapsed)
                else:
                    print('skipped 393')
            except socket.timeout:
                print("sock timeout error\n")
                self.errorOccured.emit()
                break

        print("getDataRecevierWorker while loop ended")
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


class fitdatathread(QtCore.QThread):
    dataReady = pyqtSignal(float, np.ndarray, float)

    def __init__(self, dataA, dataB, trigtime):
        QtCore.QThread.__init__(self)
        self.dataA = dataA
        self.dataB = dataB
        self.trigtime = trigtime

    def __del__(self):
        self.wait()

    def run(self):
        try:
            newRBcentre = fr.fitRblines(x, self.dataB)

            etalondata = signal.sosfiltfilt(sos, self.dataA)
            etaloncentre = fr.fitEtalon(x, etalondata, 10)

            self.dataReady.emit(etaloncentre, newRBcentre, self.trigtime)
        except (ValueError, TypeError, RuntimeError) as err:
            print("fit error({0}):".format(err))
            # raise err
            pass
        finally:
            pass
            # self.terminate()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RbMoniterProgram()
    win.show()
    win.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

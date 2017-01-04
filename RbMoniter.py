#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:11:52 2016

@author: chrisbetters
"""

import socket
import subprocess
import sys
import os
import time

import numpy as np
import scipy.io
from scipy import signal
from scipy.signal import savgol_filter
from scipy.stats import binned_statistic

import PyQt5
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import pyqtgraph

import RBfitting as fr
import TCPIPreceiver
from PID import PID
from remoteexecutor import remoteexecutor


sos = np.asarray([[5.80953794660816e-06, 1.16190758932163e-05, 5.80953794660816e-06, 1, -1.99516198526679, 0.995185223418579],[0.00240740227660535, 0.00240740227660535, 0, 1, -0.995185195446789, 0]])

#from FibreSwitchControl import FibreSwitchs

if getattr(sys, 'frozen', False):
        # we are running in a bundle
        # noinspection PyProtectedMember
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

aquisitionsize = 20000

localIP=socket.gethostbyname(socket.gethostname()) #socket.getfqdn()
rpIP=socket.gethostbyname('redpitaya1.sail-laboratories.com')

print(localIP)
print(rpIP)

x = np.arange(aquisitionsize)

temp=4.5

class getDataRecevierWorker(QtCore.QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal(np.ndarray, np.ndarray, float, float, float)
    errorOccured = pyqtSignal()

    running = True
    PIDready = False
    curErr = 0
    curtemp = temp

    def __init__(self, ur):
        QtCore.QObject.__init__(self)
        self.ur = ur

    @pyqtSlot()
    def dataRecvLoop(self):
        print("dataRecvLoop start\n")
        self.running = True
        while self.running:
            try:
                if self.PIDready:
                    self.tempchange = self.PID.update(self.curErr, self.ur.timetrigger)
                    # self.curtemp=self.curtemp + self.tempchange
                    # print(self.curtemp+self.tempchange)

                t = time.time()
                self.ur.doALL(self.curtemp)
                elapsed = time.time() - t

                self.dataReady.emit(self.ur.dataA, self.ur.dataB, self.ur.timetrigger, self.ur.temp, elapsed)

                if not self.PIDready:
                    self.PID = PID(kp=0.0005, starttime=float(self.ur.timetrigger))
                    self.PIDready = True

            except socket.timeout:
                print("sock timeout error\n")
                self.errorOccured.emit()
                break

        print("getDataRecevierWorker while loop ended")
        self.finished.emit()

    @pyqtSlot()
    def stopLoop(self):
        self.running = False

    @pyqtSlot(float)
    def setError(self, curErr):
        self.curErr = curErr


class RbMoniterProgram(QtWidgets.QMainWindow):
    rbcentres = []
    etaloncentres = []
    trigtimes = []
    temps = []
    looptimes = []

    errorValueReady = pyqtSignal(float)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        uic.loadUi(os.path.join(bundle_dir, 'RbMoniter.ui'), self)

        self.ur = TCPIPreceiver.TCPIPreceiver(12345, 12346, 12347, aquisitionsize, rpIP)
        if sys.platform == 'win32':
            sshcmd = "C:\Program Files (x86)\PuTTY\plink.exe -pw notroot -ssh "
            subprocess.run(sshcmd + "root@" + rpIP + " killall UDPStreamer")

            self.exec = remoteexecutor(sshcmd + "-t " + "-t " + "root@" + rpIP  + " ~/RpRbDAQ/UDPStreamer -i " + localIP)
        else:
            subprocess.run(["ssh", "root@" + rpIP, "killall UDPStreamer"])
            sshcmd=["ssh", "-t", "-t", "root@" + rpIP, "~/RpRbDAQ/UDPStreamer","-i",localIP]
            print(" ".join(sshcmd))
            self.exec = remoteexecutor(sshcmd)

        time.sleep(0.5)
        self.ur.sendAckResponse(temp)
        time.sleep(0.5)
        self.ur.receiveDACData()
        self.ur.recieveTrigerTimeAndTemp()

        self.startbutton.clicked.connect(self.startUdpRecevierThread)
        self.stopbutton.clicked.connect(self.stopUdpRecevierThread)
        self.pushButton_savedata.clicked.connect(self.saveTimeSeries)
        # self.pushButton_resetUDP.clicked.connect(self.restartRP)
        self.pushButton_clearData.clicked.connect(self.clearData)
        #self.radioButton_RbMointer.toggled.connect(self.toggleSwitch)
        #self.radioButton_Spec.clicked.connect(self.toggleSwitch)

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

        #self.fs=FibreSwitchs(port='/dev/tty.usbmodem142121')
        #self.fs.setStateTwo()

        #self.showMaximized()
        print("Started.")

    def clearData(self):
        self.rbcentres = []
        self.etaloncentres = []
        self.trigtimes = []
        self.temps = []
        self.looptimes = []

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
                subprocess.run(["ssh", "root@"+rpIP, "killall UDPStreamer"])
                print("done\n")
            finally:
                event.accept()
        else:
            event.ignore()

    def startUdpRecevierThread(self):
        self.UdpRecevierThread = QtCore.QThread(self)
        self.UdpRecevierThread.setTerminationEnabled(True)
        self.worker = getDataRecevierWorker(self.ur)

        self.worker.moveToThread(self.UdpRecevierThread)
        self.UdpRecevierThread.started.connect(self.worker.dataRecvLoop)
        self.stopbutton.clicked.connect(self.worker.stopLoop, type=QtCore.Qt.DirectConnection)
        self.errorValueReady.connect(self.worker.setError, type=QtCore.Qt.DirectConnection)

        self.worker.finished.connect(self.UdpRecevierThread.quit)
        self.worker.dataReady.connect(self.plotdata)
        self.checkBox_fitting.stateChanged.connect(self.toggleFittingsConection)
        if self.checkBox_fitting.isChecked():
            self.worker.dataReady.connect(self.fitdata)

        self.worker.errorOccured.connect(self.restartRP)

        self.UdpRecevierThread.start()

        self.startbutton.setEnabled(False)
        self.stopbutton.setEnabled(True)

    def toggleFittingsConection(self):
        if self.checkBox_fitting.isChecked():
            self.worker.dataReady.connect(self.fitdata)
        else:
            self.worker.dataReady.disconnect(self.fitdata)

    def stopUdpRecevierThread(self):
        # QtWidgets.QApplication.processEvents()
        if (self.UdpRecevierThread.isRunning()):
            self.UdpRecevierThread.terminate()
            # while not self.UdpRecevierThread.isFinished():
            #    time.sleep(0.1)

        # self.UdpRecevierThread.terminate()
        self.startbutton.setEnabled(True)
        self.stopbutton.setEnabled(False)

    def receiveData(self, dataA, dataB, trigtime, temp, looptime):
        pass


    @pyqtSlot(np.ndarray, np.ndarray, float, float, float,name="plotdata")
    def plotdata(self, dataA, dataB, trigtime, temp, looptime):



        if not len(self.trigtimes) % self.spinBox_updaterate.value():  # update every spinBox_updaterate.value() samples
            # print(trigtime,temp,1/looptime)
            if self.tabWidget.currentIndex():
                self.DiagnosticRbPlot.setData(y=dataB, x=x)
                self.DiagnosticEtalonPlot.setData(y=dataA, x=x)
            else:
                # t = time.time()
                #
                self.plot_etalondata.setData(y=dataA, x=x)
                self.plot_rbdata.setData(y=dataB, x=x)
                if (len(self.trigtimes)>1):
                    self.plot_temp.setData(y=self.temps,x=(np.asarray(self.trigtimes)-self.trigtimes[0])/1000)
                # start, finish = fr.getRbWindow(dataB[0:120000])



        # if not len(self.trigtimes) % 30:
        #    self.plot_rbdata.getViewBox().setXRange(start, finish)

    @pyqtSlot(np.ndarray, np.ndarray, float, float, float)
    def fitdata(self, dataA, dataB, trigtime, temp, looptime):
        # t = time.time()

        if (len(self.trigtimes) > 1):
            self.lcdNumber_dateRate.display(1 / np.mean(np.diff(self.trigtimes[-100:]) / 1000))
            # self.lcdNumber_triggerCount.display(1 / np.mean(self.looptimes[-20:]))
            self.lcdNumber_triggerCount.display(len(self.looptimes))

        try:
            newRBcentre =  fr.fitRblines(x, dataB)
            etalondata = signal.sosfiltfilt(sos, dataA)

            etaloncentre = fr.fitEtalon(x[0:20000:1], etalondata[0:20000:1],30)
            if len(self.rbcentres) > 2 and (abs(np.mean(newRBcentre)-np.mean(self.rbcentres[-1]))>20 or abs(etaloncentre-self.etaloncentres[-1])>20):
                raise RuntimeError
            else:
                self.etaloncentres.append(etaloncentre)
                self.rbcentres.append(newRBcentre)
                self.trigtimes.append(trigtime)
                self.temps.append(temp)
                self.looptimes.append(looptime)

        except RuntimeError:
            pass

        plotime = np.asarray(self.trigtimes) / 1000
        plotime -= plotime[0]

        if len(self.rbcentres) > 2:
            # rbplotdata = savgol_filter(np.mean(np.asarray(self.rbcentres), axis=1),
            #                            self.spinBox_smoothingWindow.value(), 3)
            rbplotdata = np.mean(np.asarray(self.rbcentres), axis=1)
            rbplotdata -= rbplotdata[0]

            etalonplotdata = np.asarray(self.etaloncentres)
            etalonplotdata-=etalonplotdata[0]

            error = rbplotdata-etalonplotdata
            if 0:
                error = fr.nm2ms((error - error[0:31].mean()) * 1.9881681277862515e-06)
            else:
                pass
                #error -= error[0:31].mean()

            self.errorValueReady.emit(error[-30:].mean())

            if self.checkBox_etalonsmoothing.isChecked():
                smootherror, veltimes, binnumber = \
                    binned_statistic(plotime, error,
                                     bins=np.arange(plotime.min(), plotime.max(),
                                                    self.doubleSpinBox_etalonbinsize.value()))
                veltimes = veltimes[1:]
            else:
                smootherror = error
                veltimes = plotime

            if not len(self.trigtimes) % 4:
                self.plot_rawtimeseries1.setData(y=rbplotdata - rbplotdata.mean(), x=plotime)
                self.plot_rawtimeseries2.setData(y=etalonplotdata - etalonplotdata.mean(), x=plotime)
                self.plot_velocitytimeseries.setData(y=smootherror, x=veltimes)
                self.plot_temp.setData(y=np.asarray(self.temps), x=plotime)

        if len(self.rbcentres) > 101 and not len(self.trigtimes) % 2:
            # self.lcdNumber_rbStd.display(sigma_clip(rbplotdata,sigma=4).std())
            # self.lcdNumber_etalonStd.display(sigma_clip(etalonplotdata,sigma=4).std())
            self.lcdNumber_rbStd.display(rbplotdata.std() * 1.9881681277862515e-06)
            self.lcdNumber_etalonStd.display(smootherror.std())
            # print(1/(time.time() - t))

    def saveTimeSeries(self):
        scipy.io.savemat('data.mat',
                         mdict={'rbdata': self.rbcentres,
                                'etalondata': self.etaloncentres,
                                'trigtimes': self.trigtimes,
                                'temps': self.temps,
                                'looptimes': self.looptimes
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
    # @pyqtSlot()
    # def toggleSwitch(self):
    #     if self.radioButton_RbMointer.isChecked():
    #         self.fs.setStateTwo()
    #     else:
    #         self.fs.setStateOne()



def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RbMoniterProgram()
    win.show()
    win.raise_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

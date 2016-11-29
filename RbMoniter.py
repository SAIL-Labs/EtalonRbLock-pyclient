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
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import pyqtgraph
from scipy.signal import savgol_filter
from scipy.stats import binned_statistic

import RBfitting as fr
import TCPIPreceiver
from PID import PID
from remoteexecutor import remoteexecutor
#from FibreSwitchControl import FibreSwitchs

if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

aquisitionsize = 150000

#rpIP='10.66.101.123'
#localIP='10.66.101.133'

#rpIP='192.168.2.2'
#localIP='192.168.2.1'

#rpIP='10.42.0.249'
#localIP='10.42.0.1'

#rpIP='192.168.2.7'
#localIP='192.168.2.6'

#rpIP='192.168.1.100'
#localIP='192.168.1.1'

localIP=socket.gethostbyname(socket.gethostname()) #socket.getfqdn()
rpIP=socket.gethostbyname('redpitaya1.sail-laboratories.com')
print(localIP)
print(rpIP)

x = np.arange(aquisitionsize)

class getDataRecevierWorker(QtCore.QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal(np.ndarray, np.ndarray, float, float, float)
    errorOccured = pyqtSignal()

    running = True
    PIDready = False
    curErr = 0
    curtemp = 10

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

        time.sleep(1)
        self.ur.sendAckResponse(10)
        time.sleep(1)
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
        self.plot_rawtimeseriesPlot = self.glw_rawtimeseries.addPlot()
        self.plot_rawtimeseries1 = self.plot_rawtimeseriesPlot.plot(pen=(0, 0, 200))
        self.plot_rawtimeseries2 = self.plot_rawtimeseriesPlot.plot(pen=(0, 128, 0))
        self.plot_velocitytimeseries = self.pw_velocitytimeseries.plot()
        self.plot_temp = self.pw_temp.plot()

        self.plot_etalondata.setDownsampling(method='peak', auto=True)
        self.plot_rbdata.setDownsampling(method='peak', auto=True)
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
        try:
            self.UdpRecevierThread.terminate()
        finally:
            pass

        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               "Are you sure to quit?", QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.UdpRecevierThread.start()
            try:
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

    @pyqtSlot(np.ndarray, np.ndarray, float, float, float)
    def plotdata(self, dataA, dataB, trigtime, temp, looptime):
        # print(trigtime,temp,1/looptime)

        # t = time.time()
        # if not len(self.trigtimes) % 15:
        self.plot_etalondata.setData(y=dataA, x=x)
        self.plot_rbdata.setData(y=dataB, x=x)
        # start, finish = fr.getRbWindow(dataB[0:120000])

        self.trigtimes.append(trigtime)
        self.temps.append(temp)
        self.looptimes.append(looptime)

        self.lcdNumber_dateRate.display(1 / np.mean(np.diff(self.trigtimes[-20:]) / 1000))
        # self.lcdNumber_triggerCount.display(1 / np.mean(self.looptimes[-20:]))
        self.lcdNumber_triggerCount.display(len(self.looptimes))


        # if not len(self.trigtimes) % 30:
        #    self.plot_rbdata.getViewBox().setXRange(start, finish)

    @pyqtSlot(np.ndarray, np.ndarray, float, float, float)
    def fitdata(self, dataA, dataB, trigtime, temp, looptime):
        # t = time.time()



        self.lcdNumber_dateRate.display(1 / np.mean(np.diff(self.trigtimes[-20:]) / 1000))
        # self.lcdNumber_triggerCount.display(1 / np.mean(self.looptimes[-20:]))
        self.lcdNumber_triggerCount.display(len(self.looptimes))

        start, finish = fr.getRbWindow(dataB[0:116000])
        newRBcentre = fr.fitRblines(x[start:finish:1], dataB[start:finish:1] * -1, start, finish)
        self.rbcentres.append(newRBcentre)

        centrestart = dataA.argmax()
        etaloncentre = fr.fitEtalon(x[centrestart - 40000:centrestart + 50000:10],
                                    dataA[centrestart - 40000:centrestart + 50000:10], centrestart)
        self.etaloncentres.append(etaloncentre)

        plotime = np.asarray(self.trigtimes) / 1000
        plotime -= plotime[0]

        if len(self.rbcentres) > 81:
            rbplotdata = savgol_filter(np.mean(np.asarray(self.rbcentres), axis=1),
                                       self.spinBox_smoothingWindow.value(), 3)
            etalonplotdata = np.asarray(self.etaloncentres)
            error = etalonplotdata - rbplotdata
            if 0:
                error = fr.nm2ms((error - error[0:31].mean()) * 3.1577e-7)
            else:
                error -= error[0:31].mean()

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

            if not len(self.trigtimes) % 5:
                self.plot_rawtimeseries1.setData(y=rbplotdata - rbplotdata.mean(), x=plotime)
                self.plot_rawtimeseries2.setData(y=etalonplotdata - etalonplotdata.mean(), x=plotime)
                self.plot_velocitytimeseries.setData(y=smootherror, x=veltimes)
                self.plot_temp.setData(y=np.asarray(self.temps), x=plotime)

        if len(self.rbcentres) > 101 and not len(self.trigtimes) % 30:
            # self.lcdNumber_rbStd.display(sigma_clip(rbplotdata,sigma=4).std())
            # self.lcdNumber_etalonStd.display(sigma_clip(etalonplotdata,sigma=4).std())
            self.lcdNumber_rbStd.display(rbplotdata.std() * 3.1577e-7)
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

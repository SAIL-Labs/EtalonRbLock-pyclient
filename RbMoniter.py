#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:11:52 2016

@author: chrisbetters
"""

from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
import pyqtgraph
import sys

from remoteexecutor import remoteexecutor
import RBfitting as fr
import updreceiver
import numpy as np
import scipy.io
import time
import subprocess
import socket
from RbMoniterUI import Ui_RbMoniter
from astropy.stats import sigma_clip

aquisitionsize=200000

x = np.arange(aquisitionsize)


class getDataRecevierWorker(QtCore.QObject):
    finished = pyqtSignal()
    dataReady = pyqtSignal(np.ndarray,np.ndarray,float,float,float)
    errorOccured = pyqtSignal()

    running=True

    def __init__(self,ur):
        QtCore.QObject.__init__(self)
        self.ur=ur

    @pyqtSlot()
    def dataRecvLoop(self):
        while self.running:
            try:
                t = time.time()
                self.ur.doALL()
                elapsed = time.time() - t

                self.dataReady.emit(self.ur.dataA,self.ur.dataB,self.ur.timetrigger,self.ur.temp,elapsed)
                QtWidgets.QApplication.processEvents()
            except socket.timeout:
                print("sock timeout error")
                self.errorOccured.emit()
                break
        print("getDataRecevierWorker while loop ended")
        self.finished.emit()

    @pyqtSlot()
    def stopLoop(self):
        self.running=False


class RbMoniterProgram(QtWidgets.QMainWindow,Ui_RbMoniter):
    rbcentres = []
    etaloncentres = []
    trigtimes = []
    temps = []
    looptimes = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        uic.loadUi('RbMoniter.ui', self)

        self.ur = updreceiver.updreceiver(12345, 12346, 12347, aquisitionsize, "10.66.101.121")
        if sys.platform == 'win32':
            sshcmd = "C:\Program Files (x86)\PuTTY\plink.exe -pw notroot -ssh"
        else:
            sshcmd = "ssh"

        subprocess.run(["ssh", "root@10.66.101.121", "killall UDPStreamer"])
        self.exec = remoteexecutor([sshcmd, "-t", "-t", "root@10.66.101.121", "~/RpRbDAQ/UDPStreamer"])

        self.startbutton.clicked.connect(self.startUdpRecevierThread)
        self.stopbutton.clicked.connect(self.stopUdpRecevierThread)
        self.pushButton_savedata.clicked.connect(self.saveTimeSeries)
        #self.pushButton_resetUDP.clicked.connect(self.restartRP)


        self.plot_etalondata = self.pw_etalondata.plot()
        self.plot_rbdata = self.pw_rbdata.plot()
        self.plot_rawtimeseriesPlot = self.pw_rawtimeseries.addPlot()
        #self.plot_rawtimeseriesPlotItem2 = self.pw_rawtimeseries.addPlot()
        self.plot_rawtimeseries1=self.plot_rawtimeseriesPlot.plot(pen=(0,0,200))
        self.plot_rawtimeseries2=self.plot_rawtimeseriesPlot.plot(pen=(0,128,0))
#        self.plot_rawtimeseries1=setPen

        self.plot_velocitytimeseries = self.pw_velocitytimeseries.plot()

        self.plot_etalondata.setDownsampling(method='peak',auto=True)
        self.plot_rbdata.setDownsampling(method='peak',auto=True)
        self.plot_rawtimeseries1.setDownsampling(method='peak', auto=True)
        self.plot_rawtimeseries2.setDownsampling(method='peak', auto=True)

    def closeEvent(self, event):
        self.UdpRecevierThread.terminate()
        reply = QtWidgets.QMessageBox.question(self, 'Message',
        "Are you sure to quit?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.UdpRecevierThread.start()
            try:
                self.ur.sendEndResponse()
                #print("closing ssh\n")
                self.exec.close()
                subprocess.run(["ssh", "root@10.66.101.121", "killall UDPStreamer"])
                #print("done\n")
            finally:
                event.accept()
        else:
            event.ignore()

    def startUdpRecevierThread(self):
        self.UdpRecevierThread = QtCore.QThread()
        self.UdpRecevierThread.setTerminationEnabled(True)
        self.worker = getDataRecevierWorker(self.ur)

        self.worker.moveToThread(self.UdpRecevierThread)
        self.UdpRecevierThread.started.connect(self.worker.dataRecvLoop)
        self.stopbutton.clicked.connect(self.worker.stopLoop)

        self.worker.finished.connect(self.UdpRecevierThread.quit)
        self.worker.dataReady.connect(self.plotdata)
        self.worker.dataReady.connect(self.fitdata)
        self.worker.errorOccured.connect(self.restartRP)

        self.UdpRecevierThread.start()

        self.startbutton.setEnabled(False)
        self.stopbutton.setEnabled(True)

    def stopUdpRecevierThread(self):
        #QtWidgets.QApplication.processEvents()
        if (self.UdpRecevierThread.isRunning()):
            self.UdpRecevierThread.terminate()
            #while not self.UdpRecevierThread.isFinished():
            #    time.sleep(0.1)

        #self.UdpRecevierThread.terminate()
        self.startbutton.setEnabled(True)
        self.stopbutton.setEnabled(False)

    @pyqtSlot(np.ndarray,np.ndarray,float,float,float)
    def plotdata(self,dataA,dataB,trigtime,temp,looptime):
        #print(trigtime,temp,1/looptime)

        #t = time.time()
        self.plot_etalondata.setData(y=dataA, x=x)
        self.plot_rbdata.setData(y=dataB, x=x)

    @pyqtSlot(np.ndarray,np.ndarray,float,float,float)
    def fitdata(self,dataA,dataB,trigtime,temp,looptime):
        # t = time.time()
        self.trigtimes.append(trigtime)
        self.temps.append(temp)
        self.looptimes.append(looptime)

        self.lcdNumber_dateRate.display(1/np.mean(self.looptimes))
        self.lcdNumber_triggerCount.display(len(self.looptimes))

        start = np.argmin(dataB[0:130000]) - 19000-2000
        #start = np.argmin(dataB[0:130000]) - 8000
        finish = start + 20000
        newRBcentre = fr.fitRblines(x[start:finish:1], dataB[start:finish:1] * -1, start, finish)
        self.rbcentres.append(newRBcentre)

        centrestart = dataA.argmax()
        # print(centrestart)
        etaloncentre = fr.fitEtalon(x[centrestart - 30000:centrestart + 50000:20],
                                 dataA[centrestart - 30000:centrestart + 50000:20], centrestart)
        self.etaloncentres.append(etaloncentre)

        plotime=np.asarray(self.trigtimes)
        plotime-=plotime[0]
        #error=np.mean(self.rbcentres)-self.etaloncentres
        rbplotdata=np.mean(self.rbcentres - self.rbcentres[0],axis=1)
        etalonplotdata=self.etaloncentres - self.etaloncentres[0]
        error=rbplotdata-etalonplotdata
        if len(self.rbcentres)>1:
            self.plot_rawtimeseries1.setData(y=rbplotdata, x=plotime/1000)
            self.plot_rawtimeseries2.setData(y=etalonplotdata, x=plotime / 1000)
            self.plot_velocitytimeseries.setData(y=error, x=plotime / 1000)
        if len(self.rbcentres) > 15:
            self.lcdNumber_rbStd.display(sigma_clip(rbplotdata,sigma=4).std())
            self.lcdNumber_etalonStd.display(sigma_clip(etalonplotdata,sigma=4).std())
        #print(1/(time.time() - t))

    def saveTimeSeries(self):
        scipy.io.savemat('data.mat',
                         mdict={'rbdata': self.rbcentres,
                                'etalondata': self.etaloncentres,
                                'trigtimes' : self.trigtimes,
                                'temps' : self.temps,
                                'looptimes' : self.looptimes
                                })

    @pyqtSlot()
    def restartRP(self):

        self.stopUdpRecevierThread()

        del(self.ur)
        #self.ur=[]
        self.ur = updreceiver.updreceiver(12345, 12346, 12347, aquisitionsize, "10.66.101.121")
        if sys.platform == 'win32':
            sshcmd = "C:\Program Files (x86)\PuTTY\plink.exe -pw notroot -ssh"
        else:
            sshcmd = "ssh"

        subprocess.run(["ssh", "root@10.66.101.121", "killall UDPStreamer"])
        self.exec = remoteexecutor([sshcmd, "-t", "-t", "root@10.66.101.121", "~/RpRbDAQ/UDPStreamer"])

        self.startUdpRecevierThread()

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RbMoniterProgram()
    win.show()
    win.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
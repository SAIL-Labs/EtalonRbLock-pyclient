# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RbMoniter.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RbMoniter(object):
    def setupUi(self, RbMoniter):
        RbMoniter.setObjectName("RbMoniter")
        RbMoniter.resize(1619, 992)
        self.centralwidget = QtWidgets.QWidget(RbMoniter)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(1280, 16777215))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_fullMoniter = QtWidgets.QWidget()
        self.tab_fullMoniter.setObjectName("tab_fullMoniter")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_fullMoniter)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pw_rawtimeseries = GraphicsLayoutWidget(self.tab_fullMoniter)
        self.pw_rawtimeseries.setObjectName("pw_rawtimeseries")
        self.gridLayout.addWidget(self.pw_rawtimeseries, 1, 0, 1, 2)
        self.pw_velocitytimeseries = PlotWidget(self.tab_fullMoniter)
        self.pw_velocitytimeseries.setObjectName("pw_velocitytimeseries")
        self.gridLayout.addWidget(self.pw_velocitytimeseries, 2, 0, 1, 2)
        self.pw_etalondata = PlotWidget(self.tab_fullMoniter)
        self.pw_etalondata.setObjectName("pw_etalondata")
        self.gridLayout.addWidget(self.pw_etalondata, 0, 0, 1, 1)
        self.pw_rbdata = PlotWidget(self.tab_fullMoniter)
        self.pw_rbdata.setObjectName("pw_rbdata")
        self.gridLayout.addWidget(self.pw_rbdata, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab_fullMoniter, "")
        self.tab_diagnostic = QtWidgets.QWidget()
        self.tab_diagnostic.setObjectName("tab_diagnostic")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_diagnostic)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.EtalonPlot = PlotWidget(self.tab_diagnostic)
        self.EtalonPlot.setObjectName("EtalonPlot")
        self.gridLayout_2.addWidget(self.EtalonPlot, 0, 0, 1, 1)
        self.RbPlot = QtWidgets.QGraphicsView(self.tab_diagnostic)
        self.RbPlot.setObjectName("RbPlot")
        self.gridLayout_2.addWidget(self.RbPlot, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_diagnostic, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.tabWidget1 = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget1.setMinimumSize(QtCore.QSize(0, 250))
        self.tabWidget1.setMaximumSize(QtCore.QSize(320, 16777215))
        font = QtGui.QFont()
        font.setKerning(True)
        self.tabWidget1.setFont(font)
        self.tabWidget1.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget1.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget1.setElideMode(QtCore.Qt.ElideRight)
        self.tabWidget1.setTabBarAutoHide(False)
        self.tabWidget1.setObjectName("tabWidget1")
        self.tabWidgetPage1 = QtWidgets.QWidget()
        self.tabWidgetPage1.setObjectName("tabWidgetPage1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tabWidgetPage1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.tabWidgetPage1)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.startbutton = QtWidgets.QPushButton(self.groupBox)
        self.startbutton.setDefault(False)
        self.startbutton.setFlat(False)
        self.startbutton.setObjectName("startbutton")
        self.gridLayout_3.addWidget(self.startbutton, 0, 0, 1, 1)
        self.stopbutton = QtWidgets.QPushButton(self.groupBox)
        self.stopbutton.setEnabled(False)
        self.stopbutton.setObjectName("stopbutton")
        self.gridLayout_3.addWidget(self.stopbutton, 0, 1, 1, 1)
        self.pushButton_savedata = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_savedata.setObjectName("pushButton_savedata")
        self.gridLayout_3.addWidget(self.pushButton_savedata, 1, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupBox, 0, QtCore.Qt.AlignTop)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tabWidgetPage1)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lcdNumber_dateRate = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_dateRate.setMaximumSize(QtCore.QSize(16777215, 16777212))
        self.lcdNumber_dateRate.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_dateRate.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lcdNumber_dateRate.setSmallDecimalPoint(False)
        self.lcdNumber_dateRate.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_dateRate.setObjectName("lcdNumber_dateRate")
        self.gridLayout_4.addWidget(self.lcdNumber_dateRate, 0, 1, 1, 1)
        self.lcdNumber_rbStd = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_rbStd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_rbStd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_rbStd.setProperty("value", 0.0)
        self.lcdNumber_rbStd.setObjectName("lcdNumber_rbStd")
        self.gridLayout_4.addWidget(self.lcdNumber_rbStd, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAutoFillBackground(False)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setAutoFillBackground(False)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAutoFillBackground(False)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 0, 2, 1, 1)
        self.lcdNumber_triggerCount = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_triggerCount.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_triggerCount.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_triggerCount.setProperty("value", 0.0)
        self.lcdNumber_triggerCount.setObjectName("lcdNumber_triggerCount")
        self.gridLayout_4.addWidget(self.lcdNumber_triggerCount, 0, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 2, 2, 1, 1)
        self.lcdNumber_etalonStd = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_etalonStd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_etalonStd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_etalonStd.setObjectName("lcdNumber_etalonStd")
        self.gridLayout_4.addWidget(self.lcdNumber_etalonStd, 2, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.tabWidget1.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QtWidgets.QWidget()
        self.tabWidgetPage2.setObjectName("tabWidgetPage2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tabWidgetPage2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabWidgetPage2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_resetUDP = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_resetUDP.setObjectName("pushButton_resetUDP")
        self.gridLayout_5.addWidget(self.pushButton_resetUDP, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.tabWidget1.addTab(self.tabWidgetPage2, "")
        self.horizontalLayout.addWidget(self.tabWidget1, 0, QtCore.Qt.AlignTop)
        RbMoniter.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(RbMoniter)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1619, 22))
        self.menubar.setObjectName("menubar")
        RbMoniter.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(RbMoniter)
        self.statusbar.setObjectName("statusbar")
        RbMoniter.setStatusBar(self.statusbar)
        self.actionAbout = QtWidgets.QAction(RbMoniter)
        self.actionAbout.setObjectName("actionAbout")

        self.retranslateUi(RbMoniter)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget1.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(RbMoniter)

    def retranslateUi(self, RbMoniter):
        _translate = QtCore.QCoreApplication.translate
        RbMoniter.setWindowTitle(_translate("RbMoniter", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_fullMoniter), _translate("RbMoniter", "Full Moniter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_diagnostic), _translate("RbMoniter", "Diagnostic"))
        self.groupBox.setTitle(_translate("RbMoniter", "Data Aquisition"))
        self.startbutton.setText(_translate("RbMoniter", "Start"))
        self.stopbutton.setText(_translate("RbMoniter", "Stop"))
        self.pushButton_savedata.setText(_translate("RbMoniter", "Save Date"))
        self.groupBox_2.setTitle(_translate("RbMoniter", "Measurements"))
        self.label.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Data Rate</p></body></html>"))
        self.label_3.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Std Rb</p></body></html>"))
        self.label_2.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Trigger Cnt</p></body></html>"))
        self.label_4.setText(_translate("RbMoniter", "Std Etalon"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage1), _translate("RbMoniter", "Live"))
        self.groupBox_3.setTitle(_translate("RbMoniter", "GroupBox"))
        self.pushButton_resetUDP.setText(_translate("RbMoniter", "Reset UdpReciever"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage2), _translate("RbMoniter", "Settings"))
        self.actionAbout.setText(_translate("RbMoniter", "About"))

from pyqtgraph import GraphicsLayoutWidget, PlotWidget

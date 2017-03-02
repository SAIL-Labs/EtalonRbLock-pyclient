# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/chrisbetters/Dropbox/github/postdoc_code/PhotonicComb/EtalonRbLock-pyclient/RbMoniter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RbMoniter(object):
    def setupUi(self, RbMoniter):
        RbMoniter.setObjectName("RbMoniter")
        RbMoniter.resize(1293, 1058)
        self.centralwidget = QtWidgets.QWidget(RbMoniter)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_fullMoniter = QtWidgets.QWidget()
        self.tab_fullMoniter.setObjectName("tab_fullMoniter")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_fullMoniter)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pw_temp = PlotWidget(self.tab_fullMoniter)
        self.pw_temp.setObjectName("pw_temp")
        self.gridLayout.addWidget(self.pw_temp, 3, 0, 1, 2)
        self.pw_velocitytimeseries = PlotWidget(self.tab_fullMoniter)
        self.pw_velocitytimeseries.setObjectName("pw_velocitytimeseries")
        self.gridLayout.addWidget(self.pw_velocitytimeseries, 2, 0, 1, 2)
        self.pw_etalondata = PlotWidget(self.tab_fullMoniter)
        self.pw_etalondata.setObjectName("pw_etalondata")
        self.gridLayout.addWidget(self.pw_etalondata, 0, 0, 1, 1)
        self.glw_rawtimeseries = GraphicsLayoutWidget(self.tab_fullMoniter)
        self.glw_rawtimeseries.setObjectName("glw_rawtimeseries")
        self.gridLayout.addWidget(self.glw_rawtimeseries, 1, 0, 1, 2)
        self.pw_rbdata = PlotWidget(self.tab_fullMoniter)
        self.pw_rbdata.setObjectName("pw_rbdata")
        self.gridLayout.addWidget(self.pw_rbdata, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab_fullMoniter, "")
        self.tab_diagnostic = QtWidgets.QWidget()
        self.tab_diagnostic.setObjectName("tab_diagnostic")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_diagnostic)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pw_DiagnosticEtalonPlot = PlotWidget(self.tab_diagnostic)
        self.pw_DiagnosticEtalonPlot.setObjectName("pw_DiagnosticEtalonPlot")
        self.gridLayout_2.addWidget(self.pw_DiagnosticEtalonPlot, 0, 0, 1, 1)
        self.pw_DiagnosticRbPlot = PlotWidget(self.tab_diagnostic)
        self.pw_DiagnosticRbPlot.setObjectName("pw_DiagnosticRbPlot")
        self.gridLayout_2.addWidget(self.pw_DiagnosticRbPlot, 1, 0, 1, 1)
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
        self.doubleSpinBox_etalonbinsize = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_etalonbinsize.setReadOnly(False)
        self.doubleSpinBox_etalonbinsize.setPrefix("")
        self.doubleSpinBox_etalonbinsize.setMinimum(0.1)
        self.doubleSpinBox_etalonbinsize.setMaximum(1000.0)
        self.doubleSpinBox_etalonbinsize.setProperty("value", 1.0)
        self.doubleSpinBox_etalonbinsize.setObjectName("doubleSpinBox_etalonbinsize")
        self.gridLayout_3.addWidget(self.doubleSpinBox_etalonbinsize, 6, 1, 1, 1)
        self.stopbutton = QtWidgets.QPushButton(self.groupBox)
        self.stopbutton.setEnabled(False)
        self.stopbutton.setObjectName("stopbutton")
        self.gridLayout_3.addWidget(self.stopbutton, 0, 1, 1, 1)
        self.startbutton = QtWidgets.QPushButton(self.groupBox)
        self.startbutton.setDefault(False)
        self.startbutton.setFlat(False)
        self.startbutton.setObjectName("startbutton")
        self.gridLayout_3.addWidget(self.startbutton, 0, 0, 1, 1)
        self.checkBox_fitting = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_fitting.setEnabled(True)
        self.checkBox_fitting.setChecked(False)
        self.checkBox_fitting.setObjectName("checkBox_fitting")
        self.gridLayout_3.addWidget(self.checkBox_fitting, 3, 1, 1, 1)
        self.spinBox_smoothingWindow = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_smoothingWindow.setSuffix("")
        self.spinBox_smoothingWindow.setMinimum(5)
        self.spinBox_smoothingWindow.setMaximum(2001)
        self.spinBox_smoothingWindow.setSingleStep(2)
        self.spinBox_smoothingWindow.setProperty("value", 51)
        self.spinBox_smoothingWindow.setObjectName("spinBox_smoothingWindow")
        self.gridLayout_3.addWidget(self.spinBox_smoothingWindow, 5, 1, 1, 1)
        self.checkBox_etalonsmoothing = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_etalonsmoothing.setObjectName("checkBox_etalonsmoothing")
        self.gridLayout_3.addWidget(self.checkBox_etalonsmoothing, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 5, 0, 1, 1)
        self.pushButton_clearData = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_clearData.setObjectName("pushButton_clearData")
        self.gridLayout_3.addWidget(self.pushButton_clearData, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 6, 0, 1, 1)
        self.pushButton_savedata = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_savedata.setObjectName("pushButton_savedata")
        self.gridLayout_3.addWidget(self.pushButton_savedata, 1, 0, 1, 1)
        self.spinBox_updaterate = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_updaterate.setMinimum(5)
        self.spinBox_updaterate.setObjectName("spinBox_updaterate")
        self.gridLayout_3.addWidget(self.spinBox_updaterate, 7, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 7, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 8, 0, 1, 1)
        self.doubleSpinBox_tempsetpoint = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_tempsetpoint.setDecimals(4)
        self.doubleSpinBox_tempsetpoint.setMinimum(-99.0)
        self.doubleSpinBox_tempsetpoint.setMaximum(99.0)
        self.doubleSpinBox_tempsetpoint.setSingleStep(0.0001)
        self.doubleSpinBox_tempsetpoint.setProperty("value", 0.0)
        self.doubleSpinBox_tempsetpoint.setObjectName("doubleSpinBox_tempsetpoint")
        self.gridLayout_3.addWidget(self.doubleSpinBox_tempsetpoint, 8, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox)
        self.label_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 9, 0, 1, 1)
        self.spinBox_plotwindowsize = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_plotwindowsize.setMinimum(500)
        self.spinBox_plotwindowsize.setMaximum(20000)
        self.spinBox_plotwindowsize.setSingleStep(500)
        self.spinBox_plotwindowsize.setProperty("value", 2000)
        self.spinBox_plotwindowsize.setObjectName("spinBox_plotwindowsize")
        self.gridLayout_3.addWidget(self.spinBox_plotwindowsize, 9, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
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
        self.lcdNumber_etalonStd = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_etalonStd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_etalonStd.setSmallDecimalPoint(False)
        self.lcdNumber_etalonStd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_etalonStd.setObjectName("lcdNumber_etalonStd")
        self.gridLayout_4.addWidget(self.lcdNumber_etalonStd, 2, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 2, 2, 1, 1)
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
        self.lcdNumber_rbStd = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_rbStd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_rbStd.setSmallDecimalPoint(False)
        self.lcdNumber_rbStd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_rbStd.setProperty("value", 0.0)
        self.lcdNumber_rbStd.setObjectName("lcdNumber_rbStd")
        self.gridLayout_4.addWidget(self.lcdNumber_rbStd, 2, 1, 1, 1)
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
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 4, 1, 1)
        self.lcdNumber_triggerCount = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_triggerCount.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_triggerCount.setSmallDecimalPoint(False)
        self.lcdNumber_triggerCount.setDigitCount(6)
        self.lcdNumber_triggerCount.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_triggerCount.setProperty("value", 0.0)
        self.lcdNumber_triggerCount.setObjectName("lcdNumber_triggerCount")
        self.gridLayout_4.addWidget(self.lcdNumber_triggerCount, 0, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.lcdNumber_fitrate = QtWidgets.QLCDNumber(self.groupBox_2)
        self.lcdNumber_fitrate.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcdNumber_fitrate.setFrameShadow(QtWidgets.QFrame.Raised)
        self.lcdNumber_fitrate.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_fitrate.setObjectName("lcdNumber_fitrate")
        self.gridLayout_4.addWidget(self.lcdNumber_fitrate, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tabWidgetPage1)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_12 = QtWidgets.QLabel(self.groupBox_4)
        self.label_12.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_6.addWidget(self.label_12, 3, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_6.addWidget(self.label_11, 2, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_6.addWidget(self.label_10, 1, 0, 1, 1)
        self.doubleSpinBox_P = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_P.setDecimals(8)
        self.doubleSpinBox_P.setMinimum(-1.0)
        self.doubleSpinBox_P.setMaximum(1.0)
        self.doubleSpinBox_P.setSingleStep(1e-06)
        self.doubleSpinBox_P.setProperty("value", -0.01)
        self.doubleSpinBox_P.setObjectName("doubleSpinBox_P")
        self.gridLayout_6.addWidget(self.doubleSpinBox_P, 1, 1, 1, 1)
        self.doubleSpinBox_D = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_D.setDecimals(8)
        self.doubleSpinBox_D.setMinimum(-99.0)
        self.doubleSpinBox_D.setObjectName("doubleSpinBox_D")
        self.gridLayout_6.addWidget(self.doubleSpinBox_D, 3, 1, 1, 1)
        self.doubleSpinBox_I = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_I.setDecimals(8)
        self.doubleSpinBox_I.setMinimum(-99.0)
        self.doubleSpinBox_I.setObjectName("doubleSpinBox_I")
        self.gridLayout_6.addWidget(self.doubleSpinBox_I, 2, 1, 1, 1)
        self.checkBox_PIDonoff = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_PIDonoff.setObjectName("checkBox_PIDonoff")
        self.gridLayout_6.addWidget(self.checkBox_PIDonoff, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.tabWidget1.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QtWidgets.QWidget()
        self.tabWidgetPage2.setObjectName("tabWidgetPage2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tabWidgetPage2)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabWidgetPage2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.lineEdit_localIP = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_localIP.setReadOnly(True)
        self.lineEdit_localIP.setObjectName("lineEdit_localIP")
        self.gridLayout_7.addWidget(self.lineEdit_localIP, 0, 1, 1, 1)
        self.lineEdit_rpIP = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_rpIP.setReadOnly(True)
        self.lineEdit_rpIP.setObjectName("lineEdit_rpIP")
        self.gridLayout_7.addWidget(self.lineEdit_rpIP, 1, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setObjectName("label_13")
        self.gridLayout_7.addWidget(self.label_13, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setObjectName("label_14")
        self.gridLayout_7.addWidget(self.label_14, 1, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_3, 0, 1, 1, 1, QtCore.Qt.AlignTop)
        self.tabWidget1.addTab(self.tabWidgetPage2, "")
        self.horizontalLayout.addWidget(self.tabWidget1, 0, QtCore.Qt.AlignTop)
        RbMoniter.setCentralWidget(self.centralwidget)
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
        RbMoniter.setWindowTitle(_translate("RbMoniter", "SAIL Photonic Comb Rb Lock/Moniter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_fullMoniter), _translate("RbMoniter", "Full Moniter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_diagnostic), _translate("RbMoniter", "Diagnostic"))
        self.groupBox.setTitle(_translate("RbMoniter", "Data Aquisition"))
        self.doubleSpinBox_etalonbinsize.setSuffix(_translate("RbMoniter", " sec"))
        self.stopbutton.setText(_translate("RbMoniter", "Stop"))
        self.startbutton.setText(_translate("RbMoniter", "Start"))
        self.checkBox_fitting.setText(_translate("RbMoniter", "Fitting Enabled"))
        self.checkBox_etalonsmoothing.setText(_translate("RbMoniter", "Smooth Etalon"))
        self.label_5.setText(_translate("RbMoniter", "Rb Smooth Window"))
        self.pushButton_clearData.setText(_translate("RbMoniter", "Clear Data"))
        self.label_6.setText(_translate("RbMoniter", "Etalon Bin Size"))
        self.pushButton_savedata.setText(_translate("RbMoniter", "Save Date"))
        self.label_7.setText(_translate("RbMoniter", "Update Rate (sam)"))
        self.label_9.setText(_translate("RbMoniter", "Temp Set Point"))
        self.doubleSpinBox_tempsetpoint.setSuffix(_translate("RbMoniter", "°C"))
        self.label_15.setText(_translate("RbMoniter", "Plot Window Size"))
        self.groupBox_2.setTitle(_translate("RbMoniter", "Measurements"))
        self.label.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Data Rate</p></body></html>"))
        self.label_4.setText(_translate("RbMoniter", "Std Etalon"))
        self.label_2.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Trigger Cnt</p></body></html>"))
        self.label_3.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Std Rb</p></body></html>"))
        self.label_8.setText(_translate("RbMoniter", "<html><head/><body><p align=\"right\">Fit rate</p></body></html>"))
        self.groupBox_4.setTitle(_translate("RbMoniter", "PID"))
        self.label_12.setText(_translate("RbMoniter", "D"))
        self.label_11.setText(_translate("RbMoniter", "I"))
        self.label_10.setText(_translate("RbMoniter", "P"))
        self.checkBox_PIDonoff.setText(_translate("RbMoniter", "Enabled"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage1), _translate("RbMoniter", "Live"))
        self.groupBox_3.setTitle(_translate("RbMoniter", "Receiver Settings"))
        self.label_13.setText(_translate("RbMoniter", "Local IP"))
        self.label_14.setText(_translate("RbMoniter", "RP IP"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage2), _translate("RbMoniter", "Settings"))
        self.actionAbout.setText(_translate("RbMoniter", "About"))

from pyqtgraph import GraphicsLayoutWidget, PlotWidget

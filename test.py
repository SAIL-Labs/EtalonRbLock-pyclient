# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with 
the left/right mouse buttons. Right click on any plot to show a context menu.
"""

#import initExample ## Add path to library (just for examples; you do not need this)


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys
import time
sys.path.append('..')
import updreceiver
sys.path.remove('..')

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
#QtGui.QApplication.setGraphicsSystem('raster')
# app = QtGui.QApplication([])

ur=updreceiver.updreceiver(12345,12346,12347,360000,"10.66.101.121")
ur.sendAckResponse(10.0)
ur.receiveDACData()
x = np.arange(360000)

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title="Multiple curves")
p2 = win.addPlot(title="Multiple curves")
while 1:
    t = time.time()
    ur.sendAckResponse(10.0)
    ur.receiveDACData()
    ur.recieveTrigerTimeAndTemp()

    elapsed = time.time() - t
    # p1.plot(x,ur.dataA,clear=True)
    # p2.plot(x,ur.dataB,clear=True)
    pg.QtGui.QApplication.processEvents()
    print(ur.temp)
    print(1/elapsed)

## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()

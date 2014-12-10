#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Matplotlib Qt widget
"""

import os, sys
import numpy as np


### SLOTH ###
from __init__ import _libDir
sys.path.append(_libDir)
from genericutils import ipythonAutoreload

# Set the QT API to PyQt4
HAS_PYSIDE = False
if "PySide" in sys.modules:
    HAS_PYSIDE = True
if HAS_PYSIDE:
    os.environ['QT_API'] = 'pyside'
    from PySide import QtGui as qt
else:
    os.environ['QT_API'] = 'pyqt'
    # force API 2
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
    from PyQt4 import QtGui as qt

#Import Matplotlib stuff
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class MplCanvas(FigureCanvas):
    """ mpl canvas """
    def __init__(self, parent=None, figW=5, figH=4, figDpi=100):
        fig = plt.figure(figsize=(figW, figH), dpi=figDpi)
        self.axes = fig.add_subplot(111)
        # clear axes at every plot()
        self.axes.hold(False)
        super(MplCanvas, self).__init__(fig)
        #self.setParent(parent)
    
class MplWidget(qt.QWidget):
    """ mpl widget = canvas plus layout """
    def __init__(self, parent=None, **kws):
        super(MplWidget, self).__init__(parent)

        mpl = MplCanvas(parent, **kws)
        
        # layout
        layout = qt.QVBoxLayout(self)
        layout.addWidget(mpl)
    
if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    mpl = MplWidget()
    mpl.show()
    sys.exit(app.exec_())

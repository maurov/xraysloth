#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Qt graphical user interface for sloth
============================================

..notes

Load designer.ui into python

To directly show in Ipython, simply:

main = uic.loadUi('designer.ui')
main.show()

"""
import os, sys

# force API 2
import sip
try:
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QtextStream', 2)
    sip.setapi('Qtime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)
except:
    raise RuntimeError('Could not set API version (%s): did you import PyQt4 directly?' % e)

try:
    from PyQt5 import QtGui, uic
except:
    from PyQt4 import QtGui, uic

# PyMca
HAS_PYMCA = False
try:
    from PyMca5.PyMcaGui import ScanWindow
    HAS_PYMCA = True
except ImportError:
    try:
        from PyMca import ScanWindow
        HAS_PYMCA = True
    except ImportError:
        pass

### SLOTH ###
from __init__ import _libDir
sys.path.append(_libDir)

uifile = os.path.join(_libDir, "sloth_gui.ui")
UiClass, BaseClass = uic.loadUiType(uifile)

from qt_widget_mpl import MplCanvas, MplWidget
from qt_widget_ipy import IPyConsoleWidget

class SlothMain(BaseClass, UiClass):

    def __init__(self, parent=None):
        super(SlothMain, self).__init__(parent)
        self.setupUi(self)
        self.actionExit.triggered.connect(self.close)

        ipy_cons = IPyConsoleWidget()
        layout_ipy = QtGui.QVBoxLayout(self.ipy_widget)
        layout_ipy.addWidget(ipy_cons)
        #layout_mpl = QtGui.QVBoxLayout(self.plt_widget)
        #layout_mpl.addWidget(MplWidget())

        # if HAS_PYMCA:
        #     scan_win = ScanWindow.ScanWindow()
        #     scan_win.setDefaultPlotLines(True)
        #     scan_win.setUpdatesEnabled(True)
        #     scan_win.setActiveCurveColor(color='red')
        #     layout_sw = QtGui.QVBoxLayout(self.plt_widget)
        #     layout_sw.addWidget(scan_win)
        #     # push it to the console
        #     ipy_cons.ipy.push_variables({'pw':scan_win})

        self._fname = None
        
    def on_actionOpen_triggered(self):
        fname = QtGui.QFileDialog.getOpenFileName()
        if fname:
            self._fname = unicode(fname) # will not work on python3!
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    appli = SlothMain()
    appli.show()
    sys.exit(app.exec_())

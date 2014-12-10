"""
Load designer.ui into python

To directly show in Ipython, simply:

main = uic.loadUi('designer.ui')
main.show()

"""

import os, sys

# force API 2
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt4 import QtGui as qt

from PyQt4 import uic

#Import Matplotlib stuff
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from qt_widget_mpl import MplCanvas, MplWidget
from qt_widget_ipy import IPyConsoleWidget

### SLOTH ###
from __init__ import _libDir
sys.path.append(_libDir)

uifile = os.path.join(_libDir, "sloth.ui")
UiClass, BaseClass = uic.loadUiType(uifile)

class SlothMain(BaseClass, UiClass):

    def __init__(self, parent=None):
        super(SlothMain, self).__init__(parent)
        self.setupUi(self)
        self.actionExit.triggered.connect(self.close)

        layout_ipy = qt.QVBoxLayout(self.ipy_widget)
        layout_ipy.addWidget(IPyConsoleWidget())
        #layout_mpl = qt.QVBoxLayout(self.mpl_widget)
        #layout_mpl.addWidget(MplWidget())

        self._fname = None
        
    def on_actionOpen_triggered(self):
        fname = qt.QFileDialog.getOpenFileName()
        if fname:
            self._fname = unicode(fname) # will not work on python3!
        
if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    appli = SlothMain()
    appli.show()
    sys.exit(app.exec_())

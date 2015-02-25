"""
Simple Qt graphical user interface for sloth
============================================

..notes

Load designer.ui into python

To directly show in Ipython, simply:

main = uic.loadUi('designer.ui')
main.show()

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__owner__ = "Mauro Rovezzi"
__year__ = "2014-2015"

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

from PyQt4 import QtGui, uic

### SLOTH ###
from __init__ import _libDir, __version__
sys.path.append(_libDir)

uifile = os.path.join(_libDir, "sloth.ui")
UiClass, BaseClass = uic.loadUiType(uifile)

from qt_widget_mpl import MplCanvas, MplWidget
from qt_widget_ipy import IPyConsoleWidget

class SlothMain(BaseClass, UiClass):

    def __init__(self, parent=None):
        super(SlothMain, self).__init__(parent)
        self.setupUi(self)
        self.actionExit.triggered.connect(self.close)

        layout_ipy = QtGui.QVBoxLayout(self.ipy_widget)
        layout_ipy.addWidget(IPyConsoleWidget())
        #layout_mpl = QtGui.QVBoxLayout(self.mpl_widget)
        #layout_mpl.addWidget(MplWidget())

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

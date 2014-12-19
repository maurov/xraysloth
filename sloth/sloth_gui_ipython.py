#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple IPython graphical user interface for sloth

The starting code is taken from PyMca5/PyMcaGui/misc/QIPythonWidget.py
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = "V. Armando Solé (PyMca)"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__owner__ = "Mauro Rovezzi"
__year__ = "2014"
__version__ = "0.0.1"
__status__ = "in progress"
__date__ = "Dec 2014"

# GLOBAL VARIABLES
SLOTH_IPY_WELCOME = "Welcome to Sloth IPython console, version {0}\n".format(__version__)

import os, sys
import numpy as np
import math

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
    from PySide import QtGui
else:
    os.environ['QT_API'] = 'pyqt'
    # force API 2
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
    from PyQt4 import QtGui

# another option is to load Qt via PyMca (seems slower)
# HAS_PYMCA = False
# try:
#     from PyMca5.PyMca import PyMcaQt as Qt
#     HAS_PYMCA = True
# except ImportError:
#     try:
#         from PyMca import PyMcaQt as Qt
#         HAS_PYMCA = True
#     except ImportError:
#         print(sys.exc_info()[1])
#         pass

# Import the console machinery from ipython
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

#Import Matplotlib stuff
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure 


class QIPythonWidget(RichIPythonWidget):
    """convenience class for a live IPython console widget.

    Parameters
    ----------
    customBanner : string, None
                   to replace the standard banner show at beginning of
                   IPython console

    """
    def __init__(self, customBanner=None, *args, **kwargs):
        if customBanner != None:
            self.banner = customBanner
        super(QIPythonWidget, self).__init__(*args, **kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()
        guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self, variableDict):
        """push a dictionary of variables to the IPthon console

        Parameters
        ----------
        variableDict : dict
                       name / value pairs
        """
        self.kernel_manager.kernel.shell.push(variableDict)
        
    def clearTerminal(self):
        """clear the terminal """
        self._control.clear()

    def printText(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)
        
    def exeCmd(self, command):
        """ Execute a command in the frame of the console widget """
        self._execute(command, False)

class IPyConsoleWidget(QtGui.QWidget):
    """IPython console widget

    NOTE: this layer is not required, unless one wants to make a
    layout on top of QIPythonWidget

    """
    def __init__(self, parent=None):
        super(IPyConsoleWidget, self).__init__(parent)

        ipy = QIPythonWidget(customBanner=SLOTH_IPY_WELCOME)
        
        #self.btnClose = QtGui.QPushButton('Exit')
        #self.btnClose.clicked.connect(self.close)
        
        # layout
        layout = QtGui.QVBoxLayout(self)
        #layout.addWidget(self.btnClose)
        layout.addWidget(ipy)
        
        # This allows the variable foo and method print_process_id to be accessed from the ipython console
        #ipyConsole.pushVariables({"foo":43,"print_process_id":print_process_id})
        #ipyConsole.printText("The variable 'foo' and the method 'print_process_id()' are available. Use the 'whos' command for information.")

def print_process_id():
    print('Process ID is:', os.getpid())

class MplCanvas(FigureCanvas):
    """ mpl canvas """
    def __init__(self, parent=None, figW=5, figH=4, figDpi=100):
        fig = Figure(figsize=(figW, figH), dpi=figDpi)
        self.axes = fig.add_subplot(111)
        # clear axes at every plot()
        self.axes.hold(False)
        super(MplWidget, self).__init__(self, fig)
        self.setParent(parent)
    
    
class MplWidget(QtGui.QWidget):
    def __init__(self, parent=None, **kws):
        super(MplWidget, self).__init__(parent)

        mpl = MplCanvas(parent)
        
        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(mpl)
    
class SlothMainWindow(QtGui.QMainWindow):
    """ main window """
    
    def __init__(self, parent=None):
        super(SlothMainWindow, self).__init__(parent)

        #Menu bar
        # quit_act = QtGui.QAction('Exit', self)
        # quit_act.triggered.connect(self.close)
        # menu = self.menuBar().addMenu('File')
        # menu.addAction(quit_act)

        #Toolbar
        tbar = QtGui.QToolBar('Toolbar')
        self.addToolBar(tbar)
        tbar.addAction('Exit')
        tbar.actionTriggered.connect(self.close)

        #Dock bar (not working yet!)
        #dock = QtGui.QDockWidget()
        #dock.setWidget(IPyConsoleWidget)
        #self.addDockWidget(dock)
        
        #Central Widget
        self.setCentralWidget(IPyConsoleWidget(self))
        #self.setCentralWidget(MplWidget(self))
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = SlothMainWindow()
    main.show()
    sys.exit(app.exec_())

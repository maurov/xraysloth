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

# Set the QT API to PyQt4
import os, sys

### SLOTH ###
from __init__ import _libDir
sys.path.append(_libDir)
from genericutils import ipythonAutoreload


HAS_PYSIDE = False
if "PySide" in sys.modules:
    HAS_PYSIDE = True
if HAS_PYSIDE:
    os.environ['QT_API'] = 'pyside'
    from PySide.QtGui import QWidget, QVBoxLayout, QPushButton, QApplication
else:
    os.environ['QT_API'] = 'pyqt'
    if 1:
        #is this really needed?
        #If I get rid of it IPython complains
        import sip
        sip.setapi("QString", 2)
        sip.setapi("QVariant", 2)
    from PyQt4.QtGui import QWidget, QVBoxLayout, QPushButton, QApplication

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

class SlothWidget(QWidget):
    """main GUI widget: exit button and IPython console widget
    """
    def __init__(self, parent=None):
        super(SlothWidget, self).__init__(parent)

        ipy = QIPythonWidget(customBanner=SLOTH_IPY_WELCOME)
        
        self.btnClose = QPushButton('Exit')
        self.btnClose.clicked.connect(self.close)
        
        # layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.btnClose)
        layout.addWidget(ipy)
        
        # This allows the variable foo and method print_process_id to be accessed from the ipython console
        #ipyConsole.pushVariables({"foo":43,"print_process_id":print_process_id})
        #ipyConsole.printText("The variable 'foo' and the method 'print_process_id()' are available. Use the 'whos' command for information.")

def print_process_id():
    print('Process ID is:', os.getpid())

def main():
    app  = QApplication([])
    widget = SlothWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()


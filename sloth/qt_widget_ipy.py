#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""IPython Qt widget
====================

This code is based on:

1. PyMca5/PyMcaGui/misc/QIPythonWidget.py (taken from
http://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application)
2. https://github.com/sir-wiggles/PyInterp
3. https://github.com/klusta-team/klustaviewa/blob/master/klustaviewa/views/ipythonview.py
4. https://github.com/gpoulin/python-test/blob/master/embedded_qtconsole.py


TODO
====

- Move to Jupyter/qtconsole!

http://jupyter.org/qtconsole/stable/#qt-and-the-qtconsole

https://github.com/ipython/ipykernel/blob/master/examples/embedding/inprocess_qtconsole.py

https://github.com/ipython/ipykernel/blob/master/examples/embedding/ipkernel_qtapp.py

none working like this one!!!

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__owner__ = "Mauro Rovezzi"
__year__ = "2011-2015"

import os, sys
import numpy as np
import math

# control deps
HAS_QT = False
HAS_PYSIDE = False
HAS_IPYTHON = False

# Qt import PySide or PyQt4
if "PySide" in sys.modules:
    HAS_PYSIDE = True
if HAS_PYSIDE:
    os.environ['QT_API'] = 'pyside'
    from PySide import QtGui
    HAS_QT = True
else:
    os.environ['QT_API'] = 'pyqt'
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
        print(sys.exc_info()[1])
        pass
    from PyQt4 import QtGui
    HAS_QT = True

# IPy machinery
try:
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
    from IPython.qt.inprocess import QtInProcessKernelManager
    from IPython.lib import guisupport
    HAS_IPYTHON = True
except:
    print(sys.exc_info()[1])
    pass

### SLOTH ###
from __init__ import _libDir, __version__
sys.path.append(_libDir)

SLOTH_IPY_WELCOME = "Welcome to Sloth IPython console, version {0}\n".format(__version__)

#from genericutils import ipythonAutoreload

def _get_ipy_mods():
    """push modules to ipy"""
    _mods = {'os' : os,
             'sys' : sys,
             'np' : np,
             'math' : math}

    return _mods

def _get_ipy_mods_text():
    """show info text of loaded modules"""

    _imods = 'Imported modules in this console:\n'+\
             'os, sys : System utilities\n'+\
             'math, np : Math and Numpy\n'

    return _imods

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
        kernel_manager.kernel.gui = 'qt'
        kernel_manager.kernel.pylab_import_all = False
        
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()
        guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def push_variables(self, varsDict):
        """push a dictionary of variables to the IPthon console

        Parameters
        ----------
        varsDict : dict
                   name / value pairs
        """
        self.kernel_manager.kernel.shell.push(varsDict)
        
    def clear_terminal(self):
        """clear the terminal """
        self._control.clear()

    def print_text(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)
        
    def exec_cmd(self, command):
        """ Execute a command in the frame of the console widget """
        self._execute(command, False)

class IPyConsoleWidget(QtGui.QWidget):
    """IPython console widget

    NOTE: this layer is not required, unless one wants to make a
    layout on top of QIPythonWidget

    """
    def __init__(self, parent=None):
        super(IPyConsoleWidget, self).__init__(parent)
        self.ipy = ipy = QIPythonWidget(customBanner=SLOTH_IPY_WELCOME)

        ipy.push_variables(_get_ipy_mods())
        ipy.print_text('Process ID is {0}\n'.format(os.getpid()))
        ipy.print_text(_get_ipy_mods_text())
      
        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(ipy)
        
        
if __name__ == '__main__':
    if (HAS_QT and HAS_IPYTHON):
        app = QtGui.QApplication(sys.argv)
        ipy = IPyConsoleWidget()
        ipy.show()
        sys.exit(app.exec_())
    else:
        pass

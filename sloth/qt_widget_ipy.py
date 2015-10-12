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
    from PyQt4 import QtGui, Qt
    HAS_QT = True

# IPy machinery
try:
    from qtconsole.rich_jupyter_widget import RichJupyterWidget as RichIPythonWidget
    from qtconsole.inprocess import QtInProcessKernelManager
    from IPython.lib import guisupport
    from IPython.lib.kernel import connect_qtconsole
    from ipykernel.kernelapp import IPKernelApp
    HAS_IPYTHON = True
except:
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

#-----------------------------------------------------------------------------
# from: internal_ipkernel.py
# https://github.com/ipython/ipykernel/blob/master/examples/embedding/internal_ipkernel.py
#-----------------------------------------------------------------------------
def mpl_kernel(gui):
    """Launch and return an IPython kernel with matplotlib support for the desired gui
    """
    kernel = IPKernelApp.instance()
    kernel.initialize(['python', '--matplotlib=%s' % gui,
                       #'--log-level=10'
                       ])
    return kernel


class InternalIPKernel(object):

    def init_ipkernel(self, backend):
        # Start IPython kernel with GUI event loop and mpl support
        self.ipkernel = mpl_kernel(backend)
        # To create and track active qt consoles
        self.consoles = []
        
        # This application will also act on the shell user namespace
        self.namespace = self.ipkernel.shell.user_ns

        # Example: a variable that will be seen by the user in the shell, and
        # that the GUI modifies (the 'Counter++' button increments it):
        self.namespace['app_counter'] = 0
        #self.namespace['ipkernel'] = self.ipkernel  # dbg

    def print_namespace(self, evt=None):
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.items():
            if not k.startswith('_'):
                print('%s -> %r' % (k, v))
        sys.stdout.flush()

    def new_qt_console(self, evt=None):
        """start a new qtconsole connected to our kernel"""
        return connect_qtconsole(self.ipkernel.abs_connection_file, profile=self.ipkernel.profile)

    def count(self, evt=None):
        self.namespace['app_counter'] += 1

    def cleanup_consoles(self, evt=None):
        for c in self.consoles:
            c.kill()

#-----------------------------------------------------------------------------
# from: ipkernel_qtapp.py
# https://github.com/ipython/ipykernel/blob/master/examples/embedding/ipkernel_qtapp.py
#-----------------------------------------------------------------------------
class SimpleWindow(Qt.QWidget, InternalIPKernel):

    def __init__(self, app):
        Qt.QWidget.__init__(self)
        self.app = app
        self.add_widgets()
        self.init_ipkernel('qt')
        self.new_qt_console()

    def add_widgets(self):
        self.setGeometry(300, 300, 400, 70)
        self.setWindowTitle('IPython in your app')

        # Add simple buttons:
        console = Qt.QPushButton('Qt Console', self)
        console.setGeometry(10, 10, 100, 35)
        self.connect(console, Qt.SIGNAL('clicked()'), self.new_qt_console)

        namespace = Qt.QPushButton('Namespace', self)
        namespace.setGeometry(120, 10, 100, 35)
        self.connect(namespace, Qt.SIGNAL('clicked()'), self.print_namespace)

        count = Qt.QPushButton('Count++', self)
        count.setGeometry(230, 10, 80, 35)
        self.connect(count, Qt.SIGNAL('clicked()'), self.count)

        # Quit and cleanup
        quit = Qt.QPushButton('Quit', self)
        quit.setGeometry(320, 10, 60, 35)
        self.connect(quit, Qt.SIGNAL('clicked()'), Qt.qApp, Qt.SLOT('quit()'))

        self.app.connect(self.app, Qt.SIGNAL("lastWindowClosed()"),
                         self.app, Qt.SLOT("quit()"))

        self.app.aboutToQuit.connect(self.cleanup_consoles)

#-----------------------------------------------------------------------------
# previous approach
#-----------------------------------------------------------------------------
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
        super(QIPythonWidget, self).__init__(*args, **kwargs)
        #RichIPythonWidget.__init__(self, *args, **kwargs)
        if customBanner != None:
            self.banner = customBanner
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
        #QtGui.QWidget.__init__(self, parent)
        self.ipy = ipy = QIPythonWidget(customBanner=SLOTH_IPY_WELCOME)

        ipy.push_variables(_get_ipy_mods())
        ipy.print_text('Process ID is {0}\n'.format(os.getpid()))
        ipy.print_text(_get_ipy_mods_text())
      
        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(ipy)
        
        
if __name__ == '__main__':
    if (HAS_QT and HAS_IPYTHON):
        # CURRENT
        app = Qt.QApplication([]) 
        win = SimpleWindow(app)
        win.show()
        # Very important, IPython-specific step: this gets GUI event loop
        # integration going, and it replaces calling app.exec_()
        win.ipkernel.start()
        #
        # PREVIOUS
        #app = QtGui.QApplication(sys.argv)
        #ipy = IPyConsoleWidget()
        #ipy.show()
        #sys.exit(app.exec_())
    else:
        pass

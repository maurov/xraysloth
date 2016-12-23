#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic utilities for daily work
===================================

TODO
====

- collect all bits and pieces here

"""

import numpy as np

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2011-2016"


### colorized output ###
HAS_TERMCOLOR = False
try:
    from termcolor import colored
    HAS_TERMCOLOR = True
except:
    pass

def colorstr(instr, color='green', on_color=None, attrs=['bold']):
    """colorized string

    Parameters
    ----------
    color : str, 'green'
            Available text colors:
            'red', 'green', 'yellow', 'blue', 'magenta', 'cyan',
            'white'

    on_color : str, None
               Available text highlights:
               'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta',
               'on_cyan', 'on_white'

    attrs : list of str, ['bold']
            Available attributes:
            'bold', 'dark', 'underline', 'blink', 'reverse', 'concealed'
    """
    if HAS_TERMCOLOR:
        return colored(instr, color=color, on_color=None, attrs=attrs)
    else:
        return instr

### Files ###
def cp_replace(grepfns, grepstr, rplstr, splitstr='_'):
    """given a filenames search string, copy the files with replaced string

    Parameters
    ----------
    grepfns : string
              search string passed to glob to generate files list to
              copy
    grepstr : string
              string to replace
    rplstr : string
             new string
    splitstr : string, '_'
               string used as separator
    """
    import glob
    import subprocess
    fns = glob.glob(grepfns)
    for fn in fns:
        _fn2 = [w.replace(grepstr, rplstr) for w in fn.split(splitstr)]
        fn2 = splitstr.join(_fn2)
        subprocess.call('cp {0} {1}'.format(fn, fn2), shell=True)
        print(fn2)

### Numpy ###
def imin(arr, check=False):
    """index of minimum value"""
    _im = np.argmin(arr)
    if check:
        print('Check: {0} = {1}'.format(np.min(arr), arr[_im]))
    return _im
        
def imax(arr, check=False):
    """index of maximum value"""
    _im = np.argmax(arr)
    if check:
        print('Check: {0} = {1}'.format(np.max(arr), arr[_im]))
    return _im
        
### IPython ###
def ipythonAutoreload():
    """force ipython to autoreload imported modules"""
    from IPython import get_ipython
    mgc = get_ipython().magic
    mgc(u'%load_ext autoreload')
    mgc(u'%autoreload 2')

def run_from_ipython():
    """check if inside ipython"""
    try:
        __IPYTHON__
        return True
    except NameError:
        return False
    
### PyMca ###
def getPyMcaMain(fload=None):
    """show PyMcaMain from a shell (e.g. IPython) and return its obj"""
    from matplotlib import rcParams
    rcParams['text.usetex'] = False
    HAS_PYMCA = False
    try:
        from PyMca5.PyMcaGui.pymca import PyMcaMain
        HAS_PYMCA = True
    except:
        from PyMca import PyMcaMain
        HAS_PYMCA = True

    if HAS_PYMCA:
        m = PyMcaMain.PyMcaMain()
        if fload is not None: m.sourceWidget.sourceSelector.openFile(fload)
        m.show()
        return m
    else:
        print("PyMca not found")
        return 0
        
### Matplotlib ###
def mplSetPubFont(size=8, usetex=True):
    """very basic mpl set font for publication-quality figures"""
    from matplotlib import rc
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size':size})
    rc('text', usetex=usetex)


### Qt ###
def qt_create_window(window_class):
    """Create a Qt window in Python, or interactively in IPython with Qt
    GUI event loop integration.

    Credits: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/

    """
    from PyQt4 import QtCore, QtGui
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        app_created = True
    app.references = set()
    window = window_class()
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    return window

def qt_close_all_windows():
    """close all qt windows!!!"""
    from PyMca5.PyMcaGui import PyMcaQt as qt
    qt.QApplication.closeAllWindows()
    
def qt5_get_version():
    from PyQt5.QtCore import QT_VERSION_STR
    from PyQt5.Qt import PYQT_VERSION_STR
    from sip import SIP_VERSION_STR

    print("Qt version:", QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", PYQT_VERSION_STR)

    
if __name__ == '__main__':
    #qt5_get_version()
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic utilities for daily work
===================================

TODO
====
- collect all bits and pieces here

"""
import sys, os
import numpy as np

########################
### COLORIZED OUTPUT ###
########################
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


def get_efermi(fn):
    """get the Fermi level energy from a FDMNES out file"""
    try:
        f = open(fn)
    except:
        return 0
    l = f.readline()
    f.close()
    ef = float(l.split()[6])
    if DEBUG: print('Calculated Fermi level: {0}'.format(ef))
    return ef

#############
### NUMPY ###
#############
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

###############
### IPython ###
###############
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

def is_in_notebook():
    """check if code is run from IPython notebook

    .. note:: code from StackOverflow `https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook/24937408#24937408`_
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

##################
### Matplotlib ###
##################
def mplSetPubFont(size=8, usetex=True):
    """very basic mpl set font for publication-quality figures"""
    from matplotlib import rc
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size':size})
    rc('text', usetex=usetex)

##########
### Qt ###
##########
def qt_create_window(window_class):
    """Create a Qt window in Python, or interactively in IPython with Qt
    GUI event loop integration.

    Credits: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/

    """
    from silx.gui import qt
    app_created = False
    app = qt.QCoreApplication.instance()
    if app is None:
        app = qt.QApplication(sys.argv)
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
    from silx.gui import qt
    qt.QApplication.closeAllWindows()

def qt_get_version():
    from silx.gui import qt
    from sip import SIP_VERSION_STR

    print("Qt version:", qt.QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", qt.PYQT_VERSION_STR)


if __name__ == '__main__':
    #qt5_get_version()
    pass

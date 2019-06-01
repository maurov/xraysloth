#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities related to Qt
-----------------------
"""
import sys
from silx.gui import qt

######
# Qt #
######


def qt_create_window(window_class):
    """Create a Qt window in Python, or interactively in IPython with Qt
    GUI event loop integration.

    Credits: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/

    """
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
    qt.QApplication.closeAllWindows()


def qt_get_version():
    from sip import SIP_VERSION_STR

    print("Qt version:", qt.QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", qt.PYQT_VERSION_STR)

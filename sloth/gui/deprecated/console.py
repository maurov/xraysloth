#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""custom version of IPythonWidget (from silx.gui.console)
==========================================================

"""
import warnings
import os
import sys
import math
from collections import OrderedDict

from silx.gui.console import IPythonWidget

import sloth

# NAMESPACES => _pushDict / _pushInfos ###
_pushDict = OrderedDict()
_pushInfos = []

_pushDict.update({'os': os,
                  'sys': sys,
                  'math': math})
_pushInfos.extend(['os', 'sys', 'math'])

HAS_NUMPY = False
try:
    import numpy as np
    HAS_NUMPY = True
    _pushDict.update({'np': np})
    _pushInfos.extend(['np: Numpy'])
except ImportError:
    pass

HAS_MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
    _pushDict.update({'plt': plt})
    _pushInfos.extend(['plt : matplotlib.pyplot'])
except ImportError:
    pass

HAS_SILX_QT = False
try:
    from silx.gui import qt
    HAS_SILX_QT = True
    _pushDict.update({'qt': qt})
    _pushInfos.append('qt : silx.gui.qt')
except ImportError:
    pass

HAS_XRAYLIB = False
try:
    import xraylib as xl
    HAS_XRAYLIB = True
    _pushDict.update({'xl': xl})
    _pushInfos.append('xl : xraylib')
except ImportError:
    pass

HAS_LARCH = False
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import larch
    from larch import Interpreter
    _lar = Interpreter(with_plugins=False)
    HAS_LARCH = True
    _pushDict.update({'larch': larch,
                      '_lar': _lar})
    _pushInfos.extend(['larch : larch',
                       '_lar : larch.Interpreter'])
except ImportError:
    pass

# SLOTH KIT => _slothKit ###
_slothKit = {}

try:
    from sloth.utils.bragg import (SI_ALAT, GE_ALAT, ev2wlen, wlen2ev,
                                   bragg_ev, bragg_th, theta_b,
                                   d_cubic, xray_bragg, findhkl)
    _slothKit.update({'SI_ALAT': SI_ALAT,
                      'GE_ALAT': GE_ALAT,
                      'ev2wlen': ev2wlen,
                      'wlen2ev': wlen2ev,
                      'bragg_ev': bragg_ev,
                      'bragg_th': bragg_th,
                      'xray_bragg': xray_bragg,
                      'theta_b': theta_b,
                      'd_cubic': d_cubic,
                      'findhkl': findhkl})
except ImportError:
    pass

try:
    from sloth.utils.xdata import (ELEMENTS, SHELLS, LINES_DICT,
                                   LINES, LINES_K, LINES_L, LINES_M,
                                   TRANSITIONS, TRANS_DICT, TRANS_K,
                                   TRANS_L, TRANS_M, xray_line, xray_edge)
    _slothKit.update({'ELEMENTS': ELEMENTS,
                      'SHELLS': SHELLS,
                      'LINES_DICT': LINES_DICT,
                      'LINES': LINES,
                      'LINES_K': LINES_K,
                      'LINES_L': LINES_L,
                      'LINES_M': LINES_M,
                      'TRANSITIONS': TRANSITIONS,
                      'TRANS_DICT': TRANS_DICT,
                      'TRANS_K': TRANS_K,
                      'TRANS_L': TRANS_L,
                      'TRANS_M': TRANS_M,
                      'xray_line': xray_line,
                      'xray_edge': xray_edge})
except ImportError:
    pass


try:
    from sloth.fit.peakfit import (fit_splitpvoigt, fit_results)
    _slothKit.update({'fit_splitpvoigt': fit_splitpvoigt,
                      'fit_results': fit_results})
except ImportError:
    pass

SLOTH_BANNER = "Sloth console, version {0}\n".format(sloth.__version__)


class customIPythonWidget(IPythonWidget):
    """customized IPythonWidget"""

    def __init__(self, *args, **kwargs):
        super(customIPythonWidget, self).__init__(custom_banner=SLOTH_BANNER,\
                                                  *args, **kwargs)

        self.pushVariables({'os': os,
                            'sys': sys,
                            'np': np,
                            'math': math})


def main():
    """Run a Qt app with an IPython console"""
    app = qt.QApplication([])
    widget = customIPythonWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()

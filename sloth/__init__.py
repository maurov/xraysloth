#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sloth: some utilies for x-ray spectroscopists

Naming
======

* classes MixedUpperCase
* varables lowerUpper _or_ lower
* functions underscore_separated _or_ lowerUpper

"""
from __future__ import (absolute_import, print_function, division,
                        unicode_literals)

### NAMESPACES => _pushDict / _pushInfos ###
import os, sys, warnings
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

__author__ = "Mauro Rovezzi"
__version__ = "0.3.0-dev"

_libDir = os.path.dirname(os.path.realpath(__file__))

_resourcesPath = os.path.join(_libDir, 'resources')

__pkgs__ = ['sloth',
            'sloth.test',       #test suite (main)
            'sloth.utils',      #utilities (generic)
            'sloth.math',       #math&friends
            'sloth.collects',   #data containers
            'sloth.fit',        #fit utilities
            'sloth.gui',        #graphical user interface widgets
            'sloth.io',         #input-output
            'sloth.inst',       #instrumentation
            'sloth.raytracing', #ray tracing (shadow)
            'sloth.exafs',      #exafs analysis tools
            'sloth.xanes',      #xanes analysis tools
            'sloth.rixs',       #rixs analysis tools
            'sloth.xes'         #xes analysis tools
            ]

_pushDict = OrderedDict()
_pushInfos = []

_pushDict.update({'os'   : os,
                  'sys'  : sys,
                  'math' : math,
                  'np'   : np,
                  'plt'  : plt})

_pushInfos.extend(['os', 'sys', 'math',
                   'np : Numpy',
                   'plt : matplotlib.pyplot'])

HAS_SILX_QT = False
try:
    from silx.gui import qt
    HAS_SILX_QT = True
    _pushDict.update({'qt'   : qt})
    _pushInfos.append('qt : Qt from SILX')
except:
    pass

HAS_XRAYLIB = False
try:
    import xraylib as xl
    HAS_XRAYLIB = True
    _pushDict.update({'xl'   : xl})
    _pushInfos.append('xl : XrayLib')
except:
    pass

HAS_LARCH = False
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import larch
    from larch import Interpreter
    _larch = Interpreter(with_plugins=False)
    HAS_LARCH = True
    _pushDict.update({'larch'   : larch,
                      '_larch'  : _larch})
    _pushInfos.extend(['larch : Larch lib',
                       '_larch : Larch interpreter'])
except:
    pass

### SLOTH KIT => _slothKit ###
_slothKit = {}

try:
    from sloth.utils.bragg import (SI_ALAT, GE_ALAT, ev2wlen, wlen2ev,
                                   bragg_ev, bragg_th, theta_b,
                                   d_cubic, xray_bragg, findhkl)
    _slothKit.update({'SI_ALAT'         : SI_ALAT,
                      'GE_ALAT'         : GE_ALAT,
                      'ev2wlen'         : ev2wlen,
                      'wlen2ev'         : wlen2ev,
                      'bragg_ev'        : bragg_ev,
                      'bragg_th'        : bragg_th,
                      'xray_bragg'      : xray_bragg,
                      'theta_b'         : theta_b,  
                      'd_cubic'         : d_cubic,
                      'findhkl'         : findhkl})   
except:
    pass

try:
    from sloth.utils.xdata import (ELEMENTS, SHELLS, LINES_DICT,
                                   LINES, LINES_K, LINES_L, LINES_M,
                                   TRANSITIONS, TRANS_DICT, TRANS_K,
                                   TRANS_L, TRANS_M, xray_line, xray_edge)
    _slothKit.update({'ELEMENTS'        : ELEMENTS,
                      'SHELLS'          : SHELLS,
                      'LINES_DICT'      : LINES_DICT,
                      'LINES'           : LINES,
                      'LINES_K'         : LINES_K,
                      'LINES_L'         : LINES_L,
                      'LINES_M'         : LINES_M,
                      'TRANSITIONS'     : TRANSITIONS,
                      'TRANS_DICT'      : TRANS_DICT,
                      'TRANS_K'         : TRANS_K,
                      'TRANS_L'         : TRANS_L,
                      'TRANS_M'         : TRANS_M,
                      'xray_line'       : xray_line,
                      'xray_edge'       : xray_edge})
except:
    pass


try:
    from sloth.fit.peakfit import (fit_splitpvoigt, fit_results)
    _slothKit.update({'fit_splitpvoigt' : fit_splitpvoigt,
                      'fit_results'     : fit_results})
except:
    pass
    
if __name__ == '__main__':
    pass

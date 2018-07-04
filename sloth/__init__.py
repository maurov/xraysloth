#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sloth: some utilies for x-ray spectroscopists

Naming
======

* classes MixedUpperCase
* varables lowerUpper _or_ lower
* functions underscore_separated _or_ lowerUpper

"""
from __future__ import absolute_import, print_function, division, unicode_literals

import os, sys
import math
import numpy as np
import matplotlib.pyplot as plt

HAS_SILX_QT = False
try:
    from silx.gui import qt
    HAS_SILX_QT = True
except:
    pass

HAS_XRAYLIB = False
try:
    import xraylib as xl
    HAS_XRAYLIB = True
except:
    pass

HAS_LARCH = False
try:
    import larch
    from larch import Interpreter
    _larch = Interpreter()
    HAS_LARCH = True
except:
    pass

from sloth.utils.bragg import (SI_ALAT, GE_ALAT,\
                               ev2wlen, wlen2ev, bragg_ev, bragg_th, theta_b,\
                               d_cubic, xray_bragg, findhkl)

from sloth.utils.xdata import (ELEMENTS, SHELLS, LINES_DICT, LINES,\
                               LINES_K, LINES_L, LINES_M, TRANSITIONS,\
                               TRANS_DICT, TRANS_K, TRANS_L, TRANS_M,\
                               xray_line)

from sloth.fit.peakfit import fit_splitpvoigt, fit_results

__author__ = "Mauro Rovezzi"
__version__ = "0.3.0-dev"

_libDir = os.path.dirname(os.path.realpath(__file__))

_resourcesPath = os.path.join(_libDir, 'resources')

_pushDict = {'os'   : os,
             'sys'  : sys,
             'math' : math,
             'np'   : np,
             'plt'  : plt}
_pushInfos = ['os, sys, math',
              'np : Numpy',
              'plt : matplotlib.pyplot']

if HAS_SILX_QT:
    _pushDict.update({'qt'   : qt})
    _pushInfos.append('qt : Qt from SILX')

if HAS_XRAYLIB:
    _pushDict.update({'xl'   : xl})
    _pushInfos.append('xl : XrayLib')

if HAS_LARCH:
    _pushDict.update({'larch'   : larch,
                      '_larch'  : _larch})
    _pushInfos.append('larch : Larch lib')
    _pushInfos.append('_larch : Larch interpreter')
    
_slothKit = {'SI_ALAT'         : SI_ALAT,
             'GE_ALAT'         : GE_ALAT,
             'ELEMENTS'        : ELEMENTS,
             'SHELLS'          : SHELLS,
             'LINES_DICT'      : LINES_DICT,
             'LINES'           : LINES,
             'TRANSITIONS'     : TRANSITIONS,
             'TRANS_DICT'      : TRANS_DICT,
             'ev2wlen'         : ev2wlen,
             'wlen2ev'         : wlen2ev,
             'bragg_ev'        : bragg_ev,
             'bragg_th'        : bragg_th,
             'xray_bragg'      : xray_bragg,
             'theta_b'         : theta_b,
             'd_cubic'         : d_cubic,
             'findhkl'         : findhkl,
             'xray_line'       : xray_line,
             'fit_splitpvoigt' : fit_splitpvoigt,
             'fit_results'     : fit_results}


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

if __name__ == '__main__':
    pass

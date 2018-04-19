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

__author__ = "Mauro Rovezzi"
__version__ = "0.3.0"

import os, sys
_libDir = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(_libDir)

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

#__all__ = ['a', 'b', 'c']
from sloth.utils.bragg import (SI_ALAT, GE_ALAT,\
                               ev2wlen, wlen2ev, bragg_ev, theta_b,\
                               d_cubic,\
                               findhkl)

from sloth.fit.peakfit import fit_splitpvoigt, fit_results

_slothKit = {'SI_ALAT'         : SI_ALAT,
             'GE_ALAT'         : GE_ALAT,
             'ev2wlen'         : ev2wlen,
             'wlen2ev'         : wlen2ev,
             'bragg_ev'        : bragg_ev,
             'theta_b'         : theta_b,
             'd_cubic'         : d_cubic,
             'findhkl'         : findhkl,
             'fit_splitpvoigt' : fit_splitpvoigt,
             'fit_results'     : fit_results}

if __name__ == '__main__':
    pass

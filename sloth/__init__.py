#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sloth: some utilies for x-ray spectroscopists

Naming
======

* classes MixedUpperCase
* varables lowerUpper _or_ lower
* functions underscore_separated _or_ lowerUpper

"""
from __future__ import absolute_import, print_function, division

__author__ = "Mauro Rovezzi"
__version__ = "0.2.1"

import os, sys
_libDir = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(_libDir)

__pkgs__ = ['sloth',
            'sloth.collects',   #data containers
            'sloth.exafs',      #exafs analysis tools
            'sloth.fit',        #fit
            'sloth.gui',        #graphical user interface widgets
            'sloth.io',         #input-output
            'sloth.inst',       #instrumentation
            'sloth.math',       #math&friends
            'sloth.raytracing', #ray tracing
            'sloth.rixs',       #rixs
            'sloth.tests',      #test suite
            'sloth.utils',      #utilities
            'sloth.xanes',      #xanes analysis tools
            'sloth.xes'         #xes analysis tools
            ]


#__all__ = ['a', 'b', 'c']

if __name__ == '__main__':
    pass

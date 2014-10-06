#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EXAMPLES/TESTS FOR SLOTH
https://github.com/maurov/xraysloth
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2011-2014"

import os, sys
_curDir = os.path.dirname(os.path.realpath(__file__))
_parDir = os.path.realpath(os.path.join(_curDir, os.path.pardir))
_libDir = os.path.join(_parDir, 'sloth')
sys.path.append(_libDir)

if __name__ == '__main__':
    pass
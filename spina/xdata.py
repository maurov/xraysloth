#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple utility to retrieve x-ray data from external libraries/databases


Available x-ray libraries/dbs
==============================

* `xraylib <https://github.com/tschoonj/xraylib>`_
* ``xraydb_plugin.py`` in `Larch <https://github.com/xraypy/xraylarch>`_
* ``Elements`` in `PyMca <https://github.com/vasole/pymca>`_

TODO
====

- move here '_core_width()' from convolution1D.py

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__owner__ = "Mauro Rovezzi"
__year__ = "2013-2014"
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Sept 2014"

import os, sys
import numpy as np

HAS_XRAYLIB = False
HAS_LARCH = False
HAS_PYMCA5 = False

try:
    import xraylib as xl
    HAS_XRAYLIB = True
except ImportError:
    pass

try:
    from larch import use_plugin_path
    use_plugin_path('xray')
    from xraydb import xrayDB
    HAS_LARCH = True
except:
    pass
    
#GLOBAL VARIABLES
ELEMENTS = ('H', 'He',
            'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
            'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
            'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
            'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',
            'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
            'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am')

# SHELLS
# K = 1 (s)
# L = 2 (s, p)
# M = 3 (s, p, d)
# N = 4 (s, p, d, f)
# O = 5 (s, p, d, f)
# P = 6 (s, p)

# TRANS
# 1 = s
# 2, 3 = p (1/2, 3/2)
# 4, 5 = d (3/2, 5/2)
# 6, 7 = f 

SHELLS = ('K',
          'L1', 'L2', 'L3',
          'M1', 'M2', 'M3', 'M4', 'M5',
          'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7',
          'O1', 'O2', 'O3', 'O4', 'O5',
          'P1', 'P2', 'P3')

# TODO
LINES = ('KL3', 'KL2', 'KM3', 'KM2',
         'L1L2', 'L1M3', 'L1O2', 'L2M4', 'L2N4', 'L3M5', 'L3N5', 'L3M1')

### XRAYLIB-BASED FUNCTIONS ###
def find_edge(emin, emax, shells=None):
    """ return the edge energy in a given energy range [emin,emax] (eV)"""
    if shells is None:
        shells = SHELLS
    for el in ELEMENTS:
        for sh in shells:
            edge = xl.EdgeEnergy(xl.SymbolToAtomicNumber(el), getattr(xl, sh+'_SHELL'))*1000
            if ((edge >= emin) and (edge <= emax)):
                print('{0} \t {1} \t {2:>.2f} eV'.format(el, sh, edge))

def find_line(emin, emax, elements=None, lines=None):
    """ return the line energy in a given energy range [emin,emax] (eV)"""
    if lines is None:
        lines = LINES
    if elements is None:
        elements = ELEMENTS
    for el in elements:
        for ln in lines:
            line = xl.LineEnergy(xl.SymbolToAtomicNumber(el), getattr(xl, ln+'_LINE'))*1000
            if ((line >= emin) and (line <= emax)):
                print('{0} \t {1} \t {2:>.2f} \t eV'.format(el, ln, line))

def ene_res(emin, emax, shells=['K']):
    """ used in spectro.py """
    s = {}
    s['el'] = []
    s['en'] = []
    s['edge'] = []
    s['ch'] = []
    s['dee'] = []
    for el in ELEMENTS:
        for sh in shells:
            edge = xl.EdgeEnergy(xl.SymbolToAtomicNumber(el), getattr(xl, sh+'_SHELL'))*1000
            ch = xl.AtomicLevelWidth(xl.SymbolToAtomicNumber(el), getattr(xl, sh+'_SHELL'))*1000
            if ((edge >= emin) and (edge <= emax)):
                s['el'].append(el)
                s['en'].append(xl.SymbolToAtomicNumber(el))
                s['edge'].append(edge)
                s['ch'].append(ch)
                s['dee'].append(ch/edge)
    return s


### LARCH-BASED FUNCTIONS ###
def _core_width(element=None, edge=None):
    """returns core hole width for a given element and edge

    See 'core_width' in Larch
    """
    if ((element is None) or (edge is None)):
        print('ERROR: element or edge not given, returning 0')
        return 0
    else:
        if HAS_LARCH:
            xdb = xrayDB()
            return xdb.corehole_width(element=element, edge=edge)
        else:
            print('ERROR: Larch not found, returning 0')
            return 0
    
if __name__ == '__main__':
    # see tests/examples in xdata_tests.py
    pass


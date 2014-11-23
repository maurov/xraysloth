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
ELEMENTS = ('H', 'He',\
            'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',\
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',\
            'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',\
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',\
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',\
            'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',\
            'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',\
            'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',\
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',\
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

SHELLS = ('K',\
          'L1', 'L2', 'L3',\
          'M1', 'M2', 'M3', 'M4', 'M5',\
          'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7',\
          'O1', 'O2', 'O3', 'O4', 'O5',\
          'P1', 'P2', 'P3')

# dictionary of lines
# Ln in Hepheastus is LE in Xraylib
# Mz in Hepheastus not in Xraylib (the single transitions yes!)
LINES_DICT = {'K' : ('KA1', 'KA2', 'KA3',\
                     'KB1', 'KB2', 'KB3', 'KB4', 'KB5'),
              'L1' : ('LB3', 'LB4', 'LG2', 'LG3'),
              'L2' : ('LB1', 'LG1', 'LG6', 'LE'),
              'L3' : ('LA1', 'LA2', 'LB2', 'LB5', 'LB6', 'LL'),
              'M3' : ('MG',),
              'M4' : ('MB',),
              'M5' : ('MA1', 'MA2')}

LINES_K = LINES_DICT['K']
LINES_L = LINES_DICT['L1'] + LINES_DICT['L2'] + LINES_DICT['L3']
LINES_M = LINES_DICT['M3'] + LINES_DICT['M4'] + LINES_DICT['M5']
LINES = LINES_K + LINES_L + LINES_M

TRANSITIONS = ('KL3', 'KL2', 'KL1',\
               'KM3', 'KN3', 'KM2', 'KN5', 'KM5',\
               'L3M5', 'L3M4',\
               'L2M4', 'L3N5', 'L1M3', 'L1M2', 'L3O45', 'L3N1',\
               'L2N4', 'L1N2', 'L1N3', 'L2O4',\
               'L3M1', 'L2M1',\
               'M5N7', 'M5N6',\
               'M4N6',\
               'M3N5')

# INDEX DICTIONARY: KEYS=LINES : VALUES=(LINES[IDX], SHELLS[IDX_XAS], SHELLS[IDX_XES])
LINES2TRANS = {'KA1' : (0, 0, 3),
               'KA2' : (1, 0, 2),
               'KA3' : (2, 0, 1),
               'KB1' : (3, 0, 6),
               'KB2' : (4, 0, 11),
               'KB3' : (5, 0, 5),
               'KB4' : (6, 0, 13),
               'KB5' : (7, 0, 8),
               'LA1' : (8, 3, 8),
               'LA2' : (9, 3, 7),
               'LB1' : (10, 2, 7),
               'LB2' : (11, 3, 13),
               'LB3' : (12, 1, 6),
               'LB4' : (13, 1, 5),
               'LB5' : (14, 3, 19), #WARNING: here is only O4
               'LB6' : (15, 3, 9),
               'LG1' : (16, 2, 12),
               'LG2' : (17, 1, 10),
               'LG3' : (18, 1, 11),
               'LG6' : (19, 2, 19),
               'LL' : (20, 3, 4),
               'LE' : (21, 2, 4),
               'MA1' : (22, 8, 15),
               'MA2' : (23, 8, 14),
               'MB' : (24, 7, 14),
               'MG' : (25, 6, 13)}

def mapLine2Trans(line):
    """ returns a tuple of strings mapping the transitions for a given line """
    try:
        idx = LINES2TRANS[line]
        return (LINES[idx[0]], TRANSITIONS[idx[0]], SHELLS[idx[1]], SHELLS[idx[2]])
    except:
        print('ERROR: line {0} not in the list; returning 0'.format(line))
        return 0

### XRAYLIB-BASED FUNCTIONS ###
def find_edge(emin, emax, shells=None):
    """ return the edge energy in a given energy range [emin,emax] (eV)"""
    if HAS_XRAYLIB is False:
        print('ERROR: xraylib required')
        return 0
    if shells is None:
        shells = SHELLS
    for el in ELEMENTS:
        for sh in shells:
            edge = xl.EdgeEnergy(xl.SymbolToAtomicNumber(el), getattr(xl, sh+'_SHELL'))*1000
            if ((edge >= emin) and (edge <= emax)):
                print('{0} \t {1} \t {2:>.2f} eV'.format(el, sh, edge))

def find_line(emin, emax, elements=None, lines=None, outDict=False):
    """ return the line energy in a given energy range [emin,emax] (eV)

    Parameters
    ----------

    emin, emax : float
                 [minimum, maximum] energy range (eV)
    elements : list of str
               list of elements, [ELEMENTS (all)] 
    lines : list of str
            list of lines, [LINES (all)]
    outDict : boolean, False
              returns a dictionary instead of printing to screen with keywords:
              _out['el'] : element symbol, list of strs
              _out['eln] : element number, list of ints
              _out['ln'] : line, list of strs
              _out['en'] : energy eV, list of floats
              _out['w']  : width eV, list of floats

    Returns
    -------
    None, prints to screen the results (unless outDict given)
    """
    if HAS_XRAYLIB is False:
        print('ERROR: xraylib required')
        return 0
    if lines is None:
        lines = LINES
    if elements is None:
        elements = ELEMENTS
    _out = {}
    _out['el'] = []
    _out['eln'] = []
    _out['ln'] = []
    _out['en'] = []
    _out['w'] = []
    for el in elements:
        eln = xl.SymbolToAtomicNumber(el)
        for ln in lines:
            try:
                line = xl.LineEnergy(eln, getattr(xl, ln+'_LINE'))*1000
            except:
                print('{0}.{1} none'.format(el, ln))
                continue
            if ((line >= emin) and (line <= emax)):
                w = fluo_width(elem=el, line=ln)
                _out['el'].append(el)
                _out['eln'].append(eln)
                _out['ln'].append(ln) 
                _out['en'].append(line)
                _out['w'].append(w)
    # returns
    if outDict:
        return _out
    else:
        for eln, el, ln, line, w in zip(_out['eln'], _out['el'], _out['ln'], _out['en'], _out['w']):
            print('{0} \t {1} \t {2} \t {3:>.2f} \t {4:>.2f}'.format(eln, el, ln, line, w))
                
def ene_res(emin, emax, shells=['K']):
    """ used in spectro.py """
    if HAS_XRAYLIB is False:
        print('ERROR: xraylib required')
        return 0
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


def fluo_width(elem=None, line=None):
    """ returns the line width in eV"""
    if HAS_XRAYLIB is False:
        print('ERROR: xraylib required')
        return 0
    if ((elem is None) or (line is None)):
        print('ERROR: element or edge not given, returning 0')
        return 0
    else:
        ln = mapLine2Trans(line)
        try:
            lw_xas = xl.AtomicLevelWidth(xl.SymbolToAtomicNumber(elem), getattr(xl, ln[2]+'_SHELL'))*1000
            lw_xes = xl.AtomicLevelWidth(xl.SymbolToAtomicNumber(elem), getattr(xl, ln[3]+'_SHELL'))*1000
            return lw_xas + lw_xes
        except:
            return 0

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


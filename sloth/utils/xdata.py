#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple utility to retrieve x-ray data from external libraries/databases

Available x-ray libraries/dbs
==============================

* `xraylib <https://github.com/tschoonj/xraylib>`_
* ``xraydb_plugin.py`` in `Larch <https://github.com/xraypy/xraylarch>`_
* ``Elements`` in `PyMca <https://github.com/vasole/pymca>`_

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__owner__ = "Mauro Rovezzi"
__year__ = "2011--2015"

import os, sys, math
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
# TRANSITIONS
# 1 = s
# 2, 3 = p (1/2, 3/2)
# 4, 5 = d (3/2, 5/2)
# 6, 7 = f (5/2, 7/2)
SHELLS = ('K',                                       #0
          'L1', 'L2', 'L3',                          #1, 2, 3
          'M1', 'M2', 'M3', 'M4', 'M5',              #4, 5, 6, 7, 8
          'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7',  #9, 10, 11, 12, 13, 14, 15
          'O1', 'O2', 'O3', 'O4', 'O5',              #16, 17, 18, 19, 20
          'P1', 'P2', 'P3')                          #21, 22, 23
# dictionary of lines
# Ln in Hepheastus is LE in Xraylib
# Mz in Hepheastus not in Xraylib (the single transitions yes!)
LINES_DICT = {'K' : ('KA1', 'KA2', 'KA3',                       #LINES[0, 1, 2]
                     'KB1', 'KB2', 'KB3', 'KB4', 'KB5'),        #LINES[3, 4, 5, 6, 7]
              'L1' : ('LB3', 'LB4', 'LG2', 'LG3'),              #LINES[8, 9, 10, 11]
              'L2' : ('LB1', 'LG1', 'LG6', 'LE'),               #LINES[12, 13, 14, 15]
              'L3' : ('LA1', 'LA2', 'LB2', 'LB5', 'LB6', 'LL'), #LINES[16, 17, 18, 19, 20, 21]
              'M3' : ('MG',),                                   #LINES[22] 
              'M4' : ('MB',),                                   #LINES[23] 
              'M5' : ('MA1', 'MA2')}                            #LINES[24, 25] 
LINES_K = LINES_DICT['K']
LINES_L = LINES_DICT['L1'] + LINES_DICT['L2'] + LINES_DICT['L3']
LINES_M = LINES_DICT['M3'] + LINES_DICT['M4'] + LINES_DICT['M5']
LINES = LINES_K + LINES_L + LINES_M
#
TRANS_DICT = {'K' : ('KL3', 'KL2', 'KL1',
                     'KM3', 'KN3', 'KM2', 'KN5', 'KM5'),
              'L1' : ('L1M3', 'L1M2', 'L1N2', 'L1N3'),
              'L2' : ('L2M4', 'L2N4', 'L2O4', 'L2M1'),
              'L3' : ('L3M5', 'L3M4', 'L3N5', 'L304', 'L3N1', 'L3M1'),
              'M3' : ('M3N5',),
              'M4' : ('M4N6',),
              'M5' : ('M5N7', 'M5N6')}
TRANS_K = TRANS_DICT['K']
TRANS_L = TRANS_DICT['L1'] + TRANS_DICT['L2'] + TRANS_DICT['L3']
TRANS_M = TRANS_DICT['M3'] + TRANS_DICT['M4'] + TRANS_DICT['M5']
TRANSITIONS = TRANS_K + TRANS_L + TRANS_M
#INDEX DICTIONARY: KEYS=LINES : VALUES=(LINES[IDX], SHELLS[IDX_XAS], SHELLS[IDX_XES])
LINES2TRANS = {'KA1' : (0, 0, 3),
               'KA2' : (1, 0, 2),
               'KA3' : (2, 0, 1),
               'KB1' : (3, 0, 6),
               'KB2' : (4, 0, 11),
               'KB3' : (5, 0, 5),
               'KB4' : (6, 0, 13),
               'KB5' : (7, 0, 8),
               'LB3' : (8, 1, 6),
               'LB4' : (9, 1, 5),
               'LG2' : (10, 1, 10),
               'LG3' : (11, 1, 11),
               'LB1' : (12, 2, 7),
               'LG1' : (13, 2, 12),
               'LG6' : (14, 2, 19),
               'LE' :  (15, 2, 4),
               'LA1' : (16, 3, 8),
               'LA2' : (17, 3, 7),
               'LB2' : (18, 3, 13),
               'LB5' : (19, 3, 19), #WARNING: here is only O4               
               'LB6' : (20, 3, 9),
               'LL' :  (21, 3, 4),
               'MG' :  (22, 6, 13),
               'MB' :  (23, 7, 14),
               'MA1' : (24, 8, 15),
               'MA2' : (25, 8, 14)}

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


def fluo_width(elem=None, line=None, herfd=False, showInfos=True):
    """returns the line width in eV

    Parameters
    ----------

    elem : string or int, given element
    line : string, siegbahn notation for emission line

    Return
    ------
    herfd=False (default): lw_xas + lw_xes
    herfd=True: 1/(math.sqrt(lw_xas**2 + lw_xes**2))

    """
    if HAS_XRAYLIB is False:
        print('ERROR: xraylib required')
        return 0
    if ((elem is None) or (line is None)):
        print('ERROR: element or edge not given, returning 0')
        return 0
    if type(elem) is str:
        elem_z = xl.SymbolToAtomicNumber(elem)
        elem_str = elem
    else:
        elem_z = elem
        elem_str = xl.AtomicNumberToSymbol(elem)
    ln = mapLine2Trans(line)
    try:
        lw_xas = xl.AtomicLevelWidth(elem_z, getattr(xl, ln[2]+'_SHELL'))*1000
        lw_xes = xl.AtomicLevelWidth(elem_z, getattr(xl, ln[3]+'_SHELL'))*1000
        if showInfos: print('{0} {1} (={2}): XAS={3:.2f} eV, XES={4:.2f} eV'.format(elem_str, line, ln[1], lw_xas, lw_xes))
        if herfd is True:
            return 1./(math.sqrt(lw_xas**2 + lw_xes**2))
        else:
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


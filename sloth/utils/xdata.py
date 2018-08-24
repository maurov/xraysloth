#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple utility to retrieve X-ray data from external
libraries/databases

Available libraries/dbs
=======================

* `xraylib <https://github.com/tschoonj/xraylib>`_
* ``xraydb_plugin.py`` in `Larch <https://github.com/xraypy/xraylarch>`_
* ``Elements`` in `PyMca <https://github.com/vasole/pymca>`_

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"

import os, sys, math
import numpy as np
import logging

HAS_SILX = False
try:
    from silx.gui.plot import Plot1D
    HAS_SILX = True
except:
    pass

HAS_XRAYDB = False
try:
    import xraylib as xl
    HAS_XRAYLIB = True
except ImportError:
    pass

HAS_LARCH = False
try:
    import larch
    from larch import Interpreter
    _larch = Interpreter() #init larch session
    from larch_plugins.xray.xraydb_plugin import get_xraydb
    xdb = get_xraydb(_larch)
    HAS_LARCH = True
except:
    pass

_logger = logging.getLogger(__name__)

#ERROR MESSAGES
def _larch_error(ret=None):
    """print a missing larch error message and return 'ret'"""
    _logger.error("Larch not found")
    return ret

def _xraylib_error(ret=None):
    """print a missing xraylib error message and return 'ret'"""
    _logger.error("Xraylib not found")
    return ret

#SIGMA <-> FWHM
F2S = 2*math.sqrt(2*math.log(2))

def fwhm2sigma(fwhm):
    """get sigma from FWHM"""
    return fwhm/F2S

def sigma2fwhm(sigma):
    """get FWHM from sigma"""
    return sigma*F2S

def lorentzian(x, amplitude=1.0, center=0.0, sigma=1.0):
    """Return a 1-dimensional Lorentzian function.
    
    lorentzian(x, amplitude, center, sigma) = (amplitude/(1 +
    ((1.0*x-center)/sigma)**2)) / (pi*sigma)

    """
    return (amplitude/(1 + ((1.0*x-center)/sigma)**2)) / (math.pi*sigma)

##########################
### ELEMENTS AND LINES ###
##########################

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

# SHELLS / EDGES
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
    """returns a tuple of strings mapping the transitions for a given line"""
    try:
        idx = LINES2TRANS[line]
        return (LINES[idx[0]], TRANSITIONS[idx[0]], SHELLS[idx[1]], SHELLS[idx[2]])
    except:
        _logger.error('line {0} not in the list; returning 0'.format(line))
        return 0

###############################
### XRAYLIB-BASED FUNCTIONS ###
###############################

def get_element(elem):
    """get a tuple for element name and number"""
    if (type(elem) is str) and (elem in ELEMENTS):
        elem_z = xl.SymbolToAtomicNumber(elem)
        if elem_z == 0:
            raise NameError("unknown element name")
        elem_str = elem
    elif (type(elem) is int):
        elem_str = xl.AtomicNumberToSymbol(elem)
        if elem_str is None:
            raise NameError("element Z out of range")
        elem_z = elem
    else:
        raise NameError("check element argument")
    return (elem_str, elem_z)
    
def find_edge(emin, emax, shells=None):
    """return the edge energy in a given energy range [emin, emax] (eV)"""
    if HAS_XRAYLIB is False: _xraylib_error(0)
    if shells is None:
        shells = SHELLS
    for el in ELEMENTS:
        for sh in shells:
            edge = xl.EdgeEnergy(xl.SymbolToAtomicNumber(el), getattr(xl, sh+'_SHELL'))*1000
            if ((edge >= emin) and (edge <= emax)):
                print('{0} \t {1} \t {2:>.2f} eV'.format(el, sh, edge))

def find_line(emin, emax, elements=None, lines=None, outDict=False):
    """return the line energy in a given energy range [emin,emax] (eV)

    Parameters
    ==========

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
    =======
    
    None, prints to screen the results (unless outDict boolean given)

    """
    if HAS_XRAYLIB is False: _xraylib_error(0)
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
                if not w == 0:
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
            print('{eln} \t {el} \t {ln} \t {line:>.2f} \t {w:>.2f}'.format(**_out))
                
def ene_res(emin, emax, shells=['K']):
    """ used in spectro.py """
    if HAS_XRAYLIB is False: _xraylib_error(0)
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
    if HAS_XRAYLIB is False: _xraylib_error(0)
    if ((elem is None) or (line is None)):
        print('ERROR: element or edge not given, returning 0')
        return 0
    elm = get_element(elem)
    ln = mapLine2Trans(line)
    try:
        lw_xas = xl.AtomicLevelWidth(elm[1], getattr(xl, ln[2]+'_SHELL'))*1000
        lw_xes = xl.AtomicLevelWidth(elm[1], getattr(xl, ln[3]+'_SHELL'))*1000
        if showInfos:
            print('{0} {1} (={2}): XAS={3:.2f} eV, XES={4:.2f} eV'.format(elm[0], line, ln[1], lw_xas, lw_xes))
        if herfd is True:
            return 1./(math.sqrt(lw_xas**2 + lw_xes**2))
        else:
            return lw_xas + lw_xes
    except:
        return 0

def fluo_amplitude(elem, line, excitation=None, barn_unit=False):
    """get the fluorescence cross section for given element/line

    Parameters
    ==========

    elem : string or number
           element
    
    line : string
           emission line Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')

    excitation : float [None]
                 excitation energy in eV

    barn_unit : boolean [False]

    Returns
    =======

    fluo_amp (in 'cm2/g' or 'barn/atom' if barn_unit is True)

    """
    if excitation is None:
        _logger.warning("excitation energy not given, using 10 keV")
        excitation = 10.
    #guess if eV or keV
    elif excitation >= 200.:
        excitation /= 1000
    else:
        _logger.warning("excitation energy given in keV")
    el_n = get_element(elem)[1]
    if barn_unit:
        CSfluo = xl.CSb_FluorLine_Kissel_Cascade
    else:
        CSfluo = xl.CS_FluorLine_Kissel_Cascade
    try:
        fluo_amp = CSfluo(el_n, getattr(xl, line+'_LINE'), excitation)
    except:
        _logger.error("line is wrong")
        fluo_amp = 0
    return fluo_amp

def xray_line(element, line=None, initial_level=None):
    """get the energy in eV for a given element/line or level

    :param element: string or number
    :param line: string, Siegbahn notation, e.g. 'KA1' [None]
    :param initial_level: string, initial core level, e.g. 'K' [None]
    :returns: dictionary {'line' : [], 'ene' : []} or a number
    
    """
    if HAS_XRAYLIB is False: _xraylib_error(0)
    el_n = get_element(element)[1]
    outdict = {'line' : [],
               'ene' : []}
    _retNum = False
    if (line is None) and (initial_level is not None):
        try:
            lines = [line for line in LINES if initial_level in line]
        except:
            _logger.error('initial_level is wrong')
    else:
        lines = [line]
        _retNum = True
    for _line in lines:
        try:
            line_ene = xl.LineEnergy(el_n, getattr(xl, _line+'_LINE'))*1000
            outdict['line'].append(_line)
            outdict['ene'].append(line_ene)
        except:
            _logger.error("line is wrong")
            continue
    if _retNum:
        return outdict['ene'][0]
    else:
        return outdict

def xray_edge(element, initial_level=None):
    """get the energy edge in eV for a given element

    :param element: string or number
    :param initial_level: string, initial core level, e.g. 'K' or list [None]
    :returns: dictionary {'edge' : [], 'ene' : []} or a number
    
    """
    if HAS_XRAYLIB is False: _xraylib_error(0)
    el_n = get_element(element)[1]
    outdict = {'edge' : [],
               'ene' : []}
    _retNum = False
    if initial_level is None:
        initial_level = SHELLS
    if (type(initial_level) == str):
        initial_level = [initial_level, ]
        _retNum = True
    else:
        _logger.error('initial_level is wrong')
    for _level in initial_level:
        try:
            edge_ene = xl.EdgeEnergy(el_n, getattr(xl, _level+'_SHELL'))*1000
            outdict['edge'].append(_level)
            outdict['ene'].append(edge_ene)
        except:
            _logger.warning("{0} {1} edge unknown".format(get_element(element)[0], _level))
            continue
    if _retNum:
        return outdict['ene'][0]
    else:
        return outdict

def fluo_spectrum(elem, line, xwidth=3, xstep=0.05,\
                  plot=False, showInfos=True, **kws):
    """generate a fluorescence spectrum for a given element/line

    .. note:: it generates a Lorentzian function with the following parameters:
              - center: emission energy (eV)
              - sigma: from FWHM of sum of atomic levels widths (XAS+XES)
              - amplitude: CS_FuorLine_Kissel_Cascade
              - xmin, xmax: center -+ xwidth*fwhm

    Parameters
    ==========

    elem : string or int

    line : string
           emission line Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')

    xwidth : int or float [3]
             multiplication factor to establish xmin, xmax (= center -+ xwidth*fwhm)

    xstep : float [0.05]
            energy step in eV

    showInfos : boolean [True]
                print the `info` dict
    
    plot : boolean [False]
           plot the line before returning it

    **kws : keyword arguments for :func:`fluo_width`, :func:`fluo_amplitude`

    Returns
    =======

    xfluo, yfluo, info : XY arrays of floats, dictionary

    """
    el = get_element(elem)
    exc = kws.get('excitation', 10000.)
    bu = kws.get('barn_unit', False)
    if bu is True:
        yunit = 'barn/atom'
    else:
        yunit = 'cm2/g'
    fwhm = fluo_width(elem, line, showInfos=showInfos)
    amp = fluo_amplitude(el[1], line, excitation=exc, barn_unit=bu)
    cen = xl.LineEnergy(el[1], getattr(xl, line+'_LINE'))*1000
    if (fwhm == 0) or (amp == 0) or (cen == 0):
        raise NameError('no line found')
    sig = fwhm2sigma(fwhm)
    xmin = cen - xwidth*fwhm
    xmax = cen + xwidth*fwhm
    xfluo = np.arange(xmin, xmax, xstep)
    yfluo = lorentzian(xfluo, amplitude=amp, center=cen, sigma=sig)
    info = {'el'    : el[0],
            'eln'   : el[1],
            'ln'    : line,
            'exc'   : exc,
            'cen'   : cen,
            'fwhm'  : fwhm,
            'amp'   : amp,
            'yunit' : yunit}
    legend = '{eln} {ln}'.format(**info)
    if showInfos:
        print('Lorentzian => cen: {cen:.3f} eV, amp: {amp:.3f} {yunit}, fwhm: {fwhm:.3f} eV'.format(**info))
    if plot and HAS_SILX:
        p1 = Plot1D()
        p1.addCurve(xfluo, yfluo, legend=legend, replace=True,\
                    xlabel='energy (eV)', ylabel='intensity ({0})'.format(yunit))
        p1.show()
        input('PRESS ENTER to close the plot window and return')
    return xfluo, yfluo, info
    
def fluo_lines(elem, lines, **fluokws):
    """generate the emission spectrum of a given element and list of lines

    Parameters
    ==========

    elem : string or int

    lines : list of strings
            emission lines as Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')

    **fluokws : keyword arguments for :func:`fluo_spectrum`

    Returns
    =======

    xcom, ycom : arrays of floats
                 energy/intensity of the whole spectrum

    """
    plot = fluokws.get('plot', False)
    xstep = fluokws.get('xstep', 0.05)
    fluokws.update({'plot': False})
    xi, yi, ii = [], [], []
    for ln in lines:
        try:
            x, y, i = fluo_spectrum(elem, ln, **fluokws)
            xi.append(x)
            yi.append(y)
            ii.append(i)
        except:
            print("INFO: no line found for {0}-{1}".format(elem, ln))
    xmin = min([x.min() for x in xi])
    xmax = max([x.max() for x in xi])
    xcom = np.arange(xmin, xmax, xstep)
    ycom = np.zeros_like(xcom)
    for x, y in zip(xi, yi):
        yinterp = np.interp(xcom, x, y)
        ycom += yinterp

    if plot and HAS_SILX:
        p = Plot1D()
        p.addCurve(xcom, ycom, legend='sum', color='black', replace=True,\
                   xlabel='energy (eV)', ylabel='intensity')
        for x, y, i in zip(xi, yi, ii):
            p.addCurve(x ,y, legend=i['ln'], replace=False,)
        p.show()
        
    return xcom, ycom


#############################
### LARCH-BASED FUNCTIONS ###
#############################

#xdb.function()
#--------------------------------------------------------------------------------
#function 	     : description
#--------------------:-----------------------------------------------------------
#atomic_number()     : atomic number from symbol
#atomic_symbol()     : atomic symbol from number
#atomic_mass() 	     : atomic mass
#atomic_density()    : atomic density (for pure element)
#xray_edge() 	     : xray edge data for a particular element and edge
#xray_line() 	     : xray emission line data for an element and line
#xray_edges() 	     : dictionary of all X-ray edges data for an element
#xray_lines() 	     : dictionary of all X-ray emission line data for an element
#fluo_yield() 	     : fluorescence yield and weighted line energy
#core_width() 	     : core level width for an element and edge
#                      (Keski-Rahkonen and Krause)
#mu_elam() 	     : absorption cross-section
#coherent_xsec()     : coherent cross-section
#incoherent_xsec()   : incoherent cross-section
#f0() 	             : elastic scattering factor (Waasmaier and Kirfel)
#f0_ions() 	     : list of valid “ions” for f0() (Waasmaier and Kirfel)
#chantler_energies() : energies of tabulation for Chantler data (Chantler)
#f1_chantler()       : f’ anomalous factor (Chantler)
#f2_chantler()       : f” anomalous factor (Chantler)
#mu_chantler()       : absorption cross-section (Chantler)
#xray_delta_beta()   : anomalous components of the index of refraction for a material
#f1f2_cl()           : f’ and f” anomalous factors (Cromer and Liberman)

#Table of X-ray Edge / Core electronic levels
# +-----+-----------------+-----+-----------------+-----+-----------------+
# |Name |electronic level |Name |electronic level |Name |electronic level |
# +=====+=================+=====+=================+=====+=================+
# | K   |    1s           | N7  |    4f7/2        | O3  |     5p3/2       |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | L3  |    2p3/2        | N6  |    4f5/2        | O2  |     5p1/2       |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | L2  |    2p1/2        | N5  |    4d5/2        | O1  |     5s          |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | L1  |    2s           | N4  |    4d3/2        | P3  |     6p3/2       |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | M5  |    3d5/2        | N3  |    4p3/2        | P2  |     6p1/2       |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | M4  |    3d3/2        | N2  |    4p1/2        | P1  |     6s          |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | M3  |    3p3/2        | N1  |    4s           |     |                 |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | M2  |    3p1/2        |     |                 |     |                 |
# +-----+-----------------+-----+-----------------+-----+-----------------+
# | M1  |    3s           |     |                 |     |                 |
# +-----+-----------------+-----+-----------------+-----+-----------------+

#Table of X-ray emission line names and the corresponding Siegbahn and IUPAC notations
# +--------+---------------------+--------+-----+----------+----------+
# | Name   | Siegbahn            | IUPAC  | Name| Siegbahn | IUPAC    |
# +========+=====================+========+=====+==========+==========+
# | Ka1    | K\alpha_1           | K-L3   | Lb4 | L\beta_4 | L1-M2    |
# +--------+---------------------+--------+-----+----------+----------+
# | Ka2    | K\alpha_2           | K-L2   | Lb5 | L\beta_5 | L3-O4,5  |
# +--------+---------------------+--------+-----+----------+----------+
# | Ka3    | K\alpha_3           | K-L1   | Lb6 | L\beta_6 | L3-N1    |
# +--------+---------------------+--------+-----+----------+----------+
# | Kb1    | K\beta_1            | K-M3   | Lg1 | L\gamma_1| L2-N4    |
# +--------+---------------------+--------+-----+----------+----------+
# | Kb2    | K\beta_2            | K-N2,3 | Lg2 | L\gamma_2| L1-N2    |
# +--------+---------------------+--------+-----+----------+----------+
# | Kb3    | K\beta_3            | K-M2   | Lg3 | L\gamma_3| L1-N3    |
# +--------+---------------------+--------+-----+----------+----------+
# | Kb4    | K\beta_2            | K-N4,5 | Lg6 | L\gamma_6| L2-O4    |
# +--------+---------------------+--------+-----+----------+----------+
# | Kb5    | K\beta_3            | K-M4,5 | Ll  | Ll       | L3-M1    |
# +--------+---------------------+--------+-----+----------+----------+
# | La1    | L\alpha_1           | L3-M5  | Ln  | L\nu     | L2-M1    |
# +--------+---------------------+--------+-----+----------+----------+
# | La2    | L\alpha_1           | L3-M4  | Ma  | M\alpha  | M5-N6,7  |
# +--------+---------------------+--------+-----+----------+----------+
# | Lb1    | L\beta_1            | L2-M4  | Mb  | M\beta   | M4-N6    |
# +--------+---------------------+--------+-----+----------+----------+
# | Lb2,15 | L\beta_2,L\beta_{15}| L3-N4,5| Mg  | M\gamma  | M3-N5    |
# +--------+---------------------+--------+-----+----------+----------+
# | Lb3    | L\beta_3            | L1-M3  | Mz  | M\zeta   | M4,5-N6,7|
# +--------+---------------------+--------+-----+----------+----------+


if __name__ == '__main__':
    # see tests/examples in xdata_tests.py
    pass


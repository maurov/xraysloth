#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utility to retrieve x-ray data from external libraries/databases
===================================================================

Available libraries/dbs and order of usage
------------------------------------------

1. `xraylib <https://github.com/tschoonj/xraylib>`_
2. ``Elements`` in `PyMca <https://github.com/vasole/pymca>`_
3. ``xraydb_plugin.py`` in `Larch <https://github.com/xraypy/xraylarch>`_

.. note:: `XrayDB <https://github.com/xraypy/XrayDB>`_ has its own package now

"""
import math
import numpy as np

try:
    from PyMca5.PyMcaPhysics.xrf.Elements import Element

    HAS_PYMCA = True
except ImportError:
    HAS_PYMCA = False
    ELEMENTS_DICT = None
    pass

try:
    import xraylib as xl

    #xl.SetErrorMessages(0)  #: disable showing error messages // DEPRECATED since xraylib 4.1.1
    HAS_XRAYLIB = True
except ImportError:
    HAS_XRAYLIB = False
    pass

try:
    import xraydb
    HAS_XRAYDB = True
except ImportError:
    HAS_XRAYDB = False
    pass

from sloth.bragg import findhkl

from sloth.math.lineshapes import lorentzian, fwhm2sigma

#: MODULE LOGGER
from .logging import getLogger

_LOGGER = getLogger("sloth.utils.xdata", level="INFO")

#: ERROR MESSAGES


def _larch_error(ret=None):
    """Log a missing larch error message and return given 'ret'"""
    _LOGGER.error("Larch not found")
    return ret


def _xraylib_error(ret=None):
    """Log a missing xraylib error message and return given 'ret'"""
    _LOGGER.error("Xraylib not found")
    return ret


def _pymca_error(ret=None):
    """Log a missing PyMca5 error message and return given 'ret'"""
    _LOGGER.error("PyMca5 not found")
    return ret


def _xraydb_error(ret=None):
    """Log a missing XrayDB error message and return given 'ret'"""
    _LOGGER.error("XrayDB not found")
    return ret


#######################
#: ELEMENTS AND LINES #
#######################

#: Taken from PyMca5/PyMcaPhysics/xrf/Elements.py
#
#   Symbol  Atomic Number   x y ( positions on table )
#       name,  mass, density
#
ELEMENTS_INFO = (
    ("H", 1, 1, 1, "hydrogen", 1.00800, 0.08988),
    ("He", 2, 18, 1, "helium", 4.00300, 0.17860),
    ("Li", 3, 1, 2, "lithium", 6.94000, 534.000),
    ("Be", 4, 2, 2, "beryllium", 9.01200, 1848.00),
    ("B", 5, 13, 2, "boron", 10.8110, 2340.00),
    ("C", 6, 14, 2, "carbon", 12.0100, 1580.00),
    ("N", 7, 15, 2, "nitrogen", 14.0080, 1.25000),
    ("O", 8, 16, 2, "oxygen", 16.0000, 1.42900),
    ("F", 9, 17, 2, "fluorine", 19.0000, 1108.00),
    ("Ne", 10, 18, 2, "neon", 20.1830, 0.90020),
    ("Na", 11, 1, 3, "sodium", 22.9970, 970.000),
    ("Mg", 12, 2, 3, "magnesium", 24.3200, 1740.00),
    ("Al", 13, 13, 3, "aluminium", 26.9700, 2720.00),
    ("Si", 14, 14, 3, "silicon", 28.0860, 2330.00),
    ("P", 15, 15, 3, "phosphorus", 30.9750, 1820.00),
    ("S", 16, 16, 3, "sulphur", 32.0660, 2000.00),
    ("Cl", 17, 17, 3, "chlorine", 35.4570, 1560.00),
    ("Ar", 18, 18, 3, "argon", 39.9440, 1.78400),
    ("K", 19, 1, 4, "potassium", 39.1020, 862.000),
    ("Ca", 20, 2, 4, "calcium", 40.0800, 1550.00),
    ("Sc", 21, 3, 4, "scandium", 44.9600, 2992.00),
    ("Ti", 22, 4, 4, "titanium", 47.9000, 4540.00),
    ("V", 23, 5, 4, "vanadium", 50.9420, 6110.00),
    ("Cr", 24, 6, 4, "chromium", 51.9960, 7190.00),
    ("Mn", 25, 7, 4, "manganese", 54.9400, 7420.00),
    ("Fe", 26, 8, 4, "iron", 55.8500, 7860.00),
    ("Co", 27, 9, 4, "cobalt", 58.9330, 8900.00),
    ("Ni", 28, 10, 4, "nickel", 58.6900, 8900.00),
    ("Cu", 29, 11, 4, "copper", 63.5400, 8940.00),
    ("Zn", 30, 12, 4, "zinc", 65.3800, 7140.00),
    ("Ga", 31, 13, 4, "gallium", 69.7200, 5903.00),
    ("Ge", 32, 14, 4, "germanium", 72.5900, 5323.00),
    ("As", 33, 15, 4, "arsenic", 74.9200, 5730.00),
    ("Se", 34, 16, 4, "selenium", 78.9600, 4790.00),
    ("Br", 35, 17, 4, "bromine", 79.9200, 3120.00),
    ("Kr", 36, 18, 4, "krypton", 83.8000, 3.74000),
    ("Rb", 37, 1, 5, "rubidium", 85.4800, 1532.00),
    ("Sr", 38, 2, 5, "strontium", 87.6200, 2540.00),
    ("Y", 39, 3, 5, "yttrium", 88.9050, 4405.00),
    ("Zr", 40, 4, 5, "zirconium", 91.2200, 6530.00),
    ("Nb", 41, 5, 5, "niobium", 92.9060, 8570.00),
    ("Mo", 42, 6, 5, "molybdenum", 95.9500, 10220.0),
    ("Tc", 43, 7, 5, "technetium", 99.0000, 11500.0),
    ("Ru", 44, 8, 5, "ruthenium", 101.0700, 12410.0),
    ("Rh", 45, 9, 5, "rhodium", 102.9100, 12440.0),
    ("Pd", 46, 10, 5, "palladium", 106.400, 12160.0),
    ("Ag", 47, 11, 5, "silver", 107.880, 10500.0),
    ("Cd", 48, 12, 5, "cadmium", 112.410, 8650.00),
    ("In", 49, 13, 5, "indium", 114.820, 7280.00),
    ("Sn", 50, 14, 5, "tin", 118.690, 5310.00),
    ("Sb", 51, 15, 5, "antimony", 121.760, 6691.00),
    ("Te", 52, 16, 5, "tellurium", 127.600, 6240.00),
    ("I", 53, 17, 5, "iodine", 126.910, 4940.00),
    ("Xe", 54, 18, 5, "xenon", 131.300, 5.90000),
    ("Cs", 55, 1, 6, "caesium", 132.910, 1873.00),
    ("Ba", 56, 2, 6, "barium", 137.360, 3500.00),
    ("La", 57, 3, 6, "lanthanum", 138.920, 6150.00),
    ("Ce", 58, 4, 9, "cerium", 140.130, 6670.00),
    ("Pr", 59, 5, 9, "praseodymium", 140.920, 6769.00),
    ("Nd", 60, 6, 9, "neodymium", 144.270, 6960.00),
    ("Pm", 61, 7, 9, "promethium", 147.000, 6782.00),
    ("Sm", 62, 8, 9, "samarium", 150.350, 7536.00),
    ("Eu", 63, 9, 9, "europium", 152.000, 5259.00),
    ("Gd", 64, 10, 9, "gadolinium", 157.260, 7950.00),
    ("Tb", 65, 11, 9, "terbium", 158.930, 8272.00),
    ("Dy", 66, 12, 9, "dysprosium", 162.510, 8536.00),
    ("Ho", 67, 13, 9, "holmium", 164.940, 8803.00),
    ("Er", 68, 14, 9, "erbium", 167.270, 9051.00),
    ("Tm", 69, 15, 9, "thulium", 168.940, 9332.00),
    ("Yb", 70, 16, 9, "ytterbium", 173.040, 6977.00),
    ("Lu", 71, 17, 9, "lutetium", 174.990, 9842.00),
    ("Hf", 72, 4, 6, "hafnium", 178.500, 13300.0),
    ("Ta", 73, 5, 6, "tantalum", 180.950, 16600.0),
    ("W", 74, 6, 6, "tungsten", 183.920, 19300.0),
    ("Re", 75, 7, 6, "rhenium", 186.200, 21020.0),
    ("Os", 76, 8, 6, "osmium", 190.200, 22500.0),
    ("Ir", 77, 9, 6, "iridium", 192.200, 22420.0),
    ("Pt", 78, 10, 6, "platinum", 195.090, 21370.0),
    ("Au", 79, 11, 6, "gold", 197.200, 19370.0),
    ("Hg", 80, 12, 6, "mercury", 200.610, 13546.0),
    ("Tl", 81, 13, 6, "thallium", 204.390, 11860.0),
    ("Pb", 82, 14, 6, "lead", 207.210, 11340.0),
    ("Bi", 83, 15, 6, "bismuth", 209.000, 9800.00),
    ("Po", 84, 16, 6, "polonium", 209.000, 0),
    ("At", 85, 17, 6, "astatine", 210.000, 0),
    ("Rn", 86, 18, 6, "radon", 222.000, 9.73000),
    ("Fr", 87, 1, 7, "francium", 223.000, 0),
    ("Ra", 88, 2, 7, "radium", 226.000, 0),
    ("Ac", 89, 3, 7, "actinium", 227.000, 0),
    ("Th", 90, 4, 10, "thorium", 232.000, 11700.0),
    ("Pa", 91, 5, 10, "proactinium", 231.03588, 0),
    ("U", 92, 6, 10, "uranium", 238.070, 19050.0),
    ("Np", 93, 7, 10, "neptunium", 237.000, 0),
    ("Pu", 94, 8, 10, "plutonium", 239.100, 19700.0),
    ("Am", 95, 9, 10, "americium", 243, 0),
    ("Cm", 96, 10, 10, "curium", 247, 0),
    ("Bk", 97, 11, 10, "berkelium", 247, 0),
    ("Cf", 98, 12, 10, "californium", 251, 0),
    ("Es", 99, 13, 10, "einsteinium", 252, 0),
    ("Fm", 100, 14, 10, "fermium", 257, 0),
    ("Md", 101, 15, 10, "mendelevium", 258, 0),
    ("No", 102, 16, 10, "nobelium", 259, 0),
    ("Lr", 103, 17, 10, "lawrencium", 262, 0),
    ("Rf", 104, 4, 7, "rutherfordium", 261, 0),
    ("Db", 105, 5, 7, "dubnium", 262, 0),
    ("Sg", 106, 6, 7, "seaborgium", 266, 0),
    ("Bh", 107, 7, 7, "bohrium", 264, 0),
    ("Hs", 108, 8, 7, "hassium", 269, 0),
    ("Mt", 109, 9, 7, "meitnerium", 268, 0),
)
ELEMENTS = [elt[0] for elt in ELEMENTS_INFO]
ELEMENTS_N = [elt[1] for elt in ELEMENTS_INFO]

#: SHELLS / EDGES
#: K = 1 (s)
#: L = 2 (s, p)
#: M = 3 (s, p, d)
#: N = 4 (s, p, d, f)
#: O = 5 (s, p, d, f)
#: P = 6 (s, p)
SHELLS = (
    "K",  # 0
    "L1",
    "L2",
    "L3",  # 1, 2, 3
    "M1",
    "M2",
    "M3",
    "M4",
    "M5",  # 4, 5, 6, 7, 8
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
    "N6",
    "N7",  # 9, 10, 11, 12, 13, 14, 15
    "O1",
    "O2",
    "O3",
    "O4",
    "O5",  # 16, 17, 18, 19, 20
    "P1",
    "P2",
    "P3",
)  # 21, 22, 23

#: TRANSITIONS
#: 1 = s
#: 2, 3 = p (1/2, 3/2)
#: 4, 5 = d (3/2, 5/2)
#: 6, 7 = f (5/2, 7/2)
LEVELS_DICT = {
    "K": "1s",
    "L1": "2s",
    "L2": "2p1/2",
    "L3": "2p3/2",
    "M1": "3s",
    "M2": "3p1/2",
    "M3": "3p3/2",
    "M4": "3d3/2",
    "M5": "3d5/2",
    "N1": "4s",
    "N2": "4p1/2",
    "N3": "4p3/2",
    "N4": "4d3/2",
    "N5": "4d5/2",
    "N6": "4f5/2",
    "N7": "4f7/2",
    "O1": "5s",
    "O2": "5p1/2",
    "O3": "5p3/2",
    "P1": "6s",
    "P2": "6p1/2",
    "P3": "6p3/2",
}

#: dictionary of lines
#: Ln in Hepheastus is LE in Xraylib
#: Mz in Hepheastus not in Xraylib (the single transitions yes!)
LINES_DICT = {
    "K": (
        "KA1",
        "KA2",
        "KA3",  # LINES[0, 1, 2]
        "KB1",
        "KB2",
        "KB3",
        "KB4",
        "KB5",
    ),  # LINES[3, 4, 5, 6, 7]
    "L1": ("LB3", "LB4", "LG2", "LG3"),  # LINES[8, 9, 10, 11]
    "L2": ("LB1", "LG1", "LG6", "LE"),  # LINES[12, 13, 14, 15]
    #: LINES[16, 17, 18, 19, 20, 21]
    "L3": ("LA1", "LA2", "LB2", "LB5", "LB6", "LL"),
    "M3": ("MG",),  # LINES[22]
    "M4": ("MB",),  # LINES[23]
    "M5": ("MA1", "MA2"),
}  # LINES[24, 25]
LINES_K = LINES_DICT["K"]
LINES_L = LINES_DICT["L1"] + LINES_DICT["L2"] + LINES_DICT["L3"]
LINES_M = LINES_DICT["M3"] + LINES_DICT["M4"] + LINES_DICT["M5"]
LINES = LINES_K + LINES_L + LINES_M
#
TRANS_DICT = {
    "K": ("KL3", "KL2", "KL1", "KM3", "KN3", "KM2", "KN5", "KM5"),
    "L1": ("L1M3", "L1M2", "L1N2", "L1N3"),
    "L2": ("L2M4", "L2N4", "L2O4", "L2M1"),
    "L3": ("L3M5", "L3M4", "L3N5", "L304", "L3N1", "L3M1"),
    "M3": ("M3N5",),
    "M4": ("M4N6",),
    "M5": ("M5N7", "M5N6"),
}
TRANS_K = TRANS_DICT["K"]
TRANS_L = TRANS_DICT["L1"] + TRANS_DICT["L2"] + TRANS_DICT["L3"]
TRANS_M = TRANS_DICT["M3"] + TRANS_DICT["M4"] + TRANS_DICT["M5"]
TRANSITIONS = TRANS_K + TRANS_L + TRANS_M
#: INDEX DICTIONARY: KEYS=LINES : VALUES=(LINES[IDX],\
#                                         SHELLS[IDX_XAS], SHELLS[IDX_XES])
LINES2TRANS = {
    "KA1": (0, 0, 3),
    "KA2": (1, 0, 2),
    "KA3": (2, 0, 1),
    "KB1": (3, 0, 6),
    "KB2": (4, 0, 11),
    "KB3": (5, 0, 5),
    "KB4": (6, 0, 13),
    "KB5": (7, 0, 8),
    "LB3": (8, 1, 6),
    "LB4": (9, 1, 5),
    "LG2": (10, 1, 10),
    "LG3": (11, 1, 11),
    "LB1": (12, 2, 7),
    "LG1": (13, 2, 12),
    "LG6": (14, 2, 19),
    "LE": (15, 2, 4),
    "LA1": (16, 3, 8),
    "LA2": (17, 3, 7),
    "LB2": (18, 3, 13),
    "LB5": (19, 3, 19),  # WARNING: here is only O4
    "LB6": (20, 3, 9),
    "LL": (21, 3, 4),
    "MG": (22, 6, 13),
    "MB": (23, 7, 14),
    "MA1": (24, 8, 15),
    "MA2": (25, 8, 14),
}


def mapLine2Trans(line):
    """returns a tuple of strings mapping the transitions for a given line"""
    try:
        idx = LINES2TRANS[line]
        return (LINES[idx[0]], TRANSITIONS[idx[0]], SHELLS[idx[1]], SHELLS[idx[2]])
    except KeyError:
        _LOGGER.error("Line {0} not known; returning 0".format(line))
        return 0


############################
#: XRAYLIB-BASED FUNCTIONS #
############################


def get_element(elem):
    """get a tuple of information for a given element"""
    _errstr = f"Element {elem} not known!"
    if (isinstance(elem, str) and (elem in ELEMENTS)):
        return [elt for elt in ELEMENTS_INFO if elt[0] == elem][0]
    if (isinstance(elem, int) and (elem in ELEMENTS_N)):
        return [elt for elt in ELEMENTS_INFO if elt[1] == elem]
    _LOGGER.error(_errstr)
    raise NameError(_errstr)


def get_line(line):
    """Check the line name is a valid name and return it"""
    if line not in LINES:
        _errstr = f"Line {line} is not a valid name in Siegbahn notation"
        _LOGGER.error(_errstr)
        raise NameError(_errstr)
    return line


def find_edge(emin, emax, shells=None):
    """Get the edge energy in a given energy range [emin, emax] (eV)

    Parameters
    ----------
    emin, emax : floats
        energy range to search for an absorption edege (eV)
    shells : list of str (optional)
        list of shells to search for [None -> use SHELLS (=all)]
    """
    if HAS_XRAYLIB is False:
        _xraylib_error(0)
    if shells is None:
        shells = SHELLS
    for el in ELEMENTS:
        eln = get_element(el)
        for sh in shells:
            edge = (xl.EdgeEnergy(eln[1], getattr(xl, sh + "_SHELL")) * 1000)
            if (edge >= emin) and (edge <= emax):
                _LOGGER.info("{0} \t {1} \t {2:>.2f} eV".format(el, sh, edge))


def find_line(emin, emax, elements=None, lines=None, outDict=False, backend="xraylib", skip_zero_width=True):
    """Get the emission line energy in a given energy range [emin,emax] (eV)

    Parameters
    ----------
    emin, emax : float
        [minimum, maximum] energy range (eV)
    elements : list of str (optional)
        list of elements, [None -> ELEMENTS (all)]
    lines : list of str (optional)
        list of lines, [None -> LINES (all)]
    outDict : boolean, False
        returns a dictionary instead of printing to screen
    skip_zero_width : boolean, True
        True: if fluo_width == 0, not include in the results

    Returns
    -------
    None or outDict
        if outDict:
            _out['el']: element symbol, list of strs
            _out['eln]: element number, list of ints
            _out['ln']: line, list of strs
            _out['en']: energy eV, list of floats
            _out['w'] : width eV, list of floats
        else:
            prints to screen the results
    """
    if backend == "pymca" and (not HAS_PYMCA):
        _pymca_error()
        backend = "xraylib"
        _LOGGER.warning("Changed backend to %s", backend)
    if backend == "xraylib" and (not HAS_XRAYLIB):
        _xraylib_error()
        _LOGGER.error("No backend available!")
        return None
    if lines is None:
        lines = LINES
    if elements is None:
        elements = ELEMENTS
    _out = {}
    _out["el"] = []
    _out["eln"] = []
    _out["ln"] = []
    _out["en"] = []
    _out["w"] = []
    for el in elements:
        eln = get_element(el)
        for ln in lines:
            try:
                if backend == "pymca":
                    line = Element[eln[0]][mapLine2Trans(ln)[1]]["energy"] * 1000
                else:
                    line = xl.LineEnergy(eln[1], getattr(xl, ln + "_LINE")) * 1000
            except Exception:
                _LOGGER.debug("{0}.{1} none".format(el, ln))
                continue
            if (line >= emin) and (line <= emax):
                w = fluo_width(elem=el, line=ln, showInfos=False)
                if w == 0:
                    _LOGGER.warning(f"{el}.{ln} zero width")
                    if skip_zero_width:
                        _LOGGER.info(f"{el}.{ln} skipped")
                        continue
                _out["el"].append(eln[0])
                _out["eln"].append(eln[1])
                _out["ln"].append(ln)
                _out["en"].append(line)
                _out["w"].append(w)
    #: returns
    if outDict:
        return _out
    else:
        for eln, el, ln, line, w in zip(
            _out["eln"], _out["el"], _out["ln"], _out["en"], _out["w"]
        ):
            _LOGGER.info(f"{eln} {el} {ln} {line:>.3f} {w:>.2f}")


def ene_res(emin, emax, shells=["K"]):
    """ used in spectro.py """
    if HAS_XRAYLIB is False:
        _xraylib_error(0)
    s = {}
    s["el"] = []
    s["en"] = []
    s["edge"] = []
    s["ch"] = []
    s["dee"] = []
    for el in ELEMENTS:
        eln = get_element(el)
        for sh in shells:
            edge = (xl.EdgeEnergy(eln[1], getattr(xl, sh + "_SHELL")) * 1000)
            ch = (xl.AtomicLevelWidth(eln[1], getattr(xl, sh + "_SHELL")) * 1000)
            if (edge >= emin) and (edge <= emax):
                s["el"].append(el)
                s["en"].append(xl.SymbolToAtomicNumber(el))
                s["edge"].append(edge)
                s["ch"].append(ch)
                s["dee"].append(ch / edge)
    return s


def fluo_width(elem=None, line=None, herfd=False, showInfos=True):
    """Get the fluorescence line width in eV

    Parameters
    ----------
    elem : string or int
        absorbing element
    line : string
        Siegbahn notation for emission line

    Returns
    -------
    herfd=False (default): lw_xas + lw_xes
    herfd=True: 1/(math.sqrt(lw_xas**2 + lw_xes**2))

    """
    if HAS_XRAYLIB is False:
        _xraylib_error(0)
    if (elem is None) or (line is None):
        _LOGGER.error("element or edge not given, returning 0")
        return 0
    elm = get_element(elem)
    ln = mapLine2Trans(line)
    try:
        lw_xas = xl.AtomicLevelWidth(elm[1], getattr(xl, ln[2] + "_SHELL")) * 1000
        lw_xes = xl.AtomicLevelWidth(elm[1], getattr(xl, ln[3] + "_SHELL")) * 1000
        lw_herfd = 1.0 / (math.sqrt(lw_xas ** 2 + lw_xes ** 2))
        if showInfos:
            ln_ev = xl.LineEnergy(elm[1], getattr(xl, line + "_LINE")) * 1000
            _LOGGER.info(f"{elm[0]} {line} (={ln[1]}): {ln_ev:.2f} eV")
            _LOGGER.info(
                f"Atomic levels widths: XAS={lw_xas:.2f} eV, XES={lw_xes:.2f} eV"
            )
            _LOGGER.info(f"... -> STD={lw_xas+lw_xes:.2f} eV, HERFD={lw_herfd:.2f} eV]")
        if herfd is True:
            return lw_herfd
        else:
            return lw_xas + lw_xes
    except Exception:
        return 0


def fluo_amplitude(elem, line, excitation=None, barn_unit=False):
    """Get the fluorescence cross section for a given element/line

    Parameters
    ----------
    elem : string or number
        element
    line : string
        emission line Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')
    excitation : float (optional)
        excitation energy in eV [None -> 10 keV]
    barn_unit : boolean
        use units of barn/atom [None -> cm2/g]

    Returns
    -------
    fluo_amp (in 'cm2/g' or 'barn/atom' if barn_unit is True)

    """
    if excitation is None:
        _LOGGER.warning("Excitation energy not given, using 10 keV")
        excitation = 10.0
    #: guess if eV or keV
    elif excitation >= 200.0:
        excitation /= 1000
    _LOGGER.info(f"Excitation energy is {excitation} keV")
    el_n = get_element(elem)[1]
    if barn_unit:
        CSfluo = xl.CSb_FluorLine_Kissel_Cascade
    else:
        CSfluo = xl.CS_FluorLine_Kissel_Cascade
    try:
        fluo_amp = CSfluo(el_n, getattr(xl, line + "_LINE"), excitation)
    except Exception:
        _LOGGER.warning("Line not known")
        fluo_amp = 0
    return fluo_amp


def xray_line(element, line=None, initial_level=None):
    """Get the emission energy in eV for a given element/line or level

    Parameters
    ----------
    element : string or int
        absorbing element
    line: string (optional)
        Siegbahn notation, e.g. 'KA1' [None -> LINES (all)]
    initial_level: string
        initial core level, e.g. 'K' [None]

    Returns
    -------
    dictionary {'line': [], 'ene': []} or a number

    """
    if HAS_XRAYLIB is False:
        _xraylib_error(0)
    el_n = get_element(element)[1]
    outdict = {"line": [], "ene": []}
    _retNum = False
    if (line is None) and (initial_level is not None):
        try:
            lines = [line for line in LINES if initial_level in line]
        except Exception:
            _LOGGER.error("initial_level is wrong")
    else:
        lines = [line]
        _retNum = True
    for _line in lines:
        try:
            line_ene = xl.LineEnergy(el_n, getattr(xl, _line + "_LINE")) * 1000
            outdict["line"].append(_line)
            outdict["ene"].append(line_ene)
        except Exception:
            _LOGGER.error("line is wrong")
            continue
    if _retNum:
        return outdict["ene"][0]
    else:
        return outdict


def xray_edge(element, initial_level=None):
    """Get the energy edge in eV for a given element

    :param element: string or number
    :param initial_level: string, initial core level, e.g. 'K' or list [None]
    :returns: dictionary {'edge' : [], 'ene' : []} or a number

    """
    if HAS_XRAYLIB is False:
        _xraylib_error(0)
    el_n = get_element(element)[1]
    outdict = {"edge": [], "ene": []}
    _retNum = False
    if initial_level is None:
        initial_level = SHELLS
    if type(initial_level) == str:
        initial_level = [initial_level]
        _retNum = True
    else:
        _LOGGER.error("initial_level is wrong")
    for _level in initial_level:
        try:
            edge_ene = xl.EdgeEnergy(el_n, getattr(xl, _level + "_SHELL")) * 1000
            outdict["edge"].append(_level)
            outdict["ene"].append(edge_ene)
        except Exception:
            _LOGGER.warning(
                "{0} {1} edge unknown".format(get_element(element)[0], _level)
            )
            continue
    if _retNum:
        return outdict["ene"][0]
    else:
        return outdict


def fluo_spectrum(elem, line, xwidth=3, xstep=0.05, plot=False, showInfos=True, **kws):
    """Generate a fluorescence spectrum for a given element/line

    .. note:: it generates a Lorentzian function with the following parameters:
              - center: emission energy (eV)
              - sigma: from FWHM of sum of atomic levels widths (XAS+XES)
              - amplitude: CS_FuorLine_Kissel_Cascade
              - xmin, xmax: center -+ xwidth*fwhm

    Parameters
    ----------
    elem : string or int
        absorbing element
    line : string
        emission line Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')
    xwidth : int or float (optional)
        FWHM multiplication factor to establish xmin, xmax range
        (= center -+ xwidth*fwhm) [3]
    xstep : float (optional)
        energy step in eV [0.05]
    showInfos : boolean (optional)
        print the `info` dict [True]
    plot : boolean (optional)
        plot the line before returning it [False]
    **kws : keyword arguments for :func:`fluo_width`, :func:`fluo_amplitude`

    Returns
    -------
    xfluo, yfluo, info : XY arrays of floats, dictionary

    """
    el = get_element(elem)
    exc = kws.get("excitation", 10000.0)
    bu = kws.get("barn_unit", False)
    if bu is True:
        yunit = "barn/atom"
    else:
        yunit = "cm2/g"
    fwhm = fluo_width(elem, line, showInfos=showInfos)
    amp = fluo_amplitude(el[1], line, excitation=exc, barn_unit=bu)
    cen = xl.LineEnergy(el[1], getattr(xl, line + "_LINE")) * 1000
    if (fwhm == 0) or (amp == 0) or (cen == 0):
        raise NameError("no line found")
    sig = fwhm2sigma(fwhm)
    xmin = cen - xwidth * fwhm
    xmax = cen + xwidth * fwhm
    xfluo = np.arange(xmin, xmax, xstep)
    yfluo = lorentzian(xfluo, amplitude=amp, center=cen, sigma=sig)
    info = {
        "el": el[0],
        "eln": el[1],
        "ln": line,
        "exc": exc,
        "cen": cen,
        "fwhm": fwhm,
        "amp": amp,
        "yunit": yunit,
    }
    legend = "{eln} {ln}".format(**info)
    if showInfos:
        _LOGGER.info(
            "Lorentzian => cen: {cen:.3f} eV, amp: {amp:.3f} {yunit}, fwhm: {fwhm:.3f} eV".format(
                **info
            )
        )
    if plot:
        from sloth.gui.plot.plot1D import Plot1D

        p1 = Plot1D()
        p1.addCurve(
            xfluo,
            yfluo,
            legend=legend,
            replace=True,
            xlabel="energy (eV)",
            ylabel="intensity ({0})".format(yunit),
        )
        p1.show()
        input("PRESS ENTER to close the plot window and return")
    return xfluo, yfluo, info


def fluo_lines(elem, lines, retAll=False, **fluokws):
    """Generate a cumulative emission spectrum of a given element and
    list of lines

    Parameters
    ----------
    elem : string or int
    lines : list of str
        emission lines as Siegban (e.g. 'LA1') or IUPAC (e.g. 'L3M5')
    **fluokws : keyword arguments for :func:`fluo_spectrum`

    Returns
    -------
    xcom, ycom : arrays of floats
        energy/intensity of the whole spectrum
    if retAll:
        xcom, ycom, [xi, yi, ii]
    """
    plot = fluokws.get("plot", False)
    xstep = fluokws.get("xstep", 0.05)
    fluokws.update({"plot": False})
    xi, yi, ii = [], [], []
    for ln in lines:
        try:
            x, y, i = fluo_spectrum(elem, ln, **fluokws)
            xi.append(x)
            yi.append(y)
            ii.append(i)
        except Exception:
            _LOGGER.info("no line found for {0}-{1}".format(elem, ln))
    xmin = min([x.min() for x in xi])
    xmax = max([x.max() for x in xi])
    xcom = np.arange(xmin, xmax, xstep)
    ycom = np.zeros_like(xcom)
    for x, y in zip(xi, yi):
        yinterp = np.interp(xcom, x, y)
        ycom += yinterp

    if plot:
        from sloth.gui.plot.plot1D import Plot1D

        p = Plot1D()
        p.addCurve(
            xcom,
            ycom,
            legend="sum",
            color="black",
            replace=True,
            xlabel="energy (eV)",
            ylabel="intensity",
        )
        for x, y, i in zip(xi, yi, ii):
            p.addCurve(x, y, legend=i["ln"], replace=False)
        p.show()

    if retAll:
        return xcom, ycom, [xi, yi, ii]
    else:
        return xcom, ycom


##########################
#: LARCH-BASED FUNCTIONS #
##########################

#: xdb.function()
# -----------------------------------------------------------
#: function 	     : description
# --------------------:--------------------------------------
#: atomic_number()     : atomic number from symbol
#: atomic_symbol()     : atomic symbol from number
#: atomic_mass() 	     : atomic mass
#: atomic_density()    : atomic density (for pure element)
#: xray_edge() 	     : xray edge data for a particular element and edge
#: xray_line() 	     : xray emission line data for an element and line
#: xray_edges() 	     : dictionary of all X-ray edges data for an element
#: xray_lines() 	     : dictionary of all X-ray emission line data for an element
#: fluo_yield() 	     : fluorescence yield and weighted line energy
#: core_width() 	     : core level width for an element and edge
#:                       (Keski-Rahkonen and Krause)
#: mu_elam() 	     : absorption cross-section
#: coherent_xsec()     : coherent cross-section
#: incoherent_xsec()   : incoherent cross-section
#: f0() 	             : elastic scattering factor (Waasmaier and Kirfel)
#: f0_ions() 	     : list of valid “ions” for f0() (Waasmaier and Kirfel)
#: chantler_energies() : energies of tabulation for Chantler data (Chantler)
#: f1_chantler()       : f’ anomalous factor (Chantler)
#: f2_chantler()       : f” anomalous factor (Chantler)
#: mu_chantler()       : absorption cross-section (Chantler)
#: xray_delta_beta()   : anomalous components of the index of refraction for a material
#: f1f2_cl()           : f’ and f” anomalous factors (Cromer and Liberman)

#: Table of X-ray Edge / Core electronic levels
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

#: Table of X-ray emission line names and the corresponding Siegbahn and IUPAC notations
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


if __name__ == "__main__":
    # see tests/examples in xdata_tests.py
    pass

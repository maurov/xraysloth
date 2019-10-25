#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
spectro14: FAME-UHD (ESRF/BM16) X-ray emission spectrometer
===========================================================

"""

import math
import numpy as np

from sloth.utils.bragg import (
    HC,
    SI_ALAT,
    GE_ALAT,
    d_cubic,
    get_dspacing,
    kev2wlen,
    wlen2kev,
    kev2ang,
    ang2kev,
)


def calc_det_dzh(theta):
    """Calculate detector vertical offset of the top raw

    .. note:: formula taken from Table 2 on pag. 68 of CE document
              vol. 3 (Olivier Proux et al.), theta in deg

    """
    return 919.49 - 27.018 * theta + 0.26209 * theta ** 2 - 0.00083803 * theta ** 3


def calc_det_dzb(theta):
    """Calculate detector vertical offset of the bottom raw

    .. note:: formula taken from Table 2 on pag. 68 of CE document
              vol. 3 (Olivier Proux et al.), theta in deg

    """
    return -677.96 + 19.121 * theta - 0.17315 * theta ** 2 + 0.00049335 * theta ** 3


def calc_det_dz(theta):
    """Calc detector vertical offset from focus both rows"""
    return abs(calc_det_dzh(theta)) + abs(calc_det_dzb(theta))


def calc_pos_com(emi, d=0, r=0, dz=0, sz=0):
    """Get spectrometer positions for common axes

    Parameters
    ----------
    emi  : emission energy [keV]
    d    : analyser d-spacing [nm]
    r    : crystal bending radius (=diameter Rowland circle) [mm]
    dz   : offset in z from the central row [mm]
    sz   : offset in z of the sample from top table [mm]

    Returns
    -------
    dictionary with real motors positions

    {
        "xs"     : float, #horizontal position central row [mm]
        "zeq"    : float, #vertical position central row   [mm]
        "zd"     : float, #vertical position detector      [mm]
        "xh"     : float, #hor correction top row          [mm]
        "xb"     : float, #hor correction bottom row       [mm]
        "thetah" : float, #theta correction top row        [deg]
        "thetab" : float  #theta correction bottom row     [deg]
     }

    """
    _rtheta = kev2ang(emi, d, deg=False)
    _xs = r * math.sin(_rtheta) * math.sin(_rtheta)
    _zeq = r * math.sin(_rtheta) * math.cos(_rtheta)
    _zd = 2 * _zeq  # detector
    _rsth = r * math.sin(_rtheta)
    try:
        _xh = math.sqrt(_rsth ** 2 - (_zeq + dz) ** 2) - _xs
        _xb = math.sqrt(_rsth ** 2 - (_zeq - dz) ** 2) - _xs
        _thetah = math.degrees(
            math.atan((_zeq + dz) / (_xh + _xs)) + _rtheta - (math.pi / 2.0)
        )
        _thetab = math.degrees(
            math.atan((_zeq - dz) / (_xb + _xs)) + _rtheta - (math.pi / 2.0)
        )
    except Exception:
        _xh = 0.0
        _xb = 0.0
        _thetah = 0.0
        _thetab = 0.0

    _com_dict = {
        "xs": _xs,
        "zeq": _zeq + sz,
        "zd": _zd + sz,
        "xh": _xh,
        "xb": _xb,
        "thetah": _thetah,
        "thetab": _thetab,
    }

    return _com_dict


def calc_pos_mod(nmodule):
    """get positions per module

    """
    pass


def show_spectro_overview(theta, d=None, r=1000.0, dz=82.0, sz=500.0, retdict=False):
    """show an overview of the spectrometer geometry calculations"""

    if d is not None:
        ene = ang2kev(theta, d)
    else:
        ene = "no dspacing"
    rtheta = math.radians(theta)

    p = r * math.sin(rtheta)
    xs = r * math.sin(rtheta) ** 2
    zeq = r * math.sin(rtheta) * math.cos(rtheta)
    xsh = math.sqrt(p ** 2 - (zeq + dz) ** 2)
    xsb = math.sqrt(p ** 2 - (zeq - dz) ** 2)
    xh = xsh - xs
    xb = xsb - xs
    rth = math.acos(xsh / p) + rtheta - math.pi / 2.0
    rtb = math.acos(xsb / p) + rtheta - math.pi / 2.0
    th = math.degrees(rth)
    tb = math.degrees(rtb)

    #: using SolidWorks model v1804 (TODO: check!!!)
    xdb = 2 * zeq * math.sin(abs(rtb))
    zdb = xdb / math.tan(rtheta + rtb)

    dzh = calc_det_dzh(theta)
    dzb = calc_det_dzb(theta)

    dxh = dzh / math.tan(math.pi / 2.0 - rtheta)
    dxb = dzb / math.tan(math.pi / 2.0 - rtheta)

    # ADD SAMPLE Z OFFSET
    zd = zeq * 2 + sz
    zeq += sz

    outdict = {
        "theta": theta,
        "ene": ene,
        "r": r,
        "dz": dz,
        "sz": sz,
        "p": p,
        "xs": xs,
        "zeq": zeq,
        "zd": zd,
        "xh": xh,
        "th": th,
        "xb": xb,
        "tb": tb,
        "dzh": dzh,
        "dzb": dzb,
        "dxh": dxh,
        "dxb": dxb,
        "xdb": xdb,
        "zdb": zdb,
        "str_h": " top ",
        "str_b": " bottom ",
        "str_det": " DETECTOR ",
        "str_ana": " CRYSTALS TABLE ",
        "nl": "\n",
    }
    outstr = "\
============================{nl}\
SPECTRO14 POSITIONS OVERVIEW{nl}\
============================{nl}\
CONFIG: theta = {theta:>10.4f} (ene = {ene}), r = {r:>10.3f}, dz = {dz:>10.3f}, sz = {sz:>10.3f}{nl}\
UNITS: deg, eV, mm{nl}\
{str_ana:=^40}{nl}\
p   = {p:>10.3f}{nl}\
xs  = {xs:>10.3f}{nl}\
zeq = {zeq:>10.3f}{nl}\
zd  = {zd:>10.3f}{nl}\
{str_h:=^16} | {str_b:=^16}{nl}\
xh = {xh:>10.3f}  | xb = {xb:>10.3f}{nl}\
th = {th:>10.3f}  | tb = {tb:>10.3f}{nl}\
{str_det:=^40}{nl}\
{str_h:=^16} | {str_b:=^16}{nl}\
dzh = {dzh:>10.3f} | dzb = {dzb:>10.3f}{nl}\
dxh = {dxh:>10.3f} | dxb = {dxb:>10.3f}{nl}\
(=== SW 1804: abolute detector offsets ===){nl}\
(dyb = {xdb:>10.3f}){nl}\
(dzb = {zdb:>10.3f}){nl}\
"
    if retdict:
        return outdict
    else:
        print(outstr.format(**outdict))


# FOR TESTS #
if __name__ == "__main__":
    si555 = d_cubic(SI_ALAT, (5, 5, 5))
    show_spectro_overview(80, d=si555)
    pass

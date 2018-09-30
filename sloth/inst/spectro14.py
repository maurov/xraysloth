#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
spectro14: FAME-UHD (ESRF/BM16) X-ray emission spectrometer
===========================================================

"""

import math
import numpy as np

from sloth.utils.bragg import (HC, SI_ALAT, GE_ALAT, d_cubic, get_dspacing,
                               kev2wlen, wlen2kev, kev2ang, ang2kev)

def calc_det_dzh(theta):
    """calculate detector vertical offset of the top raw

    .. note:: formula taken from Table 2 on pag. 68 of CE document
              vol. 3 (Olivier Proux et al.), theta in deg

    """
    return 919.49-27.018*theta+0.26209*theta**2-0.00083803*theta**3
    
def calc_det_dzb(theta):
    """calculate detector vertical offset of the bottom raw

    .. note:: formula taken from Table 2 on pag. 68 of CE document
              vol. 3 (Olivier Proux et al.), theta in deg

    """
    return -677.96+19.121*theta-0.17315*theta**2+0.00049335*theta**3

def calc_det_dz(theta):
    """calc detector vertical offset from focus both rows"""
    return abs(calc_det_dzh(theta))+abs(calc_det_dzb(theta))

def calc_pos_com(emi, d=0, r=0, dz=0, sz=0):
    """get spectrometer positions for common axes 

    Parameters
    ==========
    emi  : emission energy [keV]
    d    : analyser d-spacing [nm]
    r    : crystal bending radius (=diameter Rowland circle) [mm]
    dz   : offset in z from the central row [mm]
    sz   : offset in z of the sample from top table [mm]
    
    Returns
    =======
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
    _xs = r*math.sin(_rtheta)*math.sin(_rtheta)
    _zeq = r*math.sin(_rtheta)*math.cos(_rtheta)
    _zd = 2*_zeq #detector
    _rsth = r*math.sin(_rtheta)
    try:
        _xh = math.sqrt(_rsth**2-(_zeq+dz)**2)-_xs
        _xb = math.sqrt(_rsth**2-(_zeq-dz)**2)-_xs
        _thetah = math.degrees(math.atan((_zeq+dz)/(_xh+_xs))+_rtheta-(math.pi/2.))
        _thetab = math.degrees(math.atan((_zeq-dz)/(_xb+_xs))+_rtheta-(math.pi/2.))
    except:
        _xh = 0.
        _xb= 0.
        _thetah = 0.
        _thetab = 0.

    _com_dict = {"xs"     : _xs,
                 "zeq"    : _zeq+sz,
                 "zd"     : _zd+sz,
                 "xh"     : _xh,
                 "xb"     : _xb,
                 "thetah" : _thetah,
                 "thetab" : _thetab}
    
    return _com_dict

def calc_pos_mod(nmodule):
    """get positions per module
    
    """
    pass

def show_spectro_overview(theta, d=None, r=1000., dz=82., sz=500.):
    """show an overview of the spectrometer geometry calculations"""

    if d is not None:
        ene = ang2kev(theta, d)
    else:
        ene = 'no dspacing'
    rtheta = math.radians(theta)
    p = r*math.sin(rtheta)
    xs = r*math.sin(rtheta)**2
    zeq = r*math.sin(rtheta)*math.cos(rtheta)
    xsh = math.sqrt(p**2 - (zeq+dz)**2)
    xsb = math.sqrt(p**2 - (zeq-dz)**2)
    xh = xsh-xs
    xb = xsb-xs
    rth = math.acos(xsh/p) + rtheta - math.pi/2.
    rtb = math.acos(xsb/p) + rtheta - math.pi/2.
    th = math.degrees(rth)
    tb = math.degrees(rtb)
    
    xdb = 2*zeq*math.sin(abs(rtb))
    zdb = xdb/math.tan(rtheta+rtb)

    dzh = calc_det_dzh(theta)
    dzb = calc_det_dzb(theta)

    dxh = dzh / math.tan(math.pi/2. - rtheta)
    dxb = dzb / math.tan(math.pi/2. - rtheta)
    
    #ADD SAMPLE Z OFFSET
    zd = zeq*2 + sz
    zeq += sz

    print("= SPECTRO14 POSITIONS OVERVIEW =")
    print("CONFIG: theta = {0} (ene = {3}), r = {1}, dz = {2}, sz = {4}".format(theta, r, dz, ene, sz))
    print("p = {0}".format(p))
    print("xs = {0}".format(xs))
    print("zeq = {0}".format(zeq))
    print("zd = {0}".format(zd))
    print("=== top row ===")
    print("xh = {0}".format(xh))
    print("th = {0}".format(th))
    print("=== bottom row ===")
    print("xb = {0}".format(xb))
    print("tb = {0}".format(tb))
    print("=== DETECTOR ===")
    print("dzh = {0}".format(dzh))
    print("dyh = {0}".format(dxh))
    print("dzb = {0}".format(dzb))
    print("dyb = {0}".format(dxb))
    print("=== detector offsets (absolute) using SolidWorks model v1804 ===")
    print("dyb = {0}".format(xdb))
    print("dzb = {0}".format(zdb))
  

# FOR TESTS #
if __name__ == '__main__':
    show_spectro_overview(65)
    pass

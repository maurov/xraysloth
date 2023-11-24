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
================================{nl}\
SPECTRO14 POSITIONS (ANALITICAL){nl}\
================================{nl}\
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


# === NUMERICAL APPROACH ===


def rotation_matrix(axis, angle):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by a given angle (degree).
    """
    rangle = np.deg2rad(angle)
    axis = axis / getnorm(axis)
    a = np.cos(rangle / 2.0)
    b, c, d = -axis * np.sin(rangle / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ]
    )


def getnorm(vector):
    """norm of a vector"""
    return np.sqrt(np.dot(vector, vector))


def normalize(vector):
    """unit vector"""
    n = getnorm(vector)
    if n == 0:
        return np.array([0, 0, 0])
    else:
        return vector / n

def get_angle(v1, v2):
    """angle (degrees) between two vectors"""
    n1 = getnorm(v1)
    n2 = getnorm(v2)
    return np.rad2deg(np.arccos(np.dot(v1, v2) / (n1 * n2)))


class AnalyserBM16:
    """Base class for a spherical crystal analyser on a Rowland circle for the BM16 spectrometer (a.k.a spectro14)"""
    
    def __init__(self, theta, pos, dz, row=None, beta=8, R=1000, pos_cen=4, sz=500, flag=1):
        """constructor
        
        Parameters
        ----------
        
        theta : float
            Bragg angle in degrees
        
        pos : int
            module position possible (e.g. 1,2,3,4,5,6,7)
            the central analyser is given by 'pos_cen' variable (below)

        dz : float
            vertical distance from the central row in mm
            *NOTE* spectro14 +- 82 mm

        row : string (optional)
            string identifying the row of analysers
            dz > 0 => "h", top
            dz < 0 => "b", bottom
            dz = 0 => "c", central
        
        beta : float (optional)
            radial spacing between analysers in degrees [default: 8 (spectro14)]
                       
        R : float
            diameter of the Rowland circle in mm [default: 1000]
        
        pos_cen : int
            position of the central analyser, that is at beta = 0 [default: 4]
            
        sz : float
            sample offset in Z, that is, sample position is at (0, 0, sz) [default: 500]
            
        flag : int
            to use (1) or not (0) the given analyses [default: 1]
            
        Notes
        -----
        
        - [Reference system] Here a global XYZ reference system is used, that is, the ESRF XYZ starndard reference system (right hand, X along the beam) rotated by -90 de counterclockwise around Z
            
        """
        self.pos_cen = pos_cen
        self.pos = pos
        self.dz = dz
        if (row is None) and (dz > 0):
            row = "h"
        if (row is None) and (dz < 0):
            row = "b"
        if (row is None) and (dz == 0):
            row = "c"
        assert isinstance(row, str) 
        self.row = row
        self.sz = sz
        self.theta = theta
        self.beta = beta
        self.R = R
        self.flag = flag
        self._init_position = True
        self.info = {}
        self.get_info(show=False)
        
    @property
    def xaxis(self):
        return np.array([1, 0, 0])

    @property
    def yaxis(self):
        return np.array([0, 1, 0])

    @property
    def zaxis(self):
        return np.array([0, 0, 1])
    
    @property
    def theta(self):
        self._theta = 90 - get_angle(self.normal, self.position)
        self._rtheta = np.deg2rad(self._theta)
        return self._theta

    @theta.setter
    def theta(self, value):
        self._theta = value
        self._rtheta = np.deg2rad(self._theta)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value * (self.pos_cen - self.pos)

    @property
    def R(self):
        return self._R

    @R.setter
    def R(self, value):
        self._R = value

    @property
    def gamma(self):
        """gamma angle for the current analyser"""      
        Rp = self.R * np.sin(self._rtheta)
        gamma_ = np.arcsin(np.cos(self._rtheta) + self.dz / Rp)
        return -(np.rad2deg(gamma_) - 90 + self._theta)

    @property 
    def name(self):
        """name of the crystal in the form of '{row}{position}'"""
        return f"{self.row}{self.pos}"

    @property
    def virt_cen_pos(self):
        """position of the central analyser of the virtual row"""
        return np.array([self.R * np.sin(self._rtheta)**2, 0 , self.R * np.sin(self._rtheta) * np.cos(self._rtheta)])

    @property
    def x0(self):
        return self.virt_cen_pos[0]

    @property
    def y0(self):
        return self.virt_cen_pos[1]

    @property
    def z0(self):
        return self.virt_cen_pos[2] + self.sz
    
    @property
    def position(self):
        """analyser XYZ position"""
        if self._init_position == False:
            return self._pos
        else:
            rz_beta = np.dot(rotation_matrix(self.zaxis, self.beta), self.virt_cen_pos)
            ry_gam = np.dot(rotation_matrix(self.yaxis, self.gamma), rz_beta)
            ry_gam[2] += self.sz
            self._pos = ry_gam
            return self._pos
  
    def init_position(self):
        self._init_position = True
        _ = self.position
        
    @position.setter
    def position(self, value):
        """this setter in case one want to manually change the position of the analyser"""
        self._init_position = False
        assert (isinstance(value, np.ndarray) and len(value)==3), f"{value} should be a numpy array of 3 elements"
        self._pos = value
    
    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    @property
    def z(self):
        return self.position[2]
    
    @property
    def normal(self):
        """normal to the analyser"""
        rz_beta = np.dot(rotation_matrix(self.zaxis, self.beta), self.xaxis)
        ry_gam = np.dot(rotation_matrix(self.yaxis, self.gamma), rz_beta)
        return ry_gam
    
    def get_info(self, show=True):
        xstr = f"x{self.row}"
        thstr = f"t{self.row}"
        idict = apos = show_spectro_overview(self._theta, retdict=True)
        if self.row == "c":
            apos[xstr] = 0
            apos[thstr] = 0
        idict.update({'name' : self.name,
                      'theta' : self._theta,
                      'x' : self.x,
                      'y' : self.y,
                      'z' : self.z,
                      'pitch' : self.pitch,
                      'yaw' : self.yaw,
                      'roll': 0,
                      'zeqdz' : apos['zeq'] + self.dz,
                      'zoff' : self.z - (apos['zeq'] + self.dz),
                      'x0' : self.x0,
                      'xs_num' : self.xs,
                      'xan' : apos[xstr],
                      'xapos' : apos['xs'] + apos[xstr],
                      'xstr' : xstr,
                      'xoff' : self.xs - (apos['xs'] + apos[xstr]),
                      'thstr' : thstr,
                      'than' : apos[thstr],
                      'thnm' : -self.gamma,
                })
        istr = ["ANALYSER {name} @ theta: {theta:.4f} deg"]
        istr.append("3D POSITION | ORIENTATION")
        istr.append("X: {x:.4f}, Y: {y:.4f}, Z: {z:.4f} | pitch: {pitch:.3f}, yaw: {yaw:.3f}, roll: {roll}")
        istr.append("ANALYTICAL | NUMERICAL | DIFFERENCE")
        istr.append("zeq: {zeq:.4f}, zeq+dz: {zeqdz:.4f} | z: {z:.4f} | zoff=z-(zeq+dz): {zoff:.4f}")
        istr.append("xs: {xs:.4f}, {xstr}: {xan:.4f}, xs+{xstr}: {xapos:.4f} | xs_num: {xs_num:.4f} | xoff=xs_num-(xs+{xstr}): {xoff:.4f}")
        istr.append("{thstr}: {than:.3f} | -gamma: {thnm:.3f}")
        
        istr = '\n'.join(istr).format(**idict)
        if show:
            print(istr)
        else:
            self.info.update(idict)
   
    @property
    def pitch(self):
        return get_angle(self.normal, self.xaxis)
    
    @property
    def yaw(self):
        return self.beta
    
    @property
    def roll(self):
        raise NotImplementedError

    @property
    def xs(self):
        """xs is the radial distance from the sample along beta"""
        return np.sqrt(self.x**2 + self.y**2)

    
    
class SpectrometerBM16:
    """BM16 spectrometer, a.k.a. spectro14"""
    
    def __init__(self, theta, dz_abs=82, beta=8, R=1000, pos_cen=4, sz=500):
        
        self.theta = theta
        
        self._anas = {}
    
        #bottom row
        for idx in range(1,8):
            name = f"b{idx}"
            self._anas[name] = AnalyserBM16(self.theta, pos=idx, dz=-1*dz_abs, beta=beta, pos_cen=pos_cen, sz=sz, R=R, flag=1)

        #top row
        for idx in range(1,8):
            name = f"h{idx}"
            self._anas[name] = AnalyserBM16(self.theta, pos=idx, dz=dz_abs, beta=beta, pos_cen=pos_cen, sz=sz, R=R, flag=1)

        #central row
        for idx in range(1,8):
            name = f"c{idx}"
            self._anas[name] = AnalyserBM16(self.theta, pos=idx, dz=0, beta=beta, pos_cen=pos_cen, sz=sz, R=R, flag=0)

    def get_analysers(self):
        analysers = []
        for name, ana in self._anas.items():
            if ana.flag == 0:
                continue
            analysers.append(ana.name)
        return analysers
            
    def get_info(self):
        
        istr = ["SPECTROMETER BM16"]
        istr.append(f"Analysers: {len(self.get_analysers())}")
        istr.append(f"Theta Bragg: {self.theta}")
        
        
        istr.append("name, ")
        for name, ana in self._anas.items():
            if ana.flag == 0:
                continue
            ana.get_info(show=False)
            istr.append(f"{ana.info['name']}")
        print('\n'.join(istr))



























# FOR TESTS #
if __name__ == "__main__":
    si555 = d_cubic(SI_ALAT, (5, 5, 5))
    show_spectro_overview(80, d=si555)
    pass

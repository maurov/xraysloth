#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rowland circle geometry
=======================

Units here:

 angular [deg]
 spatial [mm]
 energy [eV]

Table of variables and conventions

| description            | here    | XRT    | RT4XES  | SHADOW3 |
|------------------------+---------+--------+---------+---------|
| Bragg angle            | \theta  | \theta | \theta  | \theta  |
| Rowland circle radius  | Rm      | Rm     | R/2     |         |
| crystal bending radius | 2*Rm    | 2*Rm   | R       |         |
| rays direction         | Y       | Y      | X       | Y       |
| sagittal direction     | X       | X      | Y       | X       |
| meridional direction   | Z       | Z      | Z       |         |
| sample pos (X,Y,Z)     | (0,0,0) |        | (0,0,0) |         |
|                        |         |        |         |         |


RT4XES
------

ID26specVII.m

- sample at (0,0,0); crystal at (Xa,0,Za); detector at (0,0,Zd=2*Za)

TODO
----

- check formulas when a miscut is given (alpha != 0)

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.4"
__status__ = "in progress"
__date__ = "Oct 2014"

import sys, os
import math
import numpy as np

from rotmatrix import rotate

### GLOBAL VARIABLES ###
HC = 1.2398418743309972e-06 # eV * m
ED0 = 1e-4 # minimum energy step (eV) considered as 0 
AZ0 = 1e-4 # minimum Z step (mm) considered as 0

### UTILITIES ###
def cs_h(c, R):
    r"""
    Height of the circular segment, given its radius R and chord length c
    See: [http://en.wikipedia.org/wiki/Circular_segment]
    """
    if c >= 2*R:
        print('WARNING: the chord is greater than the diameter!')
        print('WARNING: returning maximum height, the radius')
        return R
    else:
        return R - np.sqrt( R**2 - (c**2/4) )

def acenx(n, asx=25., agx=5.):
    """n-th analyser center (starting from 0!) in x, given its size
    (asx) and gap between two (agx) in mm

    """
    return (asx + agx) * n

### CLASS ###
class RowlandCircle(object):
    """ Rowland circle geometry """

    def __init__(self, Rm=1000., theta0=0., alpha=0., aL=0., d=None,\
                 inCircle=False, useCm=False, showInfos=True):
        """Rowland circle geometry

        Parameters
        ----------
        theta0 : Bragg angle for the center in deg
        Rm : [1000] radius of the Rowland circle (meridional radius) in mm
        alpha : miscut angle in deg (TODO) the angle between the surface
                of the crystal and the normal of the Bragg planes (0 <= alpha <= \pi/2)
        aL : float, distance of analyser center from the chi rotation  (affects => Chi, SagOff)
        d : crystal d-spacing in \AA (this is simply an utility to convert theta to energy - in eV)
        inCircle : sample inside the Rowland cicle (dispersive)
                   [False] otherwise give the y offset
        useCm : boolean, False
                use cm instead of mm (as in SHADOW)
        showInfos : boolean [True] print extra informations (sometimes useful)
        
        Returns
        -------
        None (set attributes)

        self.Rm
        self.inCircle
        self.sampPos : sample position center, always at (0,0,0)
        self.alpha
        self.ralpha
        self.showInfos
        
        """
        if useCm:
            self.uDist = 'cm'
        else:
            self.uDist = 'mm'
        self.Rm = Rm
        self.aL = aL
        self.Rs = 0.
        self.d = d
        self.inCircle = inCircle
        self.showInfos = showInfos
        if inCircle is False:
            self.sampPos = np.array([0,0,0])
        elif (('int' in str(type(inCircle))) or ('float' in str(type(inCircle)))):
            self.sampPos = np.array([0,inCircle,0])
        else:
            raise NameError('Sample inside the Rowland circle: y offset is required')
        self.alpha = alpha
        self.ralpha = np.deg2rad(self.alpha)
        if (theta0 != 0) : self.setTheta0(theta0)

    def setDspacing(self, d):
        """ sets crystal d-spacing (\AA) """
        self.d = d
        
    def setTheta0(self, theta0):
        """ sets attributes for a given theta0 (Bragg angle = center theta)
        self.theta0 : in degrees
        self.rtheta0 : in radians
        self.sd : sample-detector distance (independent of \alpha)
        self.p : sample-analyzer distance
        self.q : analyzer-detector distance
        self.Rs : sagittal radius (analyser center, self.aL == 0.)
        """
        self.theta0 = theta0
        self.rtheta0 = math.radians(self.theta0)       
        self.sd = 2. * self.Rm * math.sin(2. * self.rtheta0)
        self.p0 = 2. * self.Rm * math.sin(self.rtheta0 + self.ralpha)
        self.p = self.p0 - self.sampPos[1]
        self.q0 = 2. * self.Rm * math.sin(self.rtheta0 - self.ralpha)
        self.q = self.q0 # TODO: generic case!
        if self.p == self.p0:
            if self.alpha == 0:
                if self.showInfos: print('INFO: sagittal focusing, symmetric formula')
                self.Rs = 2 * self.Rm * (math.sin(self.rtheta0))**2 # no miscut
            else :
                print('WARNING: sagittal focusing with miscut (CHECK FORMULA!)')
                self.Rs = self.Rm * (math.cos(2*self.alpha) - math.cos(2*self.theta0)) # TODO: check this
        else :
            # generic sagittal focusing # TODO: check this!!!
            print('WARNING: sagittal focusing generic (CHECK FORMULA!)')
            self.Rs = ( 2. * math.sin(self.rtheta0) * self.p * self.q ) / (self.p + self.q)
        if self.showInfos:
            print("INFO: theta0 = {0:.3f} deg".format(self.theta0))
            if self.d is not None:
                print("INFO: ene0 = {0:.2f} eV".format(self.getEne()))
                print("INFO: d = {0:.3f} \AA".format(self.d))
            print("INFO: p = {0:.3f} {1}".format(self.p, self.uDist))
            print("INFO: q = {0:.3f} {1}".format(self.q, self.uDist))
            print("INFO: Rs = {0:.3f} {1}".format(self.Rs, self.uDist))
            print("INFO: aL = {0:.3f} {1}".format(self.aL, self.uDist))

    def setEne0(self, ene0, d=None):
        """ set the central energy (eV) and relative Bragg angle """
        if d is None:
            d = self.d
        try:
            theta0 = self.getTheta(ene0, d=d, isDeg=True)
            self.setTheta0(theta0)
        except:
            print("ERROR: energy not setted!")

    def getTheta(self, ene=None, d=None, isDeg=True):
        """ get theta angle (deg or rad, controlled by isDeg var) for a given energy (eV) and d-spacing """
        if d is None:
            d = self.d
        if ene is None:
            ene = self.getEne(theta=None, d=d, isDeg=isDeg)
        if (d is not None) and not (self.d == 0) and not (ene == 0):
            wlen = ( HC / ene ) * 1e10
            theta = math.asin( wlen / (2*d) )
            if isDeg: theta = math.degrees(theta)
            return theta
        else:
            raise NameError("wrong d-spacing or energy")
            
    def getEne(self, theta=None, d=None, isDeg=True):
        """ get energy (eV) for a given angle (deg) and d-spacing """
        if theta is None:
            theta = self.rtheta0
            isDeg = False
        if d is None:
            d = self.d
        if isDeg:
            rtheta = math.radians(theta)
        else:
            rtheta = theta
        if d is not None:
            wlen = 2 * d * math.sin(rtheta)
            return ( HC / wlen ) * 1e10
        else:
            raise NameError("give d-spacing (\AA)")

    def getDth(self, eDelta):
        """ Delta\theta using differential Bragg law """
        if abs(eDelta) <= ED0:
            return 0
        ene = self.getEne(theta=self.rtheta0, isDeg=False)
        return -1 * ( eDelta / ene ) * math.tan(self.rtheta0)
            
    def getChi(self, aXoff, Rs=None, aL=None, inDeg=True):
        """ get \chi angle in sagittal focusing """
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        Rs2 = Rs + aL
        rchi = math.atan( aXoff / math.sqrt(Rs2**2 - aXoff**2) )
        if (inDeg is True):
            return np.rad2deg(rchi)
        else:
            return rchi

    def getSagOff(self, aXoff, Rs=None, aL=None, retAll=False):
        """ analyser sagittal offset from the center one """
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        rchi = self.getChi(aXoff, Rs=Rs, aL=aL, inDeg=False)
        aXoff0 = aXoff - aL*math.sin(rchi)
        rchi0 = self.getChi(aXoff0, Rs=Rs, aL=0, inDeg=False) # this is equal to rchi!
        SagOff0 = cs_h(aXoff0*2, Rs)
        SagOff = SagOff0 - aL*math.cos(rchi)
        if self.showInfos:
            _tmpl_ihead = "INFO: {0:=^10} {1:=^12} {2:=^13}"
            _tmpl_idata = "INFO: {0:^ 10.5f} {1:^ 12.5f} {2:^ 13.5f}"
            print(_tmpl_ihead.format('Chi', 'aXoff', 'SagOff'))
            print(_tmpl_idata.format(math.degrees(rchi), aXoff, SagOff))
            print(_tmpl_ihead.format('Chi0', 'aXoff0', 'SagOff0'))
            print(_tmpl_idata.format(math.degrees(rchi0), aXoff0, SagOff0))
        if retAll:
            return [math.degrees(rchi), aXoff, SagOff, math.degrees(rchi0), aXoff0, SagOff0]
        else:
            return SagOff

    def getAzOff(self, eDelta, rtheta0=None, d=None, Rm=None):
        """ get analyser Z offset for a given energy delta (eV) """
        if abs(eDelta) <= ED0:
            return 0.
        if rtheta0 is None:
            rtheta0 = self.rtheta0
        if d is None:
            d = self.d
        if d is None:
            raise NameError("give d-spacing")
        if Rm is None:
            Rm = self.Rm
        _dth = self.getDth(eDelta)
        if self.showInfos:
            print('INFO: dth = {0:.1f} urad ({1:.5f} deg)'.format(_dth*1e6, math.degrees(_dth)))
            print('INFO: daz [tan(dth) ~ dth] = {0}'.format(_dth * 2 * Rm * math.sin(rtheta0) ))
            print('INFO: daz [tan(dth) ~ dth and sin(th) ~ 1 = {0}'.format(_dth * 2 * Rm) )
        return 2 * Rm * math.sin(rtheta0) * math.tan(_dth)

    def getEneOff(self, aZoff, rtheta0=None, d=None, Rm=None):
        """ get analyser delta E for a given Z offset """
        if abs(aZoff) <= AZ0:
            return 0.
        if rtheta0 is None:
            rtheta0 = self.rtheta0
        if d is None:
            d = self.d
        if d is None:
            raise NameError("give d-spacing")
        if Rm is None:
            Rm = self.Rm
        #
        _dth = math.atan( aZoff /  (2 * Rm * math.sin(rtheta0)) )
        if self.showInfos:
            print('INFO: dth = {0:.1f} urad ({1:.5f} deg)'.format(_dth*1e6, math.degrees(_dth)))
        _ene = self.getEne(theta=rtheta0, d=d, isDeg=False)
        _de = _ene * _dth / math.tan(rtheta0)
        return _de

            
class RcVert(RowlandCircle):
    """ Rowland circle vertical frame: sample-detector on XZ plane along Z axis """

    def __init__(self, *args, **kws):
        """ RowlandCircle init
        
        Parameters
        ==========
        rotHor : boolean, rotate to horizontal [False]
    
        """
        try:
            self.rotHor = kws.pop('rotHor')
        except:
            self.rotHor = False
        RowlandCircle.__init__(self, *args, **kws)

    def getPos(self, vect):
        """ utility method: return 'vect' or its rotated form if self.rotHor """
        if self.rotHor:
            return rotate(vect, np.array([1,0,0]), (math.pi/2.-self.rtheta0))
        else:
            return vect

    def getDetPos(self):
        """ returns detector center position [X,Y,Z] """
        zDet = 4 * self.Rm * math.sin(self.rtheta0) * math.cos(self.rtheta0)
        vDet = np.array([0, 0, zDet])
        return self.getPos(vDet)

    def getAnaPos(self, aXoff=0.):
        """ returns analyser XYZ center position for a given X offset

        Parameters
        ==========
        aXoff : offset in X direction for the analyser
        """
        yAcen = 2 * self.Rm * math.sin(self.rtheta0)**2
        zAcen = 2 * self.Rm * math.sin(self.rtheta0) * math.cos(self.rtheta0)
        Acen = np.array([0, yAcen, zAcen])
        if (aXoff == 0.):
            return self.getPos(Acen)
        else:
            Chi = self.getChi(aXoff, inDeg=False)
            Aside = rotate(Acen, np.array([0,0,1]), Chi)
            return self.getPos(Aside)

class RcHoriz(RowlandCircle):
    """ Rowland circle horizontal frame: sample-analyzer on XY plane along Y axis """

    def __init__(self, *args, **kws):
        """RowlandCircle init """
        RowlandCircle.__init__(self, *args, **kws)

    def getDetPos(self):
        """ returns detector position [X,Y,Z] """
        yDet = self.p + self.q * math.cos(2 * self.rtheta0)
        zDet = self.q * math.sin(2 * self.rtheta0)
        return np.array([0, yDet, zDet])

    def getAnaPos(self, aXoff=0.):
        """ analyzer analyser XYZ center position for a given X offset

        Parameters
        ==========
        aXoff : offset in X direction for the analyser
        """
        Acen = np.array([0, self.q, 0])
        if (aXoff == 0.):
            return Acen
        else:
            SDax = self.getDetPos()
            Chi = self.getChi(aXoff, inDeg=False)
            Aside = rotate(Acen, SDax, Chi)
            return Aside


if __name__ == "__main__":
    #tests/examples in rowland_tests.py
    pass

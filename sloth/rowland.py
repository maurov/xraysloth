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
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Aug 2014"

import sys, os
import math
import numpy as np

from rotmatrix import rotate

### GLOBAL VARIABLES ###
HC = 1.2398418743309972e-06 # eV * m

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

    def __init__(self, Rm=1000., theta0=0., alpha=0., aL=0., d=None, inCircle=False, showInfos=True):
        """Rowland circle geometry

        Parameters
        ----------
        theta0 : Bragg angle for the center in deg
        Rm : [1000] radius of the Rowland circle (meridional radius) in mm
        alpha : miscut angle in deg (TODO) the angle between the surface
                of the crystal and the normal of the Bragg planes (0 <= alpha <= \pi/2)
        aL : float, analyser center distance from the chi rotation  (affects => Chi, SagOff)
        d : crystal d-spacing in \AA (this is simply an utility to convert theta to energy - in eV)
        inCircle : sample inside the Rowland cicle (dispersive)
                   [False] otherwise give the y offset
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
        self.rtheta0 = np.deg2rad(self.theta0)       
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
            print("INFO: theta0 = {0}".format(self.theta0))
            print("INFO: p = {0}".format(self.p))
            print("INFO: q = {0}".format(self.q))
            print("INFO: Rs = {0}".format(self.Rs))
            print("INFO: aL = {0}".format(self.aL))

    def setEne0(self, ene0, d=None):
        """ set the central energy (eV) and relative Bragg angle """
        self.d = d
        if (self.d is not None) and not (self.d == 0) and not (ene0 == 0):
            wlen0 = ( HC / ene0 ) * 1e10
            theta0 = math.degrees( math.arcsin( wlen0/(2*self.d) ) )
            self.setTheta0(theta0)
        else:
            print("ERROR: energy not setted!")
            
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
        aXoff0 = aXoff
        rchi0 = self.getChi(aXoff0, Rs=Rs, aL=0, inDeg=False)
        SagOff0 = cs_h(aXoff0*2, Rs)        
        aXoff = aXoff0 + aL
        Rs2 = Rs + aL
        rchi = self.getChi(aXoff, Rs=Rs2, aL=aL, inDeg=False)
        aXoff2 = aXoff - aL * math.sin(rchi)
        print('aXoff2 = {0}'.format(aXoff2))
        SagOff = cs_h(aXoff2*2, Rs)
        if self.showInfos:
            _tmpl_ihead = "INFO: {0:=^10} {1:=^12} {2:=^13}"
            _tmpl_idata = "INFO: {0:^ 10.4f} {1:^ 12.4f} {2:^ 13.4f}"
            print(_tmpl_ihead.format('Chi', 'aXoff', 'SagOff'))
            print(_tmpl_idata.format(math.degrees(rchi), aXoff, SagOff))
            print(_tmpl_ihead.format('Chi0', 'aXoff0', 'SagOff0'))
            print(_tmpl_idata.format(math.degrees(rchi0), aXoff0, SagOff0))
        if retAll:
            return [math.degrees(rchi), aXoff, SagOff, math.degrees(rchi0), aXoff0, SagOff0]
        else:
            return SagOff

    def getAzOff(self, eMono, eSpec, azSpec, rtheta0=None, Rm=None):
        """ analyser Z offset """
        if rtheta0 is None:
            rtheta0 = self.rtheta0
        if Rm is None:
            Rm = self.Rm
        return 2 * Rm * ((eMono-azSpec)/eSpec) * math.tan(rtheta0)
            
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

### TESTS ###
def testSagOff(Rm, theta0, aXoff, aL=100.):
    rc = RcHoriz(Rm, theta0, aL=aL, showInfos=True)
    rc.getSagOff(aXoff)

def testChiOpt():
    #from specfiledatawriter import SpecfileDataWrite
    #fname = 'testChiOpt.spec'
    #sfout = SpecfileDataWriter(fname)
    ths = np.linspace(34., 86., 27.) #theta scan
    rms = [250., 500.]
    als = [0., 25., 50., 100.]
    agxs = [0., 5.]
    dres = {'rm' : [],
            'th' : [],
            'al' : [],
            'chi' : [],
            'axoff' : [],
            'sagoff' : [],
            'chi0' : [],
            'axoff0' : [],
            'sagoff0' : []}
    for rm in rms:
        for al in als:
            rc = RcHoriz(rm, aL=al, showInfos=False)
            axoff = acenx(5, asx=25., agx=5.)
            for th in ths:
                rc.setTheta0(th)
                #[math.degrees(rchi), aXoff, SagOff, math.degrees(rchi0), aXoff0, SagOff0]
                lso = rc.getSagOff(axoff, retAll=True)
                dres['rm'].append(rm)
                dres['th'].append(th)
                dres['al'].append(al)
                dres['chi'].append(lso[0])
                dres['axoff'].append(lso[1])
                dres['sagoff'].append(lso[2])
                dres['chi0'].append(lso[3])
                dres['axoff0'].append(lso[4])
                dres['sagoff0'].append(lso[5])
    return dres

if __name__ == "__main__":
    #pass
    testSagOff(250., 35., 150., aL=90.)
    #dres = testChiOpt()
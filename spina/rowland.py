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

#SpectroX (https://github.com/maurov/spectrox)
from rotation_matrix import rotate

DEBUG = False

class RowlandCircle(object):
    """ Rowland circle geometry """

    def __init__(self, Rm=1000., theta=0., alpha=0., inCircle=False):
        """Rowland circle geometry

        Parameters
        ----------
        theta : Bragg angle in deg
        Rm : [1000] radius of the Rowland circle (meridional radius)
        in mm
        alpha : miscut angle in deg (TODO)

        inCircle : sample inside the Rowland cicle (dispersive)
                   [False] otherwise give the y offset

        Returns
        -------
        None (set attributes)

        self.Rm
        self.sampPos : sample position center, always at (0,0,0)
        self.alpha
        self.ralpha

        """
        self.Rm = Rm
        self.inCircle = inCircle
        if inCircle is False:
            self.sampPos = np.array([0,0,0])
        elif (('int' in str(type(inCircle))) or ('float' in str(type(inCircle)))):
            self.sampPos = np.array([0,inCircle,0])
        else:
            raise NameError('Sample inside the Rowland circle: y offset is required')
        self.alpha = alpha
        self.ralpha = np.deg2rad(self.alpha)
        if (theta != 0) : self.setTheta(theta)
        
    def setTheta(self, theta):
        """ sets attributes for a given theta
        self.theta : in degrees
        self.rtheta : in radians
        self.sd : sample-detector distance (independent of \alpha)
        self.p : sample-analyzer distance
        self.q : analyzer-detector distance
        self.Rs : sagittal radius
        """
        self.theta = theta
        self.rtheta = np.deg2rad(self.theta)
        self.sd = 2. * self.Rm * math.sin(2. * self.rtheta)
        self.p0 = 2. * self.Rm * math.sin(self.rtheta + self.ralpha)
        self.p = self.p0 - self.sampPos[1]
        self.q = 2. * self.Rm * math.sin(self.rtheta - self.ralpha)
        # generic sagittal focusing
        self.Rs = ( 2. * math.sin(self.rtheta) * self.p * self.q ) / (self.p + self.q)
        # if p = p0
        # self.Rs = 2 * self.Rm * (math.sin(self.rtheta))**2 # no miscut
        # self.Rs = self.Rm * (math.cos(2*self.alpha) - math.cos(2*self.theta)) # TODO: check this
        if DEBUG:
            print("RowlandCircle.setTheta({0}):".format(self.theta))
            print("p = {0}".format(self.p))
            print("q = {0}".format(self.q))
            print("Rs = {0}".format(self.Rs))

    def getChi(self, aXoff, inDeg=True):
        """ get \chi angle in sagittal focusing """
        rchi = math.atan( aXoff / math.sqrt(self.Rs**2 - aXoff**2) )
        if (inDeg is True):
            return np.rad2deg(rchi)
        else:
            return rchi

class RcVert(RowlandCircle):
    """Rowland circle vertical frame: sample-detector on XZ plane along Z
    axis

    Parameters
    ==========

    rotHor : boolean, rotate to horizontal [False]

    """

    def __init__(self, *args, **kws):
        """ init """
        try:
            self.rotHor = kws.pop('rotHor')
        except:
            self.rotHor = False
        RowlandCircle.__init__(self, *args, **kws)

    def getPos(self, vect):
        """ vect or its rotated form """
        if self.rotHor:
            return rotate(vect, np.array([1,0,0]), (math.pi/2.-self.rtheta))
        else:
            return vect

    def getDetPos(self):
        """ detector center position [X,Y,Z] """
        zDet = 4 * self.Rm * math.sin(self.rtheta) * math.cos(self.rtheta)
        vDet = np.array([0, 0, zDet])
        return self.getPos(vDet)

    def getAnaPos(self, aXoff=0.):
        """ analyser XYZ center position for a given X offset """
        yAcen = 2 * self.Rm * math.sin(self.rtheta)**2
        zAcen = 2 * self.Rm * math.sin(self.rtheta) * math.cos(self.rtheta)
        Acen = np.array([0, yAcen, zAcen])
        if (aXoff == 0.):
            return self.getPos(Acen)
        else:
            Chi = self.getChi(aXoff, inDeg=False)
            Aside = rotate(Acen, np.array([0,0,1]), Chi)
            return self.getPos(Aside)

class RcHoriz(RowlandCircle):
    """Rowland circle horizontal frame: sample-analyzer on XY plane along
    Y axis

    """

    def __init__(self, *args, **kws):
        """ init """
        RowlandCircle.__init__(self, *args, **kws)

    def getDetPos(self):
        """ detector position [X,Y,Z] """
        yDet = self.p + self.q * math.cos(2 * self.rtheta)
        zDet = self.q * math.sin(2 * self.rtheta)
        return np.array([0, yDet, zDet])

    def getAnaPos(self, aXoff=0.):
        """ analyzer position """
        Acen = np.array([0, self.q, 0])
        if (aXoff == 0.):
            return Acen
        else:
            SDax = self.getDetPos()
            Chi = self.getChi(aXoff, inDeg=False)
            Aside = rotate(Acen, SDax, Chi)
            return Aside

if __name__ == "__main__":
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Rowland circle geometry
==========================

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

.. note::

   The sagittal plane local reference system is a 2D coordinate
   system. All analysers are sitting/sliding on this plane. The origin
   is located at the central analyser axis at "aL" parametric distance
   from the central analyser surface (away from the sample). The
   coordinates are (aXoff, SagOff). ``aXoff`` is positive on the right
   of the central analyser when looking at the sample. ``SagOff`` is
   positive toward the sample.

.. note::

   The following code has been tested with a 3D CAD model built using
   SolidWorks: ``RowlandSketchPrototype-v1512``

.. note ::

   Lens equations used here are taken from:

   - Suortti et al., J. Synchrotron Rad. 6, 69 (1999), DOI: 10.1107/S0909049599000291
   - Podorov et al., J. Phys. D: Appl. Phys 34, 2363 (2001), DOI: 10.1088/0022-3727/34/15/317

   *Meridional*

   p0 = 2 * Rm * sin(theta0 - alpha)
   q0 = 2 * Rm * sin(theta0 + alpha)

   p0/p + q0/q = 2

   *Sagittal*

   1/p + 1/q = ( sin(theta0 - alpha) + sin(theta0 + alpha) ) / Rs

RT4XES
------

ID26specVII.m

- sample at (0,0,0); crystal at (Xa,0,Za); detector at (0,0,Zd=2*Za)

TODO
----

- all the bender-related things should go only in RcHoriz!!!
- check the full thing formulas when a miscut is given (alpha != 0)

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"

import sys, os, math
import numpy as np

from ..math.rotmatrix import rotate

try:
    xrange
except NameError:
    xrange = range

DEBUG = 0

### GLOBAL VARIABLES ###
HC = 1.2398418743309972e-06 # eV * m
ED0 = 1e-4 # minimum energy step (eV) considered as 0 
AZ0 = 1e-4 # minimum Z step (mm) considered as 0

### UTILITIES ###
def cs_h(c, R):
    """Height of the circular segment, given its radius R and chord
    length c See: [http://en.wikipedia.org/wiki/Circular_segment]

    """
    if c >= 2*R:
        print('WARNING: the chord is greater than the diameter!')
        print('WARNING: returning maximum height, the radius')
        return R
    else:
        return R - math.sqrt( R**2 - (c**2/4) )

def acenx(n, asx=25., agx=5.):
    """n-th analyser center (starting from 0!) in x, given its size (asx)
    and gap between two (agx) in mm

    """
    return (asx + agx) * n

def det_pos_rotated(dxyz, drot=35., doffsets=[0,0]):
    """return the detector positions in a rotated reference system with
    the origin at the sample

    Parameters
    ----------

    dxyz : numpy array of floats
           [X, Y, Z] detector position in the global coordinate system
           (detector assumed on the YZ plane)

    drot : float [35.]
           angle of rotation, counter-clock-wise, around X axis

    doffsets : numpy array of floats [0, 0]
               [Y, Z] offsets of the detector reference system origin

    Return
    ------

    [dy, dz] : numpy array of floats
               absolute positions of the detector stages
               NOTE: the sign may depend on the definition of the origin

    """
    x, y, z = dxyz[0], dxyz[1], dxyz[2]
    dr = math.sqrt(y**2 + z**2)
    if y == 0.:
        alpha = math.pi/2. - math.radians(drot)
    else:
        alpha = math.atan(z/y) - math.radians(drot)
    if DEBUG: print('DEBUG(det_pos_rotated): alpha is {0} deg'.format(math.degrees(alpha)))
    dpar = dr * math.cos(alpha)
    dper = dr * math.sin(alpha)
    #insert offset of the detector origin
    dy = dpar - doffsets[0]
    dz = doffsets[1] - dper
    
    return np.array([dy, dz])
    
### CLASS ###
class RowlandCircle(object):
    """Rowland circle geometry"""

    def __init__(self, Rm=500., theta0=0., alpha=0., d=None,\
                 aW=0., aWext=0., rSext=0., aL=0.,\
                 bender_version=None, bender=(0., 0., 0.), actuator=(0., 0.),\
                 inCircle=False, useCm=False, showInfos=True, **kws):
        """
        Parameters
        ----------
        
        Rm : float, 500.

             radius of the Rowland circle (meridional radius) in [mm]
             
        theta0 : float, 0.
                 Bragg angle for the central Rowland circle [deg]
        
        alpha : float, 0.

                miscut angle in deg: the angle between the surface of
                the crystal and the crystal planes at the centre
                point; for positive alpha, q > p, that is, the center
                analyser moves downward (or clockwise) the vertical
                Rowland circle

        d : float, None

            crystal d-spacing in \AA (this is simply an utility to
            convert theta to energy - in eV)

        aW : float, 0.

             crystal analyser optical width
                
        aWext : float, 0.

                crystal analyser extended width (NOTE: this width is
                used in self.get_chi2, that is, the width to get two
                adjacent analysers touching)

        rSext : float, 0.

                sagittal radius offset where aWext is referred to,
                that is, aWext condition is given for Rs+rSext
        
        aL : float, 0.

             distance of analyser center from the chi rotation
             (affects => Chi, SagOff)

        bender_version : string, None
                         defines the bender tuple keyword argument
                         see -> self.get_bender_pos()
        
        bender : tuple of floats, (0., 0., 0.) corresponds to
                 if (bender_version is None) or (bender_version == 0):
                 (length_arm0_mm, length_arm1_mm, angle_between_arms_deg)
                 if (bender_version == 1):
                 (length_arm0_mm, length_arm1_mm, length_anchor_actuator_mm)

        actuator : tuple of floats, (0., 0.) corresponts to
                   (axoff_actuator_mm, length_actuator_arm_mm)

        inCircle : boolean, False

                   sample on the Rowland cicle otherwise give the y
                   offset if inside (dispersive)

        useCm : boolean, False
        
                use cm instead of mm (as default in SHADOW)

        showInfos : boolean, True

                    print extra informations (sometimes useful)
        
        Returns
        -------
        None (set attributes)

        self.Rm
        self.inCircle
        self.sampPos
        self.alpha
        self.ralpha
        self.aL
        self.aW
        self.aWext
        self.rSext
        self.bender
        self.actuator
        self.bender_version
        self.showInfos

        """
        if useCm:
            self.uDist = 'cm'
        else:
            self.uDist = 'mm'
        self.Rm = Rm
        self.aW = aW
        self.aWext = aWext
        self.rSext = rSext
        self.bender = bender
        self.actuator = actuator
        if bender_version is None: bender_version = 0
        self.bender_version = bender_version
        self.aL = aL
        self.Rs = 0.
        self.d = d
        self.inCircle = inCircle
        self.showInfos = showInfos
        self.infos_dict = {}
        if inCircle is False:
            self.sampPos = np.array([0,0,0])
        elif (('int' in str(type(inCircle))) or ('float' in str(type(inCircle)))):
            self.sampPos = np.array([0,inCircle,0])
            print('WARNING: inCircle not tested/implementd yet, REVERTED to 0 position!')
            self.sampPos = np.array([0,0,0])
        else:
            raise NameError('Sample inside the Rowland circle: y offset is required')
        self.alpha = alpha
        self.ralpha = np.deg2rad(self.alpha)
        if (theta0 != 0) : self.set_theta0(theta0)
        #no need to return self; this method will not be called in sequence
        #return self

    def set_dspacing(self, d):
        """set crystal d-spacing (\AA)"""
        self.d = d
        
    def set_theta0(self, theta0, showInfos=None):
        """set correct attributes for a given theta0 (Bragg angle =
        center theta)

        Returns
        -------
        None (set attributes)
        
        self.theta0  : in degrees
        self.rtheta0 : in radians
        self.sd      : sample-detector distance (independent of \alpha?)
        self.p       : sample-analyser distance
        self.q       : analyser-detector distance
        self.Rs      : sagittal radius (analyser center, self.aL == 0.)
        """
        if showInfos is None: showInfos = self.showInfos
        self.theta0 = theta0
        self.rtheta0 = math.radians(self.theta0)       
        self.sd = 2. * self.Rm * math.sin(2. * self.rtheta0)
        self.p0 = 2. * self.Rm * math.sin(self.rtheta0 - self.ralpha)
        #self.p = self.p0 - self.sampPos[1] #not fully tested yet
        self.p = self.p0
        self.q0 = 2. * self.Rm * math.sin(self.rtheta0 + self.ralpha)
        self.q = self.q0 # TODO: generic case!
        if self.p == self.p0:
            if self.alpha == 0:
                if self.showInfos: print('INFO: sagittal focusing, symmetric formula')
                self.Rs = 2 * self.Rm * (math.sin(self.rtheta0))**2 # no miscut
            else :
                print('WARNING: sagittal focusing with miscut (CHECK FORMULA!)')
                #self.Rs = self.Rm * (math.cos(2*self.ralpha) - math.cos(2*self.theta0)) # TODO: check this
                self.Rs = 2 * self.Rm * math.sin(self.rtheta0 - self.ralpha) * math.sin(self.rtheta0 + self.ralpha) #this one should be correct: TO TEST!
        else :
            # generic sagittal focusing # TODO: check this!!!
            print('WARNING: sagittal focusing generic (CHECK FORMULA!)')
            self.Rs = ( 2. * math.sin(self.rtheta0) * self.p * self.q ) / (self.p + self.q)
        if showInfos:
            print("INFO: theta0 = {0:.3f} deg".format(self.theta0))
            print("INFO: alpha = {0:.3f} deg".format(self.alpha))
            if self.d is not None:
                print("INFO: ene0 = {0:.2f} eV".format(self.get_ene()))
                print("INFO: d = {0:.3f} \AA".format(self.d))
            print("INFO: p = {0:.3f} {1}".format(self.p, self.uDist))
            print("INFO: q = {0:.3f} {1}".format(self.q, self.uDist))
            print("INFO: Rm = {0:.3f} {1}".format(self.Rm, self.uDist))
            print("INFO: Rs = {0:.3f} {1}".format(self.Rs, self.uDist))
            print("INFO: aW = {0:.3f} {1}".format(self.aW, self.uDist))
            print("INFO: aWext = {0:.3f} {1}".format(self.aWext, self.uDist))
            print("INFO: aL = {0:.3f} {1}".format(self.aL, self.uDist))
        return self

    def get_infos(self):
        """show useful information on distances/parameters"""
        self.infos_dict.update({'theta0' : [self.theta0, 'deg'],
                                'p' : [self.p, self.uDist],
                                'q' : [self.q, self.uDist],
                                'Rm' : [self.Rm, self.uDist],
                                'Rs' : [self.Rs, self.uDist],
                                'aW' : [self.aW, self.uDist],
                                'aWext' : [self.aWext, self.uDist],
                                'aL' : [self.aL, self.uDist]})

        if self.d is not None:
            self.infos_dict.update({'d' : [self.d, '\AA'],
                                    'ene0' : [self.get_ene(), 'eV']})
        return self.infos_dict

    def set_ene0(self, ene0, d=None):
        """set the central energy (eV) and relative Bragg angle"""
        if d is None:
            d = self.d
        try:
            theta0 = self.get_theta(ene0, d=d, isDeg=True)
            self.set_theta0(theta0)
        except:
            print("ERROR: energy not setted!")

    def get_theta(self, ene=None, d=None, isDeg=True):
        """get theta angle (deg or rad, controlled by isDeg var) for a
        given energy (eV) and d-spacing"""
        if d is None:
            d = self.d
        if ene is None:
            ene = self.get_ene(theta=None, d=d, isDeg=isDeg)
        if (d is not None) and not (self.d == 0) and not (ene == 0):
            wlen = ( HC / ene ) * 1e10
            theta = math.asin( wlen / (2*d) )
            if isDeg: theta = math.degrees(theta)
            return theta
        else:
            raise NameError("wrong d-spacing or energy")
            
    def get_ene(self, theta=None, d=None, isDeg=True):
        """get energy (eV) for a given angle (deg) and d-spacing"""
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

    def get_dth(self, eDelta):
        """Delta\theta using differential Bragg law"""
        if abs(eDelta) <= ED0:
            return 0
        ene = self.get_ene(theta=self.rtheta0, isDeg=False)
        return -1 * ( eDelta / ene ) * math.tan(self.rtheta0)
            
    def get_chi(self, aXoff, Rs=None, aL=None, inDeg=True):
        """get \chi angle in sagittal focusing using offset from
        centre analyser (aXoff)"""
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        Rs2 = Rs + aL
        rchi = math.atan( aXoff / math.sqrt(Rs2**2 - aXoff**2) )
        if (inDeg is True):
            return np.rad2deg(rchi)
        else:
            return rchi

    def get_chi2(self, aN=1., aWext=None, Rs=None, rSext=None, inDeg=True):
        """get \chi angle in sagittal focusing using touching/connected analysers

        Description
        -----------
        
        Using the extended radius Rsp=Rs+rSext, can be calculated as
        aN times the chi/2 of the first analyser given by:
        
        \chi/2 = \atan((aWext/2)/Rsp)

        Parameters
        ----------
        aN : float, 1.
             n-th analyser (0 is the central one)

        """
        if aWext is None: aWext = self.aWext
        if Rs is None: Rs = self.Rs
        if rSext is None: rSext = self.rSext
        Rsp = Rs + rSext
        rchi = ( 2 * math.atan((aWext/2)/Rsp) ) * aN
        if (inDeg is True):
            return math.degrees(rchi)
        else:
            return rchi

    def get_ana_dist(self, chi, aN=1., aW=None, Rs=None, inDeg=True):
        """get analyser-analyser distance at Rs"""
        if aW is None: aW = self.aW
        if Rs is None: Rs = self.Rs
        if not (aN == 0): chi = chi/aN
        if inDeg:
            chihalf = math.radians(chi/2.)
        else:
            chihalf = chi/2.
        aDist = 2 * Rs * math.sin(chihalf) - aW * math.cos(chihalf)
        if self.showInfos:
            print('INFO: analyser #{0:.0f}-#{1:.0f} (edge-to-edge) = {2:.4f} {3}'.format(aN, aN-1, aDist, self.uDist))
            print('INFO: delta chi = {0:.4f} deg'.format(chi))
        return aDist

    def get_axoff(self, chi, Rs=None, aL=None):
        """get aXoff for the pivot point when chi is known (simple case)"""
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        return (Rs + aL) * math.sin(math.radians(chi))

    def get_axoff0(self, chi, Rs=None):
        """get aXoff at the surface of the analyser"""
        return self.get_axoff(chi, Rs=Rs, aL=0)
        
    def get_axoff_line(self, aXoffMin, SagOffMin, degRot=0., Rs=None, aL=None):
        """get aXoff for the pivot point when only a linear trajectory is known

        Description
        -----------
        
        The local sagittal cartesian coordinate system is assumed: the
        origin is at the pivot point of the central analyser, the
        abscissa is pointing toward the center of the sagittal circle
        and the ordinate is pointing on the right side when looking in
        the abscissa direction. In the following is given the solution
        of the linear equations system consisting in the interception
        of the sagittal circle with the linear trajectory of the pivot
        point, that is:

        (x-Rs-aL)^2 + y^2 - (Rs+aL)^2 = 0
        x = x0 - d*cos(phi)
        y = y0 + d*sin(phi)
        
        where:

        x is SagOff
        y is aXoff
        x0, y0 is SagOffMin, aXoffMin at minimum Rs
        phi is degRot

        d is the distance of x, y from x0, y0 on the local polar
        coordinate system of the pivot point

        Parameters
        ----------

        aXoffMin, SagOffMin : float

                              coordinates of the minimum position of
                              the pivot point on the linear trajectory
                              on the sagittal plane.                              

        degRot : float, 0.
        
                 angle (deg) of the linear trajectory with respect to
                 the abscissa (horizontal)

        Returns
        -------
        aXoff1 : float
        """
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        y0 = aXoffMin
        x0 = SagOffMin
        phi = math.radians(degRot)
        if (phi == 0):
            if self.showInfos:
                print('INFO: simple case where aXoff is constant at aXoffMin')
                print('INFO: aXoffMin = {0:.5f}'.format(aXoffMin))
            return aXoffMin
        sinphi = math.sin(phi)
        cosphi = math.cos(phi)
        a = 1 #sinphi**2 + cosphi**2
        b = -2*x0*cosphi + 2*Rs*cosphi + 2*y0*sinphi + 2*aL*cosphi
        c = x0**2 + y0**2 - 2*Rs*x0 - 2*aL*x0
        #solutions to: a*y**2 + b*y + c = 0
        y1 = (-b + math.sqrt(b**2 - 4*a*c)) / (2*a) #good solution!
        y2 = (-b - math.sqrt(b**2 - 4*a*c)) / (2*a)
        if self.showInfos:
            print('INFO: two solutions for polar distance d:')
            print('INFO: 1 = {0:.5f} (good)'.format(y1))
            print('INFO: 2 = {0:.5f} (bad)'.format(y2))
        aXoff1 = y1*sinphi + aXoffMin
        SagOff1 = SagOffMin - y1*cosphi
        aXoff2 = y2*sinphi + aXoffMin
        SagOff2 = SagOffMin - y2*cosphi
        if self.showInfos:
            print('INFO: aXoffMin = {0:.5f}, SagOffMin = {1:.5f}, degRot = {2:.3f}'.format(aXoffMin, SagOffMin, degRot))
            print('INFO: aXoff1 = {0:.5f}, SagOff1 = {1:.5f}'.format(aXoff1, SagOff1))
            print('INFO: aXoff2 = {0:.5f}, SagOff2 = {1:.5f}'.format(aXoff2, SagOff2))
        return aXoff1

    def get_sag_off(self, aXoff, Rs=None, aL=None, retAll=False):
        """analyser sagittal offset from the center one (Y-like direction)

        Parameters
        ----------
        
        aXoff : float, required position at the pivot point (will give
                       a wrong result using the position at the
                       analyser surface)

        retAll : boolean, False

                 control return

        Returns
        -------

        if retAll: list of float
        
                   [chi_angle_deg, aXoff, SagOff, chi0_angle_deg, aXoff0, SagOff0]
                   where the 0 is referred to the case with aL=0
        else:
                   float

                   SagOff

        """
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        rchi = self.get_chi(aXoff, Rs=Rs, aL=aL, inDeg=False)
        aXoff0 = aXoff - aL*math.sin(rchi)
        rchi0 = self.get_chi(aXoff0, Rs=Rs, aL=0, inDeg=False) #to check this is equal to rchi!
        SagOff0 = cs_h(aXoff0*2, Rs)
        SagOff = SagOff0 - aL*math.cos(rchi) + aL
        if self.showInfos:
            print("INFO: === surface (0) vs pivot (aL={0:.0f}) ===".format(aL))
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

    def get_sag_off0(self, aXoff):
        """quick wrap to get the sagittal offset at the analyser
        surface, use get_sag_off() for full control!"""
        return self.get_sag_off(aXoff, retAll=True)[-1]

    def get_sag_off_mots(self, aXoff, degRot=0., pivotSide=10., Rs=None, aL=None):
        """motors positions for sagittal offset
        TODO: not working yet, sagoff also negative
        """
        print('WARNING: deprecated/broken method!!!')
        return 0, 0
    
        # sagoffs = self.get_sag_off(aXoff, Rs=Rs, aL=aL, retAll=True)
        # tS = sagoffs[2] / math.cos(math.radians(degRot))
        # rS = sagoffs[0] - degRot
        # tPS = pivotSide * math.sin(math.radians(rS))
        # if self.showInfos:
        #     print('Pivot center : {0}'.format(tS))
        #     print('Pivot side ({0}): +/- {1}'.format(pivotSide, tPS))
        # return tS + tPS, tS - tPS

    def get_bender_pos(self, aN=5, bender=None, Rs=None, aL=None, rSext=None, bender_version=None):
        """get the position (aXoff, SagOff) of the bender point (B)"""
        if aN < 3:
            print('ERROR: this method works only for aN>=3')
            return (0., 0.)
        if bender is None: bender = self.bender
        if Rs is None: Rs = self.Rs
        if aL is None: aL = self.aL
        if rSext is None: rSext = self.rSext
        if bender_version is None: bender_version = self.bender_version

        #map last 3 pivot points positions
        _c2 = [self.get_chi2(_n) for _n in xrange( int(aN-2), int(aN+1) )] #CHIs
        dchi = _c2[2]-_c2[0]
        if self.showInfos:
            print('INFO: == CHI ==')
            print('INFO: \chi{0:.0f} = {1:.5f}'.format(aN, _c2[2]))
            print('INFO: \Delta\chi{0}{1} = {2:.5f} deg'.format(aN, aN-2, dchi))
        _p = [self.get_sag_off(self.get_axoff(_cn), retAll=True) for _cn in _c2] #SagOffs
            
        #find the angle between the last pivot point _p[-1] and the bender point (B)
        #we use for this the position of the end point of bender[1] (C)
        _R = Rs + aL
        rdch = math.radians(dchi/2.)
        h = _R * (1 - math.cos(rdch)) #chord between pivots 0 and -2
        chalf = _R * math.sin(rdch) #half the chord length from circular segment formula
        #find coordinates of point B (pb) of the bender (anchor point with actuator[1])
        ra = math.acos(chalf/bender[1])
        dc = bender[1] * math.sin(ra) - h #aperture of the pantograph along radius
        if bender_version == 0:
            sc = self.get_axoff(_c2[1], Rs=Rs+dc) #aXoff_point_C
            #pc = self.get_sag_off(sc, retAll=True)
            axlp = _p[2][1] #aXoff last pivot point
            rb = math.acos( (axlp-sc) / bender[1])
            rc = math.pi - math.radians(bender[2]) - rb
            pb_axoff = axlp + bender[0] * math.cos(rc) #aXoff_bender_point(B)
            pb_sagoff = axlp - bender[0] * math.sin(rc) #SagOff_bender_point(B)
        elif bender_version == 1:
            adc = math.asin( (dc/2) / bender[0] ) #angle opposite to dc
            pdc = bender[0] * math.cos(adc) #perpendicular to dc
            pb_ang = math.atan(pdc / (Rs + aL + dc/2)) #angle between last analyzer and point B
            pb_h = _R * (1 - math.cos(pb_ang)) #chord for the anchoring point
            pb_chalf = _R * math.sin(pb_ang) #from circular segment formula
            pb_ra = math.acos(pb_chalf / bender[0])
            pb_dc = bender[0] * math.sin(pb_ra) - pb_h
            pb_chi = pb_ang + self.get_chi2(aN, inDeg=False) #radians
            pb_rs = Rs + aL + pb_dc
            pb_axoff = pb_rs * math.sin(pb_chi)
            pb_sagoff = _R - (pb_rs * math.cos(pb_chi))
            print(pb_axoff, pb_sagoff)
        else:
            raise NameError("ERROR with bender_version")
        if self.showInfos:
                print('INFO: bender point (B) coordinates (local sagittal reference)')
                print('INFO: aXoff={0:.5f}, SagOff={1:.5f}'.format(pb_axoff, pb_sagoff)) 
        return (pb_axoff, pb_sagoff)

    def get_bender_mot(self, bender_pos, actuator=None, bender_version=None):
        """get the motor position of the bender, given its point
        position (B) and the actuator specifications, plus the version of the mechanics

        Parameters
        ----------
        bender_pos : tuple of floats
                     (bender_axoff_mm, bender_sagoff_mm)

        actuator : tuple of floats, None
                   (axoff_actuator_mm, length_actuator_mm)

        bender_version : version of the mechanics
                         0 -> prototype
                         1 -> pantograph 2017

        """
        if actuator is None: actuator = self.actuator
        if bender_version is None:  bender_version = self.bender_version
        try:
            if bender_version == 0:
                rd = math.asin( (actuator[0] - bender_pos[0]) / actuator[1] )
            elif bender_version == 1:
                rd = math.asin((actuator[0] - self.bender[2] - bender_pos[0]) / actuator[1])
            else:
                raise NameError("ERROR with bender_version")
            mot_sagoff = actuator[1] * math.cos(rd) + bender_pos[1]
            return mot_sagoff
        except:
            print('ERROR with bender actuator position')
            return 0.

    def get_az_off(self, eDelta, rtheta0=None, d=None, Rm=None):
        """get analyser Z offset for a given energy delta (eV)"""
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
        _dth = self.get_dth(eDelta)
        if self.showInfos:
            print('INFO: dth = {0:.1f} urad ({1:.5f} deg)'.format(_dth*1e6, math.degrees(_dth)))
            print('INFO: daz [tan(dth) ~ dth] = {0}'.format(_dth * 2 * Rm * math.sin(rtheta0) ))
            print('INFO: daz [tan(dth) ~ dth and sin(th) ~ 1 = {0}'.format(_dth * 2 * Rm) )
        return 2 * Rm * math.sin(rtheta0) * math.tan(_dth)

    def get_ay_off(self, eDelta, rtheta0=None, d=None, Rm=None):
        """get analyser Y offset for a given energy delta (eV)"""
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
        _dth = self.get_dth(eDelta)
        if self.showInfos:
            print('INFO: dth = {0:.1f} urad ({1:.5f} deg)'.format(_dth*1e6, math.degrees(_dth)))
        return 2 * Rm * math.tan(rtheta0) * math.tan(_dth)
        
    def get_ene_off(self, aZoff, rtheta0=None, d=None, Rm=None):
        """get analyser delta E for a given Z offset """
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
        _ene = self.get_ene(theta=rtheta0, d=d, isDeg=False)
        _de = _ene * _dth / math.tan(rtheta0)
        return _de

            
class RcVert(RowlandCircle):
    """Rowland circle vertical frame: sample-detector on XZ plane along Z axis

    """

    def __init__(self, *args, **kws):
        """RowlandCircle init
        
        Parameters
        ==========
        rotHor : boolean, rotate to horizontal [False]

        """
        try:
            self.rotHor = kws.pop('rotHor')
        except:
            self.rotHor = False
        RowlandCircle.__init__(self, *args, **kws)

    def get_pos(self, vect):
        """utility method: return 'vect' or its rotated form if self.rotHor"""
        if self.rotHor:
            return rotate(vect, np.array([1,0,0]), (math.pi/2.-self.rtheta0))
        else:
            return vect

    def get_det_pos(self):
        """detector center position [X,Y,Z]"""
        zDet = 4 * self.Rm * math.sin(self.rtheta0) * math.cos(self.rtheta0)
        vDet = np.array([0, 0, zDet])
        return self.get_pos(vDet)

    def get_ana_pos(self, aXoff=0.):
        """analyser XYZ center position for a given chi

        Parameters
        ==========
        
        chi : float, 0. [deg]
              rotation angle on the sagittal plane (hor plane here)

        """
        yAcen = 2 * self.Rm * math.sin(self.rtheta0)**2
        zAcen = 2 * self.Rm * math.sin(self.rtheta0) * math.cos(self.rtheta0)
        Acen = np.array([0, yAcen, zAcen])
        if (chi == 0.):
            return self.get_pos(Acen)
        else:
            Aside = rotate(Acen, np.array([0,0,1]), math.radians(chi))
            return self.get_pos(Aside)

    def get_miscut_off(self, alpha=None, Rm=None):
        """returns horizontal and vertical offsets for a given miscut angle
        TODO: NOT CORRECT, CHECK THIS!
        """
        if (alpha is None) or (Rm is None):
            ralpha = self.ralpha
            Rm = self.Rm
        return - Rm * (1-math.cos(ralpha)), - Rm * math.sin(ralpha)

class RcHoriz(RowlandCircle):
    """Rowland circle horizontal frame: sample-analyser on XY plane along
Y axis

    """

    def __init__(self, *args, **kws):
        """RowlandCircle init """
        RowlandCircle.__init__(self, *args, **kws)

    def get_det_pos(self):
        """detector position [X,Y,Z]"""
        yDet = self.p + self.q * math.cos(2 * self.rtheta0)
        zDet = self.q * math.sin(2 * self.rtheta0)
        return np.array([0, yDet, zDet])

    def get_ana_pos(self, chi=0.):
        """analyser XYZ center position for a given chi

        Parameters
        ==========
        
        chi : float, 0. [deg]
              rotation angle on the sagittal plane (around sample-detector axis)
        
        """
        Acen = np.array([0, self.q, 0])
        if (chi == 0.):
            return Acen
        else:
            SDax = self.get_det_pos() - self.sampPos
            Aside = rotate(Acen, SDax, math.radians(chi))
            return Aside
        
    def get_miscut_off(self, alpha=None, p=None):
        """returns horizontal and vertical offsets for a given miscut angle
        TODO: NOT CORRECT CHECK THIS!
        """
        if (alpha is None) or (p is None):
            ralpha = self.ralpha
            p = self.p
        return - p * math.cos(ralpha/2.), - p * math.sin(ralpha/2.)


if __name__ == "__main__":
    #tests/examples in rowland_tests.py
    pass

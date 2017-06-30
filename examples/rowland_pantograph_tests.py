#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for sloth.inst.rowland (pantograph movements part)
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"

import os, sys
import math

import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib import rc, cm, gridspec
from matplotlib.ticker import MultipleLocator

### SLOTH ###
try:
    from sloth import __version__ as sloth_version
    from sloth.inst.rowland import cs_h, acenx, det_pos_rotated, RcHoriz, RcVert
    from sloth.utils.genericutils import colorstr
    from sloth.utils.bragg import d_cubic, d_hexagonal
except:
    raise ImportError('sloth is not installed (required version >= 0.2.0)')

### USEFUL GLOBAL VARIABLES ###
SI_ALAT = 5.431065 # Ang at 25C
dSi111 = d_cubic(SI_ALAT, (1,1,1))
dSi220 = d_cubic(SI_ALAT, (2,2,0))

### TESTS FOR THE PANTOGRAPH PROTOTYPE (A.K.A. FRICTION PROTOTYPE) ###
def testFrictionPrototype(Rm, theta0, d=dSi111):
    """implemented in get_bender_pos and get_bender_mot methods in sloth 0.2.0

    Pantograph parameters (sloth 0.2.0)
    -----------------------------------

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

    
        bender : tuple of floats, (0., 0., 0.) corresponds to
                 (length_arm0_mm, length_arm1_mm, angle_between_arms_deg)

        actuator : tuple of floats, (0., 0.) corresponts to
                   (axoff_actuator_mm, length_actuator_arm_mm)

    here:

    bender = (bender_arm0, bender_arm, bender_angle)
    actuator = (act_axoff, act_dist)

    ref 3D CAD: ``RowlandSketchPrototype-v1512``

    """
    # get pivot points positions
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                aW=25., aWext=32, rSext=10., aL=97.,\
                showInfos=False)
    bender_arm0 = 40. #arm to anchor p5 to actuator
    bender_arm = 60. #arm bender to the trapezoids, mm
    bender_angle = 100. #deg
    act_axoff = 269. #aXoff actuator
    act_dist = 135. #distance from actuator, mm
    _R = t.Rs + t.rSext
    c5 = t.get_chi2(5., Rs=_R)
    c4 = t.get_chi2(4., Rs=_R)
    c3 = t.get_chi2(3., Rs=_R)
    dchi = c5-c3
    # pivot points of 5, 4 and 3
    s5 = t.get_axoff(c5)
    p5 = t.get_sag_off(s5, retAll=True)
    s4 = t.get_axoff(c4)
    p4 = t.get_sag_off(s4, retAll=True)
    s3 = t.get_axoff(c3)
    p3 = t.get_sag_off(s3, retAll=True)
    # get position of point c where the bender arm is linked, on the radius of p4
    _R2 = t.Rs + t.aL
    rdch = math.radians(dchi/2.)
    h = _R2 * (1 - math.cos(rdch))
    chalf = _R2 * math.sin(rdch)
    ra = math.acos(chalf/bender_arm)
    dc = bender_arm * math.sin(ra) - h
    sc = t.get_axoff(c4, Rs=t.Rs+dc)
    pc = t.get_sag_off(sc, retAll=True)
    rb = math.acos( (p5[1]-pc[1])/bender_arm )
    #print(p5[1]-pc[1])
    #print('Angle last pivot point and bender = {0:.6f}'.format(180-100-math.degrees(rb)))
    rc = math.pi - math.radians(bender_angle) - rb
    # B point, where the actuator is anchored
    #[math.degrees(rchi), aXoff, SagOff, math.degrees(rchi0), aXoff0, SagOff0]
    pb = []
    pb.append(0.) #no chi pos
    pb.append( p5[1] + bender_arm0 * math.cos(rc) )
    pb.append( p5[2] - bender_arm0 * math.sin(rc) )
    #print(pb)
    # up to here everything seems correct
    rd = math.asin((act_axoff - pb[1]) / act_dist)
    #print(math.degrees(rd))
    mot_sagoff = act_dist * math.cos(rd) + pb[2]
    print('Actuator position = {0} (test)'.format(mot_sagoff))
    # WORKS!!!!!
    return t

def testFrictionPrototypeInMethod(Rm, theta0, d=dSi111,\
                                  aW=25., aWext=32, rSext=20., aL=97.,\
                                  bender=(40., 60., 100.), actuator=(269., 135.),\
                                  showInfos=True):
    """as testFrictionPrototype implemented in sloth 0.2.0"""
    if not (sloth_version == '0.2.0'):
        print('This test works only with sloth 0.2.0')
        return 0
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                aW=aW, aWext=aWext, rSext=rSext, aL=aL,\
                bender=bender, actuator=actuator,\
                showInfos=showInfos)
    mot_sagoff = t.get_bender_mot(t.get_bender_pos(aN=5))
    print('Actuator position = {0} (in method)'.format(mot_sagoff))
    return t

### TESTS FOR THE PANTOGRAPH VERSION 2017 ###
def testPantograph2017(Rm, theta0, d=dSi111,\
                       aW=25., aWext=32, rSext=20., aL=107.,\
                       bender=(0., 60., 0.), actuator=(),\
                       showInfos=True):
    """implemented in get_bender_pos and get_bender_mot methods in sloth 0.2.1

    Pantograph parameters (sloth 0.2.1)
    -----------------------------------
    
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

    
        bender : tuple of floats, (0., 0., 0.) corresponds to
                 (length_arm0_mm, length_arm1_mm, angle_between_arms_deg)

        actuator : tuple of floats, (0., 0.) corresponts to
                   (axoff_actuator_mm, length_actuator_arm_mm)

    here:

    bender = (bender_arm0, bender_arm, bender_angle)
    actuator = (act_axoff, act_dist)

    ref 3D CAD: ``RowlandSketchPrototype-v1706``

    """
    #init rc + bender
    rc = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                 aW=aW, aWext=aWext, rSext=rSext, aL=aL,\
                 showInfos=showInfos)

    #TOO: to include in get_bender_pos
    
    #map 3 pivot points positions
    _c2 = [rc.get_chi2(_n) for _n in xrange( int(aN-2), int(aN+1) )]
    dchi = _c2[2]-_c2[0]
    if rc.showInfos:
        print('INFO: == CHI ==')
        print('INFO: \chi{0:.0f} = {1:.5f}'.format(aN, _c2[2]))
        print('INFO: \Delta\chi{0}{1} = {2:.5f} deg'.format(aN, aN-2, dchi))
    _p = [rc.get_sag_off(rc.get_axoff(_cn), retAll=True) for _cn in _c2]


if __name__ == "__main__":
    #plt.close('all')
    #t1 = testFrictionPrototype(240., 65.)
    t2 = testFrictionPrototypeInMethod(250., 75.)
    #t3 = testPantograph2017(240., 80.)
    pass

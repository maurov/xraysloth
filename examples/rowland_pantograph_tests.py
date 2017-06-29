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

### TESTS ###
def testFrictionPrototype(Rm, theta0, d=dSi111):
    """implemented in get_bender_pos and get_bender_mot methods"""
    # get pivot points positions
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d, aW=25., aWext=32, rSext=10., aL=97., showInfos=False)
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

def testFrictionPrototypeInMethod(Rm, theta0, d=dSi111):
    """as previous test but with the method implemented in the class"""
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                aW=25., aWext=32, rSext=10., aL=97.,\
                bender=(40., 60., 100.), actuator=(269., 135.),\
                showInfos=False)
    mot_sagoff = t.get_bender_mot(t.get_bender_pos())
    print('Actuator position = {0} (in method)'.format(mot_sagoff))
    t0 = testFrictionPrototype(Rm, theta0)
    return t

if __name__ == "__main__":
    #plt.close('all')
    t1 = testFrictionPrototype(240., 65.)
    t2 = testFrictionPrototypeInMethod(240., 65.)
    pass

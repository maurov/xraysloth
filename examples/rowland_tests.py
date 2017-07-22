#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for sloth.inst.rowland (generic tests)

See also more specific tests (older first)
------------------------------------------

- rowland_sagittal_tests (data evaluation sagittal prototype)
- rowland_detector_tests (figures showing detector movements)
- rowland_pantograph_tests (pantograph control movements)

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"

import os, sys
import math

import numpy as np
import matplotlib.pyplot as plt

### SLOTH ###
try:
    from sloth import __version__ as sloth_version
    from sloth.inst.rowland import cs_h, acenx, RcHoriz, RcVert
    from sloth.utils.genericutils import colorstr
    from sloth.utils.bragg import d_cubic, d_hexagonal
except:
    raise ImportError('sloth is not installed (required version >= 0.2.0)')

RS_MIN = 157.915
RS_MAX = 1012.252

SI_ALAT = 5.431065 # Ang at 25C
GE_ALAT = 5.6579060 # Ang at 25C
SIO2_A = 4.913 # beta-quartz, hexagonal
SIO2_C = 5.405

dSi111 = d_cubic(SI_ALAT, (1,1,1))
dGe111 = d_cubic(GE_ALAT, (1,1,1))
dSi220 = d_cubic(SI_ALAT, (2,2,0))
dGe220 = d_cubic(GE_ALAT, (2,2,0))
dQz100 = d_hexagonal(SIO2_A, SIO2_C, (1,0,0))

### TESTS ###
def testSagOff(Rm, theta0, aXoff, aL=100.):
    rc = RcHoriz(Rm, theta0, aL=aL, showInfos=True)
    rc.get_sag_off(aXoff)

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
                rc.set_theta0(th)
                #[math.degrees(rchi), aXoff, SagOff, math.degrees(rchi0), aXoff0, SagOff0]
                lso = rc.get_sag_off(axoff, retAll=True)
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

def testAzOff(eDelta, Rm=500., theta0=35, d=dSi111):
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d)
    return t.get_az_off(eDelta)

def testSagFocus(d=dSi111):
    """not finished yet!"""
    #first get the minimum position
    t0 = RcHoriz(Rm=250., theta0=35., d=d, aW=25., aWext=31.0266, aL=45.)
    c0 = t0.get_chi2(5.)
    d0 = t0.get_ana_dist(c0, 5.)
    s0 = t0.get_axoff(c0)
    sag0 = t0.get_sag_off(s0, retAll=True)
    t0.aXoffMin = sag0[1]
    t0.SagOffMin = sag0[2]
    #move theta and get new pivot point position
    t0.Rm = 510.
    t0.set_theta0(85.)
    s1 = t0.get_axoff_line(t0.aXoffMin, t0.SagOffMin, degRot=35.)
    return t0
    
def testMiscutOff1Ana(Rm, theta, alpha, d=dSi111):
    """test miscut offsets NOT WORKING YET!!!"""
    tv = RcVert(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    tv_mo = tv.get_miscut_off()
    th = RcHoriz(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    th_mo = th.get_miscut_off()
    print('RcVert: {0}'.format(tv_mo))
    print('RcHor: {0}'.format(th_mo))

if __name__ == "__main__":
    #plt.close('all')
    #testSagOff(250., 35., 150., aL=12.)
    #dres = testChiOpt()
    #testAzOff(0.5)
    #testMiscutOff1Ana(500., 65., 36.)
    #t0 = testSagFocus()
    pass

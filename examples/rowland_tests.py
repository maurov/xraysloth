#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for rowland
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.4"
__status__ = "in progress"
__date__ = "Oct 2014"

import sys
from __init__ import _libDir
sys.path.append(_libDir)

import numpy as np
from rowland import cs_h, acenx, det_pos_rotated, RcHoriz, RcVert

SI_ALAT = 5.431065 # Ang at 25C
GE_ALAT = 5.6579060 # Ang at 25C
SIO2_A = 4.913 # beta-quartz, hexagonal
SIO2_C = 5.405
from bragg import d_cubic, d_hexagonal
dSi111 = d_cubic(SI_ALAT, (1,1,1))
dGe111 = d_cubic(GE_ALAT, (1,1,1))
dSi220 = d_cubic(SI_ALAT, (2,2,0))
dGe220 = d_cubic(GE_ALAT, (2,2,0))
dQz100 = d_hexagonal(SIO2_A, SIO2_C, (1,0,0))

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

def testAzOff(eDelta, Rm=500., theta0=35, d=dSi111):
    t = RcHoriz(Rm=Rm, theta0=theta0, d=d)
    return t.getAzOff(eDelta)


def testDetMove(Rm=510):
    """test detector position in two ref frames"""
    ths = np.linspace(35., 85., 51)
    dres = {'th' : [],
            'dx' : [],
            'dz' : [],
            'dpar' : [],
            'dper' : []}
    for th in ths:
        r = RcHoriz(Rm, theta0=th, showInfos=False)
        d0 = r.getDetPos()
        d1 = det_pos_rotated(d0, drot=35.)
        dres['th'].append(th)
        dres['dx'].append(d0[1])
        dres['dz'].append(d0[2])
        dres['dpar'].append(d1[0])
        dres['dper'].append(d1[1])
    return dres
    
    
if __name__ == "__main__":
    #pass
    #testSagOff(250., 35., 150., aL=12.)
    #dres = testChiOpt()
    #testAzOff(0.5)
    dres = testDetMove()
    
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for rowland
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014--2015"

import sys
from __init__ import _libDir
sys.path.append(_libDir)

import numpy as np
from rowland import cs_h, acenx, det_pos_rotated, RcHoriz, RcVert

RS_MIN = 157.915
RS_MAX = 1012.252

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
        d0 = r.get_det_pos()
        d1 = det_pos_rotated(d0, drot=35.)
        dres['th'].append(th)
        dres['dx'].append(d0[1])
        dres['dz'].append(d0[2])
        dres['dpar'].append(d1[0])
        dres['dper'].append(d1[1])
    return dres
    
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

class TestProtoBender(object):
    """test class for the friction design prototype"""

    def __init__(self, Rm=500, theta0=35, d=dSi111,\
                 aW=25, aWext=32., rSext=10., aL=97.,\
                 bender=(40., 60., 100.), actuator=(269., 135.),\
                 showInfos=False):
        self.rc = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                          aW=aW, aWext=aWext, rSext=rSext, aL=aL,\
                          bender=bender, actuator=actuator,\
                          showInfos=showInfos)
        self.rs0 = self.rc.Rs #store Rs for a given Rm/theta0

    def set_rm(self, Rm, theta0=None, showInfos=None):
        """refresh all positions with new Rm and theta0 (optional)"""
        if theta0 is None: theta0 = self.rc.theta0
        self.rc.Rm = Rm
        self.rc.set_theta0(theta0, showInfos=showInfos) #to refresh positions
        self.rs0 = self.rc.Rs #store Rs for updated Rm/theta0
        self.sb = self.get_sb() #self.rc.Rs is updated in set_theta0
        print('INFO: bender motor at {0:.3f}'.format(self.sb))

    def get_sb(self, Rs=None):
        """get sagittal bender motor position, manual Rs may be given"""
        return self.rc.get_bender_mot(self.rc.get_bender_pos(Rs=Rs))

    def get_ana_xyz(self, xyz0=(0.,0.,0.)):
        """show xyz positions for 6 analyzers: 0 (cen) +5 (side)

        Parameters
        ----------
        xyz0 : tuple of floats, (0,0,0)
               output positions are shifted by this point
        """
        xyz0 = np.array(xyz0)
        _headstr = '{0: >2s}: {1: >7s} {2: >7s} {3: >7s}'
        _outstr = '{0: >2.0f}: {1: >7.3f} {2: >7.3f} {3: >7.3f}'
        print(_headstr.format('#', 'X', 'Y', 'Z'))
        for aN in xrange(6):
            chi = self.rc.get_chi2(aN=aN)
            axoff = self.rc.get_axoff(chi)
            axyz = self.rc.get_ana_pos(aXoff=axoff)
            if aN == 0: xyz0 -= axyz #output relative to the cen ana
            pxyz = [i+j for i,j in zip(axyz, xyz0)]
            print(_outstr.format(aN, *pxyz))

    def get_circle_3p(self, A, B, C):
        """center and radius of a circle given 3 points in space
        http://stackoverflow.com/questions/20314306/find-arc-circle-equation-given-three-points-in-space-3d"""
        a = np.linalg.norm(C - B)
        b = np.linalg.norm(C - A)
        c = np.linalg.norm(B - A)
        s = (a + b + c) / 2
        R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
        b1 = a*a * (b*b + c*c - a*a)
        b2 = b*b * (a*a + c*c - b*b)
        b3 = c*c * (a*a + b*b - c*c)
        P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
        P /= b1 + b2 + b3
        return R, P

    def read_data(self, fname):
        """read data (custom format) using flushing technique"""
        import csv
        import copy
        angs = {}
        with open(fname, 'rb') as f:
            fr = csv.reader(f, skipinitialspace=True)
            _pts = np.zeros((12, 3))
            _apos = {}
            _runs = {}
            _bpos = 0
            _ptx = False
            _rnx = 0
            _angx = 0
            for irow, row in enumerate(fr):
                if row[0][0] == '#': continue
                try:
                    ang = int(row[1])
                    run = int(row[2])
                    pos = float(row[3])
                    pt = int(row[4])
                    if _ptx:
                        #flush points
                        _apos[str(_bpos)] = _pts
                        _ptx = False
                        _pts = np.zeros((12, 3))
                    _pts[pt] = map(float, row[-3:])
                    if pt == 11:
                        _bpos = copy.deepcopy(pos)
                        _ptx = True
                    if run != _rnx:
                        #flush positions
                        _runs[_rnx] = copy.deepcopy(_apos)
                        _rnx = copy.deepcopy(run)
                        _apos = {}
                    if ang != _angx:
                        #flush runs
                        _runs[_rnx] = copy.deepcopy(_apos)
                        angs[_angx] = copy.deepcopy(_runs)
                        _angx = copy.deepcopy(ang)
                        _rnx = 0
                        _runs = {}
                except:
                    print('ERROR reading line {0}: {1}'.format(irow+1, row))
                    break
            #final flush all
            _apos[str(_bpos)] = _pts
            _runs[_rnx] = copy.deepcopy(_apos)
            angs[_angx] = copy.deepcopy(_runs)
        return angs

        
def testMiscutOff1Ana(Rm, theta, alpha, d=dSi111):
    """test miscut offsets NOT WORKING YET!!!"""
    tv = RcVert(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    tv_mo = tv.get_miscut_off()
    th = RcHoriz(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    th_mo = th.get_miscut_off()
    print('RcVert: {0}'.format(tv_mo))
    print('RcHor: {0}'.format(th_mo))

if __name__ == "__main__":
    #pass
    #testSagOff(250., 35., 150., aL=12.)
    #dres = testChiOpt()
    #testAzOff(0.5)
    #dres = testDetMove()
    import math
    #t0 = testSagFocus()
    #t1 = testFrictionPrototype(240., 65.)
    #t = testFrictionPrototypeInMethod(240., 65.)
    fname = '2015-06-18-all_points.dat'
    t = TestProtoBender()
    t.d = t.read_data(fname)
    #testMiscutOff1Ana(500., 65., 36.)
    

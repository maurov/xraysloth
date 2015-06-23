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
import matplotlib.pyplot as plt

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
    """test class for the friction design prototype

    Description
    ===========

    This is a very specific example class, but still generic and
    useful. Here an overview of what this class is for: 6 analyzers (0
    at cen + 5 at side) sliding on the sagittal plane via a
    bender-like system. 12 points (two per analyzer) are measured as a
    function of the bragg angle (angle between the sagittal plane and
    the horizontal plane) and the position of the actuator motor of
    the bender. The goal is to check if the exact rowland tracking is
    satified for each analyzer.
    """

    def __init__(self, Rm=500, theta0=35, d=dSi111,\
                 aW=25, aWext=32., rSext=10., aL=97.,\
                 bender=(40., 60., 100.), actuator=(269., 135.),\
                 showInfos=False):
        """init the Rowland circle geometry plus design of the system"""
        self.rc = RcHoriz(Rm=Rm, theta0=theta0, d=d,\
                          aW=aW, aWext=aWext, rSext=rSext, aL=aL,\
                          bender=bender, actuator=actuator,\
                          showInfos=showInfos)
        self.rs0 = self.rc.Rs #store Rs for a given Rm/theta0
        self.sp = None

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

    def set_sag_plane(self, P0, th0, showPlot=False):
        """set sagittal plane Ax+By+Cz+D=0 at point P0(x,y,z) for a given th0
(deg)

        """
        from rotmatrix import rotate
        norm = rotate(np.array([0,0,1]), np.array([1,0,0]), math.radians(90.-th0))
        d = -P0.dot(norm)
        self.sp = np.array([norm[0], norm[1], norm[2], d])
        self.th0 = th0
        if showPlot:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            # create x,y
            xypts = 10
            xrng_mesh = np.linspace(P0[0], P0[0]+xypts, xypts)
            yrng_mesh = np.linspace(P0[1], P0[1]-xypts, xypts)
            xx, yy = np.meshgrid(xrng_mesh, yrng_mesh)
            # calculate corresponding z
            zz = -1 * (norm[0] * xx + norm[1] * yy + d) / norm[2]
            # plot the surface
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_wireframe(xx, yy, zz)
            #ax.quiver(P0[0], P0[1], norm[0], norm[1])
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_zlim(P0[2]-xypts, P0[2]+xypts)
            plt.show()
        
    def get_sag_plane_dist(self, P):
        """get the distance of point P(x,y,z) from the sagittal plane

        """
        if self.sp is None:
            print('ERROR: generate first the sagittal plane using get_sag_plane')
            return 0
        else:
            sp = self.sp
        return abs(P[0]*sp[0] + P[1]*sp[1] + P[2]*sp[2] + sp[3]) / math.sqrt(sp[0]**2 + sp[1]**2 + sp[2]**2)
            
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

    def read_data(self, fname, retAll=False):
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
            _frun = True
            for irow, row in enumerate(fr):
                if row[0][0] == '#': continue
                try:
                    _frun = True
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
                        _frun = False
                    if ang != _angx:
                        #flush runs
                        if _frun:
                            _runs[_rnx] = copy.deepcopy(_apos)
                            _apos = {}
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
        if retAll:
            return angs
        else:
            self.dats = angs

    def eval_data(self, ang, run, **kws):
        """data evaluation: main method"""
        self.eval_data_th0s(ang, run, showPlot=False)
        self.eval_data_dists(ang, run, showPlot=True)
            
    def eval_data_th0s(self, ang, run, dats=None, retAll=False,\
                       setSp=True, showPlot=False):
        """data evaluation

        Parameters
        ----------

        ang, run : int
                   select angle/run data sets in dats dictionary

        dats : dictionary, None
               as parsed by read_data method (if None: self.dats)

        retAll : boolean, False
                 returns a Numpy array with the calculated theta0
                 positions

        setSp : boolean, True

                sets the sagittal plane (self.sp) for the average
                theta0, using position of point 0

        showPlot : boolean, False

                plot the sagittal plane
        """
        #TODO: move this common check to a method
        if dats is None: dats = self.dats
        try:
            d = dats[ang][run]
        except:
            print('ERROR: dats[ang][run] not found!')
            return 0
        #header/output format strings
        _headstr = '{0: >3s} {1: >3s} {2: >10s} {3: >7s}'
        _outstr = '{0: >3.0f} {1: >3.0f} {2: >10s} {3: >7.3f}'
        _headx = True
        sp = d.items()
        sp.sort()
        th0s = []
        x0s, y0s, z0s = [], [], []
        for _pos, _pts in sp:
            x0, y0, z0 = _pts[0][0:3]
            x6, y6, z6 = _pts[6][0:3]
            x0s.append(x0)
            y0s.append(y0)
            z0s.append(z0)
            try:
                #inclination angle given by the centre analyzer
                beta = math.atan((z0-z6)/(y6-y0))
            except:
                print('ERROR getting measured theta0')
                print('z0 = {0}; z6 = {1}; z0-z6 = {2}'.format(z0, z1, z0-z1))
                print('y0 = {0}; y6 = {1}; y6-y0 = {2}'.format(y0, y1, y1-y0))
                print('(z0-z6)/(y6-y0) = {0}'.format((z0-z1)/(y1-y0)))
                return 0
            th0 = math.degrees(math.pi/2.-beta)
            th0s.append(th0)
            if _headx:
                print('INFO: angle given by the centre analyzer (P0-P6)')
                print(_headstr.format('ang', 'run', 'pos', 'th0'))
                print(_headstr.format('#', '#', 'spec', 'deg'))
                _headx = False
            print(_outstr.format(ang, run, _pos, th0))
        ath0s = np.array(th0s)
        ax0s = np.array(x0s)
        ay0s = np.array(y0s)
        az0s = np.array(z0s)
        if setSp:
            #set sagittal plane at mean P0 and th0
            avgP0 = np.array([np.mean(ax0s), np.mean(ay0s), np.mean(z0s)])
            stdP0 = np.array([np.std(ax0s), np.std(ay0s), np.std(z0s)])
            avgth0 = np.mean(ath0s)
            stdth0 = np.std(ath0s)
            self.set_sag_plane(avgP0, avgth0, showPlot=showPlot)
            print('INFO: sagittal plane at centre analyzer')
            print('P0_mean ( {0:.4f}, {1:.4f}, {2:.4f} ) mm'.format(avgP0[0], avgP0[1], avgP0[2]))
            print('P0_std ({0:.4f}, {1:.4f}, {2:.4f}) mm'.format(stdP0[0], stdP0[1], stdP0[2]))
            print('th0_mean = {0:.4f} +/- {1:.4f} deg'.format(avgth0, stdth0))
        if retAll: return ath0s

    def eval_data_dists(self, ang, run, dats=None, retAll=False,\
                        setSp=True, showPlot=False):
        """data evaluation: points distances from sagittal plane

        Parameters
        ----------

        ang, run : int
                   select angle/run data sets in dats dictionary

        dats : dictionary, None
               as parsed by read_data method (if None: self.dats)

        retAll : boolean, False
                 returns a Numpy array with the calculated theta0
                 positions

        setSp : boolean, True

                sets the sagittal plane (self.sp) for the average
                theta0, using position of point 0

        showPlot : boolean, False

                plot the sagittal plane
        """
        #TODO: move this common check to a method
        if dats is None: dats = self.dats
        try:
            d = dats[ang][run]
        except:
            print('ERROR: dats[ang][run] not found!')
            return 0

        sp = d.items()
        sp.sort()

        self.poss = []
        self.dists = {}
        for ipt in xrange(12):
            self.dists[ipt] = []
        for _pos, _pts in sp:
            self.poss.append(_pos)
            for ipt in xrange(12):
                self.dists[ipt].append(self.get_sag_plane_dist(_pts[ipt][0:3]))
        self.aposs = np.array(map(float, self.poss[:]))
        if showPlot:
            try:
                #https://jiffyclub.github.io/palettable/
                import palettable
                colors = palettable.colorbrewer.qualitative.Dark2_6.mpl_colors
            except:
                colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
                          (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
                          (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
                          (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
                          (0.4, 0.6509803921568628, 0.11764705882352941),
                          (0.9019607843137255, 0.6705882352941176, 0.00784313725490196)]
                pass
            from matplotlib import rcParams
            from matplotlib import gridspec
            from matplotlib.ticker import MaxNLocator, AutoLocator, MultipleLocator
            rcParams['axes.color_cycle'] = colors
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for ipt in xrange(12):
                ax.plot(self.aposs, self.dists[ipt], label=str(ipt), linewidth=2)
            ax.set_xlabel('bender motor position (spec values, mm)')
            ax.set_ylabel('distance from mean sagittal plane (mm)')
            ax.set_xlim(-0.1, 120.1)
            ax.set_ylim(-0.005, 0.7)
            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(2))
            ax.yaxis.set_major_locator(MultipleLocator(0.05))
            ax.yaxis.set_minor_locator(MultipleLocator(0.01))
            ax.set_title('Proto pos {0}, run {1}: th0 = {2:.3f} deg'.format(ang, run, self.th0))
            ax.grid(alpha=0.5)
            ax.legend(loc='upper left', ncol=6, numpoints=1, frameon=True)
            #ax.legend(bbox_to_anchor=(1.05, 1.), loc=2, ncol=1, mode="expand", borderaxespad=0.)
            plt.tight_layout()
            plt.show()
        
    def get_meas_rs(self, ang, run, dats=None):
        """get the measured sagittal radius"""
        if dats is None: dats = self.dats
        _headstr = '{0: >3s} {1: >3s} {2: >10s} {3: >10s} {4: >10s}'
        _outstr = '{0: >3.0f} {1: >3.0f} {2: >10s} {3: >10.3f} {4: >10.3f}'
        _headx = True
        try:
            d = dats[ang][run]
        except:
            print('ERROR: dats[ang][run] not found!')
            return 0
        sp = d.items()
        sp.sort()
        for _pos, _pts in sp:
            a, b, c = _pts[0:3]
            rs012, cen012 = self.get_circle_3p(a,b,c)
            a, b, c = _pts[3:6]
            rs345, cen345 = self.get_circle_3p(a,b,c)
            if _headx:
                print(_headstr.format('ang', 'run', 'pos', 'rs012', 'rs345'))
                print(_headstr.format('#', '#', 'spec', 'mm', 'mm'))
                _headx = False
            print(_outstr.format(ang, run, _pos, rs012, rs345))
         
        
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
    t.read_data(fname)
    plt.close('all')
    t.eval_data(5,0)
    #testMiscutOff1Ana(500., 65., 36.)
    

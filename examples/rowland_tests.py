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

import os, sys
from __init__ import _libDir
sys.path.append(_libDir)

import numpy as np
import matplotlib.pyplot as plt

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

from rowland import cs_h, acenx, det_pos_rotated, RcHoriz, RcVert
from genericutils import colorstr

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

epsilon = 1.E-10 # Default epsilon for equality testing of points and vectors

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
        for aN in range(6):
            chi = self.rc.get_chi2(aN=aN)
            axoff = self.rc.get_axoff(chi)
            axyz = self.rc.get_ana_pos(aXoff=axoff)
            if aN == 0: xyz0 -= axyz #output relative to the cen ana
            pxyz = [i+j for i,j in zip(axyz, xyz0)]
            print(_outstr.format(aN, *pxyz))

    def set_sag_plane(self, P0, th0, plot=False):
        """set sagittal plane Ax+By+Cz+D=0 at point P0(x,y,z) at given
        th0 (deg)
        """
        from rotmatrix import rotate
        norm = rotate(np.array([0,0,1]), np.array([1,0,0]), math.radians(90.-th0))
        d = -P0.dot(norm)
        self.sp = np.array([norm[0], norm[1], norm[2], d])
        self.th0 = th0
        if plot: self.plot_sag_plane(P0=P0, sag_pl=self.sp)

    def plot_sag_plane(self, P0=None, sag_pl=None):
        """3D plot sagittal plane at P0"""
        if P0 is None: P0 = np.array([0,0,0])
        if sag_pl is None: sag_pl = self.sp
        norm, d = sag_pl[:3], sag_pl[3]
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        plt.ion()
        # create x,y
        xypts = 10
        xrng = 300
        yrng = 130
        xrng_mesh = np.linspace(P0[0], P0[0]-xrng, xypts)
        yrng_mesh = np.linspace(P0[1]-yrng/2., P0[1]+yrng, xypts)
        xx, yy = np.meshgrid(xrng_mesh, yrng_mesh)
        # calculate corresponding z
        zz = -1 * (norm[0] * xx + norm[1] * yy + d) / norm[2]
        # plot the surface
        self.fig = plt.figure()
        self.fig_ax = self.fig.add_subplot(111, projection='3d')
        self.fig_ax.plot_wireframe(xx, yy, zz, color='gray')
        #ax.quiver(P0[0], P0[1], norm[0], norm[1])
        self.fig_ax.set_xlabel('X')
        self.fig_ax.set_ylabel('Y')
        self.fig_ax.set_zlabel('Z')
        self.fig_ax.set_zlim(P0[2]-xrng, P0[2]+yrng)
        plt.show()

    def plot_meas_points(self, ang, run, pos=None):
        """plot measured points on sagittal plane"""
        dats = self.get_dats(ang, run, pos=pos)
        if pos is not None:
            self.plot_points(dats[1])
        else:
            for _pos, _pts in dats:
                self.plot_points(_pts)

    def plot_points(self, _pts, color='b', marker='o'):
        """plot set of 3D points"""
        xs, ys, zs = _pts[:,0], _pts[:,1], _pts[:,2]
        self.fig_ax.scatter(xs, ys, zs, color=color, marker=marker)
        plt.draw()
        
    def get_sag_plane_dist(self, P):
        """get the distance of point P(x,y,z) from the sagittal plane"""
        if self.sp is None:
            print('ERROR: sagittal plane not setted yet!')
            return 0
        else:
            sp = self.sp
        #return abs(P[0]*sp[0] + P[1]*sp[1] + P[2]*sp[2] + sp[3]) / math.sqrt(sp[0]**2 + sp[1]**2 + sp[2]**2)
        return abs(P[0]*sp[0] + P[1]*sp[1] + P[2]*sp[2] + sp[3]) / math.sqrt(sp.dot(sp))
            
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

    def get_circle_radius(self, point, center):
        """circle radius given point/center as 3D arrays"""
        x, y, z = point[:]
        x0, y0, z0 = center[:]
        return math.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)

    def get_intersect_lines(self, p10, p11, p20, p21):
        """intesection point, assuming line1 and line2 intersect and
        represented by two points each line, respectively, (p10, p11)
        and (p20, p21)

        """
        t = (p20 - p10) / (p11 - p10 - p21 + p20)
        return p10 + t * (p11 - p10)

    def get_intersect_angle(self, p0, p1, p2):
        """get the angle between three 3D points, p0 is the intersection point"""
        u, v = p1-p0, p2-p0
        costheta = u.dot(v) / math.sqrt(u.dot(u) * v.dot(v))
        return math.degrees(math.acos(costheta))

    def get_projection_point(self, point, plane, test=False):
        """get the orthogonal projection of a 3d point on plane

        http://stackoverflow.com/questions/7565748/3d-orthogonal-projection-on-a-plane

        Parameters
        ----------

        point : 3d P(x,y,z) => np.array([x,y,z])

        plane : Ax+By+Cz+d=0, norm = (A,B,C)
                => np.array([norm_x, norm_y, norm_z, d])

        Returns
        -------

        proj_pt : projected point = point - norm * offset
                  => np.array([proj_x, proj_y, proj_z])
        
        """
        try:
            norm = plane[:-1]
            d = plane[-1]
            offset = (point.dot(norm) + d) / norm.dot(norm)
        except:
            raise NameError('something wrong in get_projection_point')
        proj_pt = point - norm * offset
        if test:
            assert (norm.dot(proj_pt) + d <= epsilon)
        return proj_pt

    def test_point_on_plane(self, point, plane):
        """check point is on plane (within epsilon)"""
        _dist = point.dot(plane[:3]) + plane[3]
        if _dist <= epsilon:
            print('OK => point on plane')
        else:
            print('NO => point not on plane')
        
    def read_data(self, fname, retAll=False):
        """read data (custom format) using flushing technique

        Parameters
        ----------

        fname : str, file name

        File format
        -----------

        # comments:
        # theta position (0..5) => _pts.shape is (12, 3)
        # measurement run (0..1)
        # actuator abs pos (0 limit plus, 119 limit minus (-119 on sb motor)
        # point position (0..5 front, 6..11 back)

        # columns (comma separated values):
        # Collection, Theta, Run, Actuator, Point, X, Y, Z
        0, 0, 0, 0, 0, -0.030695, -0.000152, -0.028512
        [...]

        Returns
        -------
        retAll : boolean, False => set self.dats
                          True => return data dictionary 

        """
        import csv
        import copy
        angs = {}
        if sys.version < '3.0':
            access_mode = 'rb'
        else:
            access_mode = 'r'
        with open(fname, access_mode) as f:
            fr = csv.reader(f, skipinitialspace=True)
            _pts = np.zeros((12, 3)) #size depends on theta positions
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
                    _pts[pt] = list(map(float, row[-3:]))
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

    def get_dats(self, ang, run, pos=None, dats=None):
        """get data for a given angle/run"""
        if dats is None: dats = self.dats
        try:
            d = dats[ang][run]
        except:
            raise NameError('dats[{0}][{1}] not found!'.format(ang, run))
        datslist = list(d.items())
        _retlist = []
        for _pos, _pts in datslist:
            _pos = float(_pos)
            if _pos == pos:
                print("=> data for actuator position '{0}'".format(_pos))
                _retlist = [_pos, _pts]
                break
            else:
                _retlist.append((_pos, _pts))
                _retlist.sort()
        return _retlist

    def eval_data(self, ang, run, **kws):
        """data evaluation: main method

        Parameters
        ----------
        see sub-methods
        
        """
        self.eval_data_th0s(ang, run, plot=False)
        self.eval_data_dists(ang, run, plot=True)
            
    def eval_data_th0s(self, ang, run, dats=None, retAll=False,\
                       set_sp=True, plot=False):
        """data evaluation: get average th0 and set sagittal plane at it

        Parameters
        ----------

        ang, run : int
                   select angle/run data sets in dats dictionary

        dats : dictionary, None
               as parsed by read_data method (if None: self.dats)

        retAll : boolean, False
                 returns a Numpy array with the calculated theta0
                 positions

        set_sp : boolean, True

                sets the sagittal plane (self.sp) for the average
                theta0, using position of point 0

        plot : boolean, False

                plot the sagittal plane
        """
        #header/output format strings
        _headstr = '{0: >3s} {1: >3s} {2: >8s} {3: >7s}'
        _outstr = '{0: >3.0f} {1: >3.0f} {2: >8.3f} {3: >7.3f}'
        _headx = True
        dats = self.get_dats(ang, run, dats=dats)
        th0s = []
        x0s, y0s, z0s = [], [], []
        for _pos, _pts in dats:
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
                print('z0 = {0}; z6 = {1}; z0-z6 = {2}'.format(z0, z6, z0-z6))
                print('y0 = {0}; y6 = {1}; y6-y0 = {2}'.format(y0, y6, y6-y0))
                print('(z0-z6)/(y6-y0) = {0}'.format((z0-z6)/(y6-y0)))
                return 0
            th0 = math.degrees(math.pi/2.-beta)
            th0s.append(th0)
            if _headx:
                print('INFO: theta angle given by the centre analyzer (P0-P6)')
                print(_headstr.format('ang', 'run', 'pos', 'th0'))
                print(_headstr.format('#', '#', 'spec', 'deg'))
                _headx = False
            print(_outstr.format(ang, run, _pos, th0))
        ath0s = np.array(th0s)
        ax0s = np.array(x0s)
        ay0s = np.array(y0s)
        az0s = np.array(z0s)
        if set_sp:
            #set sagittal plane at mean P0 and th0
            avgP0 = np.array([np.mean(ax0s), np.mean(ay0s), np.mean(z0s)])
            stdP0 = np.array([np.std(ax0s), np.std(ay0s), np.std(z0s)])
            avgth0 = np.mean(ath0s)
            stdth0 = np.std(ath0s)
            self.set_sag_plane(avgP0, avgth0, plot=plot)
            print('INFO: setted sagittal plane at centre analyzer')
            print('P0_mean ( {0:.4f}, {1:.4f}, {2:.4f} ) mm'.format(avgP0[0], avgP0[1], avgP0[2]))
            print('P0_std ({0:.4f}, {1:.4f}, {2:.4f}) mm'.format(stdP0[0], stdP0[1], stdP0[2]))
            print('th0_mean = {0:.4f} +/- {1:.4f} deg'.format(avgth0, stdth0))
        if retAll: return ath0s

    def eval_data_dists(self, ang, run, dats=None, retAll=False,\
                        set_sp=True, plot=False):
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

        set_sp : boolean, True

                sets the sagittal plane (self.sp) for the average
                theta0, using position of point 0

        plot : boolean, False

                plot the sagittal plane
        """
        dats = self.get_dats(ang, run, dats=dats)
        self.poss = []
        self.dists = {}
        for ipt in xrange(12):
            self.dists[ipt] = []
        for _pos, _pts in dats:
            self.poss.append(_pos)
            for ipt in xrange(12):
                self.dists[ipt].append(self.get_sag_plane_dist(_pts[ipt][0:3]))
        self.aposs = np.array(map(float, self.poss[:]))
        if plot:
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
            
    def get_meas_rs(self, ang, run, set_sp=False, dats=None):
        """get the measured sagittal radius"""
        if dats is None: dats = self.dats
        _headstr = '{0: >3s} {1: >3s} {2: >8s} {3: >10s} {4: >10s}  {5: >10s}'
        _outstr = '{0: >3.0f} {1: >3.0f} {2: >8.3f} {3: >10.3f} {4: >10.3f} {5: >10.3f} '
        _headx = True
        dats = self.get_dats(ang, run, dats=dats)
        if set_sp:
            self.eval_data_th0s(ang, run)
        rss, cens = [], []
        for _pos, _pts in dats:
            a, b, c = _pts[0], _pts[3], _pts[5] #_pts[0:3]
            rs012, cen012 = self.get_circle_3p(a,b,c)
            rss.append(rs012)
            cens.append(cen012)
            if self.sp is not None:
                ap = self.get_projection_point(a, self.sp)
                bp = self.get_projection_point(b, self.sp)
                cp = self.get_projection_point(c, self.sp)
                rs012p, cen012p = self.get_circle_3p(ap,bp,cp)
            a, b, c = _pts[6], _pts[9], _pts[11] #_pts[3:6]
            rs345, cen345 = self.get_circle_3p(a,b,c)
            if self.sp is not None:
                ap = self.get_projection_point(a, self.sp)
                bp = self.get_projection_point(b, self.sp)
                cp = self.get_projection_point(c, self.sp)
                rs345p, cen345p = self.get_circle_3p(ap,bp,cp)
            if _headx:
                print(_headstr.format('ang', 'run', 'pos', 'rs012', 'rs345', 'deltars'))
                print(_headstr.format('#', '#', 'spec', 'mm', 'mm', 'mm'))
                _headx = False
            print(_outstr.format(ang, run, _pos, rs012, rs345, rs345-rs012))
            if self.sp is not None:
                print(_outstr.format(ang, run, _pos, rs012p, rs345p, rs345p-rs012p))
        return rss, cens
         
    def eval_data_rs(self, ang, run, set_sp=True, do_test=False, plot=False):
        """data evaluation: sagittal radius"""
        _headstr = '{0: >3s} {1: >3s} {2: >8s} {3: >8s} {4: >8s}  {5: >8s} {6: >8s} {7: >8s} {8: >8s}'
        _outstr = '{0: >3.0f} {1: >3.0f} {2: >8.3f} {3: >8.3f} {4: >8.3f} {5: >8.3f} {6: >8.3f}  {7: >8.3f} {8: >8.3f}'
        _headx = True
        if set_sp: self.eval_data_th0s(ang, run, plot=plot)
        dats = self.get_dats(ang, run)
        cens, rss, chis = [], [], []
        for _pos, _pts in dats:
            if plot: self.plot_points(_pts)
            pj = [self.get_projection_point(_pt, self.sp) for _pt in _pts]
            #sagittal circle center using lines (0,6) and (5,11)
            cen = t.get_intersect_lines(pj[0], pj[6], pj[5], pj[11])
            if do_test: self.test_point_on_plane(cen, self.sp)
            rs = [self.get_circle_radius(_pts[idx], cen) for idx in range(12)]
            chi = [t.get_intersect_angle(cen, pj[idx], pj[idx+1]) for idx in range(5)] 
            cens.append(cen)
            rss.append(rs)
            chis.append(chi)
            if _headx:
                print(_headstr.format('ang', 'run', 'pos', 'rs0', 'drs1', 'drs2', 'drs3', 'drs4', 'drs5'))
                print(_headstr.format('#', '#', 'spec', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm'))
                _headx = False
            print(_outstr.format(ang, run, _pos, rs[0], rs[1]-rs[0], rs[2]-rs[0], rs[3]-rs[0], rs[4]-rs[0], rs[5]-rs[0]))
        cens = np.array(cens)
        if plot: self.plot_points(cens, color='green', marker='^')
        return cens, rss, chis
        
def testMiscutOff1Ana(Rm, theta, alpha, d=dSi111):
    """test miscut offsets NOT WORKING YET!!!"""
    tv = RcVert(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    tv_mo = tv.get_miscut_off()
    th = RcHoriz(Rm=Rm, theta0=theta, alpha=alpha, d=d)
    th_mo = th.get_miscut_off()
    print('RcVert: {0}'.format(tv_mo))
    print('RcHor: {0}'.format(th_mo))

### http://stackoverflow.com/questions/15481242/python-optimize-leastsq-fitting-a-circle-to-3d-set-of-points
def distanceToPlane(p0, n0, p):
    return np.dot(np.array(n0), np.array(p) - np.array(p0))    

def residualsPlane(parameters, dataPoint):
    px, py, pz, theta, phi = parameters
    nx, ny, nz = math.sin(theta)*math.cos(phi),\
                 math.sin(theta)*math.sin(phi), math.cos(theta)
    distances = [distanceToPlane([px,py,pz], [nx,ny,nz], [x,y,z])\
                 for x,y,z in dataPoint]
    return distances

def residualsCircle(parameters, dataPoint):
    r, s, Ri = parameters
    planePointArr = s*sArr + r*rArr + np.array(point)
    distance = [np.linalg.norm( planePointArr-np.array([x,y,z]))\
                 for x,y,z in dataPoint]
    res = [(Ri-dist) for dist in distance]
    return res
    
if __name__ == "__main__":
    plt.close('all')
    #pass
    #testSagOff(250., 35., 150., aL=12.)
    #dres = testChiOpt()
    #testAzOff(0.5)
    #dres = testDetMove()
    #testMiscutOff1Ana(500., 65., 36.)
    import math
    #t0 = testSagFocus()
    #t1 = testFrictionPrototype(240., 65.)
    #t = testFrictionPrototypeInMethod(240., 65.)
    fname = '2015-06-18-all_points.dat'
    t = TestProtoBender()
    t.read_data(fname)
    ang, run, pos = 5, 0, 0.0
    d = t.get_dats(ang, run, pos=pos)[1]
    t.eval_data_th0s(ang, run, plot=False)
    dpj = [t.get_projection_point(d[idx], t.sp) for idx in range(12)]
    #t.plot_points(d)
    #a = t.get_intersect_lines(d[0], d[6], d[5], d[11])
    #ap = t.get_intersect_lines(dp[0], dp[6], dp[5], dp[11])
    #t.test_point_on_plane(a, t.sp) #not on plane
    #t.test_point_on_plane(ap, t.sp)
    #print('plotting it in green')
    #t.fig_ax.scatter(ap[0], ap[1], ap[2], color='green', marker='o')
    #plt.draw()

    cens, rss, chis = t.eval_data_rs(ang, run, do_test=False, plot=False)
    #t.eval_data(5,0)
    #t.get_meas_rs(0, 0, set_sp=True)

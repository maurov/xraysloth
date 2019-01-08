#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Analytical expression of $\Delta \theta (x, z)$ from Wittry

"""
from __future__ import print_function
import sys, os
import math
import numpy as np
import numpy.ma as ma

from sloth.io.specfile_writer import SpecfileDataWriter

# ----------------
# Global variables
# ----------------
DEG2RAD = 0.017453292519943295 # np.pi / 180
RAD2DEG = 57.29577951308232 # 180 / np.pi

# from Saint-Gobain (SG) crystals
SI_ALAT = 5.431 # cubic
SI_2D111 = 6.271  # from Matjaz
GE_ALAT = 5.658 # cubic
INSB_ALAT = 6.48 # cubic
SIO2_A = 4.913 # beta-quartz, hexagonal
SIO2_C = 5.405
SIO2_2D101 = 6.684 # from SG
#SIO2_2D100 = 8.514 # from SG
SIO2_2D100 = 8.510 # from Matjaz
INSB_2D111 = 7.480 # from SG

#
DEBUG = False

def mapCase2Num(case):
    dc2n = {'Johann' : 1,
            'Jn' : 1,
            'Johansson' : 2,
            'Js' : 2,
            'Spherical plate' : 3,
            'Spherical Jn' : 3,
            'SphJn' : 3,
            'Spherical Johansson' : 4,
            'Spherical Js' : 4,
            'SphJs' : 4,
            'Wittry' : 5,
            'Toroidal Js' : 5,
            'TorJs' : 5,
            'Js 45 deg focusing' : 6,
            'Js45focus' : 6,
            'Js focusing' : 7,
            'JsFocus' : 7,
            'Berreman' : 8,
            'Jn focusing' : 9,
            'JnFocus' : 9}
    try:
        return dc2n[case]
    except:
        return 0

def mapNum2Case(case, mode='label'):
    if (mode == 'label'):
        dn2c = {1 : 'Jn',
                2 : 'Js',
                3 : 'SphJn',
                4 : 'SphJs',
                5 : 'TorJs',
                6 : 'Js45focus',
                7 : 'JsFocus',
                8 : 'Berreman',
                9 : 'JnFocus'}
    else:
        dn2c = {1 : 'Johann',
                2 : 'Johansson',
                3 : 'Spherical Jn',
                4 : 'Spherical Johansson',
                5 : 'Toroidal Js',
                6 : 'Js 45 deg focusing',
                7 : 'Js focusing',
                8 : 'Berreman',
                9 : 'Jn focusing'}
    try:
        return dn2c[case]
    except:
        return 'Unknown'

def dThetaXZ(x, z, thetab, case=None):
    """Analytical espression of the angular deviation from Bragg
    reflection over a diffractor in conventional point-to-point
    focusing geometries

    Parameters
    ==========
    x, z : masked array of floats
           2D meshgrid where to evaluate dThetaXZ 
    thetab : float
             Bragg angle [deg]
    case : int or str
           diffractor geometries
           1 or 'Johann' or 'Jn' [cylindrical]
           2 or 'Johansson' or 'Js' [cylindrical]
           3 or 'Spherical plate' or 'Spherical Jn' or 'SphJn'
           4 or 'Spherical Johansson' or 'Spherical Js' or 'SphJs'
           5 or 'Wittry' or 'Toroidal Js' or 'TorJs'
           6 or 'Js 45 deg focusing' or 'Js45focus'
           7 or 'Js focusing' or 'JsFocus'
           8 or 'Berreman'
           9 or 'Jn focusing' or 'JnFocus'

    Returns
    =======
    dThetaXZ : 2D masked array
    
    Notes
    =====
    The following expression is taken from table I in
    [Wittry:1992_JAP]_. This is the same of Eq.12-13 in [Pestehe2]_
    and holds within the following approximations:

    - the source is an ideal point source located on the Rowland circle
    - the diffractor size is small compared with the radius of the focal circle

    .. math::

    \begin{eqnarray}\label{eq:dthetaxz}
    \Delta \theta (x,z) = A_1 x^2 + A_2 x^3 + A_3 z^2 + A_4 xz^2 \nonumber \\
    where: \nonumber \\
    A_1 = \cot \theta_B \left( 1-\frac{1}{2R_{1}} \right) \nonumber \\
    A_2 = \cot^2\ \theta_B \left( 1-\frac{1}{2R_{1}} \right) \nonumber \\
    A_3 = \frac{\tan \theta_B}{2} \left[ \frac{1}{R_{2}} - \frac{1}{R_{2}^{\prime}} + \frac{1}{\sin \theta_{B}^{2}} \left( \frac{2}{R_{2}^{\prime}} - \frac{1}{R_{2}} -1 \right) - A_{4}^{\prime} \right] \nonumber \\
    A_4 = \frac{1}{2} \left[ \frac{1}{R_{2}} + \frac{1}{\sin \theta_{B}^{2}} \left( \frac{2}{R_{2}^{2}} - \frac{1}{R_{2}} -2 \right) \right] - \frac{A_{4}^{\prime}}{2} \nonumber \\
    A_4^{\prime} = \frac{1-R_{2}^{\prime}}{R_{2}^{\prime}^{2}} \nonumber\\
    \end{eqnarray}
    
    .. [Wittry:1992_JAP] D. Wittry and S. Sun, J. Appl. Phys. **71** (1992) 564
    .. [Pestehe2] S. J. Pestehe, J. Appl. Cryst. **45** (2012) 890-901

    The parametrization is expressed with 4 radii: 1) in the
    meridional (dispesion) direction (x), R$_{1}$ and R$_{1}^\prime$
    and 2) in the sagittal (focusing) direction (z), R$_{2}$ and
    R$_{2}^\prime$. In each direction the two radii, R and R$^\prime$,
    are for the crystal surface and planes, respectively. The
    implemented cases are the following ones:

    |------+----------------------+----------+----------------+------------------+------------------|
    | Case | Name                 |  R$_{1}$ | R$_{1}^\prime$ | R$_{2}$          | R$_{2}^\prime$   |
    |      |                      |  surface |         planes | surface          | planes           |
    |------+----------------------+----------+----------------+------------------+------------------|
    |    1 | Johann (Jn)          |       1. |             1. | $\infty$         | $\infty$         |
    |    2 | Johansson (Js)       |      0.5 |             1. | $\infty$         | $\infty$         |
    |    3 | Spherical Jn (SphJn) |       1. |             1. | 1.               | 1.               |
    |    4 | Spherical Js (SphJs) |      0.5 |             1. | 0.5              | 1.               |
    |    5 | Wittry (TorJs)       |      0.5 |             1. | 1.               | 1.               |
    |    6 | Js 45 deg focusing   |      0.5 |             1. | 0.5              | 0.5              |
    |    7 | Js focusing          |      0.5 |             1. | $\sin^2(\theta)$ | $\sin^2(\theta)$ |
    |    8 | Berreman             | $\infty$ |             1. | $\sin^2(\theta)$ | $\sin^2(\theta)$ |
    |    9 | Jn focusing          |       1. |             1. | $\sin^2(\theta)$ | $\sin^2(\theta)$ |
    |------+----------------------+----------+----------------+------------------+------------------|

    It is important to note that all the coordinates are given in
    units of R$_{1}^\prime$, the bending radius of the crystal
    planes. This is crucial for converting to real dimensions (mm).

    """
    rthetab = np.deg2rad(thetab)
    # CASES
    if (case == 1 or case == 'Johann' or case == 'Jn'):
        R1 = 1.
        R1p = 1.
        R2 = np.inf
        R2p = np.inf
    elif (case == 2 or case == 'Johansson' or case == 'Js'):
        R1 = 0.5
        R1p = 1.
        R2 = np.inf
        R2p = np.inf
    elif (case == 3 or case == 'Spherical plate' or case == 'Spherical Jn' or case == 'SphJn'):
        R1 = 1.
        R1p = 1.
        R2 = 1.
        R2p = 1.
    elif (case == 4 or case == 'Spherical Johansson' or case == 'Spherical Js' or case == 'SphJs'):
        R1 = 0.5
        R1p = 1.
        R2 = 0.5
        R2p = 1.
    elif (case == 5 or case == 'Wittry' or case == 'Toroidal Js' or case == 'TorJs'):
        R1 = 0.5
        R1p = 1.
        R2 = 1.
        R2p = 1.
    elif (case == 6 or case == 'Js 45 deg focusing' or case == 'Js45focus'):
        R1 = 0.5
        R1p = 1.
        R2 = 0.5
        R2p = 0.5
    elif (case == 7 or case == 'Js focusing' or case == 'JsFocus'):
        R1 = 0.5
        R1p = 1.
        R2 = math.sin(rthetab)**2
        R2p = math.sin(rthetab)**2
    elif (case == 8 or case == 'Berreman'):
        R1 = np.inf
        R1p = 1.
        R2 = math.sin(rthetab)**2
        R2p = math.sin(rthetab)**2
    elif (case == 9 or case == 'Jn focusing' or case == 'JnFocus'):
        R1 = 1.
        R1p = 1.
        R2 = math.sin(rthetab)**2
        R2p = math.sin(rthetab)**2
    elif (case == 10 or case == 'Von Hamos' or case == 'VH'):
        R1 = np.inf
        R1p = np.inf
        R2 = 1.
        R2p = 1.
    else:
        raise NameError("case '{0}' unknown".format(case))

    # COEFFICIENTS
    if (R2p == 1. or R2p == np.inf):
        A4p = 0.
    else:
        A4p = (1. - R2p) / (R2p**2) 
    A1 = (1./math.tan(rthetab)) * (1. - 1./(2.*R1))
    A2 = (1./math.tan(rthetab))**2 * (1. - 1./(2.*R1))
    A3 = (math.tan(rthetab)/2.) * ( (1./R2) - (1./(R2p**2)) ) + ( 1./(2.*math.sin(rthetab)*math.cos(rthetab)) ) * ( (2./R2p) - (1./R2) - 1.)
    #A4 = (1./(2.*R2)) - (1./(4.*R2p)) + (1/(4.*R2p**2)) + (1./(math.sin(rthetab)**2)) * ((1./R2p) - (1./(2*R2)) - 1.)
    A4 = (1./(2.*R2)) + (1./(2.*R2p)) - (1/(2.*R2p**2)) + (1./(math.sin(rthetab)**2)) * ((1./R2p) - (1./(2*R2)) - 1.)

    if DEBUG:
        print('Analytical DeltaTheta(x,z) for {0}'.format(case))
        print('Radii: R1={0}, R1p={1}, R2={2}, R2p={3}'.format(R1, R1p, R2, R2p))
        print('Coefficients:')
        print('A1 = {0}'.format(A1))
        print('A2 = {0}'.format(A2))
        print('A3 = {0}'.format(A3))
        print('A4p = {0}'.format(A4p))
        print('A4 = {0}'.format(A4))
    
    return A1 * x**2 + A2 * x**3 + A3 * z**2 + A4 * x * z**2

def getMeshMasked(mask='circular', r1p=1000., cryst_x=50., cryst_z=10., csteps=1000j):
    """returns two 2D masked arrays representing a (flat) grid of the
    crystal surface
    
    Parameters
    ----------
    mask : str, 'circular'
           shape of the mask: 'circular' or 'rectangular'
    
    r1p : float, [1000.]
          bending radius of the crystal planes in mm (used only to get
          the mesh in normlized units)

    cryst_x : float, [50.]
              radius of circular analyzer in mm (for rectangular mask,
              this is half side in meridional/dispersive x-direction)

    cryst_z : float [10.]
              half side in sagittal/focusing z-direction of the
              rectangular analyzer in mm

    csteps  : grid steps (given as imaginary number!) [1000j]

    """
    zmin, zmax =  -1*cryst_x/r1p, cryst_x/r1p
    xmin, xmax = -1.*cryst_x/r1p, cryst_x/r1p
    x0 = np.linspace(xmin, xmax, csteps.imag)
    z0 = np.linspace(zmin, zmax, csteps.imag)
    xx0, zz0 = np.meshgrid(x0, z0)
    # using a circular crystal of given 'cryst_x'
    xx1, zz1 = np.mgrid[xmin:xmax:csteps, zmin:zmax:csteps]
    cmask = xx1**2 + zz1**2 >= (cryst_x/r1p)**2
    mxx1 = ma.array(xx0, mask=cmask)
    mzz1 = ma.array(zz0, mask=cmask)
    # using a rectangular crystal of given ('cryst_x', 'cryst_z')
    rmask1 = zz1 <= -cryst_z/r1p
    rmask2 = zz1 >= cryst_z/r1p
    mxx2 = ma.array(xx1, mask=ma.mask_or(rmask1, rmask2))
    mzz2 = ma.array(zz1, mask=ma.mask_or(rmask1, rmask2))
    # returns
    if ('circ' in mask.lower()):
        return mxx1, mzz1
    elif ('rect' in mask.lower()):
        return mxx2, mzz2
    else:
        return 0

def getDthetaDats(mxx, mzz, wrc=1.25E-4,
                  cases=['Johann', 'Johansson', 'Spherical plate', 'Wittry'],
                  angles=[15, 45, 75]):
    """calculates data (see returns for details) in given loops
    
    Parameters
    ----------
    mxx, mzz : 2D masked meshgrids, (X,Z) mapping of the analyzer
    wrc : width of the analyzer rocking curve in rad [1.25E-4]
    cases : list of str, see cases in dThetaXZ()
    angles : list of int/floats, Bragg angles 

    Returns
    -------
    dd: dictionary of dictionaries, for each case in cases
    Lists:
        dd[case]['thetaB'] : angles
        #dd[case]['dth'] : $\Delta \theta$(x,z)
        #dd[case]['mdth'] : effective $\Delta \theta$(x,z)
        dd[case]['sa'] : solid angle
        dd[case]['eres'] : energy resolution

    NOTE: dth, mdth not stored (too much space in memory!)
    """
    dd = {} #container dictonary to store results
    for cs in cases:
        dd[cs] = {}
        dd[cs]['thetaB'] = angles
        dd[cs]['dth'] = []
        dd[cs]['mdth'] = []
        dd[cs]['sa'] = []
        dd[cs]['eres'] = []
        print('Angle loop for {0}...'.format(cs))
        for th in angles:
            dth = dThetaXZ(mxx, mzz, th, case=cs)
            # calc effective (< wrc) solid angle and energy resolution
            mdth = ma.masked_where(np.abs(dth) > wrc, dth)
            gridSizeXX = (mxx.data[0][1]-mxx.data[0][0])**2
            gridSizeZZ = (mzz.data[0][1]-mzz.data[0][0])**2
            if not (gridSizeXX == 0.):
                mm = ma.ones(mxx.shape)
                mm = mm * gridSizeXX
            elif not (gridSizeZZ == 0.):
                mm = ma.ones(mzz.shape)
                mm = mm * gridSizeZZ
            else:
                print('Error: 0 grid size in solid angle for {0} at {1} deg'.format(cs, th))
                continue
            mm.mask = mdth.mask
            #eff_area = (mm.sum()/(mm.shape[0]*mm.shape[1]))*(np.pi*(r_cryst**2))
            eff_sa = mm.sum()/math.sin(np.deg2rad(th))
            #eres = math.sqrt((mdth.max()-mdth.min())**2 + wrc**2)/math.tan(np.deg2rad(th))
            eres = math.sqrt((dth.max()-dth.min())**2 + wrc**2)/math.tan(np.deg2rad(th))
            # append to output
            dd[cs]['dth'].append(dth)
            dd[cs]['mdth'].append(mdth)
            dd[cs]['sa'].append(eff_sa)
            dd[cs]['eres'].append(eres)
    #
    return dd

def writeScanDats(dd, fname, scanLabel=None, motpos=None):
    """ writes 1D scan data to SPEC file (refer to 'getMeshMasked' and 'getDthetaDats """
    mots = ['case', 'r1p', 'mask', 'cryst_x', 'cryst_z', 'wrc', 'csteps']
    ncols = ['thetaB', 'sa', 'eres']
    sfw = SpecfileDataWriter(fname)
    if DEBUG: print('scanOnly mode is {0}'.format(sfw.scanOnly))
    sfw.wHeader(title='scan data from dthetaxz.py', motnames=mots)
    for cs in dd.keys():
        dcols = [np.array(dd[cs][ncol]) for ncol in ncols]
        if scanLabel is None:
            _title = '{0}'.format(cs)
        else:
            _title = scanLabel
        sfw.wScan(ncols, dcols, title=_title, motpos=motpos)


if __name__ == '__main__':
    # TESTS in xrayspina/examples/dthetaxz_tests.py
    pass

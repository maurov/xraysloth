#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
braggutils: utilities around the Bragg's law ($ n \lambda = 2 d sin \theta $)
"""

import numpy as np
import warnings

try:
    import scipy.constants.codata as const
    HAS_CODATA = True
    h = const.value("Planck constant in eV s")  # eV s
    c = const.value("speed of light in vacuum") # m s^-1
    HC = h*c
except:
    HAS_CODATA = False
    HC = 1.2398418743309972e-06 # eV * m

### GLOBAL VARIABLES ###
HKL_MAX = 30 # maximum number of hkl index considered
SI_ALAT = 5.431065 # Ang at 25C
GE_ALAT = 5.6579060 # Ang at 25C
INSB_ALAT = 6.48 # cubic
SIO2_A = 4.913 # beta-quartz, hexagonal
SIO2_C = 5.405

DEBUG = True

### UTILS ###
def ev2wlen(energy):
    """convert photon energy (E, eV) to wavelength ($\lambda$, \AA$^{-1}$)"""
    return ( ( HC ) / energy ) * 1e10

def wlen2ev(wlen):
    """convert photon wavelength ($\lambda$, \AA$^{-1}$) to energy (E, eV)"""
    return ( ( HC ) / wlen ) * 1e10

def bragg_ev(d, theta, n=1):
    """return the Bragg energy (eV) for a given d-spacing (\AA) and angle (deg)"""
    return wlen2ev(( 2 * d * np.sin(np.deg2rad(theta)) ) / n)

def theta_b(wlen, d, n=1):
    """return the Bragg angle, $\theta_{B}$, (deg) for a given wavelength
    (\AA$^{-1}$) and d-spacing (\AA)"""
    if not (d == 0):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return np.rad2deg( np.arcsin( ( ( wlen * n ) / ( 2 * d ) ) ) )
        except:
            return 0
    else:
        return 0

def bragg_th(ene, d, n=1):
    """return the Bragg angle, $\theta_{B}$, (deg) for a given energy (eV) and d-spacing (\AA)"""
    return theta_b(ev2wlen(ene), d, n=n)

def cotdeg(theta):
    """return the cotangent (= cos/sin) of theta given in degrees"""
    dtheta = np.deg2rad(theta)
    return np.cos(dtheta) / np.sin(dtheta)

def de_bragg(theta, dth):
    """energy resolution $\frac{\Delta E}{E}$ from derivative of Bragg's law
    
    $|\frac{\Delta E}{E}| = |\frac{\Delta \theta}{\theta} = \Delta \theta \cot(\theta)|$
    """
    return dth * cotdeg(theta)

def sqrt1over(d2m):
    if (d2m == 0):
        return 0
    else:
        return np.sqrt( 1 / d2m )
    
def d_cubic(a, hkl, **kws):
    """d-spacing for a cubic lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    d2m = (h**2 + k**2 + l**2) / a**2
    return sqrt1over(d2m)

def d_tetragonal(a, c, hkl, **kws):
    """d-spacing for a tetragonal lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    d2m = ( h**2 + k**2 ) / a**2 + ( l**2 / c**2 )
    return np.sqrt( 1 / d2m )

def d_orthorhombic(a, b, c, hkl, **kws):
    """d-spacing for an orthorhombic lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    d2m = ( h**2 / a**2 ) + ( k**2 / b**2 ) + ( l**2 / c**2 )
    return sqrt1over(d2m)

def d_hexagonal(a, c, hkl, **kws):
    """d-spacing for an hexagonal lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    d2m = 4./3. * ( ( h**2 + h * k + k**2 ) / a**2 ) + ( l**2 / c**2 )
    return sqrt1over(d2m)

def d_monoclinic(a, b, c, beta, hkl, **kws):
    """d-spacing for a monoclinic lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    rbeta = np.deg2rad(beta)
    d2m = 1. / np.sin( rbeta )**2 \
          * ( ( h**2 / a**2 ) \
              + ( ( h**2 * np.sin( rbeta )**2 ) / b**2 ) \
              + ( l**2 / c**2 ) \
              - ( (2 * h * l * np.cos( rbeta ) / ( a * c ) ) ) )
    return sqrt1over(d2m)

def d_triclinic(a, b, c, alpha, beta, gamma, hkl, **kws):
    """d-spacing for a triclinic lattice"""
    h, k, l = hkl[0], hkl[1], hkl[2]
    ralpha = np.deg2rad(alpha)
    rbeta = np.deg2rad(beta)
    rgamma = np.deg2rad(gamma)
    cosralpha = np.cos(ralpha)
    cosrbeta = np.cos(rbeta)
    cosrgamma = np.cos(rgamma)
    V = a * b * c * np.sqrt( 1 - cosralpha**2 - cosrbeta**2 - cosrgamma**2 \
                             + 2 * cosralpha * cosrbeta * cosrgamma )
    d2m = ( 1. / V**2 ) * \
          ( h**2 * b**2 * c**2 * np.sin(ralpha)**2 \
            + k**2 * a**2 * c**2 * np.sin(rbeta)**2 \
            + l**2 * a**2 * b**2 * np.sin(rgamma)**2 \
            + 2 * h * k * a * b * c**2 * ( cosralpha * cosrbeta - cosrgamma ) \
            + 2 * k * l * a**2 * b * c * ( cosrbeta * cosrgamma  - cosralpha ) \
            + 2 * h * l * a * b**2 * c * ( cosralpha * cosrgamma - cosrbeta ) )
    return sqrt1over(d2m)

def findhkl(energy, thetamin=65., crystal='all', retAll=False):
    """findhkl: for a given energy (eV) finds the Si and Ge reflections
    with relative Bragg angle

    Usage
    =====
    findhkl(energy, thetamin, crystal, return_flag)
    
    energy (eV) [required]
    thetamin (deg) [optional, default: 65 deg]
    crystal ('Si', 'Ge', 'all') [optional, default: 'all']

    Output
    ======
    String: "Crystal(hkl), Bragg angle (deg)"
    
    if retAll: ("crystal", h, k, l, bragg_angle_deg)
    """
    if energy is None:
        print(findhkl.__doc__)

    retDat = [("#crystal", "h", "k", "l", "bragg_deg")] 
    import itertools
    def _find_theta(crystal, alat):
        def _structure_factor(idx):
            """ fcc crystal: the structure factor is not 0 if h,k,l
            are all odd or all even zincblende: as fcc but if all even
            (0 is even) then h+k+l = 4n
            """
            #hkl = itertools.product(idx, idx, idx)
            hkl = itertools.combinations_with_replacement(idx, 3)
            for x in hkl:
                # check all even
                if (x[0]%2 == 0 and x[1]%2 == 0 and x[2]%2 == 0) and not ((x[0]+x[1]+x[2])%4 == 0):
                    pass
                else:
                    try:
                        theta = theta_b(ev2wlen(energy), d_cubic(alat, x))
                    except:
                        continue
                    if (theta >= thetamin):
                        print('{0}({1} {2} {3}), {4} {5:2.2f}'.format(crystal, x[0], x[1], x[2], 'Bragg', theta))
                        if retAll: retDat.append((crystal, x[0], x[1], x[2], theta))
                            
        ###
        _structure_factor(reversed(range(1, HKL_MAX, 2))) # all permutations of odd (h,k,l)
        _structure_factor(reversed(range(0, HKL_MAX, 2))) # all permutations of even (h,k,l)
    if crystal == 'Si':
        _find_theta('Si', SI_ALAT)
    elif crystal == 'Ge':
        _find_theta('Ge', GE_ALAT)
    else:
        _find_theta('Si', SI_ALAT)
        _find_theta('Ge', GE_ALAT)

if __name__ == '__main__':
    pass

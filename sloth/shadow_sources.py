#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_sources: custom wrapper classes of *ShadowSource* from
Orange-Shadow_ (SHADOW3_ project)

.. note:: requires python3.x

.. note:: ShadowSource is designed as a final class, this is why the
first class, *SwSource* is a wrapper class and does not inherit from
*ShadowSource*. It is not elegant, but this will keep the
compatibility with the whole (SHADOW3_ project).

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow

"""
__author__ = "Mauro Rovezzi"
__credits__ = "Luca Rebuffi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014-2015"

import sys, os, copy, math
import numpy as np

# requirements for ShadowSource
HAS_PY3 = False
HAS_OSHADOW = False
if sys.version_info >= (3,2,0): HAS_PY3 = True
try:
    from orangecontrib.shadow.util.shadow_objects import ShadowSource
    HAS_OSHADOW = True
except:
    pass

class SwSource(object):
    """wrapper to ShadowSource"""
    
    def __init__(self):
        if not (HAS_PY3 and HAS_OSHADOW): raise ImportError("Orange-Shadow not found")
        self.sw_src = self.create_instance()

    def create_instance(self):
        return ShadowSource.create_src()

    def get_instance(self):
        return self.sw_src

class FluoSource(SwSource):
    
    def __init__(self):
        """mimic a divergent fluorescence source
        default: point source w conical angular divergence w uniform energy distribution
        """
        super(FluoSource, self).__init__()
        
        self.set_sampling()
        self.set_spatial_type()
        self.set_angle_distr()
        self.set_energy_distr()
        self.set_polarization()

        self.sw_src.src.F_OPD = 1 #store optical paths, now deprecated: fixed value

    def set_rays(self, nrays=10000, seed=0):
        """set the number of rays of the source and the seed (0=random)"""
        self.sw_src.src.NPOINT = nrays
        if (seed % 2 == 0): seed += 1
        self.sw_src.src.ISTAR1 = seed

    def set_sampling(self, fgrid=0, **kws):
        """source modelling type -- spatial/momentum
            Parameters
            ----------
            fgrid : int, 0
                    0 RANDOM/RANDOM
                    1 GRID/GRID
                    2 GRID/RANDOM
                    3 RANDOM/GRID
                    4 ELLIPSE in phase/RANDOM on the ellipse
                    5 ELLIPSE in phase/GRID on the ellipse
        """
        if not fgrid == 0:
            print('Only RANDOM/RANDOM works, revert back to it!')
            fgrid = 0
        self.sw_src.src.FGRID = fgrid

        #N.B. if not RANDOM/RANDOM
        #if fgrid>0:
        #    self.sw_src.src.IDO_VX = <grid points in x'>
        #    self.sw_src.src.IDO_VZ = <grid points in z'>
        #    self.sw_src.src.IDO_X_S = <grid points in x>
        #    self.sw_src.src.IDO_Y_S = <grid points in y>
        #    self.sw_src.src.IDO_Z_S = <grid points in z>
        #    self.sw_src.src.N_CIRCLE = <radial grid points>
        #    self.sw_src.src.N_CONE = <concentrical grid points >

    def set_spatial_type(self, fsour=0, wxsou=0.05, wzsou=0.05, fsource_depth=1, wysou=0.):
        """spatial source type/shape in X-Z plane
        
        Parameters
        ----------
        fsour : int, 1
                0 point
                1 rectangle
                2 ellipse
                3 gaussian
        wxsou : float, 0.05
                for fsour=1,2; source width (X) [cm]
        wzsou : float, 0.05
                for fsour=1,2; source height (Z) [cm]
        fsource_depth : int, 1
                source depth (Y). Options are: no depth (1),
                flat depth (2), gaussian (3), synchrotron
                depth (4)
        wysou : float, 0.
                for fsource_depth=2; source depth (Y)
        """
        self.FSOUR = fsour

        if fsour == 1 or fsour == 2:
            self.sw_src.src.WXSOU = wxsou
            self.sw_src.src.WZSOU = wzsou
        elif fsour == 3: #gaussian
            self.sw_src.src.SIGMAX = wxsou
            self.sw_src.src.SIGMAZ = wzsou

        self.sw_src.src.FSOURCE_DEPTH = fsource_depth

        if fsource_depth == 1:
            self.sw_src.src.WYSOU = wysou
        elif fsource_depth == 2:
            self.sw_src.src.SIGMAY = wysou

    def set_angle_distr(self, fdistr=5, cone=(0.0, 0.1),\
                        hdiv=(0.0, 0.0), vdiv=(6E-5, 6E-5), sigd=(0.0, 0.0)):
        """angle distribution
        
        Parameters
        ----------
        fdistr : int, 1
                 1 flat
                 2 uniform *TODO*
                 3 gaussian *TODO*
                 4 synchrotron *TODO*
                 5 conical
                 6 exact synchrotron *TODO*
        cone : tuple of floats, (0.0, 0.1)
               for fdistr=5; (minimum, maximum) half divergence [rad]
        hdiv : tuple of floats, (0.0, 0.0)
               horizontal divergence (+X, -X) (right, left) side mirror [rad]
        vdiv : tuple of floats, (6E-5, 6E-5)
               vertical divergence in (+Z, -Z) (upstream, downstream) mirror [rad]
        sigd : tuple of floats, (0.0, 0.0)
               for fdistr=3; sigma (horizontal, vertical) (X, Z) [rad]
        """
        self.sw_src.src.FDISTR = fdistr
        if fdistr == 1 or fdistr == 2:
            self.sw_src.src.HDIV1 = hdiv[0]
            self.sw_src.src.HDIV2 = hdiv[1]
            self.sw_src.src.VDIV1 = vdiv[0]
            self.sw_src.src.VDIV2 = vdiv[1]
        elif fdistr == 3:
            self.sw_src.src.HDIV1 = hdiv[0]
            self.sw_src.src.HDIV2 = hdiv[1]
            self.sw_src.src.VDIV1 = vdiv[0]
            self.sw_src.src.VDIV2 = vdiv[0]
            self.sw_src.src.SIGDIX = sigd[0]
            self.sw_src.src.SIGDIZ = sigd[1]
        elif fdistr == 5:
            self.sw_src.src.CONE_MIN = cone[0]
            self.sw_src.src.CONE_MAX = cone[1]
        else:
            raise Exception("Deprecated")

    def get_divergence(self):
        """return a tuple with current source divergence"""
        if self.sw_src.src.FDISTR == 1 or self.sw_src.src.FDISTR==2:
            return (self.sw_src.src.HDIV1, self.sw_src.src.HDIV2, self.sw_src.src.VDIV1, self.sw_src.src.VDIV2)
        elif self.sw_src.src.FDISTR == 3:
            return (self.sw_src.src.HDIV1, self.sw_src.src.HDIV2, self.sw_src.src.VDIV1, self.sw_src.src.VDIV2, self.sw_src.src.SIGDIX, self.sw_src.src.SIGDIZ)
        elif self.sw_src.src.FDISTR == 5:
            return (self.sw_src.src.CONE_MIN, self.sw_src.src.CONE_MAX)
        else:
            return None

    def set_energy_distr(self, f_color=3, f_phot=0, phn=[5.0E3, 10.0E3], rln=[0.0]):
        """photon energy distribution
        Parameters
        ----------
        f_color : int, 3
                  1 single energy
                  2 mutliple discrete energies, up to 10 energies
                  3 uniform energy distribution
                  4 relative intensities
        f_phot : int, 0
                 defines whether the photon energy will be specified
                 in eV (0) or Angstroms (1)
        phn : list of floats, [5E3, 10E3]
              photon energies up to 10
        rln : list of floats, [0.0]
              relative intensities up to 10
        """
        self.sw_src.src.F_COLOR = f_color
        self.sw_src.src.F_PHOT = f_phot

        if f_color == 1:
            self.sw_src.src.PH1  = phn[0]
        elif f_color == 2:
            phn.extend([0.0 for x in range(10)])
            self.sw_src.src.PH1  = phn[0]
            self.sw_src.src.PH2  = phn[1]
            self.sw_src.src.PH3  = phn[2]
            self.sw_src.src.PH4  = phn[3]
            self.sw_src.src.PH5  = phn[4]
            self.sw_src.src.PH6  = phn[5]
            self.sw_src.src.PH7  = phn[6]
            self.sw_src.src.PH8  = phn[7]
            self.sw_src.src.PH9  = phn[8]
            self.sw_src.src.PH10 = phn[9]
        elif f_color == 3:
            self.sw_src.src.PH1  = phn[0]
            self.sw_src.src.PH2  = phn[1]
        elif f_color == 4:
            phn.extend([0.0 for x in range(10)])
            self.sw_src.src.PH1  = phn[0]
            self.sw_src.src.PH2  = phn[1]
            self.sw_src.src.PH3  = phn[2]
            self.sw_src.src.PH4  = phn[3]
            self.sw_src.src.PH5  = phn[4]
            self.sw_src.src.PH6  = phn[5]
            self.sw_src.src.PH7  = phn[6]
            self.sw_src.src.PH8  = phn[7]
            self.sw_src.src.PH9  = phn[8]
            self.sw_src.src.PH10 = phn[9]
            rln.extend([0.0 for x in range(10)])
            self.sw_src.src.RL1  = rln[0]
            self.sw_src.src.RL2  = rln[1]
            self.sw_src.src.RL3  = rln[2]
            self.sw_src.src.RL4  = rln[3]
            self.sw_src.src.RL5  = rln[4]
            self.sw_src.src.RL6  = rln[5]
            self.sw_src.src.RL7  = rln[6]
            self.sw_src.src.RL8  = rln[7]
            self.sw_src.src.RL9  = rln[8]
            self.sw_src.src.RL10 = rln[9]
        else:
            raise Exception("wrong F_COLOR")

    def set_polarization(self, f_polar=1, f_coher=0, pol_angle=0.0, pol_deg=1.0):
        """polarization
        Parameters
        ----------
        f_polar : int, 1
                  flag defining whether or not to generate the A
                  vectors: yes (1), no (0)
        f_coher : int, 0
                  if generating the A vectors, defines whether the
                  light is incoherent (0), or coherent (1)
        pol_angle : float, 0.0
                    phase diff [deg, 0=linear, +90=ell/right]
        pol_deg : float, 1.0
                  polarization degree [cos_s/(cos_s+sin_s)]
                  0 : linear vertical
                  1 : linear horizontal
                  0.5 : linear 45 deg
        """
        self.sw_src.src.F_POLAR = f_polar
        if f_polar==1:
            self.sw_src.src.F_COHER = f_coher
            self.sw_src.src.POL_ANGLE = pol_angle
            self.sw_src.src.POL_DEG = pol_deg


if __name__ == "__main__":
    pass

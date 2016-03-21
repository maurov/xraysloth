
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_spectro1: an utility toolbox to raytrace a
wavelength-dispersive spectrometer with SHADOW3_ from Python

.. note:: this is only an idea (e.g. example) on how to automatize
          some repetitive steps in SHADOW3_ as, for example, scanning
          a variable. At the moment the object is messy and not
          general at all. It is based on a specific example that
          requires a given workspace as a starting point to generate
          the 'start.xx' files. This can be used only to get inspired,
          but the correct way to extend SHADOW3_ functionality is to
          inherit from ShadowLibExtensions!!! Please, do not inherit
          from this object. It will be soon deprecated. See also the
          current develpment of related projects as ShadowOui_,
          OASYS1_, Orange-Shadow_ or Orange-XOPPY_.

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _ShadowOui: https://github.com/lucarebuffi/ShadowOui
.. _OASYS1: https://github.com/lucarebuffi/OASYS1
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _Orange-XOPPY: https://github.com/srio/Orange-XOPPY

TODO
----

- re-structure the whole thing by inheriting from ShadowLibExtensions
  or Orange-Shadow

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014-2016"

import sys, os, platform
import math
import numpy as np
# see README.rst how to install XOP and SHADOW3
HAS_SHADOW = False
try:
    from Shadow import ShadowLib
    from Shadow import ShadowLibExtensions
    from Shadow import ShadowTools
    ShadowTools.plt.ion()
    HAS_SHADOW = True
except:
    print(sys.exc_info()[1])
    pass

from PyMca5.PyMcaGui.plotting import PlotWindow, ImageView
    
#dirty way to import -> TODO: clean when this will be a package
_curDir = os.path.dirname(os.path.realpath(__file__))
_parDir = os.path.realpath(os.path.join(_curDir, os.path.pardir))
sys.path.append(_parDir)
from peakfit import fit_splitpvoigt, fit_results
from bragg import (d_cubic, d_hexagonal,\
                   d_tetragonal, d_orthorhombic,\
                   d_monoclinic, d_triclinic, bragg_ev,\
                   SI_ALAT) 
from rowland import RcHoriz

####################################################################
# FOR WEIRD BUG ON LINUX - STRING NOT PROPERLY RETURNED BY BINDING
####################################################################
#https://github.com/lucarebuffi/ShadowOui/blob/master/orangecontrib/shadow/util/shadow_objects.py
def adjust_shadow_string(string_to_adjust):
    if string_to_adjust is None:
        return None
    else:
        if len(string_to_adjust) > 1024:
            temp = str(string_to_adjust[:1023])
            if (len(temp) == 1026 and temp[0] == "b" and temp[1] == "'" and temp[1025] == "'"):
                temp = temp[2:1025]

            return bytes(temp.rstrip(), 'utf-8')
        else:
            return string_to_adjust

def self_repair_src(cls):
    if platform.system() == 'Linux':
        distname, version, codename = platform.linux_distribution()
        distname = distname.lower()
        if distname == 'ubuntu' or distname == 'centos linux' or distname=='debian':
            cls.FILE_SOURCE      = adjust_shadow_string(cls.FILE_SOURCE)
            cls.FILE_BOUND       = adjust_shadow_string(cls.FILE_BOUND)
            cls.FILE_TRAJ       = adjust_shadow_string(cls.FILE_TRAJ)
            
def self_repair_oe(cls):
    if platform.system() == 'Linux':
        distname, version, codename = platform.linux_distribution()
        distname = distname.lower()
        if distname == 'ubuntu' or distname == 'centos linux' or distname=='debian':
            FILE_ABS = [adjust_shadow_string(cls.FILE_ABS[0]),
                        adjust_shadow_string(cls.FILE_ABS[1]),
                        adjust_shadow_string(cls.FILE_ABS[2]),
                        adjust_shadow_string(cls.FILE_ABS[3]),
                        adjust_shadow_string(cls.FILE_ABS[4]),
                        adjust_shadow_string(cls.FILE_ABS[5]),
                        adjust_shadow_string(cls.FILE_ABS[6]),
                        adjust_shadow_string(cls.FILE_ABS[7]),
                        adjust_shadow_string(cls.FILE_ABS[8]),
                        adjust_shadow_string(cls.FILE_ABS[9])]
            cls.FILE_ABS = np.array(FILE_ABS)
            cls.FILE_FAC         = adjust_shadow_string(cls.FILE_FAC)
            cls.FILE_KOMA        = adjust_shadow_string(cls.FILE_KOMA)
            cls.FILE_KOMA_CA     = adjust_shadow_string(cls.FILE_KOMA_CA)
            cls.FILE_MIR         = adjust_shadow_string(cls.FILE_MIR)
            cls.FILE_REFL        = adjust_shadow_string(cls.FILE_REFL)
            cls.FILE_R_IND_OBJ   = adjust_shadow_string(cls.FILE_R_IND_OBJ)
            cls.FILE_R_IND_IMA   = adjust_shadow_string(cls.FILE_R_IND_IMA)
            cls.FILE_RIP         = adjust_shadow_string(cls.FILE_RIP)
            cls.FILE_ROUGH       = adjust_shadow_string(cls.FILE_ROUGH)
            FILE_SCR_EXT = [adjust_shadow_string(cls.FILE_SCR_EXT[0]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[1]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[2]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[3]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[4]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[5]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[6]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[7]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[8]),
                            adjust_shadow_string(cls.FILE_SCR_EXT[9])]
            cls.FILE_SCR_EXT = np.array(FILE_SCR_EXT)
            cls.FILE_SEGMENT     = adjust_shadow_string(cls.FILE_SEGMENT)
            cls.FILE_SEGP        = adjust_shadow_string(cls.FILE_SEGP)
            cls.FILE_SOURCE      = adjust_shadow_string(cls.FILE_SOURCE)

##################################################
### SOURCES => TODO: move to shadow_sources.py ###
##################################################
class FluoSource(ShadowLibExtensions.Source):
    """mimic a divergent fluorescence source

    geometric source of rectangular shape and conical angular
    distrubution with uniform energy distribution
    """

    def __init__(self, **kws):
        super(FluoSource, self).__init__(**kws)
        self_repair_src(self)
        self.set_rays()
        self.set_sampling()
        self.set_spatial_type()
        self.set_angle_distr()
        self.set_energy_distr()
        self.set_polarization()

    def set_rays(self, nrays=10000, seed=6775431):
        """set the number of rays of the source and the seed"""
        self.NPOINT = nrays
        if (seed % 2 == 0): seed += 1
        self.ISTAR1 = seed
        
    def set_sampling(self, fgrid=0):
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
        self.FGRID = fgrid

    def set_spatial_type(self, fsour=1, wxsou=0.05, wzsou=0.05, fsource_depth=1, wysou=0.):
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
        self.WXSOU = wxsou
        self.WZSOU = wzsou
        self.FSOURCE_DEPTH = fsource_depth

    def set_angle_distr(self, fdistr=1,\
                        cone_min=0.0, cone_max=0.1,\
                        hdiv_pos=0.0, hdiv_neg=0.0,\
                        vdiv_pos=6E-5, vdiv_neg=6E-5):
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
        cone_min : float, 0.0
                   for fdistr=5; minimum half divergence [rad]
        cone_max : float, 0.1
                   for fdistr=5; maximum half divergence [rad]
        hdiv_pos : float, 0.0
                   horizontal divergence in +X (right side mirror) [rad]
        hdiv_neg : float, 0.0
                   horizontal divergence in -X (left side mirror) [rad]
        vdiv_pos : float, 6E-5
                   vertical divergence in +Z (upstream mirror) [rad]
        vdiv_neg : float, 6E-5
                   vertical divergence in -Z (downstream mirror) [rad]

        """
        self.FDISTR = fdistr
        self.CONE_MIN = cone_min
        self.CONE_MAX = cone_max
        self.HDIV1 = hdiv_pos
        self.HDIV2 = hdiv_neg
        self.VDIV1 = vdiv_pos
        self.VDIV2 = vdiv_neg

    def get_div(self):
        """return a tuple with current source divergence"""
        if self.FDISTR == 1:
            return (self.HDIV1, self.HDIV2, self.VDIV1, self.VDIV2)
        elif self.FDISTR == 5:
            return (self.CONE_MIN, self.CONE_MAX)
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
        self.F_COLOR = f_color
        self.F_PHOT = f_phot
        phn.extend([0.0 for x in range(10)])
        self.PH1  = phn[0]
        self.PH2  = phn[1] 
        self.PH3  = phn[2] 
        self.PH4  = phn[3] 
        self.PH5  = phn[4] 
        self.PH6  = phn[5] 
        self.PH7  = phn[6] 
        self.PH8  = phn[7] 
        self.PH9  = phn[8] 
        self.PH10 = phn[9]
        rln.extend([0.0 for x in range(10)])
        self.RL1  = rln[0]
        self.RL2  = rln[1] 
        self.RL3  = rln[2] 
        self.RL4  = rln[3] 
        self.RL5  = rln[4] 
        self.RL6  = rln[5] 
        self.RL7  = rln[6] 
        self.RL8  = rln[7] 
        self.RL9  = rln[8] 
        self.RL10 = rln[9]

    def set_polarization(self, f_polar=1, f_coher=0,
                        pol_angle=0.0, pol_deg=1.0):
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
        """
        self.F_POLAR = f_polar
        self.F_COHER = f_coher
        self.POL_ANGLE = pol_angle
        self.POL_DEG = pol_deg

####################################################################
### OPTICAL ELEMENTS => TODO: move to shadow_optical_elements.py ###
####################################################################
class ShadowOE(ShadowLibExtensions.OE):

    def __init__(self, **kws):
        """
        Empty Shadow optical element (default unit length = 'cm')
        
        Keyword parameters
        ------------------

        """
        super(ShadowOE, self).__init__(**kws)
        self_repair_oe(self)
        # self.set_screens()
        # self.set_empty()
        self.init_empty()
        self.set_unit()
        self.set_output_files()
        self.set_parameters()
        self.set_infinite()

    def init_empty(self):
        """template method pattern"""
        self.FMIRR = 5
        self.F_CRYSTAL = 0
        self.F_REFRAC = 2
        self.F_SCREEN = 0
        self.N_SCREEN = 0
        
    def set_unit(self, length='cm'):
        """set length unit (['cm'], 'mm' or 'm')"""
        if length == 'cm':
            self.DUMMY = 1.0
        elif length == 'mm':
            self.DUMMY = 0.1
        elif length == 'm':
            self.DUMMY = 0.0

    def set_output_files(self, fwrite=1, f_angle=0):
        """optional file output

        Parameters
        ----------

        fwrite : int [1]
                 files to write out
                 0 -> all files
                 1 -> mirror file  only -- mirr [REQUIRED FOR FOOTPRINT]
                 2 -> image file only -- star
                 3 -> none
                 
        f_angle : int [0]
                  write out incident/reflected angles [angle.xx]
                  0 -> no
                  1 -> yes
        """
        self.FWRITE = fwrite
        self.F_ANGLE = f_angle 

    def set_parameters(self, f_ext=0):
        """set internal/calculated (0) parameters vs. external/user
        defined parameters (1)
        """
        self.F_EXT = f_ext

    def set_infinite(self):
        """set infinite dimensions (fhit_c = 0)"""
        self.FHIT_C = 0

    def set_frame_of_reference(self, p, q, deg_inc, deg_refl=None,
                               deg_mirr=0.):
        """set frame of reference

        Parameters
        ----------
        p, q : float
               source, image plane distances [cm]

        deg_inc : float
                  angle of incidence wrt the normal [deg]

        deg_refl : float [None]
                   angle of reflection wrt the normal [deg]
                   if None = deg_inc
        
        deg_mirr : float [0]
                   mirror orientation [deg]
        
        """
        if deg_refl is None: deg_refl = deg_inc
        self.T_SOURCE     = p
        self.T_IMAGE      = q
        self.T_INCIDENCE  = deg_inc
        self.T_REFLECTION = deg_refl
        self.ALPHA        = deg_mirr
 
    def set_dimensions(self, fshape=1, params=np.array([0., 0., 0., 0.])):
        """set finite mirror dimensions (fhit_c = 1)

        Parameters
        ----------

        fshape : int [1]
                 1 : rectangular
                 2 : full ellipse
                 3 : ellipse with hole

        params : array of floats, np.array([0., 0., 0., 0.])
                 params[0] : dimension y plus  [cm] 
                 params[1] : dimension y minus [cm] 
                 params[2] : dimension x plus  [cm] 
                 params[3] : dimension x minus [cm] 
                 
        """
        self.FHIT_C = 1
        self.FSHAPE = fshape
        self.RLEN1  = params[0]
        self.RLEN2  = params[1]
        self.RWIDX1 = params[2]
        self.RWIDX2 = params[3]

class PlaneCrystal(ShadowOE):
    """plane crystal"""
    
    def __init__(self, **kws):
        super(PlaneCrystal, self).__init__(**kws)
        self.init_plane_crystal()
        self.set_reflectivity(f_reflec=0, f_refl=0)

    def init_plane_crystal(self):
        """template method pattern"""
        self.FMIRR = 5
        self.F_CRYSTAL = 1
        self.FILE_REFL = bytes("", 'utf-8')
        self.F_REFLECT = 0
        self.F_BRAGG_A = 0
        self.A_BRAGG = 0.0

    def set_reflectivity(self, f_reflec=0, f_refl=0):
        """set reflectivity of surface

        Parameters
        ----------

        f_reflec : int [0]

                   reflectivity of surface: no reflectivity dependence
                   (0), full polarization dependence (1), no
                   polarization dependence / scalar (2)

        f_refl : int [0]

                 for f_reflec=1,2 - source of optical constants: file
                 generated by PREREFL (0), keyboard (1), multilayers
                 (2).

        """
        self.F_REFLEC = f_reflec
        self.F_REFL = f_refl

    def set_crystal(self, file_refl, a_bragg=0.0, thickness=0.1,\
                    tune_auto=0, tune_units=0, tune_ev=0.0, tune_ang=0.0):
        """set crystal (f_crystal = 1)

        Parameters
        ----------
        
        file_refl : string
                    file containing the crystal parameters
                    for f_reflec=1,2 and f_refl=0: file with optical
                    constants
                    for f_reflec=1,2 and f_refl=2: file with
                    thicknesses and refractive indices for
                    multilayers

        a_bragg : float [0.0]
                  asymmetric angle between crystal planes and surface [deg]

        thickness : float [0.1]
                    crystal thickness (cm)
        
        tune_auto : int [0]
                    flag: auto tune angle of grating or crystal
                    -> yes (1), no (0)
        
        tune_units : int [0]
                     flag: tune to eV (0) or Angstroms (1)
        
        tune_ev : float [0.]
                  energy (eV) to autotune
        
        tune_ang : float [0.]
                   wavelength to autotune

        """
        self.F_CRYSTAL = 1
        self.FILE_REFL = adjust_shadow_string(file_refl)

        if a_bragg != 0.0: self.set_asymmetric_cut(a_bragg, thickness)

        if tune_auto == 0:
            self.F_CENTRAL = 0
        else:
            self.set_auto_tuning(f_phot_cent=tune_units,
                                 phot_cent=tune_ev,
                                 r_lambda=tune_ang)

    def set_auto_tuning(self, f_phot_cent=0, phot_cent=0.0, r_lambda=0.0):
        """set auto tuning of grating or crystal [f_central = 1]
        
        Parameters
        ----------
        
        f_phot_cent : [0] flag, tune to eV (0) or Angstroms (1)

        phot_cent : [0.0] photon energy (eV) to autotune grating/crystal to.

        r_lambda : [0.0] Angstroms to autotune grating/crystal to.

        """
        self.F_CENTRAL = 1
        self.F_PHOT_CENT = f_phot_cent
        self.PHOT_CENT = phot_cent
        self.R_LAMBDA = r_lambda

    def set_mosaic(self, mosaic_seed=4732093, spread_mos=0.0, thickness=0.1):
        """set mosaic crystal (f_mosaic = 1)

        Parameters
        ----------
        
        mosaic_seed : int [4732094]
        
                      random number seed for mosaic crystal calculations
        
        spread_mos : float [0.0]
        
                     mosaic spread FWHM (degrees)

        thickness : float [0.1]

                    crystal thickness (cm)

        Notes
        -----
        mutually exclusive with asymmetric cut and Johansson
        """
        self.F_MOSAIC = 1
        self.MOSAIC_SEED = mosaic_seed
        self.SPREAD_MOS = spread_mos
        self.THICKNESS = thickness

        #MUTUALLY EXCLUSIVE!
        self.F_BRAGG_A = 0
        self.F_JOHANSSON = 0

    def set_asymmetric_cut(self, a_bragg, thickness, order=-1.):
        """set asymmetric cut (f_bragg_a = 1)

        Parameters
        ----------
        a_bragg : float
                  asymmetric angle between crystal planes and surface [deg]
        
        thickness : float
                    thickness [cm]
        
        order : float [-1]
                diffraction order, negative inside (European convention)
                below (-1.) / onto (1.) Bragg planes


        Notes
        -----
        mutually exclusive with mosaic
        
        """
        self.F_BRAGG_A = 1
        self.F_MOSAIC = 0

        self.A_BRAGG = a_bragg
        self.THICKNESS = thickness
        self.ORDER = order
        
    def set_johansson(self, r_johansson):
        """set Johansson geometry (f_johansson = 1)

        Parameters
        ----------

        r_johansson : float
                      Johansson radius, that is, radius of the crystal planes (cm)

        Notes
        -----
        mutually exclusive with mosaic
        """
        self.F_EXT = 1
        self.F_JOHANSSON = 1
        self.R_JOHANSSON = r_johansson
        self.RMIRR = r_johansson / 2.
        
        #MUTUALLY EXCLUSIVE!
        self.F_MOSAIC = 0

class SphericalCrystal(PlaneCrystal):
    """spherical (Johann) crystal"""
    
    def __init__(self, convex=False, cyl_ang=None, rmirr=None, **kws):
        """if no keyword arguments given: init a spherical concave crystal

        Parameters
        ----------

        convex : boolean, False
                 is convex?
        
        cyl_ang : float, None
                  cylinder orientation [deg] CCW from X axis]
                  0 -> meridional bending
                  90. -> sagittal bending
        
        rmirr : float, None
                meridional radius

        """
        super(SphericalCrystal, self).__init__(**kws)
        self.init_spherical_crystal()

        # convex/concave
        if convex:
            f_convex = 1
        else:
            f_convex = 0
        self.set_curvature(f_convex)
        
        # cylindrical
        if cyl_ang is not None:
            self.set_cylindrical(cyl_ang)
            
        # radius of curvature (internal or external)
        if rmirr is None:
            self.set_calculated_shape_params(self, **kws)
        else:
            self.set_radius(rmirr)

    def init_spherical_crystal(self):
        """template method pattern"""
        self.FMIRR = 1
        self.F_CRYSTAL = 1
        self.FILE_REFL = bytes("", 'utf-8')
        self.F_REFLECT = 0
        self.F_BRAGG_A = 0
        self.A_BRAGG = 0.0
        self.F_REFRAC = 0

    def set_radius(self, rmirr):
        """set radius of curvature of the surface (rmirr)

        Parameters
        ----------

        rmirr : float
                surface radius of curvature (cm)

        """
        self.F_EXT = 1
        self.RMIRR = rmirr

    def set_curvature(self, f_convex=0):
        """set curvature (concave is default)"""
        self.F_CONVEX = f_convex

    def set_cylindrical(self, cyl_ang):
        """set cylindrical (fcyl = 1)
        
        cyl_ang : float
                  cylinder orientation [deg] CCW from X axis
                  0 -> meridional curvature
                  90. -> sagittal curvature
        """
        self.FCYL = 1
        self.CIL_ANG = cyl_ang

    def set_auto_focus(self, f_default=0, ssour=0.0, simag=0.0, theta=0.0):
        """set auto focus

        Parameters
        ----------

        f_default : int, 0
                    focii coincident with continuation plane - yes
                    (1), no (0)

         ssour : float, 0.0
                 for f_default=0: distance from object focus to the
                 mirror pole
        
         simag : float, 0.0
                 for f_default=0: distance from mirror pole to image
                 focus
        
        theta : float, 0.0
                for f_default=0: incidence angle (degrees)

        """
        self.set_parameters(f_ext=0)
        if f_default == 0:
            self.SSOUR = ssour
            self.SIMAG = simag
            self.THETA = theta

    def set_calculated_shape_params(self, coincident=True, p_cm=0.,
                                    q_cm=0., inc_deg=0.):
        """internally calculated shape parameters"""
        if self.FCYL and self.CYL_ANG == 90.0:
            # sagittal curvature
            self.F_EXT=1

            # RADIUS = (2 F1 F2 sin (theta)) / (F1+F2)
            if coincident:
                p_cm = self.T_SOURCE
                q_cm = self.T_IMAGE
                inc_deg =  self.T_REFLECTION

            self.RMIRR = ( (2 * p_cm * q_cm) / (p_cm + q_cm) ) * math.sin(math.radians(90-inc_deg))
        else:
            self.F_EXT=0
            if coincident:
                self.set_auto_focus(f_default=1)
            else:
                self.set_auto_focus(f_default=0, ssour=p_cm,
                                    simag=q_cm, theta=inc_deg)

##################################################
### PLOTTER => TODO: move to shadow_plotter.py ###
##################################################
class ShadowPlotter(object):
    """ShadowPlotter: plotxy and histo1"""
    def __init__(self):
        #self.pw1 = PlotWindow.PlotWindow()
        #self.pw2 = ImageView.ImageViewMainWindow()
        #self.keep_aspect_ratio(False)
        pass

    def keep_aspect_ratio(self, flag=True):
        """wrapper to self.miw.imageView._imagePlot.keepDataAspectRatio"""
        self.pw2.imageView._imagePlot.keepDataAspectRatio(flag)
        
    def histo1(self, *args, **kws):
        """wrapper to ShadowTools.histo1_old
        
        Plot the histogram of a column, simply counting the rays, or
        weighting with the intensity.  It returns a
        ShadowTools.Histo1_Ticket which contains the histogram data,
        and the figure.

        Parameters
        ----------
        beam : str
               instance with the name of the Shadow binary file to be loaded,
               or a Shadow.Beam() instance.
        col : int
              1   X spatial coordinate [user's unit]
              2   Y spatial coordinate [user's unit]
              3   Z spatial coordinate [user's unit]
              4   X' direction or divergence [rads]
              5   Y' direction or divergence [rads]
              6   Z' direction or divergence [rads]
              7   X component of the electromagnetic vector (s-polariz)
              8   Y component of the electromagnetic vector (s-polariz)
              9   Z component of the electromagnetic vector (s-polariz)
              10   Lost ray flag
              11   Energy [eV]
              12   Ray index
              13   Optical path length
              14   Phase (s-polarization)
              15   Phase (p-polarization)
              16   X component of the electromagnetic vector (p-polariz)
              17   Y component of the electromagnetic vector (p-polariz)
              18   Z component of the electromagnetic vector (p-polariz)
              19   Wavelength [A]
              20   R= SQRT(X^2+Y^2+Z^2)
              21   angle from Y axis
              22   the magnituse of the Electromagnetic vector
              23   |E|^2 (total intensity)
              24   total intensity for s-polarization
              25   total intensity for p-polarization
              26   K = 2 pi / lambda [A^-1]
              27   K = 2 pi / lambda * col4 [A^-1]
              28   K = 2 pi / lambda * col5 [A^-1]
              29   K = 2 pi / lambda * col6 [A^-1]
              30   S0-stokes = |Es|^2 + |Ep|^2
              31   S1-stokes = |Es|^2 - |Ep|^2
              32   S2-stokes = 2 |Es| |Ep| cos(phase_s-phase_p)
              33   S3-stokes = 2 |Es| |Ep| sin(phase_s-phase_p)
        xrange/yrange : tuple or list of 2 float [None]
                        interval of interest for x/y, the data read
                        from the chosen column.
        nbins : int, [50]
                number of bins of the histogram.
        nolost : int [0]
                 0 All rays
                 1 Only good rays
                 2 Only lost rays
        ref : int, [0]
              0 only count the rays (weight==1)
              1 weight with intensity (use col 23 |E|^2 total intensity)
              # if another col is given, it is then used for weight 
        write : int [0]
                0   don't write any file
                1   write the histogram into the file 'HISTO1'.
        title : str, ['HISTO1']
                title of the figure, it will appear on top of the window.
        xtitle/ytitle : str, [None]
                        label for the x axis.
        calfwhm : int [0]
                  0   don't compute the fwhm
                  1   compute the fwhm
        noplot : int [0]
           0   plot the histogram
           1   don't plot the histogram
        orientation : str
                      'vertical'   x axis for data, y for intensity
                      'horizontal'   y axis for data, x for intensity
        plotxy : int, [0]
                 0   standalone version
                 1   to use within plotxy

        Returns
        -------
        ShadowTools.Histo1_Ticket instance.
     
        Raises
        ------
        ArgsError

        """
        return ShadowTools.histo1_old(*args, **kws)

    def histo1_energy(self, *args, **kws):
        """energy histogram

        Parameters
        ----------
        See self.histo1
        
        Returns
        -------
        None: sets self.h1e
        """
        beam = args[0]
        col = 11
        nbins = kws.get('nbins', 500)
        nolost = kws.get('nolost', 1)
        ref = kws.get('ref', 1)
        calfwhm = kws.get('calfwhm', 1)
        noplot = kws.get('noplot', 1)
        write = kws.get('write', 0)
        return self.histo1(beam, col, nbins=nbins, nolost=nolost, ref=ref,\
                           calfwhm=calfwhm, noplot=noplot, write=write)

    def plotxy(self, *args, **kws):
        """wrapper to ShadowTools.plotxy_old

        Draw the scatter or contour or pixel-like plot of two columns
        of a Shadow.Beam instance or of a given shadow file, along
        with histograms for the intensity on the top and right side.

        Parameters
        ----------
        beam : str
               instance with the name of the shadow file to be loaded,
               or a Shadow.Beam initialized instance
        cols1, cols2 : int
              1   X spatial coordinate [user's unit]
              2   Y spatial coordinate [user's unit]
              3   Z spatial coordinate [user's unit]
              4   X' direction or divergence [rads]
              5   Y' direction or divergence [rads]
              6   Z' direction or divergence [rads]
              7   X component of the electromagnetic vector (s-polariz)
              8   Y component of the electromagnetic vector (s-polariz)
              9   Z component of the electromagnetic vector (s-polariz)
              10   Lost ray flag
              11   Energy [eV]
              12   Ray index
              13   Optical path length
              14   Phase (s-polarization)
              15   Phase (p-polarization)
              16   X component of the electromagnetic vector (p-polariz)
              17   Y component of the electromagnetic vector (p-polariz)
              18   Z component of the electromagnetic vector (p-polariz)
              19   Wavelength [A]
              20   R= SQRT(X^2+Y^2+Z^2)
              21   angle from Y axis
              22   the magnituse of the Electromagnetic vector
              23   |E|^2 (total intensity)
              24   total intensity for s-polarization
              25   total intensity for p-polarization
              26   K = 2 pi / lambda [A^-1]
              27   K = 2 pi / lambda * col4 [A^-1]
              28   K = 2 pi / lambda * col5 [A^-1]
              29   K = 2 pi / lambda * col6 [A^-1]
              30   S0-stokes = |Es|^2 + |Ep|^2
              31   S1-stokes = |Es|^2 - |Ep|^2
              32   S2-stokes = 2 |Es| |Ep| cos(phase_s-phase_p)
              33   S3-stokes = 2 |Es| |Ep| sin(phase_s-phase_p)
        nbins : int, 25
                size of the grid (nbins x nbins). It will affect the
                plot only if non scatter.
        nbins_h : int, None
                  number of bins for the histograms
        level : int, 5
                number of level to be drawn. It will affect the plot
                only if contour.
        xrange : tuple or list of length 2, None
                 interval of interest for x, the data read from the
                 chosen column
        yrange : tuple or list of length 2, None
                 interval of interest for y, counts or intensity
                 depending on ref.
        nolost : int, 0
                 0   All rays
                 1   Only good rays
                 2   Only lost rays

        title : str, 'PLOTXY' 
                title of the figure, will appear on top of the window
        xtitle : str, None
                 label for the x axis.
        ytitle : str, None 
                 label for the y axis.
        noplot : int, 0
                 0   plot the histogram
                 1   don't plot the histogram
        calfwhm : int, 0
                  0 don't compute the fwhm
                  1 compute the fwhm and draw it
                  2 in addition to calfwhm=1, it computes now the
                    intensity in a slit of FWHM_h x FWHM_v

        contour : int, 0
                  0   scatter plot
                  1   contour, black & white, only counts (without intensity)
                  2   contour, black & white, with intensity.
                  3   contour, colored, only counts (without intensity)
                  4   contour, colored, with intensity.
                  5   pixelized, colored, only counts (without intensity)
                  6   pixelized, colored, with intensity.

        Returns
        -------
        ShadowTools.Histo1_Ticket instance.
     
        Errors
        ------
        if an error occurs an ArgsError is raised.
        """
        return ShadowTools.plotxy_old(*args, **kws)

    def plotxy_footprint(self, *args, **kws):
        """foot print on optical element

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        ShadowTools.Histo1_Ticket instance
        """
        _beam = kws.get('beam', 'mirr.01')
        _col1 = kws.get('col1', 2)
        _col2 = kws.get('col1', 1)
        _nbins = kws.get('nbins', 101)
        _nolost = kws.get('nolost', 2)
        _title = kws.get('title', r'Footprint')
        _xtitle = kws.get('ytitle', r'Y - mirror meridional direction [cm]')
        _ytitle = kws.get('xtitle', r'X - mirror sagittal direction [cm]')
        _xr, _yr = 1.1, 1.1 # expand x,y ranges
        _xrange = kws.get('xrange', None)
        _yrange = kws.get('yrange', None)
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 5)
        return self.plotxy(_beam, _col1, _col2, nbins=_nbins, nolost=_nolost,\
                           title=_title, xtitle=_xtitle, ytitle=_ytitle,\
                           xrange=_xrange, yrange=_yrange,\
                           calfwhm=_calfwhm, noplot=_noplot,\
                           contour=_contour, level=_level)
        
    def plotxy_image(self, *args, **kws):
        """image of an optical element

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        ShadowTools.Histo1_Ticket instance
        """
        _beam = kws.get('beam', 'star.01')
        _col1 = kws.get('col1', 1)
        _col2 = kws.get('col1', 3)
        _nbins = kws.get('nbins', 101)
        _nolost = kws.get('nolost', 1)
        _title = kws.get('title', r'Image')
        _xtitle = kws.get('xtitle', 'x - sagittal (Hor. focusing) [cm]')
        _ytitle = kws.get('ytitle', 'z - meridional (E dispersion) [cm]')
        _xrange = kws.get('xrange', None)
        _yrange = kws.get('yrange', None) 
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 6)
        return self.plotxy(_beam, _col1, _col2, nbins=_nbins, nolost=_nolost,\
                           title=_title, xtitle=_xtitle, ytitle=_ytitle,\
                           xrange=_xrange, yrange=_yrange,\
                           calfwhm=_calfwhm, noplot=_noplot,\
                           contour=_contour, level=_level)

    def specfileReadXY(self, fname=None, **kws):
        """read x/y from a specfile and set to self.x/self.y

        by default it reads HISTO1 in current dir

        Parameters
        ----------
        fname : str, 'HISTO1'
        scanno : int, 1
        xcol : int, 1
        ycol : int, 4

        Returns
        -------
        None: sets self.x and self.y
        """
        try:
            from PyMca import specfilewrapper as specfile
        except:
            from PyMca import specfile
        
        if fname is None:
            fname = 'HISTO1'
        try:
            sf = specfile.Specfile(fname)
        except:
            print('{0} not found'.format(fname))
            return

        scanno = kws.get('scanno', 1)
        xcol = kws.get('xcol', 1)
        ycol = kws.get('ycol', 4)

        sd = sf.select(str(scanno))
        self.x = sd.datacol(xcol)
        self.y = sd.datacol(ycol)
        sf = 0 # close file       

    def fitSplitPVoigt(self, bkg='No Background',
                       plot=True, show_res=True, **kws):
        """fit self.x/self.y with a split-PseudoVoigt function

        Returns
        -------
        None: sets self.fit and self.pw (plot window)
        """
        self.fit, self.pw = fit_splitpvoigt(self.x, self.y,
                                            bkg=bkg, plot=plot,
                                            show_res=show_res)


    def runHisto1EneAndPyMcaFit(self, **kws):
        """generate energy histogram and fit with PyMca"""
        self.histo1_energy(**kws)
        self.x = self.h1e.bin_center
        self.y = self.h1e.histogram
        self.fitSplitPVoigt(**kws)
        
    def close_all_plots(self):
        """close all Matplotlib plots"""
        return ShadowTools.plt.close("all")

# ----------------------------------------------------------------------- #
# ShadowSpectro1: Spectrometer w 1 crystal analyser based on SHADOW3 only #
# ----------------------------------------------------------------------- #
class ShadowSpectro1(object):
    """Spectrometer w 1 crystal analyser based on SHADOW3"""
    def __init__(self, file_refl, oe_shape='rect', dimensions=np.array([0., 0., 0., 0.]),\
                 cyl_ang=None, set_johansson=False, init_from_file=False, **kws):
        """mimic spectrometer with 1 crystal analyzer

        Parameters
        ----------

        file_refl : str
                    reflectivity file

        oe_shape : str, 'rectangular'
                   'rectangular'
                   'ellipse'
                   'ellipse_with_hole'
        
        dimensions : array of floats, np.array([0., 0., 0., 0.])
                     dimensions[0] : dimension y plus  [cm] 
                     dimensions[1] : dimension y minus [cm] 
                     dimensions[2] : dimension x plus  [cm] 
                     dimensions[3] : dimension x minus [cm] 

        cyl_ang : float, None
                  cylinder orientation [deg] CCW from X axis]
                  0 -> cylindrical: meridional bending
                  90. -> cylindrical: sagittal bending

        set_johansson : boolean, False
                        if True, sets Johansson crystal cut (Rm should be given)
        
        init_from_file : boolean flag to load settings from file
        
        
        **kws : see RcHoriz
        
        """
        if (not HAS_SHADOW):
            raise ImportError('ShadowSpectro1 requires Shadow3, not found!')
        alpha = kws.get('alpha', None)
        if alpha is not None:
            raise NotImplementedError('miscut crystal not implemented yet!!!')
        if (file_refl is None) or (not os.path.isfile(file_refl)):
            raise NameError('file_refl not given or not existing')
        self.iwrite = kws.get('iwrite', 0) # write (1) or not (0) SHADOW
                                           # files start.xx end.xx star.xx
        #INIT
        self.rc = RcHoriz(**kws)
        self.beam = ShadowLibExtensions.Beam()
        self.src = FluoSource() # ShadowLibExtensions.Source()
        self.oe1 = SphericalCrystal(cyl_ang=cyl_ang) #ShadowLibExtensions.OE() # ShadowLib.OE()
        #self.det = ShadowLibExtensions.OE()
        self.plt = ShadowPlotter()
        print('INFO: init .rc, .beam, .src, .oe1, .det and .plt')
        if init_from_file: self.init_from_file()
        #CONFIGURE
        self.set_rowland_radius(self.rc.Rm, isJohansson=set_johansson)
        self.oe1.set_crystal(adjust_shadow_string(file_refl))
        if oe_shape == 'ellipse':
            fshape = 2
        elif oe_shape == 'ellipse_with_hole':
            fshape = 3
        else:
            fshape = 1
        self.oe1.set_dimensions(fshape=fshape, params=dimensions)
        #
        try:
            self.move_theta(deltaE=[2, 2])
        except:
            print('ERROR: CONFIGURE SRC/OE1 BEFORE RUN!')

    def init_from_file(self):
        """load shadow variables from file"""
        self.src.load('start.00')   
        self.oe1.load('start.01')
        #self.det.load('start.02')
        print('NOTE: variables loaded from start.00/start.01 files')
        
    def run(self, nrays=None, seed=None):
        """run SHADOW/source and SHADOW/trace"""
        #reset nrays/seed if given
        if (nrays is not None) and (seed is not None): self.src.set_rays(nrays=nrays, seed=seed)
        if (nrays is not None): self.src.set_rays(nrays)
        #generate source
        if self.iwrite: self.src.write("start.00")
        self_repair_src(self.src)
        self.beam.genSource(self.src)
        if self.iwrite:
            self.src.write("end.00")
            self.beam.write("begin.dat")
        #trace oe1
        if self.iwrite: self.oe1.write("start.01")
        self_repair_oe(self.oe1)
        self.beam.traceOE(self.oe1, 1)
        if self.iwrite:
            self.oe1.write("end.01")
            self.beam.write("star.01")
        #trace detector (not required yet)
        # if self.iwrite: self.det.write("start.02")
        # self.beam.traceOE(self.det, 2)
        # if self.iwrite:
        #     self.det.write("end.02")
        #     self.beam.write("star.02")

    def set_rowland_radius(self, Rm, isJohansson=False):
        """set Rowland circle radius [cm]

        Parameters
        ----------
        Rm : float
             meridional Rowland circle radius in cm
        
        isJohansson : boolean, False
                      flag to set Johansson geometry
        """
        self.oe1.F_EXT = 1
        self.oe1.FMIRR = 1
        if isJohansson:
            self.oe1.set_johansson(Rm*2.)
        else:
            self.oe1.F_JOHANSSON = 0
            self.oe1.set_radius(Rm*2.)

    def set_dspacing(self, d=None, hkl=None, latfunz=None, **kws):
        """set the crystal d-spacing [Ang]

        Parameters
        ----------
        d : float, None
            d-spacing [\AA]
        hkl : tuple, None
              (h, k, l)
        lattice : function, None
                  d_cubic -> a
                  d_hexagonal -> a, c
                  d_tetragonal -> a, c
                  d_orthorhombic -> a, b, c
                  d_monoclinic -> a, b, c, beta
                  d_triclinic -> a, b, c, alpha, beta, gamma
        a, b, c : float
        alpha, beta, gamma : float
     
        Return
        ------
        None, sets self.rc.d
        """
        if d is not None:
            self.rc.d = d
        elif (hkl is not None) and (latfunz is not None):
            try:
                self.rc.d = latfunz(hkl=hkl, **kws)
            except:
                print(sys.exc_info()[1]) 
                pass

    def move_mirr(self, move=False,\
                  offXYZ=np.array([0., 0., 0.]),\
                  rotXYZ=np.array([0., 0., 0.]),\
                  srcDiv=None):
        """mirror movement

        Parameters
        ----------
        move : boolean, False
               flag to enable mirror movement
        offXYZ : array of floats, [0., 0., 0.]
                 offsets in mirr reference frame [cm]
        rotXYZ : array of floats, [0., 0., 0.]
                 rotations in mirr reference frame [deg, positive clockwise]
        srcDiv : tuple of floats, None
                 to update the source divergence; for flat source,
                 FDISTR==1, srcDiv=(hdiv_pos, hdiv_neg, vdiv_pos,
                 vdiv_neg)=(HDIV1, HDIV2, VDIV1, VDIV2)

        """
        # update source divergence
        if (srcDiv is not None) and (self.src.FDISTR == 1):
            self.src.HDIV1 = srcDiv[0] 
            self.src.HDIV2 = srcDiv[1] 
            self.src.VDIV1 = srcDiv[2] 
            self.src.VDIV2 = srcDiv[3] 
        if move:
            self.oe1.F_MOVE = 1
            self.oe1.OFFX = offXYZ[0]
            self.oe1.OFFY = offXYZ[1]
            self.oe1.OFFZ = offXYZ[2]
            self.oe1.X_ROT = rotXYZ[0] 
            self.oe1.Y_ROT = rotXYZ[1] 
            self.oe1.Z_ROT = rotXYZ[2]
        else:
            self.oe1.F_MOVE = 0
        if self.rc.showInfos:
            print(' --- mirror movement infos ---')
            print('OE1: F_MOVE = {0}'.format(self.oe1.F_MOVE))
            print('OE1: OFFX   = {0}'.format(self.oe1.OFFX))
            print('OE1: OFFY   = {0}'.format(self.oe1.OFFY))
            print('OE1: OFFZ   = {0}'.format(self.oe1.OFFZ))
            print('OE1: X_ROT  = {0}'.format(self.oe1.X_ROT))
            print('OE1: Y_ROT  = {0}'.format(self.oe1.Y_ROT))
            print('OE1: Z_ROT  = {0}'.format(self.oe1.Z_ROT))
            print('SRC: HDIV1  = {0}'.format(self.src.HDIV1)) 
            print('SRC: HDIV2  = {0}'.format(self.src.HDIV2)) 
            print('SRC: VDIV1  = {0}'.format(self.src.VDIV1)) 
            print('SRC: VDIV2  = {0}'.format(self.src.VDIV2)) 

    def move_analyser(self, aXoff, **kws):
        """move analyser center to another Rowland circle by aXoff in cm

        Parameters
        ----------
        aXoff : float
                analyser center offset in X [cm]
        """
        _offXYZ = self.rc.get_ana_pos(aXoff) - self.rc.get_ana_pos(0.)
        _chi = self.rc.get_chi(aXoff)
        self.move_mirr(move=True, offXYZ=_offXYZ, rotXYZ=np.array([0., _chi, 0.]), **kws)
        
        #self.run()
    
    def move_theta(self, theta0=None, dth=[0.1, 0.1], deltaE=[None, None]):
        """from a starting config, go to a given Bragg angle

        Parameters
        ----------
        theta0 : float, None
                 the Bragg angle where to move [deg]
        
        dth : list of floats [0.1, 0.1]
              delta from theta0 in deg
        
        deltaE : list of floats [None, None]
                 if None, deltaE is calculated using dth values
                 E_source = [E_Bragg-deltaE[0], E_Bragg+deltaE[1]] in eV

        Returns
        -------
        None: set attributes to src and oe1
        """
        if (theta0 is None):
            if (not self.rc.theta0):
                raise NameError('move_theta(): set theta0 first!')
            else:
                theta0 = self.rc.theta0
        if not self.rc.d:
            raise NameError('move_theta(): set crystal d-spacing first!')
        if not self.rc.Rm:
            raise NameError('move_theta(): set Rowland circle radius first')

        self.rc.set_theta0(theta0)
        d = self.rc.d
        ene0 = self.rc.get_ene()
        # adjust source energy to new theta0
        self.oe1.PHOT_CENT = ene0
        if (deltaE[0] is None):
            self.src.PH1 = bragg_ev(d, theta0+abs(dth[1]))
        else:
            self.src.PH1 = ene0 - abs(deltaE[0])    
        if (deltaE[1] is None):
            self.src.PH2 = bragg_ev(d, theta0-abs(dth[0]))
        else:
            self.src.PH2 = ene0 + abs(deltaE[1])
            
        # adjust source divergence to new theta0 (assumig flat)
        _hlp = abs(self.oe1.RLEN1)  # half-length pos
        _hln = abs(self.oe1.RLEN2)  # half-length neg
        _hwp = abs(self.oe1.RWIDX1) # half-width pos
        _hwn = abs(self.oe1.RWIDX2) # half-width neg
        _rth0 = self.rc.rtheta0
        _pcm = self.rc.p # cm
        # _vdiv_pos = math.atan( (_hlp * math.sin(_rth0)) / (_pcm + _hlp * math.cos(_rth0) ) )
        # _vdiv_neg = math.atan( (_hln * math.sin(_rth0)) / (_pcm - _hln * math.cos(_rth0) ) )
        # _hdiv_pos = math.atan( (_hwp / _pcm) )
        # _hdiv_neg = math.atan( (_hwn / _pcm) )
        _vdiv_pos = (_hlp * math.sin(_rth0)) / (_pcm + _hlp * math.cos(_rth0) )
        _vdiv_neg = (_hln * math.sin(_rth0)) / (_pcm - _hln * math.cos(_rth0) )
        _hdiv_pos = (_hwp / _pcm)
        _hdiv_neg = (_hwn / _pcm)
        self.src.VDIV1 = _vdiv_pos * 1.1 # empirical!
        self.src.VDIV2 = _vdiv_neg * 1.1 # empirical!
        self.src.HDIV1 = _hdiv_pos * 1.1 # empirical!
        self.src.HDIV2 = _hdiv_neg * 1.1 # empirical!

        # adjust analyser to new theta0
        self.oe1.set_frame_of_reference(self.rc.p, self.rc.q, 90.-theta0)

        if self.rc.showInfos:
            print(' --- theta movement infos --- ')
            print('OE1: PHOT_CENT    = {0}'.format(self.oe1.PHOT_CENT   )) 
            print('SRC: PH1          = {0}'.format(self.src.PH1         )) 
            print('SRC: PH2          = {0}'.format(self.src.PH2         )) 
            print('SRC: VDIV1        = {0}'.format(self.src.VDIV1       )) 
            print('SRC: VDIV2        = {0}'.format(self.src.VDIV2       )) 
            print('SRC: HDIV1        = {0}'.format(self.src.HDIV1       )) 
            print('SRC: HDIV2        = {0}'.format(self.src.HDIV2       )) 
            print('OE1: T_SOURCE     = {0}'.format(self.oe1.T_SOURCE    )) 
            print('OE1: T_IMAGE      = {0}'.format(self.oe1.T_IMAGE     )) 
            print('OE1: T_INCIDENCE  = {0}'.format(self.oe1.T_INCIDENCE )) 
            print('OE1: T_REFLECTION = {0}'.format(self.oe1.T_REFLECTION)) 

if __name__ == '__main__':
    # NOTE: works within 'ipython'
    # NOTE: does NOT work within 'ipython --gui=qt', 'ipython --gui=qt5', 'ipython --matplotlib qt5'
    dsi111 = d_cubic(SI_ALAT, (1,1,1))
    _rootDir = os.path.realpath(os.path.join(_parDir, os.path.pardir))
    refl444 = os.path.join(_rootDir, 'data', 'Si444_refl_oasys.dat')
    refl333 = os.path.join(_rootDir, 'data', 'Si333_refl_oasys.dat')
    refl111 = os.path.join(_rootDir, 'data', 'Si111_refl_oasys.dat')
    circ_4in = np.array([5, 5, 5, 5])
    rect_texs = np.array([1.25, 1.25, 4., 4.])
    rect_tsts = np.array([0.25, 0.25, 4., 4.])
    #t = ShadowSpectro1(bytes(refl444, 'utf8'), oe_shape='ellipse', dimensions=circ_4in, theta0=75., Rm=50., d=dsi111/4., useCm=True, showInfos=True)
    t = ShadowSpectro1(bytes(refl333, 'utf8'), oe_shape='rectangle', dimensions=rect_tsts, theta0=65., Rm=50., d=dsi111/3., useCm=True, showInfos=True, set_johansson=True)
    #t = ShadowSpectro1(bytes(refl444, 'utf8'), oe_shape='rectangle', dimensions=rect_texs, theta0=75., Rm=50., d=dsi111/4., useCm=True, showInfos=True)
    #t = ShadowSpectro1(bytes(refl111, 'utf8'), oe_shape='rectangle', dimensions=rect_tsts, theta0=35., Rm=50., d=dsi111, useCm=True, showInfos=True)
    #CONFIGURE SRC
    # t.src.set_angle_distr(fdistr=5, cone_max=0.3)
    # src_ene_hw = 2 # eV
    # src_ene_min = t.rc.get_ene() - src_ene_hw
    # src_ene_max = t.rc.get_ene() + src_ene_hw
    # t.src.set_energy_distr(f_color=3, f_phot=0, phn=[src_ene_min, src_ene_max])
    
    #RUN
    #t.run(10000)
    #import IPython
    #IPython.embed(header='t => ShadowSpectro1')
    pass

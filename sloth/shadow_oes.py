#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_oes: custom wrapper classes of *ShadowOpticalElement* from
Orange-Shadow_ (SHADOW3_ project)

.. note:: ShadowOpticalElement is designed as a final class, this is
why the first class, *SwOE* is a wrapper class and does not inherit
from *ShadowOpticalElement*. It is not elegant, but this will keep the
compatibility with the whole (SHADOW3_ project).

.. note:: requires python3.x

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow

"""
__author__ = "Mauro Rovezzi"
__credits__ = "Luca Rebuffi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import sys, os, copy, math
import numpy as np

# requirements for ShadowOpticalElement
HAS_PY3 = False
HAS_OSHADOW = False
if sys.version_info >= (3,2,0): HAS_PY3 = True
try:
    from orangecontrib.shadow.util.shadow_objects import ShadowOpticalElement
    HAS_OSHADOW = True
except:
    pass

class SwOE(object):
    """wrapper to ShadowOpticalElement"""

    def __init__(self):
        if not (HAS_PY3 and HAS_OSHADOW): raise ImportError("Orange-Shadow not found")
        self.sw_oe = self.create_instance()

    def create_instance(self):
        """template method pattern"""
        return ShadowOpticalElement.create_empty_oe()

    def get_instance(self):
        return self.sw_oe

    def set_output_files(self, fwrite=0, f_angle=0):
        """ optional file output

        Parameters
        ----------

        fwrite : int [3]
                 files to write out
                 0 -> all files
                 1 -> mirror file  only -- mirr
                 2 -> image file only -- star
                 3 -> none
                 
        f_angle : int [0]
                  write out incident/reflected angles [angle.xx]
                  0 -> no
                  1 -> yes
        """
        self.sw_oe.oe.FWRITE = fwrite
        self.sw_oe.oe.F_ANGLE = f_angle 
        
    def set_frame_of_reference(self, p, q, deg_inc, deg_refl=None, deg_mirr=0.):
        """set frame of reference

        Parameters
        ----------
        p, q : float
               source, image plane distances [cm]

        deg_inc : float
                  angle of incidence wrt the normal [deg]

        deg_refl : float [None]
                   angle of reflection wrt the norma [deg]
                   if None = deg_inc
        deg_mirr : float [0]
                   mirror orientation [deg]
        
        """
        if deg_refl is None: deg_refl = deg_inc
        self.sw_oe.oe.setFrameOfReference(p, q, deg_inc, deg_refl, deg_mirr)

    def set_infinite(self):
        self.sw_oe.oe.FHIT_C = 0

    def set_dimensions(self, fshape=1, params=np.array([0., 0., 0., 0.])):
        """set mirror dimensions

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
        self.sw_oe.oe.setDimensions(fshape, params=params)

class PlaneCrystal(SwOE):
    """plane crystal"""
    
    def __init__(self):
        super(PlaneCrystal, self).__init__()
        self.create_instance()
        self.set_output_files(fwrite=0, f_angle=0)
        self.sw_oe.oe.unsetReflectivity()

    def create_instance(self):
        return ShadowOpticalElement.create_plane_crystal()

    def set_crystal(self, file_refl, a_bragg=0.0,\
                    tune_auto=0, tune_units=0, tune_ev=0.0, tune_ang=0.0):
        """set crystal

        f_crystal [1 - flag: crystal -- yes (1), no (0).]

        Parameters
        ----------
        file_refl : string
                    file containing the crystal parameters
        a_bragg : float [0.0]
                  asymmetric angle between crystal planes and surface [deg]
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

        self.sw_oe.oe.setCrystal(file_refl=bytes(file_refl, 'utf-8'), a_bragg=a_bragg)

        if tune_auto == 0:
            self.sw_oe.oe.F_CENTRAL = 0
        else:
            self.sw_oe.oe.setAutoTuning(f_phot_cent=tune_units, phot_cent=tune_ev, r_lambda=tune_ang)

    def set_mosaic(self, mos_seed, angle_spread_FWHM, thickness):
        """ set mosaic

        Parameters
        ----------
        
        mosaic_seed

        spread_mos : angle spread FWHM

        thickness

        Notes
        -----
        mutually exclusive with asymmetric cut and Johansson
        """
        self.sw_oe.oe.setMosaic(mosaic_seed=mos_seed, spread_mos=angle_spread_FWHM, thickness=thickness)

        #MUTUALLY EXCLUSIVE!
        self.sw_oe.oe.F_BRAGG_A = 0
        self.sw_oe.oe.F_JOHANSSON = 0

    def set_asymmetric_cut(self, a_bragg, thickness, order=-1.):
        """set asymmetric cut

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
        self.sw_oe.oe.F_BRAGG_A = 1
        self.sw_oe.oe.F_MOSAIC = 0

        self.sw_oe.oe.A_BRAGG = a_bragg
        self.sw_oe.oe.THICKNESS = thickness
        self.sw_oe.oe.ORDER = order
        
    def set_johansson(self, js_radius):
        """set Johansson geometry

        Parameters
        ----------

        js_radius : float
                    Johansson radius

        Notes
        -----
        mutually exclusive with mosaic
        """
        self.sw_oe.oe.F_JOHANSSON = 1
        self.sw_oe.oe.R_JOHANSSON = js_radius
        
        #MUTUALLY EXCLUSIVE!
        self.sw_oe.oe.F_MOSAIC = 0

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
                  0 -> meridional
                  90. -> sagittal
        rmirr : float, None
                meridional radius

        """
        super(SphericalCrystal, self).__init__()
        self.create_instance()
        self.set_output_files(fwrite=0, f_angle=0)
        self.sw_oe.oe.unsetReflectivity()
        # convex/concave
        if convex:
            f_convex = 1
        else:
            f_convex = 0
        self.set_curvature(f_convex)
        # cylindrical?
        if cyl_ang is not None:
            self.set_cylindrical(cyl_ang)
        # radius of curvature (internal or external)
        if rmirr is None:
            self.set_calculated_shape_params(self, **kws)
        else:
            self.set_radius(rmirr)

    def create_instance(self):
        return ShadowOpticalElement.create_spherical_crystal()

    def set_radius(self, rmirr):
        """set radius of curvature (RMIRR)

        Parameters
        ----------

        rmirr : float
                radius of curvature

        """
        self.sw_oe.oe.F_EXT = 1
        self.sw_oe.oe.RMIRR = rmirr

    def set_curvature(self, f_convex=0):
        """set curvature (concave is default)"""
        self.sw_oe.oe.F_CONVEX = f_convex

    def set_cylindrical(self, cyl_ang):
        """set cylindrical
        
        cyl_ang : float, None
                  cylinder orientation [deg] CCW from X axis]
                  0 -> meridional
                  90. -> sagittal
        """
        self.sw_oe.oe.setCylindric(cyl_ang=cyl_ang)

    def set_calculated_shape_params(self, coincident=True, p_cm=0., q_cm=0., inc_deg=0.):
        """internally calculated shape parameters"""
        if self.sw_oe.oe.FCYL and self.sw_oe.oe.CYL_ANG == 90.0: # sagittal curvature
            self.sw_oe.oe.F_EXT=1

            # RADIUS = (2 F1 F2 sin (theta)) /( F1+F2)
            if coincident:
                p_cm = self.sw_oe.oe.T_SOURCE
                q_cm = self.sw_oe.oe.T_IMAGE
                inc_deg =  self.sw_oe.oe.T_REFLECTION

            self.sw_oe.oe.RMIRR = ( (2 * p_cm * q_cm) / (p_cm + q_cm) ) * math.sin(math.radians(90-inc_deg))
        else:
            self.sw_oe.oe.F_EXT=0
            if coincident:
                self.sw_oe.oe.setAutoFocus(f_default=1)
            else:
                self.sw_oe.oe.setAutoFocus(f_default=0, ssour=p_cm, simag=q_cm, theta=inc_deg)


"""
--------------------------------------------------
CYLINDRIC MIRROR (OE2)
--------------------------------------------------
"""

class CylindricMirror(SwOE):
    cylinder_orientation = 0

    def __init__(self, cylinder_orientation=0): # 0 longitudinal, 1 sagittal
        super().__init__()

        self.turnOffFileOut()

        self.sw_oe.oe.unsetReflectivity()

        self.cylinder_orientation=cylinder_orientation
        self.sw_oe.oe.setCylindric(cyl_ang=90*cylinder_orientation)

    def createInstance(self):
        return ShadowOpticalElement.create_spherical_mirror()

    # RIFLETTIVITA

    def set_Reflectivity(self, file_prerefl):
        self.sw_oe.oe.setReflectivityFull(f_refl=0, file_refl=bytes(file_prerefl, 'utf-8'))

    # CURVATURE TYPE

    def set_SurfaceCurvature(self, surface_curvature): # 0 concave, 1 convex
        if surface_curvature == 0:
           self.sw_oe.oe.setConcave()
        else:
           self.sw_oe.oe.setConvex()

    # RADIUS OF CURVATURE

    def set_InternallyCalculatedShapeParameters(self, focii_and_continuation_plane, object_side_focal_distance=0, image_side_focal_distance=0, incidence_angle_respect_to_normal=0):
        if self.cylinder_orientation==1: # sagittal curvature
            self.sw_oe.oe.F_EXT=1

            # RADIUS = (2 F1 F2 sin (theta)) /( F1+F2)

            if focii_and_continuation_plane == 0:
                object_side_focal_distance = self.sw_oe.oe.T_SOURCE
                image_side_focal_distance = self.sw_oe.oe.T_IMAGE
                incidence_angle_respect_to_normal =  self.sw_oe.oe.T_REFLECTION

            self.sw_oe.oe.RMIRR = ((2*object_side_focal_distance*image_side_focal_distance)/(object_side_focal_distance+image_side_focal_distance))*math.sin(math.radians(90-incidence_angle_respect_to_normal))

        else:
            self.sw_oe.oe.F_EXT=0

            if focii_and_continuation_plane == 0:
                self.sw_oe.oe.setAutoFocus(f_default=1)
            else:
                self.sw_oe.oe.setAutoFocus(f_default=0,
                                                ssour=object_side_focal_distance,
                                                simag=image_side_focal_distance,
                                                theta=incidence_angle_respect_to_normal)

    def set_ExternalUserDefinedParameters(self, spherical_radius):
        self.sw_oe.oe.F_EXT=1
        self.sw_oe.oe.RMIRR = spherical_radius

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_spectro1: an utility toolbox to raytrace a
wavelength-dispersive spectrometer with SHADOW3_ from Python, via
ShadowOui_ layer

.. note:: requires python3.x

.. note:: this is only an idea (e.g. example) on how to automatize
          some repetitive steps in SHADOW3_ as, for example, scanning
          a variable. At the moment the object is messy and not
          general at all. It is based on a specific example that
          requires a given workspace as a starting point to generate
          the 'start.xx' files. This can be used only to get inspired,
          but the correct way to extend SHADOW3_ functionality is to
          inherit from ShadowLibExtensions!!! Please, do not inherit
          from this object. It will be soon deprecated. See also the
          current develpment of ShadowOui_ (OASYS1_ and Orange-Shadow_
          no more under development) or Orange-XOPPY_.

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _OASYS1: https://github.com/lucarebuffi/OASYS1
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _Orange-XOPPY: https://github.com/srio/Orange-XOPPY
.. _ShadowOui: https://github.com/lucarebuffi/ShadowOui

TODO
----

- update to ShadowOui_

- re-structure the whole thing by inheriting from ShadowLibExtensions
  or Orange-Shadow

"""
__author__ = "Mauro Rovezzi"
__credits__ = "Luca Rebuffi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014-2015"

import sys, os, copy, math
import numpy as np

HAS_SHADOW = False
HAS_SWOUI = False

try:
    from orangecontrib.shadow.util.shadow_objects import ShadowBeam
    HAS_SWOUI = True
except:
    #raise ImportError('ShadowOui not found!')
    #sys.exit(1)
    pass

try:
    from Shadow import ShadowLibExtensions as sle
    HAS_SHADOW = True
except:
    pass

#sloth
from __init__ import _libDir
sys.path.append(_libDir)

# ../xop/data
_pardir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
DATA_DIR = os.path.join(_pardir, 'xop', 'data')

from rowland import RcHoriz
from shadow_sources import GeoSource
from shadow_oes import PlaneCrystal, SphericalCrystal
from shadow_screens import SwScreen
from shadow_plotter import ShadowPlotter as sp
from shadow_plotter import SwPlot

# ---------------------------------------------------------------#
# SwSpectro1 (see also ShadowSpectro1 below)
# ---------------------------------------------------------------#
class SwSpectro1(object):
    """ Example of usage for shadow_objects in ShadowOui"""

    def __init__(self, nrays=10000, seed=0, file_refl=None, **kws):
        """mimic spectrometer with 1 crystal analyzer:
        geometric source -> crystal -> detector

        Parameters
        ----------
        nrays : int, 10000
                number of rays
        seed : int, 0 (default was 6775431)
               seed for random number generator

        file_refl : string, None
                    file containing the crystal parameter              
        
        **kws : see RcHoriz
        
        """
        if (not HAS_SWOUI):
            raise ImportError('SwSpectro1 requires ShadowOui, not found!')
            
        if (file_refl is None) or (not os.path.isfile(file_refl)):
            raise NameError('file_refl not given or not existing')

        #init rowland circle
        self.rc = RcHoriz(**kws)
        
        # init the src, oe1, det
        self.src = GeoSource()
        #self.oe1 = PlaneCrystal()
        self.oe1 = SphericalCrystal(rmirr=self.rc.Rm) #surface radius!!!
        self.det = SwScreen(10, 10)

        #configure
        self.src.set_rays(nrays, seed)
        self.src.set_spatial_type(fsour=1, wxsou=0.05, wzsou=0.01)
        self.src.set_angle_distr(fdistr=1, hdiv=(0.015, 0.015), vdiv=(0.045, 0.045)) #75 deg
        #self.src.set_angle_distr(fdistr=1, hdiv=(0.03, 0.03), vdiv=(0.045, 0.045)) #35 deg
        ene0 = self.rc.get_ene()
        
        self.oe1.set_crystal(file_refl, tune_auto=0)
        #self.oe1.set_cylindrical(0) #cylindrical meridional curvature
        self.oe1.set_dimensions(fshape=1, params=np.array([4.,4.,1.25,1.25]))
        self.oe1.set_johansson(self.rc.Rm*2.) #crystal planes radius
        #self.oe1.set_infinite()

        self.src.set_energy_distr(phn=(ene0-1.5, ene0+3.5))
        #self.src.set_angle_distr(cone=(0., 1))

        self.oe1.set_frame_of_reference(self.rc.p, self.rc.q, deg_inc=90-self.rc.theta0)
        
    def run(self, nrays=None):
        """run SHADOW/source and SHADOW/trace"""
        if nrays is not None: self.src.set_rays(nrays)
        # genereta beam from the source
        self.beam_src = ShadowBeam.traceFromSource(self.src.get_instance())
        # ray trace from source to oe1 image plane
        self.beam_oe1 = ShadowBeam.traceFromOE(input_beam=self.beam_src, shadow_oe=self.oe1.get_instance())
        # ray trace from oe1 image plane to oe2 (det) image plane
        self.beam_det = ShadowBeam.traceFromOE(input_beam=self.beam_oe1, shadow_oe=self.det.get_instance())

    def plot(self, beam):
        if not hasattr(self, 'plt'):
            self.plt = SwPlot(beam)
        else:
            self.plt.set_instance(beam)
        #self.plt.plot_histo(self.plt.get_instance(), 11, ref=23)
        #self.plt.infos = self.plt.plotxy(self.plt.get_instance(), 1, 3)
        self.plt.box.show()

    def update_divergence(self, fdistr=1, expand=1.2):
        """adjust source divergence to new analyzer position (theta0 and p)

        Parameters
        ==========

        fdistr : int, 1

                 flag for angular distribution type
                 1 flat
                 (others not implemented yet!!!)

        expand : float, 1.2

                 empirical factor to apply a common expansion to the
                 new calculated divergence
        """
        if fdistr == 1:
            _hlp = abs(self.oe1.get_instance()._oe.RLEN1)  # half-length pos
            _hln = abs(self.oe1.get_instance()._oe.RLEN2)  # half-length neg
            _hwp = abs(self.oe1.get_instance()._oe.RWIDX1) # half-width pos
            _hwn = abs(self.oe1.get_instance()._oe.RWIDX2) # half-width neg
            _rth0 = self.rc.rtheta0
            _pcm = self.rc.p # cm
            _vdiv_pos = math.atan( (_hlp * math.sin(_rth0)) / (_pcm + _hlp * math.cos(_rth0) ) )
            _vdiv_neg = math.atan( (_hln * math.sin(_rth0)) / (_pcm - _hln * math.cos(_rth0) ) )
            _hdiv_pos = math.atan( (_hwp / _pcm) )
            _hdiv_neg = math.atan( (_hwn / _pcm) )
            _f = expand
            self.src.set_angle_distr(fdistr=1,\
                                     hdiv=(_hdiv_pos*_f, _hdiv_neg*_f),\
                                     vdiv=(_vdiv_pos*_f, _vdiv_neg*_f))
            return
        else:
            print('Not implemented yet!')
            return

# ---------------------------------------------------------------#
# ShadowSpectro1
# ---------------------------------------------------------------#
class ShadowSpectro1(object):
    """Spectrometer w 1 crystal analyser based on SHADOW3 only

    .. note:: as was in shadow_spectro1_old.py but updated to
              ShadowLibExtensions refactoring

    """
    
    def __init__(self, file_refl, dimensions=np.array([0., 0., 0., 0.]),
                 nrays=10000, seed=6775431, **kws):
        """mimic spectrometer with 1 crystal analyzer

        Parameters
        ----------

        file_refl : str
                    reflectivity file

        dimensions : array of floats, np.array([0., 0., 0., 0.])
                     dimensions[0] : dimension y plus  [cm] 
                     dimensions[1] : dimension y minus [cm] 
                     dimensions[2] : dimension x plus  [cm] 
                     dimensions[3] : dimension x minus [cm] 

        
        nrays : int, 10000
                number of rays
        seed : int, 6775431
               seed for random number generator

        **kws : see RcHoriz
        
        """
        self.rc = RcHoriz(**kws)

        self.src = sle.Source()
        self.src.NPOINT = nrays
        if (seed % 2 == 0): seed += 1
        self.src.ISTAR1 = seed
        ene0 = self.rc.get_ene()
        ene_src_hwidth_ev = 2  
        emin = ene0 - ene_src_hwidth_ev
        emax = ene0 + ene_src_hwidth_ev
        self.src.set_energy_box(emin, emax)
        self.src.write("start.00")
        
        self.beam = sle.Beam()
        self.beam.genSource(self.src)
        self.beam.write("begin.dat")
        self.src.write("end.00")

        self.spe1 = sle.CompoundOE(name='spectro1')

        #spherical crystal, TODO: make separate class
        self.oe1 = sle.OE()
        self.oe1.FMIRR = 1 #spherical
        self.oe1.F_CRYSTAL = 1
        self.oe1.FILE_REFL = file_refl.encode('utf-8')
        self.oe1.F_REFLECT = 0
        self.oe1.F_REFRAC = 0
        self.oe1.F_BRAGG_A = 0
        self.oe1.A_BRAGG = 0.0
        self.oe1.ALPHA = 0.0
        self.oe1.T_INCIDENCE = 90.0 - self.rc.theta0
        self.oe1.T_REFLECTION = 90.0 - self.rc.theta0
        self.oe1.T_SOURCE = self.rc.p
        self.oe1.T_IMAGE = self.rc.q
        self.oe1.F_CONVEX = 0
        self.oe1.F_CYL = 0 # YES (1) NO (0)
        self.oe1.CIL_ANG = 0. # meridional (0.0), sagittal (90.0)
        self.oe1.F_EXT = 1
        self.oe1.RMIRR = 2 * self.rc.Rm # surface radius
        self.oe1.FHIT_C = 1 # finite dimensions yes (1), no (0)
        self.oe1.FSHAPE = 2 # rect (1), ellipse (2), ellipse w hole (3)
        self.oe1.RLEN1  = dimensions[0]
        self.oe1.RLEN2  = dimensions[1]
        self.oe1.RWIDX1 = dimensions[2]
        self.oe1.RWIDX2 = dimensions[3]
        self.oe1.F_CENTRAL = 0 # energy auto tuning: yes (1), no (0)
        self.oe1.F_PHOT_CENT = 0 # eV
        self.oe1.F_JOHANSSON = 0 # Johansson: yes (1), no (0)
        self.oe1.R_JOHANSSON = 0.0 # radius_johansson
        self.oe1.FWRITE = 3 # write no output files

        self.spe1.append(self.oe1)
        
        #TODO detector
        #self.det = sle.OE()

        print('init rc, beam, src, spe1')
        # self.run() # better not to run at init!

        #trace
        self.spe1.dump_systemfile()
        self.beam.traceCompoundOE(self.spe1,
                                  write_start_files=1,
                                  write_end_files=1,
                                  write_star_files=1)
    
if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QCoreApplication

    app = QCoreApplication.instance()
    if app is None:
        print('standart app instance')
        app = QApplication(sys.argv)

    d_si111 = 3.1356268397363549
    file_refl = os.path.join(DATA_DIR, 'Si_444-E_2000_20000_50-A_3-T_1.bragg')
    dimensions_cm=np.array([5., 5., 5., 5.])

    # ---------------------------------------------------------------#
    # SwSpectro1 tests
    # ---------------------------------------------------------------#
    if HAS_SWOUI:
        s = SwSpectro1(file_refl=file_refl, Rm=50., useCm=True,
                       showInfos=True, d=d_si111/4., theta0=75.)
        s.update_divergence(fdistr=1, expand=1.1)
        #s.src.sw_src.src.load('spectro-1411_start.src')
        #s.oe1.sw_oe._oe.load('spectro-1411_start.oe1')
        #s.det.sw_scr._oe.load('spectro-1411_start.det')

    if 0:
        s.run(10000)
    
        p = SwPlot(s.beam_src._beam)
        p.box.show()
    
        #p.plotxy(s.beam_src._beam, 4, 6, nolost=1)
        #p.plotxy(s.beam_oe1._beam, 1, 2, nolost=1)
        #p.plotxy(s.beam_oe1._beam, 4, 6, nolost=2)
        infos = p.plotxy(s.beam_oe1._beam, 1, 3, nolost=1)
    
        ene0 = s.rc.get_ene()
        fwhm_src = p.plot_histo(s.beam_src._beam, 11, ref=23, xrange=[ene0-5., ene0+5], title='src_ene')
        fwhm_oe1 = p.plot_histo(s.beam_oe1._beam, 11, ref=23, xrange=[ene0-5., ene0+5], title='oe1_ene', replace=False)

        
        #poe1 = SwPlot(s.beam_oe1._beam)
        #poe1.box.show()
        
        pp = sp()
        #p.h1 = p.histo1_energy(s.beam_oe1._beam)
        #pp.fp = pp.plotxy_footprint('rmir.01')
        
        print('===RESULTS===')
        print('Source energy FWHM {0:.3f} eV (50% intensity)'.format(fwhm_src))
        print('OE1 energy FWHM {0:.3f} eV (50% intensity)'.format(fwhm_oe1))
        print('Bragg angle {0:.2f} deg'.format(s.rc.theta0))
        print('Central energy {0:.5f} eV'.format(s.rc.get_ene()))
        print('Energy resolution {0:.3f}E-4'.format((fwhm_oe1/s.rc.get_ene())*1E4))

    else:
        print('--- TESTING MODE ---')
        print('SwSpectro1 instance is s, not run yet')
        print('plotters are ShadowPlotter (old) and SwPlotter (current)')


    # ---------------------------------------------------------------#
    # ShadowSpectro1 tests
    # ---------------------------------------------------------------#
    if HAS_SHADOW:
        s = ShadowSpectro1(file_refl=file_refl, dimensions=dimensions_cm,
                           Rm=50., useCm=True,
                           showInfos=True, d=d_si111/4., theta0=75.)

    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except:
        print('standard exec_')
        sys.exit(app.exec_())

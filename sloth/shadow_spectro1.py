#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow3_spectro1: an utility toolbox to raytrace a
wavelength-dispersive spectrometer with SHADOW3_ from Python

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
          current develpment of OASYS1_, Orange-Shadow_ or
          Orange-XOPPY_.

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _OASYS1: https://github.com/lucarebuffi/OASYS1
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _Orange-XOPPY: https://github.com/srio/Orange-XOPPY

TODO
----
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

from orangecontrib.shadow.util.shadow_objects import ShadowBeam

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

class SwSpectro1(object):
    """ Example of usage for shadow_objects in Orange-shadow"""

    def __init__(self, nrays=10000, seed=0, **kws):
        """mimic spectrometer with 1 crystal analyzer:
        geometric source -> crystal -> detector

        Parameters
        ----------
        nrays : int, 10000
                number of rays
        seed : int, 0 (default was 6775431)
               seed for random number generator

        **kws : see RcHoriz
        
        """
        self.rc = RcHoriz(**kws)
        
        # init the src, oe1, det
        self.src = GeoSource()
        #self.oe1 = PlaneCrystal()
        self.oe1 = SphericalCrystal(rmirr=self.rc.Rm) #surface radius!!!
        self.det = SwScreen(3, 3)

        #configure
        self.src.set_rays(nrays, seed)
        self.src.set_spatial_type(fsour=1, wxsou=0.05, wzsou=0.01)
        self.src.set_angle_distr(fdistr=1, hdiv=(0.015, 0.015), vdiv=(0.045, 0.045)) #75 deg
        #self.src.set_angle_distr(fdistr=1, hdiv=(0.03, 0.03), vdiv=(0.045, 0.045)) #35 deg
        ene0 = self.rc.get_ene()
        
        self.oe1.set_crystal(os.path.join(DATA_DIR, "Si_111-E_1000_10000_50.shadow"), tune_auto=0)
        self.oe1.set_cylindrical(0)
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
            _hlp = abs(self.oe1.get_instance().oe.RLEN1)  # half-length pos
            _hln = abs(self.oe1.get_instance().oe.RLEN2)  # half-length neg
            _hwp = abs(self.oe1.get_instance().oe.RWIDX1) # half-width pos
            _hwn = abs(self.oe1.get_instance().oe.RWIDX2) # half-width neg
            _rth0 = self.rc.rtheta0
            _pcm = self.rc.p # cm
            _vdiv_pos = math.atan( (_hlp * math.sin(_rth0)) / (_pcm + _hlp * math.cos(_rth0) ) )
            _vdiv_neg = math.atan( (_hln * math.sin(_rth0)) / (_pcm - _hln * math.cos(_rth0) ) )
            _hdiv_pos = math.atan( (_hwp / _pcm) )
            _hdiv_neg = math.atan( (_hwn / _pcm) )
            _f = expand
            self.src.set_angle_distr(fdistr=1, hdiv=(_hdiv_pos*_f, _hdiv_neg*_f), vdiv=(_vdiv_pos*_f, _vdiv_neg*_f))
            return
        else:
            print('Not implemented yet!')
            return
    
if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QCoreApplication

    app = QCoreApplication.instance()
    if app is None:
        print('standart app instance')
        app = QApplication(sys.argv)

    #Si(111) at 55 deg
    s = SwSpectro1(Rm=50., useCm=True, showInfos=True, d=3.1356268397363549, theta0=35.)
    s.update_divergence(fdistr=1, expand=1.1)
    #s.src.sw_src.src.load('spectro-1411_start.src')
    #s.oe1.sw_oe.oe.load('spectro-1411_start.oe1')
    #s.det.sw_scr.oe.load('spectro-1411_start.det')

    s.run(10000)
    
    p = SwPlot(s.beam_src.beam)
    p.box.show()
    
    #p.plotxy(s.beam_src.beam, 4, 6, nolost=1)
    #p.plotxy(s.beam_oe1.beam, 1, 2, nolost=1)
    #p.plotxy(s.beam_oe1.beam, 4, 6, nolost=2)
    infos = p.plotxy(s.beam_oe1.beam, 1, 3, nolost=1)
    
    ene0 = s.rc.get_ene()
    fwhm_src = p.plot_histo(s.beam_src.beam, 11, ref=23, xrange=[ene0-5., ene0+5], title='src_ene')
    fwhm_oe1 = p.plot_histo(s.beam_oe1.beam, 11, ref=23, xrange=[ene0-5., ene0+5], title='oe1_ene', replace=False)


    #poe1 = SwPlot(s.beam_oe1.beam)
    #poe1.box.show()
    
    pp = sp()
    #p.h1 = p.histo1_energy(s.beam_oe1.beam)
    pp.fp = pp.plotxy_footprint('rmir.01')

    print('===RESULTS===')
    print('Source energy FWHM {0:.3f} eV (50% intensity)'.format(fwhm_src))
    print('OE1 energy FWHM {0:.3f} eV (50% intensity)'.format(fwhm_oe1))
    print('Bragg angle {0:.2f} deg'.format(s.rc.theta0))
    print('Central energy {0:.5f} eV'.format(s.rc.get_ene()))
    print('Energy resolution {0:.3f}E-4'.format((fwhm_oe1/s.rc.get_ene())*1E4))


    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except:
        print('standard exec_')
        sys.exit(app.exec_())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow3_spectro1: an utility toolbox to raytrace a
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
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014-2015"

import sys, os
import math
import numpy as np
# see README.rst how to install XOP and SHADOW3
try:
    from Shadow import ShadowLib
    from Shadow import ShadowLibExtensions
    from Shadow import ShadowTools
except:
    print(sys.exc_info()[1])
    pass

from peakfit import fit_splitpvoigt, fit_results
import bragg as bu
from rowland import RcHoriz

# SRC => TODO: merge with shadow_sources.py
class FluoSource(ShadowLibExtensions.Source):
    """mimic a divergent fluorescence source

    geometric source of rectangular shape and conical angular
    distrubution with uniform energy distribution
    """

    def __init__(self):
        super(FluoSource, self).__init__(self)
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
                        hdiv_pos=0.0, hdiv_neg=0.0, vdiv_pos=6E-5, vdiv_neg=6E-5):
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

# OE => TODO: merge with shadow_oes.py
class CrystalFlat(ShadowLibExtensions.OE):
    """flat crystal mirror"""

    def __init__(self, **kws):
        """
        Parameters
        ----------
        source_distance : float [10.0]
                          source plane distance [cm]
        image_distance : float [20.0]
                         image plane distance [cm]
        source_angle : float [10.0]
                       incidence angle respect to normal [deg]
        image_angle : float [10.0]
                      reflection angle respect to normal [deg]
        alpha : float [0.0]
                mirror orientation angle [deg]
                  
        Returns
        -------
        None: set attributes
        """
        super(CrystalFlat, self).__init__(self)
        self.setFrameOfReference(**kws)
        self.setCrystal(**kws)

class JohannCylinder(CrystalFlat):
    """crystal bent in meridional direction"""

    def __init__(self, **kws):
        super(CrystalFlat, self).__init__(**kws)
        self.setConcave()
        self.setCylindric(cyl_ang=0.0)

class JohanssonCylinder(JohannCylinder):
    """crystal ground and bent in meridional direction"""

    def __init__(self, **kws):
        super(JohannCylinder, self).__init__(**kws)
        self.setJohansson(**kws)

# ----------------------------------------------------------------------- #
# ShadowSpectro1: Spectrometer w 1 crystal analyser based on SHADOW3 only #
# ----------------------------------------------------------------------- #
class ShadowSpectro1(object):
    """Spectrometer w 1 crystal analyser based on SHADOW3"""
    def __init__(self, file_refl, dimensions=np.array([0., 0., 0., 0.]),\
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
        self.iwrite = kws.get('iwrite', 0) # write (1) or not (0) SHADOW
                                           # files start.xx end.xx star.xx
        self.rc = RcHoriz(**kws)
        self.beam = ShadowLibExtensions.Beam()
        self.src = FluoSource() # ShadowLibExtensions.Source()
        #self.src.load('start.00')   
        self.oe1 = ShadowLibExtensions.OE() # ShadowLib.OE()
        #self.oe1.load('start.01')
        self.det = ShadowLibExtensions.OE()
        #self.det.load('start.02')
        self.src.set_rays(nrays, seed=seed)
        print('init self.rc, .beam, .src, .oe1 and .det')
        # self.run() # better not to run at init!

    def run(self, nrays=None):
        """run SHADOW/source and SHADOW/trace"""
        if nrays is not None: self.src.set_rays(nrays)
        self.beam.genSource(self.src)
        self.beam.write('begin.dat')
        self.oe1.write('start.01')
        self.beam.traceOE(self.oe1, 1)
        self.oe1.write('end.01')
        self.det.write('start.02')
        self.beam.traceOE(self.det, 2)
        self.det.write('end.02')

    def runHisto1EneAndPyMcaFit(self, **kws):
        """generate energy histogram and fit with PyMca"""
        self.histo1_energy(**kws)
        self.x = self.h1e.bin_center
        self.y = self.h1e.histogram
        self.fitSplitPVoigt(**kws)

    def plotxy(self, *args, **kws):
        """wrapper to ShadowTools.plotxy

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

    def plotxy_footprint(self, **kws):
        """source foot print on optical element

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        None, sets self.fp
        """
        _beam = kws.get('beam', 'mirr.01')
        _col1 = kws.get('col1', 2)
        _col2 = kws.get('col2', 1)
        _nbins = kws.get('nbins', 100)
        _nolost = kws.get('nolost', 2)
        _title = kws.get('title', r'Footprint at $\theta$ = {0}'.format(self.rc.theta0))
        _xtitle = kws.get('ytitle', r'mirror meridional direction [cm]')
        _ytitle = kws.get('xtitle', r'mirror sagittal direction [cm]')
        _xr, _yr = 1.1, 1.1 # expand x,y ranges
        _xrange = kws.get('xrange', (self.oe1.RLEN2*_yr, self.oe1.RLEN1*_yr))
        _yrange = kws.get('yrange', (self.oe1.RWIDX2*_xr, self.oe1.RWIDX1*_xr))
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 5)
        self.fp = self.plotxy(_beam, _col1, _col2, nbins=_nbins, nolost=_nolost,
                              title=_title, xtitle=_xtitle, ytitle=_ytitle,
                              xrange=_xrange, yrange=_yrange,
                              calfwhm=_calfwhm, noplot=_noplot,
                              contour=_contour, level=_level)

    def plotxy_detector(self, **kws):
        """oe1 foot print on detector

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        None, sets self.fp_det
        """
        _beam = kws.get('beam', 'mirr.02')
        _col1 = kws.get('col1', 1)
        _col2 = kws.get('col2', 2)
        _nbins = kws.get('nbins', 100)
        _nolost = kws.get('nolost', 1)
        _title = kws.get('title', r'Footprint at $\theta$ = {0}'.format(self.rc.theta0))
        _xtitle = kws.get('ytitle', 'x - ??? [cm]')
        _ytitle = kws.get('xtitle', 'y - ??? [cm]')
        _xrange = kws.get('xrange', None)
        _yrange = kws.get('yrange', None) 
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 6)
        self.fp_det = self.plotxy(_beam, _col1, _col2, nbins=_nbins, nolost=_nolost,
                                  title=_title, xtitle=_xtitle, ytitle=_ytitle,
                                  xrange=_xrange, yrange=_yrange,
                                  calfwhm=_calfwhm, noplot=_noplot,
                                  contour=_contour, level=_level)

        
    def plotxy_image(self, **kws):
        """image of an optical element

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        None, sets self.ip
        """
        _beam = kws.get('beam', 'star.01')
        _col1 = kws.get('col1', 1)
        _col2 = kws.get('col2', 3)
        _nbins = kws.get('nbins', 100)
        _nolost = kws.get('nolost', 1)
        _title = kws.get('title', r'Image at $\theta$ = {0}'.format(self.theta))
        _xtitle = kws.get('xtitle', 'x - sagittal (Hor. focusing) [cm]')
        _ytitle = kws.get('ytitle', 'z - meridional (E dispersion) [cm]')
        _xrange = kws.get('xrange', None)
        _yrange = kws.get('yrange', None) 
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 6)
        self.ip = self.plotxy(_beam, _col1, _col2, nbins=_nbins, nolost=_nolost,
                              title=_title, xtitle=_xtitle, ytitle=_ytitle,
                              xrange=_xrange, yrange=_yrange,
                              calfwhm=_calfwhm, noplot=_noplot,
                              contour=_contour, level=_level)


    def histo1(self, *args, **kws):
        """wrapper to ShadowTools.histo1
        
        Plot the histogram of a column, simply counting the rays, or
        weighting with the intensity.  It returns a
        ShadowTools.Histo1_Ticket which contains the histogram data,
        and the figure.

        Parameters
        ----------
        beam : str
               instance with the name of the shadow file to be loaded,
               or a ShadowLib.Beam initialized instance.
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

    def histo1_energy(self, **kws):
        """energy histogram

        Parameters
        ----------
        See self.histo1
        
        Returns
        -------
        None: sets self.h1e
        """
        beam = kws.get('beam', 'star.01')
        col = kws.get('col', 11)
        nbins = kws.get('nbins', 500)
        nolost = kws.get('nolost', 1)
        ref = kws.get('ref', 1)
        calfwhm = kws.get('calfwhm', 1)
        noplot = kws.get('noplot', 1)
        write = kws.get('write', 0)
        self.h1e = self.histo1(beam, col, nbins=nbins, nolost=nolost, ref=ref,
                               calfwhm=calfwhm, noplot=noplot, write=write)

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

    def close_all_plots(self):
        """close all Matplotlib plots"""
        return ShadowTools.plt.close("all")

    def set_rowland_radius(self, Rm, isJohansson=False):
        """set Rowland circle radius [cm]

        Parameters
        ----------
        Rm : float
             meridional Rowland radius in cm
        isJohansson : boolean, False
                      flag to set Johansson geometry
        """
        self.oe1.FMIRR = 1
        self.oe1.RMIRR = Rm
        if isJohansson:
            self.oe1.F_JOHANSSON = 1
            self.oe1.R_JOHANSSON = Rm * 2.
        else:
            self.oe1.F_JOHANSSON = 0

    def set_dspacing(self, d=None, hkl=None, latfunz=None, **kws):
        """set the crystal d-spacing [Ang]

        Parameters
        ----------
        d : float, None
            d-spacing [\AA]
        hkl : tuple, None
              (h, k, l)
        lattice : function, None
                  bu.d_cubic -> a
                  bu.d_hexagonal -> a, c
                  bu.d_tetragonal -> a, c
                  bu.d_orthorhombic -> a, b, c
                  bu.d_monoclinic -> a, b, c, beta
                  bu.d_triclinic -> a, b, c, alpha, beta, gamma
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
    
    def move_theta(self, theta0, dth=[0.1, 0.1], deltaE=[None, None]):
        """from a starting config, go to a given Bragg angle

        Parameters
        ----------
        theta0 : float
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
        if not self.rc.d:
            print('Aborted: set the crystal d-spacing first')
            return
        elif not self.rc.Rm:
            print('Aborted: set the Rowland circle radius first')
            return
        else:
            self.rc.set_theta0(theta0)
            d = self.rc.d
            ene0 = self.rc.get_ene()
            # adjust source energy to new theta0
            self.oe1.PHOT_CENT = ene0
            if (deltaE[0] is None):
                self.src.PH1 = bu.bragg_ev(d, theta0+abs(dth[1]))
            else:
                self.src.PH1 = ene0 - abs(deltaE[0])    
            if (deltaE[1] is None):
                self.src.PH2 = bu.bragg_ev(d, theta0-abs(dth[0]))
            else:
                self.src.PH2 = ene0 + abs(deltaE[1])
            # adjust source divergence to new theta0 (assumig flat)
            _hlp = abs(self.oe1.RLEN1)  # half-length pos
            _hln = abs(self.oe1.RLEN2)  # half-length neg
            _hwp = abs(self.oe1.RWIDX1) # half-width pos
            _hwn = abs(self.oe1.RWIDX2) # half-width neg
            _rth0 = self.rc.rtheta0
            _pcm = self.rc.p # cm
            _vdiv_pos = math.atan( (_hlp * math.sin(_rth0)) / (_pcm + _hlp * math.cos(_rth0) ) )
            _vdiv_neg = math.atan( (_hln * math.sin(_rth0)) / (_pcm - _hln * math.cos(_rth0) ) )
            _hdiv_pos = math.atan( (_hwp / _pcm) )
            _hdiv_neg = math.atan( (_hwn / _pcm) )
            self.src.VDIV1 = _vdiv_pos * 1.1 # empirical!
            self.src.VDIV2 = _vdiv_neg * 1.1 # empirical!
            self.src.HDIV1 = _hdiv_pos * 1.1 # empirical!
            self.src.HDIV2 = _hdiv_neg * 1.1 # empirical!

            # adjust analyser to new theta0
            self.oe1.T_SOURCE = self.rc.p # cm
            self.oe1.T_IMAGE = self.rc.q # cm
            self.oe1.T_INCIDENCE = 90.0 - theta0
            self.oe1.T_REFLECTION = 90.0 - theta0
            # adjust detector ...

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
                
            #self.run()

if __name__ == '__main__':
    dsi444 = bu.d_cubic(bu.SI_ALAT, (4,4,4))
    t = ShadowSpectro1(theta0=75., Rm=50., d=dsi444, useCm=True, showInfos=True)
    pass

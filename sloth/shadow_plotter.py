#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_plotter: custom plotting utility for SHADOW3_

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow

TODO
----
- move to PyMca5 plotting objects

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import sys, os
import math
import numpy as np

HAS_PY3 = False
HAS_SHADOW = False
HAS_OSHADOW = False

if sys.version_info >= (3,2,0): HAS_PY3 = True

# see README.rst how to install XOP and SHADOW3
try:
    from Shadow import ShadowTools as st
    from Shadow import ShadowToolsPrivate as stp
    HAS_SHADOW = True
except:
    #print(sys.exc_info()[1])
    pass

# new plotter with ShadowPlot and PyMca
from PyQt4.QtGui import QApplication, QWidget, QGridLayout, QGraphicsScene, QGraphicsView, QFrame
from PyQt4.QtCore import Qt, QCoreApplication

try:
    from orangecontrib.shadow.util.shadow_util import ShadowPlot
    HAS_OSHADOW = True
except:
    pass

from PyMca5.PyMcaGui.plotting.PlotWindow import PlotWindow
from PyMca5.PyMcaGui.plotting.MaskImageWidget import MaskImageWidget

    
class ShadowPlotter(object):
    """ShadowPlotter: plotxy and histo1"""
    def __init__(self):
        if not HAS_SHADOW: raise ImportError("Shadow not found")
        pass

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
        return st.plotxy(*args, **kws)

    def plotxy_footprint(self, *args, **kws):
        """foot print on optical element

        Parameters
        ----------
        See self.plotxy

        Returns
        -------
        ShadowTools.Histo1_Ticket instance
        """
        _beam = args[0]
        _col1 = 2
        _col2 = 1
        _nbins = kws.get('nbins', 100)
        _nolost = kws.get('nolost', 2)
        _title = kws.get('title', r'Footprint')
        _xtitle = kws.get('ytitle', r'mirror meridional direction [cm]')
        _ytitle = kws.get('xtitle', r'mirror sagittal direction [cm]')
        _xr, _yr = 1.1, 1.1 # expand x,y ranges
        _xrange = kws.get('xrange', None)
        _yrange = kws.get('yrange', None)
        _calfwhm = kws.get('calfwhm', 1)
        _level = kws.get('level', 15)
        _noplot = kws.get('noplot', 0)
        _contour = kws.get('contour', 0)
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
        _beam = args[0]
        _col1 = 1
        _col2 = 3
        _nbins = kws.get('nbins', 100)
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
        return st.histo1(*args, **kws)

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

    def close_all_plots(self):
        """close all Matplotlib plots"""
        return st.plt.close("all")

class SwPlot(object):

    def __init__(self):
        if not (HAS_PY3 and HAS_OSHADOW): raise ImportError("Orange-shadow not found")
        
        self.plot_2d = MaskImageWidget(colormap=False, selection=False, imageicons=False, aspect=False)
        self.plot_2d.setDefaultColormap(6, False)
        self.plot_2d.setMinimumHeight(350)
        self.plot_2d.setMaximumHeight(350)
        self.plot_2d.setMaximumWidth(550)
        self.plot_2d.setMaximumWidth(550)
        
        self.histo_x = PlotWindow(roi=False, control=False, position=False, plugins=False)
        self.histo_x.setDefaultPlotLines(True)
        self.histo_x.setActiveCurveColor(color='darkblue')
        self.histo_x.setFixedHeight(180)
        self.histo_x.setMaximumWidth(550)
        
        self.histo_y = PlotWindow(roi=False, control=False, position=False, plugins=False)
        self.histo_y.setDefaultPlotLines(True)
        self.histo_y.setActiveCurveColor(color='darkblue')
        self.histo_y.setFixedHeight(180)
        self.histo_y.setFixedWidth(330)
        
        scene = QGraphicsScene()
        item = scene.addWidget(self.histo_y)
        item.rotate(90)
        
        view = QGraphicsView()
        view.setScene(scene)
        view.setFixedWidth(180)
        view.setFixedHeight(350)
        view.setFrameStyle(QFrame.NoFrame)
        view.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        layout = QGridLayout()
        
        layout.addWidget(self.histo_x, 0, 0, 1, 1)
        layout.addWidget(QWidget(), 0, 1, 1, 1) # box per la statistica
        layout.addWidget(self.plot_2d, 1, 0, 1, 1)
        layout.addWidget(view, 1, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
        
        layout.setColumnMinimumWidth(0, 550)
        layout.setColumnMinimumWidth(1, 350)
        
        self.box = QWidget()
        self.box.setLayout(layout)
        
        #self.box.show()

    def plotxy(self, beam):
        self.beam = beam
        self.plot_data = ShadowPlot.plotxy(self.plot_2d, self.histo_x, self.histo_y, self.beam,
                                           1, 3, None, None, nolost=1, title="PIPPO", xtitle="X", ytitle="Z")

        print("INTENSITY = ", "{:5.4f}".format(self.plot_data.intensity))
        print("TOTAL RAYS = ", str(self.plot_data.total_number_of_rays))
        print("TOTAL GOOD RAYS = ", str(self.plot_data.total_good_rays))
        print("TOTAL LOST RAYS = ", str(self.plot_data.total_lost_rays))
        print("FWHM H = ", "{:9.8f}".format(self.plot_data.fwhm_h))
        print("FWHM V = ", "{:9.8f}".format(self.plot_data.fwhm_v))

        
        
if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        print('standart app instance')
        app = QApplication(sys.argv)
    
    p = SwPlot()
    p.box.show()

    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except:
        print('standard exec_')
        sys.exit(app.exec_())
    #pass

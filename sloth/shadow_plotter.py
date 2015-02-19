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
from PyQt4 import QtCore, QtGui, uic

from PyMca5.PyMcaGui.plotting.PlotWindow import PlotWindow
from PyMca5.PyMcaGui.plotting.MaskImageWidget import MaskImageWidget

try:
    from orangecontrib.shadow.util.shadow_util import ShadowPlot
    HAS_OSHADOW = True
except:
    pass

### SLOTH ###
from __init__ import _libDir
sys.path.append(_libDir)
uifile = os.path.join(_libDir, "shadow_plotter.ui")
UiClass, BaseClass = uic.loadUiType(uifile)


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
        _beam = args[0]
        _col = 11
        _nbins = kws.get('nbins', 500)
        _nolost = kws.get('nolost', 1)
        _ref = kws.get('ref', 1)
        _calfwhm = kws.get('calfwhm', 1)
        _noplot = kws.get('noplot', 1)
        _write = kws.get('write', 0)
        return self.histo1(_beam, _col, nbins=_nbins, nolost=_nolost, ref=_ref,\
                           calfwhm=_calfwhm, noplot=_noplot, write=_write)

    def close_all_plots(self):
        """close all Matplotlib plots"""
        return st.plt.close("all")

class SwPlot(object):

    def __init__(self, beam=None):
        if not (HAS_PY3 and HAS_OSHADOW): raise ImportError("Orange-shadow not found")

        self.set_instance(beam)

        #2D plot
        self.plot_2d = MaskImageWidget(colormap=False, selection=False, imageicons=False, aspect=False)
        self.plot_2d.setDefaultColormap(6, False)
        self.plot_2d.setMinimumHeight(350)
        self.plot_2d.setMaximumHeight(350)
        self.plot_2d.setMaximumWidth(550)
        self.plot_2d.setMaximumWidth(550)

        #projection 2D plot
        self.histo_x = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_x.setDefaultPlotLines(True)
        self.histo_x.setUpdatesEnabled(True)
        self.histo_x.setActiveCurveColor(color='black')
        self.histo_x.setFixedHeight(180)
        self.histo_x.setMaximumWidth(550)

        #projection 2D plot
        self.histo_y = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_y.setDefaultPlotLines(True)
        self.histo_y.setUpdatesEnabled(True)
        self.histo_y.setActiveCurveColor(color='black')
        self.histo_y.setFixedHeight(180)
        self.histo_y.setFixedWidth(330)

        #generic histogram (e.g. energy)
        self.histo_z = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_z.setDefaultPlotLines(True)
        self.histo_z.setUpdatesEnabled(True)
        self.histo_z.setActiveCurveColor(color='black')
        self.histo_z.setFixedHeight(350)
        self.histo_z.setFixedWidth(350)
        
        scene = QtGui.QGraphicsScene()
        item = scene.addWidget(self.histo_y)
        item.rotate(90)
        
        view = QtGui.QGraphicsView()
        view.setScene(scene)
        view.setFixedWidth(180)
        view.setFixedHeight(350)
        view.setFrameStyle(QtGui.QFrame.NoFrame)
        view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        layout = QtGui.QGridLayout()
        
        layout.addWidget(self.histo_x, 0, 0, 1, 1)
        layout.addWidget(self.histo_z, 0, 1, 1, 1)
        #layout.addWidget(QtGui.QWidget(), 0, 1, 1, 1) # box per la statistica
        layout.addWidget(self.plot_2d, 1, 0, 1, 1)
        layout.addWidget(view, 1, 1, 1, 1, QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)
        
        layout.setColumnMinimumWidth(0, 550)
        layout.setColumnMinimumWidth(1, 350)
        
        self.box = QtGui.QWidget()
        self.box.setLayout(layout)
        
        #self.box.show()

    def set_instance(self, beam):
        """set ShadowLib.Beam instance"""
        self.beam = beam

    def get_instance(self):
        """get ShadowLib.Beam instance"""
        return self.beam

    def plot_histo(self, beam, col, xrange=None, yrange=None, nbins=100, nolost=0, ref=0, fwrite=0,\
                   title='HISTO1', xtitle=None, ytitle=None, calfwhm=1, noplot=1,\
                   orientation='vertical', plotxy=0, replace=True, plotWin=None):
        """histogram plotter

        Parameters
        ----------

        beam : ShadowLib.Beam initialized instance

        [...]

        plotWin : PlotWindow instance, None

                  if None, takes self.histo_z

        """
        if plotWin is None: plotWin = self.histo_z
        try:
            stp.Histo1_CheckArg(beam, col, xrange, yrange, nbins, nolost, ref, fwrite,\
                                title, '', '', 1, 1)
        except stp.ArgsError as e:
            raise e

        col = col-1

        if ref==0:
            x, good_only = st.getshcol(beam, (col+1, 10))
            weight = np.ones(len(x))
        else:
            x, good_only, weight = st.getshcol(beam, (col+1, 10, ref))

        if nolost==0: t = np.where(good_only!=-3299)
        if nolost==1: t = np.where(good_only==1.0)
        if nolost==2: t = np.where(good_only!=1.0)

        if len(t[0])==0:
            print ("no rays match the selection, the histogram will not be plotted")
            return

        #if xrange is None: xrange = stp.setGoodRange(x[t])

        if ref==0:
            histogram, bins = np.histogram(x[t], bins=nbins, range=xrange)
        else:
            if not ytitle is None:  ytitle = ytitle + ' % ' + (stp.getLabel(ref-1))[0]
            histogram, bins = np.histogram(x[t], bins=nbins, range=xrange, weights=weight[t])

        fwhm, tf, ti = stp.calcFWHM(histogram, bins[1]-bins[0])

        bins = bins - ((np.max(x)/nbins)*0.5)

        if yrange is None: yrange = [0.0, np.max(histogram)*1.1]

        if xtitle is None: xtitle = (stp.getLabel(col))[0]
        if (ytitle is None) and (ref != 0):
            ytitle = 'Weighted by {0}'.format(stp.getLabel(ref)[0])
        else:
            ytitle = 'No weight'

        plotWin.setGraphXLabel(xtitle)
        plotWin.setGraphYLabel(ytitle)
        plotWin.setDrawModeEnabled(True, 'rectangle')
        plotWin.setZoomModeEnabled(True)
        plotWin.addCurve(bins[1:], histogram, title, symbol=',', color='blue', replace=replace) #'+', '^', ','
        return fwhm

    def plotxy(self, beam, cols1, cols2, nbins=101, nbins_h=100, level=5,\
               xrange=None, yrange=None, nolost=1, title='PLOTXY', xtitle=None, ytitle=None,\
               noplot=1, calfwhm=1, contour=6,\
               imgWidget=None, upPlotWin=None, rightPlotWin=None):
        """

        """
        if imgWidget is None: imgWidget = self.plot_2d
        if upPlotWin is None: upPlotWin = self.histo_x
        if rightPlotWin is None: rightPlotWin = self.histo_y

        try:
            stp.plotxy_CheckArg(beam, cols1, cols2, nbins, nbins_h, level, xrange, yrange, nolost,\
                                title, xtitle, ytitle, noplot, calfwhm, contour)
        except stp.ArgsError as e:
            raise e

        col1, col2, col3, col4 = st.getshcol(beam, (cols1, cols2, 10, 23))

        if xtitle==None: xtitle=(stp.getLabel(cols1-1))[0]
        if ytitle==None: ytitle=(stp.getLabel(cols2-1))[0]

        if nolost==0: t = np.where(col3!=-3299)
        if nolost==1: t = np.where(col3==1.0)
        if nolost==2: t = np.where(col3!=1.0)

        if xrange==None: xrange = stp.setGoodRange(col1[t])
        if yrange==None: yrange = stp.setGoodRange(col2[t])

        tx = np.where((col1>xrange[0])&(col1<xrange[1]))
        ty = np.where((col2>yrange[0])&(col2<yrange[1]))

        tf = set(list(t[0])) & set(list(tx[0])) & set(list(ty[0]))
        t = (np.array(sorted(list(tf))),)

        if len(t[0])==0:
            print ("no point selected")
            return None

        weight = col4

        grid = np.zeros(nbins*nbins).reshape(nbins, nbins)

        intensity = 0.0

        for i in t[0]:
          indY = stp.findIndex(col1[i], nbins, xrange[0], xrange[1])
          indX = (nbins-1)-stp.findIndex(col2[i], nbins, yrange[0], yrange[1])
          try:
            grid[indX][indY] = grid[indX][indY] + weight[i]
            intensity = intensity + weight[i]
          except IndexError:
            pass

        imgWidget.setWindowTitle(title)
        imgWidget.setXLabel(xtitle)
        imgWidget.setYLabel(ytitle)
        imgWidget.setImageData(grid, xScale=(xrange[0], (xrange[1]-xrange[0])/nbins),\
                               yScale=(yrange[0], (yrange[1]-yrange[0])/nbins))

        fwhm_h = self.plot_histo(beam, cols1, xrange=xrange, yrange=None, nolost=nolost, ref=23,\
                                 title=xtitle, plotWin=upPlotWin)
        fwhm_v = self.plot_histo(beam, cols2, xrange=yrange, yrange=None, nolost=nolost, ref=23,\
                                 title=ytitle, plotWin=rightPlotWin)

        total_number_of_rays = len(beam.rays)
        total_good_rays = len(beam.rays[np.where(beam.rays[:,9] == 1)])

        infos = {}

        infos.update({'intensity' : intensity,
                      'total_number_of_rays' : total_number_of_rays,
                      'total_good_rays' : total_good_rays,
                      'total_lost_rays' : total_number_of_rays-total_good_rays,
                      'fwhm_h' : fwhm_h,
                      'fwhm_v' : fwhm_v})
        return infos

    # def plotxy(self, beam):
    #     self.beam = beam
    #     self.plot_data = ShadowPlot.plotxy(self.plot_2d, self.histo_x, self.histo_y, self.beam,\
    #                                        1, 3, None, None, nolost=1, title="PIPPO",\
    #                                        xtitle="X", ytitle="Z")

    #     print("INTENSITY = ", "{:5.4f}".format(self.plot_data.intensity))
    #     print("TOTAL RAYS = ", str(self.plot_data.total_number_of_rays))
    #     print("TOTAL GOOD RAYS = ", str(self.plot_data.total_good_rays))
    #     print("TOTAL LOST RAYS = ", str(self.plot_data.total_lost_rays))
    #     print("FWHM H = ", "{:9.8f}".format(self.plot_data.fwhm_h))
    #     print("FWHM V = ", "{:9.8f}".format(self.plot_data.fwhm_v))

    # def plotxy_footprint(self, *args, **kws):
    #     """foot print on optical element

    #     Parameters
    #     ----------
    #     See ShadowPlot.plotxy in shadow_util

    #     Returns
    #     -------
    #     None, self.plot_data
    #     """
    #     _beam = args[0]
    #     self.beam = _beam
    #     _col1 = 2
    #     _col2 = 1
    #     _nolost = kws.get('nolost', 2)
    #     _title = kws.get('title', r'Footprint')
    #     _xtitle = kws.get('ytitle', r'mirror meridional direction [cm]')
    #     _ytitle = kws.get('xtitle', r'mirror sagittal direction [cm]')
    #     _xr, _yr = 1.1, 1.1 # expand x,y ranges
    #     _xrange = kws.get('xrange', None)
    #     _yrange = kws.get('yrange', None)
    #     self.plot_data = ShadowPlot.plotxy(self.plot_2d, self.histo_x, self.histo_y, self.beam,\
    #                                        _col1, _col2, _xrange, _yrange, _nolost,\
    #                                        _title, _xtitle, _ytitle)
    
class SwPlotterMain(BaseClass, UiClass):

    def __init__(self, parent=None):
        super(SwPlotterMain, self).__init__(parent)
        self.setupUi(self)
        self.actionExit.triggered.connect(self.close)

        #2D plot
        self.plot_2d = MaskImageWidget(colormap=True, selection=False, imageicons=False, aspect=False)
        self.plot_2d.setDefaultColormap(6, False)

        #projection 2D plot
        self.histo_x = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_x.setDefaultPlotLines(True)
        self.histo_x.setUpdatesEnabled(True)
        self.histo_x.setActiveCurveColor(color='black')

        #projection 2D plot
        self.histo_y = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_y.setDefaultPlotLines(True)
        self.histo_y.setUpdatesEnabled(True)
        self.histo_y.setActiveCurveColor(color='black')

        #generic histogram (e.g. energy)
        self.histo_z = PlotWindow(roi=False, control=False, position=True, plugins=False)
        self.histo_z.setDefaultPlotLines(True)
        self.histo_z.setUpdatesEnabled(True)
        self.histo_z.setActiveCurveColor(color='black')
        
        layout_img = QtGui.QVBoxLayout(self.image_plot)
        layout_img.addWidget(self.plot_2d)
        layout_hx = QtGui.QVBoxLayout(self.up_plot)
        layout_hx.addWidget(self.histo_x)
        layout_hy = QtGui.QVBoxLayout(self.right_plot)
        layout_hy.addWidget(self.histo_y)
        layout_hz = QtGui.QVBoxLayout(self.dia_plot)
        layout_hz.addWidget(self.histo_z)

if __name__ == '__main__':
    app = QtCore.QCoreApplication.instance()
    if app is None:
        print('standart app instance')
        app = QtGui.QApplication(sys.argv)
    
    #p = SwPlot()
    #p.box.show()
    p = SwPlotterMain()
    p.show()

    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except:
        print('standard exec_')
        sys.exit(app.exec_())
    #pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Sloth custom version of SILX Plot2D
======================================
"""
import time
import numpy as np
from silx.gui.plot import Plot2D as silxPlot2D
import logging


class Plot2D(silxPlot2D):
    """Custom Plot2D instance targeted to 2D images"""

    def __init__(self, parent=None, backend=None):

        super(Plot2D, self).__init__(parent=parent, backend=backend)
        self._logger = logging.getLogger("Plot2D")
        self._index = None
        self._image = None
        self._mask = None
        self._origin = (0, 0)
        self._scale = (1, 1)
        self._xlabel = 'X'
        self._ylabel = 'Y'
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('viridis')

    def setLogLevel(self, level=logging.INFO):
        """Set report level of the logger"""
        self._logger.setLevel(level)

    def _drawContours(self, values, lineStyleCallback=None,
                      plot_timeout=10):
        """Draw iso contours for given values

        Parameters
        ----------
        values : list or array
            intensities at which to find contours
        lineStyleCallback : function or None (optional)
            a function that return a dictionary of
            linestyle, linewidth and color for
            value, ivalue and ipolygon
        plot_timeout : int (optionale)
            time in seconds befor the plot is interrupted
        """
        if self._ms is None:
            return
        ipolygon = 0
        totTime = 0
        for ivalue, value in enumerate(values):
            startTime = time.time()
            polygons = self._ms.find_contours(value)
            polTime = time.time()
            self._logger.debug(f"Found {len(polygons)} polygon at level {value}")
            totTime += polTime - startTime
            for polygon in polygons:
                legend = "polygon-%d" % ipolygon
                if len(polygon) == 0:
                    continue

                xpoly = polygon[:, 1]
                ypoly = polygon[:, 0]
                xscale = np.ones_like(xpoly) * self._scale[0]
                yscale = np.ones_like(ypoly) * self._scale[1]
                xorigin = np.ones_like(xpoly) * self._origin[0]
                yorigin = np.ones_like(ypoly) * self._origin[1]
                x = xpoly * xscale + xorigin
                y = ypoly * yscale + yorigin

                if lineStyleCallback is not None:
                    extraStyle = lineStyleCallback(value, ivalue, ipolygon)
                else:
                    extraStyle = {"linestyle": "-",
                                  "linewidth": 0.5,
                                  "color": "gray"}
                if totTime > plot_timeout:
                    self._logger.warning("Plot contours time out reached!")
                    break
                self.addCurve(x=x, y=y, legend=legend, resetzoom=False,
                              **extraStyle)
                pltTime = time.time()
                totTime += pltTime - polTime
                ipolygon += 1

    def addContours(self, nlevels, algo='merge'):
        """Add contour lines to plot

        Parameters
        ----------
        nlevels : int
            number of contour levels to plot

        algo : str (optional)
            marching squares algorithm implementation
            'merge' -> silx
            'skimage' -> scikit-image
        color : str, optional
            color of contour lines ['gray']
        linestyle : str, optional
            line style of contour lines ['-']
        linewidth : int, optional
            line width of contour lines [1]

        Returns
        -------
        None
        """
        image = self._image
        mask = self._mask
        if image is None:
            self._logger.error('add image first!')
        if algo == 'merge':
            from silx.image.marchingsquares._mergeimpl import MarchingSquaresMergeImpl
            self._ms = MarchingSquaresMergeImpl(image, mask=mask)
        elif algo == 'skimage':
            try:
                import skimage
                from silx.image.marchingsquares._skimage import MarchingSquaresSciKitImage
                self._ms = MarchingSquaresSciKitImage(image,
                                                      mask=mask)
            except ImportError:
                self._logger.error('skimage not found')
                self._ms = None
        else:
            self._ms = None
        imgmin, imgmax = image.min(), image.max()
        delta = (imgmax - imgmin) / nlevels
        values = np.arange(imgmin, imgmax, delta)
        self._drawContours(values)

    def index(self):
        if self._index is None:
            self._index = 0
        return self._index

    def setIndex(self, value):
        self._index = value
        if self._index is not None:
            self.setWindowTitle('{}: Plot2D'.format(self._index))

    def addImage(self, data, x=None, y=None, xlabel=None, ylabel=None,
                 **kwargs):
        """Custom addImage

        Parameters
        ----------
        data : array
        x, y : None or array (optional)
            x, y to set origin and scale (both should be given!)
        xlabel, ylabel : None or str (optional)
            set self.setGraphXLabel / self.setGraphYLabel
        """
        self._image = data
        self._x = x
        self._y = y
        if (x is not None) and (y is not None):
            self._origin = (np.min(x), np.max(y))
            self._scale = (x[1]-x[0], y[1]-y[0])
        if xlabel is not None:
            self._xlabel = xlabel
            self.setGraphXLabel(xlabel)
        if ylabel is not None:
            self._ylabel = ylabel
            self.setGraphYLabel(ylabel)
        return super(Plot2D, self).addImage(data, origin=self._origin,
                                            scale=self._scale,
                                            **kwargs)


def main(contour_levels=5, noise=0.01, compare_with_matplolib=False):
    """Run a Qt app with the widget"""
    from sloth.test.dummy_data import dummy_gauss_image
    from silx import sx
    sx.enable_gui()
    xhalfrng = 10.5
    yhalfrng = 5.5
    npts = 1024
    xcen = 0
    ycen = 0
    x = np.linspace(xcen-0.7*xhalfrng, xcen+1.3*xhalfrng, npts)
    y = np.linspace(ycen-0.7*yhalfrng, ycen+1.3*yhalfrng, npts)
    x1, y1, signal1 = dummy_gauss_image(x=x, y=y, xcen=xcen, ycen=ycen,
                                        xsigma=3, ysigma=1.1,
                                        noise=noise)
    x2, y2, signal2 = dummy_gauss_image(x=x, y=y,
                                        xcen=4.2, ycen=2.2,
                                        xsigma=3, ysigma=2.1,
                                        noise=noise)
    signal = signal1 + 0.8*signal2
    p = Plot2D(backend='matplotlib')
    p.setLogLevel(logging.DEBUG)
    p.addImage(signal, x=x, y=y, xlabel='X', ylabel='Y')
    p.addContours(contour_levels)
    p.show()

    if compare_with_matplolib:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        plt.ion()
        plt.close('all')
        fig, ax = plt.subplots()
        imgMin, imgMax = np.min(signal), np.max(signal)
        values = np.linspace(imgMin, imgMax, contour_levels)
        extent = (x.min(), x.max(), y.min(), y.max())
        ax.imshow(signal, origin='lower', extent=extent,
                  cmap=cm.viridis)
        ax.contour(x, y, signal, values, origin='lower', extent=extent,
                   colors='gray', linewidths=1)
        ax.set_title("pure matplotlib")
        plt.show()

    input("Press enter to close window")


if __name__ == '__main__':
    main()

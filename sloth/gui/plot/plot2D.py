#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Sloth custom version of SILX Plot2D
======================================
"""
import numpy as np
from silx.gui.plot import Plot2D as silxPlot2D
from silx.image.marchingsquares import MarchingSquaresMergeImpl


class Plot2D(silxPlot2D):
    """Custom Plot2D instance targeted to 2D images"""

    def __init__(self, parent=None, backend=None):

        super(Plot2D, self).__init__(parent=parent, backend=backend)
        self._index = None
        self._image = None
        self._origin = (0, 0)
        self._scale = (1, 1)
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('viridis')

    def addContours(self, nlevels, color='gray', linestyle='-', linewidth=1):
        """Add contour lines to plot

        Parameters
        ----------
        nlevels : int
            number of contour levels to plot
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
        if image is None:
            print('ERROR: add image first!')
        imgmin, imgmax = np.min(image), np.max(image)
        levels = np.linspace(imgmin, imgmax, nlevels)
        ms = MarchingSquaresMergeImpl(image)
        for ilevel, level in enumerate(levels):
            contours = ms.find_contours(level=level)
            try:
                xcontours = contours[0][:, 1]
                ycontours = contours[0][:, 0]
                # xcontours = self._origin[0]*np.ones_like(contours[0][:, 1]) + self._scale[0]*contours[0][:, 1]
                # ycontours = self._origin[1]*np.ones_like(contours[0][:, 0]) + self._scale[1]*contours[0][:, 0]
                self.addCurve(xcontours, ycontours,
                              legend='contour {0}'.format(ilevel),
                              color=color, linestyle=linestyle,
                              linewidth=linewidth)
            except IndexError:
                print(f"error at level {ilevel}")
                pass

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
            self.setGraphXLabel(xlabel)
        if ylabel is not None:
            self.setGraphYLabel(ylabel)
        return super(Plot2D, self).addImage(data, origin=self._origin,
                                            scale=self._scale,
                                            **kwargs)


def main():
    """Run a Qt app with the widget"""
    from sloth.test.dummy_data import dummy_gauss_image
    from silx import sx
    sx.enable_gui()
    xhalfrng = 10.5
    yhalfrng = 5.5
    npts = 1024
    xcen = 0
    ycen = 0
    noise = 0.05
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
    p = Plot2D()
    p.addImage(signal)
    # p.addImage(signal, x=x, y=y, xlabel='X', ylabel='Y')
    # p.addContours(10)  # TODO: currently broken!!!
    p.show()
    input("Press enter to close window")


if __name__ == '__main__':
    main()

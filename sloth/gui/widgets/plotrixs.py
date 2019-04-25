#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot RIXS data
=================

.. note:: SILX equivalent of :mod:`sloth.collects.datagroup_rixs.RixsDataPlotter`

"""
import numpy as np
from silx.gui.plot import Plot2D
from silx.image.marchingsquares import MarchingSquaresMergeImpl


class RixsPlot2D(Plot2D):
    """RIXS equivalent of Plot2D"""

    def __init__(self, parent=None, backend=None):
        super(RixsPlot2D, self).__init__(parent=parent, backend=backend)
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('Blues')

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
        image = self.getActiveImage()
        if image is None:
            print('ERROR: add image first!')
            return
        else:
            image = image.getData()
        imgmin, imgmax = np.min(image), np.max(image)
        levels = np.linspace(imgmin, imgmax, nlevels)
        ms = MarchingSquaresMergeImpl(image)
        for ilevel, level in enumerate(levels):
            contours = ms.find_contours(level=level)
            try:
                self.addCurve(contours[0][:, 1], contours[0][:, 0],
                              legend='contour {0}'.format(ilevel),
                              color=color, linestyle=linestyle,
                              linewidth=linewidth)
            except IndexError:
                pass


if __name__ == '__main__':
    pass

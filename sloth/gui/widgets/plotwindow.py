#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom SILX PlotWindow
=========================

A custom PlotWindow widget based on SILX
"""
import sys
import numpy as np
from silx.gui import qt
from silx.gui.plot import actions
from silx.gui.plot import tools
from silx.gui.plot import items
# from silx.gui.plot import PlotWidget
from .plot1D import SlothPlot1D

__authors__ = ["Marius Retegan", "Mauro Rovezzi"]


class PlotWindow(SlothPlot1D):

    def __init__(self, parent=None, **kwargs):
        super(PlotWindow, self).__init__(parent=parent, **kwargs)

        if sys.platform == 'darwin':
            self.setIconSize(qt.QSize(24, 24))

        self.setActiveCurveHandling(False)
        self.setGraphGrid(None)  # do not show grid

        # Create toolbars.
        self._interactiveModeToolBar = tools.toolbars.InteractiveModeToolBar(
            parent=self, plot=self)
        self.addToolBar(self._interactiveModeToolBar)

        self._toolBar = qt.QToolBar('Curve or Image', parent=self)
        self._resetZoomAction = actions.control.ResetZoomAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._resetZoomAction)

        self._xAxisAutoScaleAction = actions.control.XAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._xAxisAutoScaleAction)

        self._yAxisAutoScaleAction = actions.control.YAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._yAxisAutoScaleAction)

        self._gridAction = actions.control.GridAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._gridAction)

        self._curveStyleAction = actions.control.CurveStyleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._curveStyleAction)

        self._colormapAction = actions.control.ColormapAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._colormapAction)

        self._keepAspectRatio = actions.control.KeepAspectRatioAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._keepAspectRatio)

        self.addToolBar(self._toolBar)

        self._outputToolBar = tools.toolbars.OutputToolBar(
            parent=self, plot=self)
        self.addToolBar(self._outputToolBar)

        windowHandle = self.window().windowHandle()
        if windowHandle is not None:
            self._ratio = windowHandle.devicePixelRatio()
        else:
            self._ratio = qt.QGuiApplication.primaryScreen().devicePixelRatio()

        self._snap_threshold_dist = 5

        self.sigPlotSignal.connect(self._plotEvent)
        self.statusBar().show()

        self._index = None

    def index(self):
        if self._index is None:
            self._index = 0
        return self._index

    def setIndex(self, value):
        self._index = value
        if self._index is not None:
            self.setWindowTitle('{}: Plot Window'.format(self._index))

    def _plotEvent(self, event):
        if event['event'] == 'mouseMoved':
            x, y = event['x'], event['y']
            xPixel, yPixel = event['xpixel'], event['ypixel']
            self._updateStatusBar(x, y, xPixel, yPixel)

    def _updateStatusBar(self, x, y, xPixel, yPixel):
        selectedItems = self._getItems(kind=('curve', 'image'))

        if not selectedItems:
            return

        distInPixels = (self._snap_threshold_dist * self._ratio) ** 2

        for item in selectedItems:
            if isinstance(item, items.curve.Curve):
                messageFormat = 'X: {:g}    Y: {:.3g}'
            elif isinstance(item, items.image.ImageData):
                messageFormat = 'X: {:g}    Y: {:g}'
                continue

            xArray = item.getXData(copy=False)
            yArray = item.getYData(copy=False)

            closestIndex = np.argmin(
                pow(xArray - x, 2) + pow(yArray - y, 2))

            xClosest = xArray[closestIndex]
            yClosest = yArray[closestIndex]

            axis = item.getYAxis()

            closestInPixels = self.dataToPixel(xClosest, yClosest, axis=axis)
            if closestInPixels is not None:
                curveDistInPixels = (
                    (closestInPixels[0] - xPixel)**2 +
                    (closestInPixels[1] - yPixel)**2)

                if curveDistInPixels <= distInPixels:
                    # If close enough, snap to data point coordinates.
                    x, y = xClosest, yClosest
                    distInPixels = curveDistInPixels

        message = messageFormat.format(x, y)
        self.statusBar().showMessage(message)

    def reset(self):
        self.clear()
        self.setKeepDataAspectRatio(False)
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)


if __name__ == '__main__':
    pass

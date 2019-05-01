# coding: utf-8
# /*##########################################################################
# MIT License
#
# Copyright (c) 2018 DAXS developers.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
from __future__ import absolute_import, division

__authors__ = ['Marius Retegan']
__license__ = 'MIT'


import numpy as np
import sys

from silx.utils.weakref import WeakList
from silx.gui import qt
from silx.gui.plot import actions, tools, items, PlotWidget


class PlotWindow(PlotWidget):

    def __init__(self, parent=None, **kwargs):
        super(PlotWindow, self).__init__(parent=parent, **kwargs)

        if sys.platform == 'darwin':
            self.setIconSize(qt.QSize(24, 24))

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')

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


class MdiSubWindow(qt.QMdiSubWindow):

    def __init__(self, parent=None):
        super(MdiSubWindow, self).__init__(parent=parent)
        self.setAttribute(qt.Qt.WA_DeleteOnClose, True)

    def closeEvent(self, event):
        super(MdiSubWindow, self).closeEvent(event)
        # Renumber the plot windows and emit the changed signal.
        self.mdiArea().renumberPlotWindows()
        self.mdiArea().changed.emit()


class PlotArea(qt.QMdiArea):

    changed = qt.pyqtSignal()

    def __init__(self, parent=None):
        super(PlotArea, self).__init__(parent=parent)

        # Context menu
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # Set the order of the subwindows returned by subWindowList.
        self.setActivationOrder(qt.QMdiArea.CreationOrder)

    def plotWindows(self):
        widgets = WeakList()
        for subWindow in self.subWindowList():
            widgets.append(subWindow.widget())
        return widgets

    def showContextMenu(self, position):
        menu = qt.QMenu('Plot Area Menu', self)

        action = qt.QAction('Add Plot Window', self,
                            triggered=self.addPlotWindow)
        menu.addAction(action)

        menu.addSeparator()

        action = qt.QAction('Cascade Windows', self,
                            triggered=self.cascadeSubWindows)
        menu.addAction(action)

        action = qt.QAction('Tile Windows', self,
                            triggered=self.tileSubWindows)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def addPlotWindow(self, *args):
        subWindow = MdiSubWindow(parent=self)

        plotWindow = PlotWindow(parent=subWindow)
        plotWindow.setIndex(len(self.plotWindows()))

        subWindow.setWidget(plotWindow)
        subWindow.show()

        self.changed.emit()

    def renumberPlotWindows(self):
        for index, plotWindow in enumerate(self.plotWindows()):
            plotWindow.setIndex(index)

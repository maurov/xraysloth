#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot RIXS data
==============

.. note:: SILX equivalent of :mod:`sloth.collects.datagroup_rixs.RixsDataPlotter`

"""
from silx.gui import qt
from sloth.gui.plot.plotarea import PlotArea, MdiSubWindow
from sloth.gui.plot.plot2D import Plot2D
from sloth.utils.logging import getLogger

class RixsPlot2D(Plot2D):
    """RIXS equivalent of Plot2D"""

    def __init__(self, parent=None, backend=None, logger=None):
        """Constructor"""

        if logger is not None:
            self._logger = logger
        else:
            self._logger = getLogger("RixsPlot2D")

        super(RixsPlot2D, self).__init__(parent=parent, backend=backend, logger=self._logger)
        self.setWindowTitle('RixsPlot2D')
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('Blues')

class RixsPlotArea(PlotArea):
    """RIXS equivalent of PlotArea"""

    def __init__(self, parent=None):
        super(RixsPlotArea, self).__init__(parent=parent)

        self.setWindowTitle('RixsPlotArea')

    def showContextMenu(self, position):
        menu = qt.QMenu('RixsPlotArea Menu', self)

        action = qt.QAction('Add RixsPlot2D Window', self,
                            triggered=self.addRixsPlot2D)
        menu.addAction(action)

        menu.addSeparator()

        action = qt.QAction('Cascade Windows', self,
                            triggered=self.cascadeSubWindows)
        menu.addAction(action)

        action = qt.QAction('Tile Windows', self,
                            triggered=self.tileSubWindows)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def addRixsPlot2D(self, *args, plotType='1D'):
        """Add a RixPlot2D window in the mdi Area"""
        subWindow = MdiSubWindow(parent=self)
        plotWindow = RixsPlot2D(parent=subWindow)
        plotWindow.setIndex(len(self.plotWindows()))
        subWindow.setWidget(plotWindow)
        subWindow.show()
        self.changed.emit()
        return plotWindow

if __name__ == '__main__':
    pass

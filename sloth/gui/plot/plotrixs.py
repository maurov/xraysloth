#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot RIXS data
==============

.. note:: SILX equivalent of :mod:`sloth.collects.datagroup_rixs.RixsDataPlotter`

"""
from itertools import cycle
from silx.gui import qt
from silx.gui.plot.Profile import ProfileToolBar
from silx.gui.plot.actions import PlotAction

from sloth.gui.plot.plotarea import PlotArea, MdiSubWindow
from sloth.gui.plot.plot1D import Plot1D
from sloth.gui.plot.plot2D import Plot2D

from sloth.utils.logging import getLogger


class RixsRotateAction(PlotAction):
    """QAction rotating a Rixs plane

    :param plot: :class:`.PlotWidget` instance on which to operate
    :param parent: See :class:`QAction`
    """
    def __init__(self, plot, parent=None):
        PlotAction.__init__(self,
                            plot,
                            icon='compare-align-auto',
                            text='Rixs_et',
                            tooltip='Rotate RIXS plane to energy transfer',
                            triggered=self.rotateImage,
                            parent=parent)

    def rotateImage(self):
        """"""
        return


class RixsProfileToolBar(ProfileToolBar):
    """RIXS-adapted Profile (=Cuts) toolbar"""

    def __init__(self, parent=None, plot=None, profileWindow=None, overlayColors=None,
                 title='RIXS profile'):
        """Constructor"""
        super(RixsProfileToolBar, self).__init__(parent=parent, plot=plot,
                                                 profileWindow=profileWindow, title=title)

        self._overlayColors = overlayColors or cycle(['#1F77B4', '#AEC7E8',
                                                      '#FF7F0E', '#FFBB78',
                                                      '#2CA02C', '#98DF8A',
                                                      '#D62728', '#FF9896',
                                                      '#9467BD', '#C5B0D5',
                                                      '#8C564B', '#C49C94',
                                                      '#E377C2', '#F7B6D2',
                                                      '#7F7F7F', '#C7C7C7',
                                                      '#BCBD22', '#DBDB8D',
                                                      '#17BECF', '#9EDAE5'])

    def _getNewColor(self):
        return next(self._overlayColors)

    def updateProfile(self):
        """Update the displayed profile and profile ROI.
        This uses the current active image of the plot and the current ROI.
        """
        image = self.plot.getActiveImage()
        if image is None:
            return

        self._overlayColor = self._getNewColor()

        self._createProfile(currentData=image.getData(copy=False),
                            origin=image.getOrigin(), scale=image.getScale(),
                            colormap=None, z=image.getZValue(),
                            method=self.getProfileMethod())


class RixsPlot2D(Plot2D):
    """RIXS equivalent of Plot2D"""

    def __init__(self, parent=None, backend=None, logger=None,
                 profileWindow=None, overlayColors=None):
        """Constructor"""

        self._logger = logger or getLogger("RixsPlot2D")

        if profileWindow is None:
            profileWindow = Plot1D()

        super(RixsPlot2D, self).__init__(parent=parent, backend=backend,
                                         logger=self._logger)

        #: cleaning toolbar
        self.getMaskAction().setVisible(False)
        self.getYAxisInvertedAction().setVisible(False)
        self.getKeepDataAspectRatioAction().setVisible(False)
        self.getColorBarAction().setVisible(False)

        # Change default profile toolbar
        self.removeToolBar(self.profile)
        self.profile = RixsProfileToolBar(plot=self,
                                          profileWindow=profileWindow,
                                          overlayColors=overlayColors)
        self.addToolBar(self.profile)

        self.setWindowTitle('RixsPlot2D')
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('Blues')


class RixsPlotArea(PlotArea):
    """RIXS equivalent of PlotArea"""

    def __init__(self, parent=None, profileWindow=None):
        super(RixsPlotArea, self).__init__(parent=parent)

        self._overlayColors = cycle(['#1F77B4', '#AEC7E8', '#FF7F0E',
                                     '#FFBB78', '#2CA02C', '#98DF8A',
                                     '#D62728', '#FF9896', '#9467BD',
                                     '#C5B0D5', '#8C564B', '#C49C94',
                                     '#E377C2', '#F7B6D2', '#7F7F7F',
                                     '#C7C7C7', '#BCBD22', '#DBDB8D',
                                     '#17BECF', '#9EDAE5'])

        self.setWindowTitle('RixsPlotArea')
        self._profileWindow = profileWindow or self._addProfileWindow()
        self.setMinimumSize(300, 300)

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

    def _addProfileWindow(self):
        """Add a ProfileWindow in the mdi Area"""
        subWindow = MdiSubWindow(parent=self)
        plotWindow = Plot1D(parent=subWindow, title='Profiles')
        plotWindow.setIndex(len(self.plotWindows()))
        subWindow.setWidget(plotWindow)
        subWindow.show()
        self.changed.emit()
        return plotWindow

    def addRixsPlot2D(self, profileWindow=None):
        """Add a RixPlot2D window in the mdi Area"""
        subWindow = MdiSubWindow(parent=self)
        if profileWindow is None:
            profileWindow = self._profileWindow
        plotWindow = RixsPlot2D(parent=subWindow,
                                profileWindow=profileWindow,
                                overlayColors=self._overlayColors)
        plotWindow.setIndex(len(self.plotWindows()))
        subWindow.setWidget(plotWindow)
        subWindow.show()
        self.changed.emit()
        return plotWindow


class RixsMainWindow(qt.QMainWindow):

    def __init__(self, parent=None):

        super(RixsMainWindow, self).__init__(parent=parent)

        if parent is not None:
            #: behave as a widget
            self.setWindowFlags(qt.Qt.Widget)
        else:
            #: main window
            self.setWindowTitle('RIXS_VIEW')

        centralWidget = qt.QWidget(self)
        self._profileWindow = Plot1D(title='Profiles')
        self._rixsPlots = RixsPlotArea(parent=self,
                                       profileWindow=self._profileWindow)
        self._rixsPlots.addRixsPlot2D()

        gridLayout = qt.QGridLayout()
        gridLayout.setContentsMargins(1, 1, 1, 1)
        #: addWidget(widget, row, column, rowSpan, columnSpan[, alignment=0]))
        gridLayout.addWidget(self._rixsPlots, 0, 0, 1, 2)
        gridLayout.addWidget(self._profileWindow, 0, 1, 1, 1)

        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setMinimumSize(600, 600)


if __name__ == '__main__':
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""custom version of PlotWidget
===============================

initial version taken from

https://github.com/mretegan/crispy/blob/master/crispy/gui/widgets/plotwidget.py

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '13/03/2018'

"""

from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict as odict

from silx.gui import qt
from silx.gui.plot import Plot1D
from silx.gui.plot.backends.BackendMatplotlib import BackendMatplotlibQt
from silx.gui.plot.tools.CurveLegendsWidget import CurveLegendsWidget
from silx.gui.widgets.BoxLayoutDockWidget import BoxLayoutDockWidget

class customBackendMatplotlibQt(BackendMatplotlibQt):

    def __init__(self, plot, parent=None):
        super(customBackendMatplotlibQt, self).__init__(plot, parent)
        self._legends = odict()

    def addCurve(self, x, y, legend, *args, **kwargs):
        container = super(customBackendMatplotlibQt, self).addCurve(
            x, y, legend, *args, **kwargs)

        # Remove the unique identifier from the legend.
        legend = legend[:-11]
        curve = container.get_children()[0]
        self._legends[curve] = legend
        self._updateLegends()

        return container

    def remove(self, container):
        super(customBackendMatplotlibQt, self).remove(container)
        try:
            curve = container.get_children()[0]
            try:
                self._legends.pop(curve)
            except KeyError:
                pass
        except IndexError:
            pass
        self._updateLegends()

    def _updateLegends(self):
        curves = list()
        legends = list()

        for curve in self._legends:
            curves.append(curve)
            legends.append(self._legends[curve])

        legend = self.ax.legend(curves, legends, prop={'size': 'medium'})
        frame = legend.get_frame()
        frame.set_edgecolor('white')
        self.postRedisplay()

class customCurveLegendsWidget(CurveLegendsWidget):
    
    """Extension of CurveLegendWidget.

    .. note:: Taken from SILX examples -> plotCurveLegendWidget
    
    This widget adds:
    - Set a curve as active with a left click its the legend
    - Adds a context menu with content specific to the hovered legend
    :param QWidget parent: See QWidget
    """

    def __init__(self, parent=None):
        super(customCurveLegendsWidget, self).__init__(parent)

        # Activate/Deactivate curve with left click on the legend widget
        self.sigCurveClicked.connect(self._switchCurveActive)

        # Add a custom context menu
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)

    def _switchCurveActive(self, curve):
        """Set a curve as active.
        This is called from the context menu and when a legend is clicked.
        :param silx.gui.plot.items.Curve curve:
        """
        plot = curve.getPlot()
        plot.setActiveCurve(
            curve.getLegend() if curve != plot.getActiveCurve() else None)

    def _switchCurveVisibility(self, curve):
        """Toggle the visibility of a curve
        :param silx.gui.plot.items.Curve curve:
        """
        curve.setVisible(not curve.isVisible())

    def _switchCurveYAxis(self, curve):
        """Change the Y axis a curve is attached to.
        :param silx.gui.plot.items.Curve curve:
        """
        yaxis = curve.getYAxis()
        curve.setYAxis('left' if yaxis is 'right' else 'right')

    def _contextMenu(self, pos):
        """Create a show the context menu.
        :param QPoint pos: Position in this widget
        """
        curve = self.curveAt(pos)  # Retrieve curve from hovered legend
        if curve is not None:
            menu = qt.QMenu()  # Create the menu

            # Add an action to activate the curve
            activeCurve = curve.getPlot().getActiveCurve()
            menu.addAction('Unselect' if curve == activeCurve else 'Select',
                           functools.partial(self._switchCurveActive, curve))

            # Add an action to switch the Y axis of a curve
            yaxis = 'right' if curve.getYAxis() == 'left' else 'left'
            menu.addAction('Map to %s' % yaxis,
                           functools.partial(self._switchCurveYAxis, curve))

            # Add an action to show/hide the curve
            menu.addAction('Hide' if curve.isVisible() else 'Show',
                           functools.partial(self._switchCurveVisibility, curve))

            globalPosition = self.mapToGlobal(pos)
            menu.exec_(globalPosition)


class customPlotWidget(Plot1D):
    def __init__(self, *args):
        
        # super(customPlotWidget, self).__init__(
        #     logScale=False, grid=True, yInverted=False,
        #     roi=False, mask=False, print_=False, backend=customBackendMatplotlibQt)
        #super(customPlotWidget, self).__init__(backend=customBackendMatplotlibQt)
        super(customPlotWidget, self).__init__()

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')
        self.setDataMargins(0, 0, 0.05, 0.05)

        # Create a MyCurveLegendWidget associated to the plot
        self.legendsWidget = customCurveLegendsWidget()
        self.legendsWidget.setPlotWidget(self)

        # Add the CurveLegendsWidget as a dock widget to the plot
        self.dock = BoxLayoutDockWidget()
        self.dock.setWindowTitle('Legends')
        self.dock.setWidget(self.legendsWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self.dock)

        # Show the plot and run the QApplication
        self.setAttribute(qt.Qt.WA_DeleteOnClose)

    def reset(self):
        self.clear()
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)
        self.keepDataAspectRatio(False)

def main():
    """Run a Qt app with the widget"""
    app = qt.QApplication([])
    widget = customPlotWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()

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


class customPlotWidget(Plot1D):
    def __init__(self, *args):
        
        # super(customPlotWidget, self).__init__(
        #     logScale=False, grid=True, yInverted=False,
        #     roi=False, mask=False, print_=False, backend=customBackendMatplotlibQt)
        
        super(customPlotWidget, self).__init__(backend=customBackendMatplotlibQt)

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')
        self.setDataMargins(0, 0, 0.05, 0.05)

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

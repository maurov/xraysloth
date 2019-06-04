#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Viewer for a stack of 1D plots
==============================


"""
import numpy as np
from silx.gui import qt
from matplotlib.pyplot import cm
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser
from sloth.gui.plot.plot1D import Plot1D


class StackView1D(qt.QMainWindow):
    """1D equivalent of :class:`silx.gui.plot.StackView.StackView`.

    It implements in a main window (qt.MainWindow) a plot window
    (:class:`silx.gui.plot.PlotWindow`) connected to a slider widget
    (:class:`silx.gui.widgets.FrameBrower.HorizontalSliderWithBrowser`)
    """

    #: QT SIGNALS
    sigFrameChanged = qt.Signal(int)
    """Signal emitter when the frame number has changed.
        This signal provides the current frame number.
    """

    sigStackChanged = qt.Signal(int)
    """Signal emitted when the stack is changed.
    This happens when new data are loaded.
    The signal provides the size (length of list) of the stack.
    This is 0 if the stack is cleared, else a positive integer.
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent=parent)
        if parent is not None:
            #: behave as a widget
            self.setWindowFlags(qt.Qt.Widget)
        else:
            self.setWindowTitle('StackView1D')

        self._index = None  #: used for embedding in PlotArea

        #: DEFAULTS SETTINGS (updated for each plot in the stack)
        self._colors = None  #: default curve colors
        self._linewidth = 1  #: default curve _linewidth
        self._xlabel = 'xlabel'
        self._ylabel = 'ylabel'
        self._title = 'title'

        #: STACK FORMAT
        self._stack = None
        """Loaded stack, a list of lists of 1D arrays plus a dictionary:
           [[ [p1_x1, p1_y1, p1_info1], [p1_x2, p1_y2, p1_info2], ...,],
            [ ... ],
            [ [pN_x1, pN_y1, pN_info1], ... ],
            ].
        """

        centralWidget = qt.QWidget(self)
        self._plot = Plot1D()
        self.sigPlotSignal = self._plot.sigPlotSignal

        self._browser = HorizontalSliderWithBrowser(centralWidget)
        self._browser.setRange(0, 0)
        self._browser.valueChanged[int].connect(self.__updateFrameNumber)
        self._browser.setEnabled(False)

        gridLayout = qt.QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        #: addWidget(widget, row, column, rowSpan, columnSpan[, alignment=0]))
        gridLayout.addWidget(self._plot, 0, 0, 1, 2)
        gridLayout.addWidget(self._browser, 1, 0, 1, 2)

        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setMinimumSize(600, 800)

    def _set_colors(self, nlevels, colormap=None):
        """set a given number of default colors as linspace in colormap"""
        if colormap is None:
            colormap = cm.rainbow
        self._colors = colormap(np.linspace(0, 1, nlevels))

    def __updateFrameNumber(self, index):
        """Update the current plot.
        :param index: index of the frame to be displayed
        """
        if self._stack is None:
            #: no data set
            return
        curves = self._stack[index]  #: lists of curves
        self._set_colors(len(curves))

        for icurve, curve in enumerate(curves):
            assert len(curve) == 3, "list of curves must have [x, y, info]"
            x, y, info = curve[0], curve[1], curve[2]
            #PLOT STYLE/INFO
            try:
                legend = info['legend']
            except KeyError:
                legend = f'UnknownCurve{icurve}'
            try:
                color = info['color']
            except KeyError:
                color = self._colors[icurve]
            try:
                linewidth = info['linewidth']
            except KeyError:
                linewidth = self._linewidth
            try:
                xlabel = info['xlabel']
                self._xlabel = xlabel  #: kept if setted once
            except KeyError:
                xlabel = self._xlabel
            try:
                ylabel = info['ylabel']
                self._ylabel = ylabel  #: kept if setted once
            except KeyError:
                ylabel = self._ylabel
            try:
                title = info['title']
            except KeyError:
                title = self._title
            if icurve == 0:
                replace = True
            else:
                replace = False
            self._plot.addCurve(x, y, legend=legend,
                                color=color,
                                linewidth=linewidth,
                                replace=replace)
            self._plot.setGraphXLabel(xlabel)
            self._plot.setGraphYLabel(ylabel)
            self._plot.setGraphTitle(title)

        self.sigFrameChanged.emit(index)

    def setStack(self, stack=None):
        """Set stack"""
        if stack is None:
            self.clear()
            self.sigStackChanged.emit(0)
            return

        #: check stack is well formatted
        assert type(stack) is list, "stack must be a list"
        assert all(type(plots) is list for plots in stack), "data in stack must be lists"

        self._stack = stack
        nplots = len(self._stack)
        self.sigStackChanged.emit(nplots)

        self._browser.setRange(0, nplots-1)

        #: init plot
        self.__updateFrameNumber(0)
        self._browser.setValue(0)

        #: enable and init browser
        self._browser.setEnabled(True)

    def index(self):
        if self._index is None:
            self._index = 0
        return self._index

    def setIndex(self, value):
        self._index = value
        if self._index is not None:
            self.setWindowTitle('{}: StackView1D'.format(self._index))


def main():
    from silx import sx
    sx.enable_gui()
    sv1 = StackView1D()
    x = np.arange(10)
    y = np.sin(x)*x
    i = {'legend': 'p1: sin'}
    ii = {'legend': 'p1: sin+10'}
    i2 = {'legend': 'p2: 2sin', 'color': 'green'}
    ii2 = {'legend': 'p2: 2sin+10', 'color': 'red'}
    stack = [
        [[x, y, i], [x, y+10, ii]],  #: plot 1
        [[x, 2*y, i2], [x, 2*y+10, ii2]],  #: plot 2
        [[x, 3*y, {}], [x, 3*y+10, {}]],  #: plot 3
        ]
    sv1.setStack(stack)
    sv1.show()
    input("Press ENTER to close the window...")


if __name__ == '__main__':
    main()

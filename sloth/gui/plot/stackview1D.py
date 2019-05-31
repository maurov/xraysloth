#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Viewer for a stack of 1D plots
==============================


"""
import numpy as np
from silx.gui import qt
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

        self._stack = None
        """Loaded stack, a list of lists of 1D arrays plus a dictionary:
           [[x1, y1, info1], ... [xN, yN, infoN]]."""

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
        self.setMinimumSize(1024, 800)

    def __updateFrameNumber(self, index):
        """Update the current plot.
        :param index: index of the frame to be displayed
        """
        if self._stack is None:
            #: no data set
            return
        curve = self._stack[index]
        x, y, info = curve[0], curve[1], curve[2]
        try:
            legend = info['legend']
        except KeyError:
            legend = 'Unknown'
        self._plot.addCurve(x, y, legend=legend, replace=True)
        self.sigFrameChanged.emit(index)

    def setStack(self, stack=None):
        """Set stack"""
        if stack is None:
            self.clear()
            self.sigStackChanged.emit(0)
            return

        #: check stack is well formatted
        assert type(stack) is list, "stack must be a list"
        assert all(type(data) is list for data in stack), "data in stack must be lists"
        assert all(len(data) == 3 for data in stack), "data in stack must be lists of length 3"
        assert all(isinstance(data[0], np.ndarray) for data in stack), "data[0] in stack should be a Numpy array"
        assert all(isinstance(data[1], np.ndarray) for data in stack), "data[1] in stack should be a Numpy array"
        assert all(isinstance(data[2], dict) for data in stack), "data[2] in stack should be a dictionary"

        self._stack = stack
        ndata = len(self._stack)
        self.sigStackChanged.emit(ndata)

        self._browser.setRange(0, ndata-1)

        #: init plot
        self.__updateFrameNumber(0)
        self._browser.setValue(0)

        #: enable and init browser
        self._browser.setEnabled(True)


def main():
    from silx import sx
    sx.enable_gui()
    sv1 = StackView1D()
    x = np.arange(10)
    y = np.sin(x)*x
    i = {'legend': 'sin'}
    ii = {'legend': 'sin+10'}
    stack = [[x, y, i], [x, y+10, ii]]
    sv1.setStack(stack)
    sv1.show()
    input("Press ENTER to close the window...")


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Sloth custom version of SILX Plot2D
======================================
"""
from silx.gui import qt
from silx.gui.plot import Plot2D


class SlothPlot2D(Plot2D):
    """Custom Plot2D instance targeted to 2D images"""

    def __init__(self, parent=None, backend=None):

        super(SlothPlot2D, self).__init__(parent=parent, backend=backend)
        self._index = None

    def index(self):
        if self._index is None:
            self._index = 0
        return self._index

    def setIndex(self, value):
        self._index = value
        if self._index is not None:
            self.setWindowTitle('{}: Plot2D'.format(self._index))


def main():
    """Run a Qt app with the widget"""
    app = qt.QApplication([])
    widget = SlothPlot2D()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()

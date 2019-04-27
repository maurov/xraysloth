#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dataView widget
==================

"""

import os
from silx.gui import qt
import sloth

class DataViewDockWidget(qt.QDockWidget):

    def __init__(self, parent=None):
        super(DataViewDockWidget, self).__init__(parent=parent)

        uiPath = os.path.join(sloth._resourcesPath,\
                              'gui', 'uis', 'dock_dataview_filter.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')

def main():
    """Run a Qt app with an IPython console"""
    app = qt.QApplication([])
    widget = DataViewDockWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# coding: utf-8
"""View based on :mod:`silx.gui.hdf5.Hdf5TreeView`
"""

import os
from silx.gui import qt
from silx.gui.hdf5 import Hdf5TreeView

from sloth.utils.logging import getLogger
logger = getLogger('sloth.gui.daxs.viewHdf5Tree')


class TreeView(Hdf5TreeView):
    """TreeView class based on :mod:`silx.gui.hdf5.Hdf5TreeView`"""

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

        # headerView = HorizontalHeaderView()
        # self.setHeader(headerView)
        """TODO: set the header following SILX approach"""

        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        """Context menu"""

    def setModel(self, model):
        super(TreeView, self).setModel(model)

    def showContextMenu(self, position):
        menu = qt.QMenu('Tree View Menu', self)

        action = qt.QAction('Load Files', self, triggered=self.loadFiles)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def loadFiles(self, filenames):
        """Load files into the model"""
        if not filenames:
            filenames, _ = qt.QFileDialog.getOpenFileNames(
                self, 'Select Files to Load', os.getcwd(),
                'Data Files (*.spec *.hdf5);; All Files (*)')

            if not filenames:
                return

        for fn in filenames:
            self.model().appendFile(fn)


class TreeViewWidget(TreeView):
    """TreeView widget with embedded TreeModel"""

    def __init__(self):
        """Constructor"""

        super(TreeViewWidget, self).__init__()
        from .modelHdf5Tree import TreeModel
        self.setModel(TreeModel())
        self.setWindowTitle("Minimal TreeView widget (with TreeModel)")
        self.setMinimumWidth(1024)
        self.setMinimumHeight(400)
        self.setSortingEnabled(False)

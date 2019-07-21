#!/usr/bin/env python
# coding: utf-8
"""
RIXS data view
"""
import os
from silx.gui import qt
#import functools
from sloth.groups.rixsdata import RixsData


class RixsListView(qt.QListView):

    def __init__(self, parent=None):
        super(RixsListView, self).__init__(parent)


        #: Context menu
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        #: Selection mode
        self.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)

    def showContextMenu(self, position):
        menu = qt.QMenu('List View Menu', self)

        # Get the index under the cursor.
        index = self.indexAt(position)
        print("sono qui")
        print(index)
        print(index.row())
        item = 0 #self.model()._rixs_data[index.row()]

        if isinstance(item, RixsData):
            action = qt.QAction('Plot Left', self, triggered=self.plotLeft)
            menu.addAction(action)
            action = qt.QAction('Plot Right', self, triggered=self.plotRight)
            menu.addAction(action)

        action = qt.QAction(
            'Load RixsData from file', self, triggered=self.loadFiles)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def loadFiles(self):
        paths, _ = qt.QFileDialog.getOpenFileNames(
            self, 'Select Files to Load', os.getcwd(),
            'RixsData Files (*.h5);; All Files (*)')

        if not paths:
            return

        for path in paths:
            self.appendRixsData(path)

    def appendRixsData(self, path):
        """Append RixsData to the model"""
        r = RixsData()
        try:
            r.load_from_h5(path)
        except Exception:
            return
        self.model().appendRow(r)

    def plotLeft(self):
        pass

    def plotRight(self):
        pass


if __name__ == '__main__':
    pass

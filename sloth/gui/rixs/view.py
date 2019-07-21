#!/usr/bin/env python
# coding: utf-8
"""
RIXS data view
"""
import os
from silx.gui import qt
import functools
from sloth.groups.rixsdata import RixsData
from sloth.gui.daxs.view import TreeView
from sloth.gui.rixs.items import RixsItem


class RixsTreeView(TreeView):

    def __init__(self, parent=None):
        super(RixsTreeView, self).__init__(parent)

    def loadFiles(self):
        paths, _ = qt.QFileDialog.getOpenFileNames(
            self, 'Select Files to Load', os.getcwd(),
            'RixsData Files (*rixs.h5)')

        if not paths:
            return

        parent = self.selectionModel().selectedRows().pop()
        parentItem = self.model().itemFromIndex(parent)
        for path in paths:
            self.addFile(path, parentItem)

    def addFile(self, path=None, parentItem=None):
        if path is None:
            return

        # Add the file to the last added experiment item.
        if parentItem is None:
            parentItem = self.model().rootItem.lastChild()

        try:
            rdata = RixsData()
            rdata.load_from_h5(path)
        except Exception:
            return

        # Create a tree item for the file and add it to the experiment item.
        item = RixsItem(rdata.sample_name, parentItem, data=rdata)
        self.model().appendRow(item)

    def rixsItems(self):
        for index in self.model().visitModel():
            item = self.model().itemFromIndex(index)
            if isinstance(item, RixsItem):
                yield item


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
        if index:
            try:
                item = self.model()._rixs_data[index.row()]
            except IndexError:
                item = None

        if isinstance(item, RixsData):
            menu.addAction('Plot Left',
                           functools.partial(self.plotLeft, item))
            menu.addAction('Plot Right',
                           functools.partial(self.plotRight, item))
        else:
            menu.addSeparator()

        menu.addAction('Load RixData from file',
                       functools.partial(self.loadFiles))

        menu.exec_(self.mapToGlobal(position))

    def loadFiles(self):
        paths, _ = qt.QFileDialog.getOpenFileNames(
            self, 'Select Files to Load', os.getcwd(),
            'RixsData Files (*rixs.h5);; All Files (*)')

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

#!/usr/bin/env python
# coding: utf-8
"""
RIXS data model
"""
from silx.gui import qt

from sloth.gui.daxs.model import TreeModel


class RixsTreeModel(TreeModel):

    def __init__(self, parent=None):

        super(RixsTreeModel, self).__init__(parent=parent)


class RixsListModel(qt.QAbstractListModel):

    def __init__(self, *args, data=None, **kwargs):
        """Constructor"""

        super(RixsListModel, self).__init__(*args, **kwargs)
        self._rixs_data = data or []

    def data(self, index, role):
        if role == qt.Qt.DisplayRole:
            rd = self._rixs_data[index.row()]
            return rd.sample_name

    def rowCount(self, index):
        return len(self._rixs_data)

    def appendRow(self, rxobj):
        self._rixs_data.append(rxobj)
        self.layoutChanged.emit()


if __name__ == '__main__':
    pass

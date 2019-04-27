#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 17:34:01 2018

@author: mauro
"""
from silx.gui import qt
from sloth.gui.models.datanode import DataNode


class DataModel(qt.QAbstractItemModel):

    sortRole = qt.Qt.UserRole
    filterRole = qt.Qt.UserRole + 1

    """INPUTS: Node, QObject"""

    def __init__(self, root, parent=None):
        super(DataModel, self).__init__(parent=parent)
        self._header = ['Name', 'TypeInfo', 'AnotherHeader']
        self._rootNode = root

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""

    def columnCount(self, parent):
        return len(self._header)

    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        typeInfo = node.typeInfo()
        if role == qt.Qt.DisplayRole or role == qt.Qt.EditRole:
            if index.column() == 0:
                return node.name()
            if index.column() == 1:
                return typeInfo
        if role == qt.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
        if role == DataModel.sortRole:
            return node.typeInfo()
        if role == DataModel.filterRole:
            return node.typeInfo()

    """INPUTS: QModelIndex, QVariant, int (flag)"""

    def setData(self, index, value, role=qt.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == qt.Qt.EditRole:
                if index.column() == 0:
                    node.setName(value)
                self.dataChanged.emit(index, index)
                return True
        return False

    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""

    def headerData(self, section, orientation, role):
        if role == qt.Qt.DisplayRole:
            if orientation == qt.Qt.Horizontal:
                return self._header[section]
            if orientation == qt.Qt.Vertical:
                return section + 1

    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""

    def flags(self, index):
        if not index.isValid():
            return
        activeFlags = (qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable |
                       qt.Qt.ItemIsEditable | qt.Qt.ItemIsUserCheckable)
        return activeFlags

    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""

    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return qt.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column
     and parent node"""

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return qt.QModelIndex()

    """CUSTOM"""
    """INPUTS: QModelIndex"""

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    """INPUTS: int, int, QModelIndex"""

    def insertRows(self, position, rows, parent=qt.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = DataNode("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return success

    """INPUTS: int, int, QModelIndex"""

    def removeRows(self, position, rows, parent=qt.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success


SUBJECT, SENDER, DATE = range(3)

# Work around the fact that QSortFilterProxyModel always filters datetime
# values in QtCore.Qt.ISODate format, but the tree views display using
# QtCore.Qt.DefaultLocaleShortDate format.


class SortFilterProxyModel(qt.QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        # Do we filter for the date column?
        if self.filterKeyColumn() == DATE:
            # Fetch datetime value.
            index = self.sourceModel().index(sourceRow, DATE, sourceParent)
            data = self.sourceModel().data(index)

            # Return, if regExp match in displayed format.
            return (self.filterRegExp().indexIn(data.toString(
                qt.Qt.DefaultLocaleShortDate)) >= 0)

        # Not our business.
        return super(SortFilterProxyModel, self).filterAcceptsRow(sourceRow,
                                                                  sourceParent)


class TestWindow(qt.QWidget):
    def __init__(self):
        super(TestWindow, self).__init__()

        self.proxyModel = SortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)

        self.sourceGroupBox = qt.QGroupBox("Original Model")
        self.proxyGroupBox = qt.QGroupBox("Sorted/Filtered Model")

        self.sourceView = qt.QTreeView()
        self.sourceView.setRootIsDecorated(False)
        self.sourceView.setAlternatingRowColors(True)

        self.proxyView = qt.QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)

        self.sortCaseSensitivityCheckBox = qt.QCheckBox("Case sensitive\
                                                        sorting")
        self.filterCaseSensitivityCheckBox = qt.QCheckBox("Case sensitive\
                                                          filter")

        self.filterPatternLineEdit = qt.QLineEdit()
        self.filterPatternLabel = qt.QLabel("&Filter pattern:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterSyntaxComboBox = qt.QComboBox()
        self.filterSyntaxComboBox.addItem("Regular expression",
                                          qt.QRegExp.RegExp)
        self.filterSyntaxComboBox.addItem("Wildcard", qt.QRegExp.Wildcard)
        self.filterSyntaxComboBox.addItem("Fixed string",
                                          qt.QRegExp.FixedString)
        self.filterSyntaxLabel = qt.QLabel("Filter &syntax:")
        self.filterSyntaxLabel.setBuddy(self.filterSyntaxComboBox)

        self.filterColumnComboBox = qt.QComboBox()
        self.filterColumnComboBox.addItem("Name")
        self.filterColumnComboBox.addItem("TypeInfo")
        self.filterColumnComboBox.addItem("Another")
        self.filterColumnLabel = qt.QLabel("Filter &column:")
        self.filterColumnLabel.setBuddy(self.filterColumnComboBox)

        self.filterPatternLineEdit.textChanged.connect(
            self.filterRegExpChanged)
        self.filterSyntaxComboBox.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.filterColumnComboBox.currentIndexChanged.connect(
            self.filterColumnChanged)
        self.filterCaseSensitivityCheckBox.toggled.connect(
            self.filterRegExpChanged)
        self.sortCaseSensitivityCheckBox.toggled.connect(self.sortChanged)

        sourceLayout = qt.QHBoxLayout()
        sourceLayout.addWidget(self.sourceView)
        self.sourceGroupBox.setLayout(sourceLayout)

        proxyLayout = qt.QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        proxyLayout.addWidget(self.filterPatternLabel, 1, 0)
        proxyLayout.addWidget(self.filterPatternLineEdit, 1, 1, 1, 2)
        proxyLayout.addWidget(self.filterSyntaxLabel, 2, 0)
        proxyLayout.addWidget(self.filterSyntaxComboBox, 2, 1, 1, 2)
        proxyLayout.addWidget(self.filterColumnLabel, 3, 0)
        proxyLayout.addWidget(self.filterColumnComboBox, 3, 1, 1, 2)
        proxyLayout.addWidget(self.filterCaseSensitivityCheckBox, 4, 0, 1, 2)
        proxyLayout.addWidget(self.sortCaseSensitivityCheckBox, 4, 2)
        self.proxyGroupBox.setLayout(proxyLayout)

        mainLayout = qt.QVBoxLayout()
        mainLayout.addWidget(self.sourceGroupBox)
        mainLayout.addWidget(self.proxyGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test DataModel with Sort/Filter")
        self.resize(500, 450)

        self.proxyView.sortByColumn(SENDER, qt.Qt.AscendingOrder)
        self.filterColumnComboBox.setCurrentIndex(SENDER)

        self.filterPatternLineEdit.setText("")
        self.filterCaseSensitivityCheckBox.setChecked(True)
        self.sortCaseSensitivityCheckBox.setChecked(True)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)
        self.sourceView.setModel(model)

    def filterRegExpChanged(self):
        syntax_nr = self.filterSyntaxComboBox.itemData(
            self.filterSyntaxComboBox.currentIndex())
        syntax = qt.QRegExp.PatternSyntax(syntax_nr)

        if self.filterCaseSensitivityCheckBox.isChecked():
            caseSensitivity = qt.Qt.CaseSensitive
        else:
            caseSensitivity = qt.Qt.CaseInsensitive

        regExp = qt.QRegExp(self.filterPatternLineEdit.text(),
                            caseSensitivity, syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.proxyModel.setFilterKeyColumn(
            self.filterColumnComboBox.currentIndex())

    def sortChanged(self):
        if self.sortCaseSensitivityCheckBox.isChecked():
            caseSensitivity = qt.Qt.CaseSensitive
        else:
            caseSensitivity = qt.Qt.CaseInsensitive

        self.proxyModel.setSortCaseSensitivity(caseSensitivity)


def addData(model, name):
    model.insertRow(0)
    model.setData(model.index(0, 0, qt.QModelIndex()), name)


if __name__ == '__main__':
    from silx import sx
    sx.enable_gui()

    import sys

    app = qt.QApplication(sys.argv)
    app.setStyle("plastique")

    rootNode = DataNode("data1")
    childNode0 = DataNode("subdata1", rootNode)
    childNode1 = DataNode("subdata2", rootNode)
    childNode2 = DataNode("subsubdata1", childNode1)
    childNode3 = DataNode("subsubdata2", childNode1)

    model = DataModel(rootNode)

    addData(model, 'testAddData1')
    addData(model, 'testAddData2')

    window = TestWindow()
    window.setSourceModel(model)
    window.show()

    sys.exit(app.exec_())

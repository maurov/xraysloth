#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""list model
=============

"""

from silx.gui import qt

class PaletteListModel(qt.QAbstractListModel):
    
    def __init__(self, colors = [], parent = None):
        qt.QAbstractListModel.__init__(self, parent)
        self.__colors = colors

    def headerData(self, section, orientation, role):
        
        if role == qt.Qt.DisplayRole:
            
            if orientation == qt.Qt.Horizontal:
                return "Palette"
            else:
                return "Color {0}".format(section)


    def rowCount(self, parent):
        return len(self.__colors)


    def data(self, index, role):
        
        if role == qt.Qt.EditRole:
            return self.__colors[index.row()].name()
        
        if role == qt.Qt.ToolTipRole:
            return "Hex code: " + self.__colors[index.row()].name()
        
        if role == qt.Qt.DecorationRole:
            
            row = index.row()
            value = self.__colors[row]
            
            pixmap = qt.QPixmap(26, 26)
            pixmap.fill(value)
            
            icon = qt.QIcon(pixmap)
            
            return icon

        if role == qt.Qt.DisplayRole:
            
            row = index.row()
            value = self.__colors[row]
            
            return value.name()

    def flags(self, index):
        return qt.Qt.ItemIsEditable | qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable
        
        
        
    def setData(self, index, value, role = qt.Qt.EditRole):
        if role == qt.Qt.EditRole:
            
            row = index.row()
            color = qt.QColor(value)
            
            if color.isValid():
                self.__colors[row] = color
                self.dataChanged.emit(index, index)
                return True
        return False

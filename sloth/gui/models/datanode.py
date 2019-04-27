#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DataNode objects to be used in TreeView
==========================================

CREDITS
-------

- Yasin Uludag, PyQt4 Model View Programming Tutorials :), http://www.yasinuludag.com/blog/?p=98
- Marius Retegan, Crispy, https://github.com/mretegan/crispy
- Riverbank Computing Limited, PyQt5 examples

"""
from silx.gui import qt


class DataNode(qt.QObject):

    def __init__(self, name, parent=None):
        super(DataNode, self).__init__()
        self._name = name
        self._children = []
        self._parent = parent
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "DATANODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):
        """simple representation of the parent/child data structure"""
        output = ""
        tabLevel += 1
        for i in range(tabLevel):
            output += "     "
        output += "|----" + self._name + "\n"
        for child in self._children:
            output += child.log(tabLevel)
        tabLevel -= 1
        output += "\n"
        return output

    def __repr__(self):
        return self.log()


if __name__ == '__main__':

    testDataNode = DataNode("data1")
    testChildNode = DataNode("subdata1", testDataNode)
    testChildChildNode = DataNode("subsubdata1", testChildNode)

    print(testDataNode)

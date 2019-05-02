# coding: utf-8
# /*##########################################################################
# MIT License
#
# Copyright (c) 2018 DAXS developers.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""
This module provides classes to implement model items for spectroscopy data.
"""

from __future__ import absolute_import, division

__authors__ = ['Marius Retegan', 'Mauro Rovezzi']
__license__ = 'MIT'

import weakref

from silx.gui.qt import Qt
from silx.utils.weakref import WeakList

from sloth.utils.logging import getLogger
logger = getLogger('sloth.gui.daxs.items')


class Signal(object):
    """Base class for signal objects."""

    def __init__(self):
        self._slots = WeakList()

    def connect(self, slot):
        """Register a slot.

        Adding an already registered slot has no effect.

        :param callable slot: The function or method to register.
        """
        if slot not in self._slots:
            self._slots.append(slot)
        else:
            logger.warning('Ignoring addition of an already registered slot')

    def disconnect(self, slot):
        """Remove a previously registered slot.

        :param callable slot: The function or method to unregister.
        """
        try:
            self._slots.remove(slot)
        except ValueError:
            logger.warning('Trying to remove a slot that is not registered')

    def emit(self, *args, **kwargs):
        """Notify all registered slots with the given parameters.

        Slots are called directly in this method.
        Slots are called in the order they were registered.
        """
        for slot in self._slots:
            slot(*args, **kwargs)


class TreeItem(object):

    def __init__(self, name=None, parentItem=None, isChecked=False):
        """Base class for items of the tree model.

        Use a weak reference for the parent item to avoid circular
        references, i.e. if the parent is destroyed, the child will only
        have a week reference to it, so the garbage collector will remove
        the parent object from memory.

        Using a weakref.proxy object for the parent makes the parentItem
        unhashable, which causes problem if they are used as dictionary keys.

        :param name: Name of the tree item, defaults to None
        :param parentItem: Parent of the tree item, defaults to None
        """
        self.name = name
        self._parentItem = None if parentItem is None else weakref.ref(parentItem)  # noqa
        self.isChecked = isChecked

        self.childItems = list()
        self.itemChanged = Signal()

    @property
    def parentItem(self):
        return self._parentItem() if self._parentItem is not None else None

    def child(self, row):
        try:
            return self.childItems[row]
        except KeyError:
            return None

    def data(self, column, name, role):
        if name is None:
            return None

        try:
            return getattr(self, name)
        except AttributeError:
            return None

    def setData(self, column, name, value, role):
        if name is None:
            return False

        try:
            setattr(self, name, value)
            return True
        except AttributeError:
            return False

    def parent(self):
        return self.parentItem

    def childPosition(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        else:
            # The root item has no parent; for this item, we return zero
            # to be consistent with the other items.
            return 0

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.name)

    def lastChild(self):
        return self.childItems[-1]

    def insertRows(self, row, count):
        for i in range(count):
            name = 'TreeItem{}'.format(self.childCount())
            item = TreeItem(name=name, parentItem=self)
            self.childItems.insert(row, item)
            logger.debug('Inserted {}'.format(name))
        return True

    def removeRows(self, row, count):
        try:
            childItem = self.childItems[row]
        except IndexError:
            return False

        for i in range(count):
            self.childItems.pop(row)

        logger.debug('Removed {}'.format(childItem.name))
        return True

    def flags(self, column):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    @property
    def legend(self):
        tokens = list()
        tokens.append(self.name)

        parentItem = self.parentItem
        while parentItem is not None:
            if parentItem.name is not None:
                tokens.append(parentItem.name)
            parentItem = parentItem.parentItem

        tokens.reverse()
        return '/'.join(tokens)


class RootItem(TreeItem):

    def __init__(self, name=None, parentItem=None):
        super(RootItem, self).__init__(name, parentItem)


class ExperimentItem(TreeItem):

    def __init__(self, name=None, parentItem=None):
        super(ExperimentItem, self).__init__(name, parentItem)


class GroupItem(TreeItem):

    def __init__(self, name=None, parentItem=None):
        super(GroupItem, self).__init__(name, parentItem)


class DatasetItem(TreeItem):

    def __init__(self, name=None, parentItem=None):
        super(DatasetItem, self).__init__(name, parentItem)


class FileItem(TreeItem):

    def __init__(self, name=None, parentItem=None):
        super(FileItem, self).__init__(name, parentItem)


class ScanItem(TreeItem):

    def __init__(self, name=None, parentItem=None, isChecked=False, data=None):
        super(ScanItem, self).__init__(name, parentItem, isChecked)
        self._xLabel = None
        self._signalLabel = None
        self._monitorLabel = None
        self._plotWindows = None
        self._currentPlotWindow = None

        self.scanData = data

    def data(self, column, name, role):
        if role == Qt.CheckStateRole:
            if column == 0:
                if self.isChecked:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
        return super(ScanItem, self).data(column, name, role)

    def setData(self, column, name, value, role):
        if role == Qt.CheckStateRole:
            if value == Qt.Checked:
                self.isChecked = True
            else:
                self.isChecked = False
            return True
        return super(ScanItem, self).setData(column, name, value, role)

    def flags(self, column):
        flags = super(ScanItem, self).flags(column)
        if column == 0:
            return flags | Qt.ItemIsUserCheckable
        else:
            return flags

    @property
    def xLabel(self):
        if self._xLabel is None:
            self._xLabel = list(self.counters)[0]
        return self._xLabel

    @xLabel.setter
    def xLabel(self, value):
        self._xLabel = value

    @property
    def signalLabel(self):
        if self._signalLabel is None:
            self._signalLabel = list(self.counters)[1]
        return self._signalLabel

    @signalLabel.setter
    def signalLabel(self, value):
        self._signalLabel = value

    @property
    def monitorLabel(self):
        if self._monitorLabel is None:
            self._monitorLabel = list(self.counters)[2]
        return self._monitorLabel

    @monitorLabel.setter
    def monitorLabel(self, value):
        self._monitorLabel = value

    @property
    def currentPlotWindowIndex(self):
        if self.currentPlotWindow is not None:
            return str(self.currentPlotWindow.index())
        else:
            return None

    @currentPlotWindowIndex.setter
    def currentPlotWindowIndex(self, value):
        try:
            self._currentPlotWindowIndex = int(value)
        except ValueError:
            self.currentPlotWindow = None
        else:
            self.currentPlotWindow = self.plotWindows[self._currentPlotWindowIndex] # noqa

    @property
    def currentPlotWindow(self):
        if self._currentPlotWindow is None:
            if self.plotWindows:
                self._currentPlotWindow = self.plotWindows[0]
        else:
            if self._currentPlotWindow not in self.plotWindows:
                if self.plotWindows:
                    self._currentPlotWindow = self.plotWindows[0]
                else:
                    self._currentPlotWindow = None
        return self._currentPlotWindow

    @currentPlotWindow.setter
    def currentPlotWindow(self, value):
        self._currentPlotWindow = value

    @property
    def plotWindowsIndexes(self):
        indexes = list()
        if self.plotWindows is not None:
            for index, _ in enumerate(self.plotWindows):
                indexes.append(str(index))
        return indexes

    @property
    def plotWindows(self):
        return self._plotWindows

    @plotWindows.setter
    def plotWindows(self, value):
        self._plotWindows = value

    @property
    def counters(self):
        return self.scanData['measurement']

    @property
    def command(self):
        return str(self.scanData['title'].value)

    @property
    def x(self):
        try:
            return self.counters[self.xLabel].value
        except KeyError:
            return None

    @property
    def signal(self):
        try:
            return self.counters[self.signalLabel].value
        except KeyError:
            return None

    @property
    def monitor(self):
        try:
            return self.counters[self.monitorLabel].value
        except KeyError:
            return None

    def plot(self):
        if self.x is None or self.signal is None:
            return

        x = self.x
        signal = self.signal
        legend = self.legend

        if 0 not in self.monitor:
            try:
                signal = signal / self.monitor
            except (TypeError, ValueError):
                pass

        if not self.currentPlotWindow.getItems():
            resetzoom = True
        else:
            resetzoom = False
        self.currentPlotWindow.addCurve(x, signal, legend=legend,
                                        resetzoom=resetzoom)
        self.currentPlotWindow.setGraphYLabel('Signal / Monitor')

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
from __future__ import absolute_import, division

__authors__ = ['Marius Retegan', 'Mauro Rovezzi']
__license__ = 'MIT'

import os
import glob
import logging

from silx.gui import qt

from .items import ScanItem
from .model import TreeModel, HeaderSection
from .view import TreeView
# from .plot import PlotArea  # original DAXS version
from sloth.gui.plot.plotarea import PlotArea  # sloth version
from .config import Config
from .delegates import ComboBoxDelegate
from .console import InternalIPyKernel
from .profiling import timeit # noqa
from sloth import _resourcesPath

logger = logging.getLogger(__name__)


class MainWindow(qt.QMainWindow):
    def __init__(self, app, parent=None, with_ipykernel=False):
        super(MainWindow, self).__init__(parent=parent)

        self.app = app
        self._with_ipykernel = with_ipykernel

        self.plotArea = PlotArea()
        self.setCentralWidget(self.plotArea)

        self.model = TreeModel()

        # Add (empty) menu bar -> contents added later
        self.menuBar = qt.QMenuBar()
        self.setMenuBar(self.menuBar)

        # Add icon to the application
        ico = qt.QIcon(os.path.join(_resourcesPath, "logo",
                                    "xraysloth_logo_04.svg"))
        self.setWindowIcon(ico)
        self.setWindowTitle("sloth-daxs")

        # Add additional sections to the header.
        values = [
            HeaderSection(
                name='Command',
                roles={qt.Qt.DisplayRole: 'command'}),
            HeaderSection(
                name='X',
                roles={
                    qt.Qt.DisplayRole: 'xLabel',
                    qt.Qt.EditRole: 'counters'},
                delegate=ComboBoxDelegate),
            HeaderSection(
                name='Y',
                roles={
                    qt.Qt.DisplayRole: 'yLabel',
                    qt.Qt.EditRole: 'counters'},
                delegate=ComboBoxDelegate),
            HeaderSection(
                name='Signal',
                roles={
                    qt.Qt.DisplayRole: 'signalLabel',
                    qt.Qt.EditRole: 'counters'},
                delegate=ComboBoxDelegate),
            HeaderSection(
                name='Monitor',
                roles={
                    qt.Qt.DisplayRole: 'monitorLabel',
                    qt.Qt.EditRole: 'counters'},
                delegate=ComboBoxDelegate),
            HeaderSection(
                name='Plot',
                roles={
                    qt.Qt.DisplayRole: 'currentPlotWindowIndex',
                    qt.Qt.EditRole: 'plotWindowsIndexes'},
                delegate=ComboBoxDelegate)]

        for value in values:
            section = len(self.model.header)
            orientation = qt.Qt.Horizontal
            self.model.setHeaderData(section, orientation, value)

        self.view = TreeView(parent=self)
        self.view.setModel(self.model)

        self.dockWidget = qt.QDockWidget(parent=self)
        self.dockWidget.setObjectName('Data View')
        self.dockWidget.setWidget(self.view)
        self.addDockWidget(qt.Qt.LeftDockWidgetArea, self.dockWidget)

        self.model.dataChanged.connect(self.updatePlot)
        self.plotArea.changed.connect(self.updateModel)

        # Add to the model the files from the data folder.
        dataPath = os.path.join(os.getcwd(), 'data')
        if os.path.exists(dataPath):
            self.view.addExperiment('Experiment')
            for specFile in glob.glob(os.path.join(dataPath, '*.spec')):
                self.view.addFile(specFile)

        # Increase by 30 % the column width of the first column of
        # the tree view.
        column = 0
        columnWidth = self.view.columnWidth(column)
        self.view.setColumnWidth(column, columnWidth + columnWidth * 0.3)
        self.view.expandAll()

        # Add two plot windows to the plot area.
        self.plotArea.addPlotWindow()
        self.plotArea.addPlotWindow()

        if self._with_ipykernel:
            # Initialize internal ipykernel
            self._ipykernel = InternalIPyKernel()
            self._ipykernel.init_kernel(backend='qt')
            self._ipykernel.add_to_namespace('main', self)
            self._ipykernel.add_to_namespace('view', self.view)
            self._ipykernel.add_to_namespace('model', self.model)
            self._ipykernel.add_to_namespace('plotArea', self.plotArea)
            # Add IPython console at menu
            self._initConsoleMenu()
        else:
            self._ipykernel = None

    def updateModel(self):
        plotWindows = self.plotArea.plotWindows()
        for item in self.view.scanItems():
            item.plotWindows = plotWindows
            if len(plotWindows) == 0:
                index = self.model.indexFromItem(item)
                self.model.dataChanged.emit(index, index)

    # @timeit
    def updatePlot(self, *args):
        topLeft, bottomRight, _ = args

        topLeftItem = self.model.itemFromIndex(topLeft)
        bottomRightItem = self.model.itemFromIndex(bottomRight)

        if topLeftItem is not bottomRightItem:
            logger.error('The indices to not point to the same '
                         'item in the model')
            return

        item = topLeftItem
        plotWindows = self.plotArea.plotWindows()

        if item.isChecked:
            if len(plotWindows) == 0:
                logger.info('There are no plot widgets available')
                return

        for plotWindow in plotWindows:
            plotWindow.remove(item.legend)
            if not plotWindow.getItems():
                plotWindow.reset()
            else:
                plotWindow.statusBar().clearMessage()

        scanItems = self.view.scanItems()
        if item.isChecked:
            if item in list(scanItems) and isinstance(item, ScanItem):
                item.plot()

    def showEvent(self, event):
        self.loadSettings()
        super(MainWindow, self).showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super(MainWindow, self).closeEvent(event)

    def loadSettings(self):
        config = Config()
        self.settings = config.read()

        if self.settings is None:
            return

        self.settings.beginGroup('MainWindow')

        state = self.settings.value('State')
        if state is not None:
            self.restoreState(qt.QByteArray(state))

        size = self.settings.value('Size')
        if size is not None:
            self.resize(qt.QSize(size))

        pos = self.settings.value('Position')
        if pos is not None:
            self.move(qt.QPoint(pos))

        self.settings.endGroup()

    def saveSettings(self):
        self.settings.beginGroup('MainWindow')
        self.settings.setValue('State', self.saveState())
        self.settings.setValue('Size', self.size())
        self.settings.setValue('Position', self.pos())
        self.settings.endGroup()
        self.settings.sync()

    # Populate the menu bar with common actions and shortcuts
    def _addMenuAction(self, menu, action, deferShortcut=False):
        """Add action to menu as well as self so that when the menu bar is
        invisible, its actions are still available. If deferShortcut
        is True, set the shortcut context to widget-only, where it
        will avoid conflict with shortcuts already bound to the
        widgets themselves.
        """
        menu.addAction(action)
        self.addAction(action)

        if deferShortcut:
            action.setShortcutContext(qt.Qt.WidgetShortcut)
        else:
            action.setShortcutContext(qt.Qt.ApplicationShortcut)

    def _initConsoleMenu(self):
        self.menuConsole = self.menuBar.addMenu("Console")

        self.newConsoleAction = qt.QAction(
            "&New Qt Console", self, shortcut="Ctrl+K",
            triggered=self._ipykernel.new_qt_console)
        self._addMenuAction(self.menuConsole, self.newConsoleAction)

        self.closeConsoleAction = qt.QAction(
            "&Quit", self, shortcut="Ctrl+Q", triggered=self.onClose)
        self._addMenuAction(self.menuConsole, self.closeConsoleAction)

    def onClose(self):
        self._ipykernel.cleanup_consoles()
        self.app.lastWindowClosed.connect(qt.pyqtSignal(quit()))

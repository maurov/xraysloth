#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot area
============

A custom QMdiArea where to add custom PlotWindows


"""
import numpy as np
from silx.utils.weakref import WeakList
from silx.gui import qt
from .plotwindow import PlotWindow

__authors__ = ["Marius Retegan"]


class MdiSubWindow(qt.QMdiSubWindow):

    def __init__(self, parent=None):
        super(MdiSubWindow, self).__init__(parent=parent)
        self.setAttribute(qt.Qt.WA_DeleteOnClose, True)

    def closeEvent(self, event):
        super(MdiSubWindow, self).closeEvent(event)
        # Renumber the plot windows and emit the changed signal.
        self.mdiArea().renumberPlotWindows()
        self.mdiArea().changed.emit()


class PlotArea(qt.QMdiArea):

    changed = qt.pyqtSignal()

    def __init__(self, parent=None):
        super(PlotArea, self).__init__(parent=parent)

        # Context menu
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # Set the order of the subwindows returned by subWindowList.
        self.setActivationOrder(qt.QMdiArea.CreationOrder)

    def getPlotWindow(self, index):
        """get the PlotWindow widget object for a given index"""
        return self.subWindowList()[index].widget()

    def plotWindows(self):
        widgets = WeakList()
        for subWindow in self.subWindowList():
            widgets.append(subWindow.widget())
        return widgets

    def showContextMenu(self, position):
        menu = qt.QMenu('Plot Area Menu', self)

        action = qt.QAction('Add Plot Window', self,
                            triggered=self.addPlotWindow)
        menu.addAction(action)

        menu.addSeparator()

        action = qt.QAction('Cascade Windows', self,
                            triggered=self.cascadeSubWindows)
        menu.addAction(action)

        action = qt.QAction('Tile Windows', self,
                            triggered=self.tileSubWindows)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def addPlotWindow(self, *args):
        subWindow = MdiSubWindow(parent=self)

        plotWindow = PlotWindow(parent=subWindow)
        plotWindow.setIndex(len(self.plotWindows()))

        subWindow.setWidget(plotWindow)
        subWindow.show()

        self.changed.emit()

    def renumberPlotWindows(self):
        for index, plotWindow in enumerate(self.plotWindows()):
            plotWindow.setIndex(index)


class PlotAreaMainWindow(qt.QMainWindow):

    def __init__(self, app, parent=None):
        super(PlotAreaMainWindow, self).__init__(parent=parent)

        self.app = app

        self.plotArea = PlotArea()
        self.setCentralWidget(self.plotArea)

        # Add (empty) menu bar -> contents added later
        self.menuBar = qt.QMenuBar()
        self.setMenuBar(self.menuBar)

        # Add two plot windows to the plot area.
        self.plotArea.addPlotWindow()
        self.plotArea.addPlotWindow()

        self.closeAction = qt.QAction(
            "&Quit", self, shortcut="Ctrl+Q", triggered=self.onClose)
        self._addMenuAction(self.menuBar, self.closeAction)

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

    def onClose(self):
        self.app.lastWindowClosed.connect(qt.pyqtSignal(quit()))



def main():
    global app
    app = qt.QApplication([])

    # Create the ad hoc window containing a PlotWidget and associated tools
    window = PlotAreaMainWindow(app)
    window.setAttribute(qt.Qt.WA_DeleteOnClose)
    window.setWindowTitle("PlotArea Main Window")
    window.show()

    # Change the default colormap
    plot0 = window.plotArea.getPlotWindow(0)
    plot1 = window.plotArea.getPlotWindow(1)

    # Add an 1D data + 2D image to the plots
    x0 = np.linspace(-10, 10, 200)
    x1 = np.linspace(-10, 5, 150)
    x = np.outer(x0, x1)
    image = np.sin(x) / x
    plot0.addCurve(x0, np.sin(x0)/x0)
    plot1.addImage(image)

    app.exec_()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main window of RIXS GUI
=======================
"""
import os
import numpy as np
from silx.gui import qt
from sloth.gui.plot.plotrixs import RixsPlotArea
from sloth import _resourcesPath
from sloth.gui.rixs.view import RixsListView
from sloth.gui.rixs.model import RixsListModel
from sloth.gui.console import InternalIPyKernel


class MainWindowRixs(qt.QMainWindow):
    """MainWindow may also behave as widget"""

    def __init__(self, parent=None, with_ipykernel=False):
        """Constructor"""

        super(MainWindowRixs, self).__init__(parent=parent)

        if parent is not None:
            #: behave as a widget
            self.setWindowFlags(qt.Qt.Widget)
        else:
            #: main window
            self.setWindowTitle('RIXS_VIEW')
            # Add icon to the application
            ico = qt.QIcon(os.path.join(_resourcesPath, "logo",
                                        "xraysloth_logo_04.svg"))
            self.setWindowIcon(ico)

        #: IPython kernel status
        self._with_ipykernel = with_ipykernel

        #: Model/view
        self._model = RixsListModel()
        self._view = RixsListView(parent=self)
        self._view.setModel(self._model)

        # Add (empty) menu bar -> contents added later
        self._menuBar = qt.QMenuBar()
        self.setMenuBar(self._menuBar)
        self._initAppMenu()

        centralWidget = qt.QWidget(self)
        self._rixsPlotArea = RixsPlotArea()
        self._profilesPlotArea = RixsPlotArea()

        gridLayout = qt.QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        #: addWidget(widget, row, column, rowSpan, columnSpan[, alignment=0]))
        gridLayout.addWidget(self._rixsPlotArea, 0, 0, 1, 2)
        gridLayout.addWidget(self._profilesPlotArea, 1, 0, 1, 2)

        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setMinimumSize(600, 800)

        self._dockDataWidget = qt.QDockWidget(parent=self)
        self._dockDataWidget.setObjectName('Data View')
        self._dockDataWidget.setWidget(self._view)
        self.addDockWidget(qt.Qt.LeftDockWidgetArea, self._dockDataWidget)
        """TreeView dock widget"""

        if self._with_ipykernel:
            # Initialize internal ipykernel
            self._ipykernel = InternalIPyKernel()
            self._ipykernel.init_kernel(backend='qt')
            self._ipykernel.add_to_namespace('view', self._view)
            self._ipykernel.add_to_namespace('model', self._model)
            self._ipykernel.add_to_namespace('plots_rixs', self._rixsPlotArea)
            self._ipykernel.add_to_namespace('plots_cuts',
                                             self._profilesPlotArea)

            # Add IPython console at menu
            self._initConsoleMenu()
        else:
            self._ipykernel = None

    def showEvent(self, event):
        self.loadSettings()
        super(MainWindowRixs, self).showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super(MainWindowRixs, self).closeEvent(event)

    def loadSettings(self):
        """TODO"""
        pass

    def saveSettings(self):
        """TODO"""
        pass

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

    def _initAppMenu(self):
        """Add application menu"""
        self._menuApp = self._menuBar.addMenu("Application")
        self._closeAppAction = qt.QAction("&Quit", self, shortcut="Ctrl+Q",
                                          triggered=self.onClose)
        self._addMenuAction(self._menuApp, self._closeAppAction)

    def _initConsoleMenu(self):
        self._menuConsole = self._menuBar.addMenu("Console")

        self._newConsoleAction = qt.QAction("&New Qt Console",
                                            self, shortcut="Ctrl+K",
                                            triggered=self._ipykernel.new_qt_console)
        self._addMenuAction(self._menuConsole, self._newConsoleAction)

    def onClose(self):
        if self._ipykernel is not None:
            self._ipykernel.cleanup_consoles()
        self.closeEvent(quit())


def main():
    from silx import sx
    sx.enable_gui()
    rx = MainWindowRixs()
    rx.show()
    input("Press ENTER to close the window...")


if __name__ == '__main__':
    main()

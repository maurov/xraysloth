#!/usr/bin/env python
# coding: utf-8
"""QMainWindow based on :mod:`silx.examples.customHdf5TreeModel`
"""

import os
from silx.gui import qt
from sloth import _resourcesPath
from .viewHdf5Tree import TreeView
from .modelHdf5Tree import TreeModel
from sloth.gui.plot.plotarea import PlotArea  # sloth version
from .console import InternalIPyKernel
from .config import Config


class MainWindowHdf5Tree(qt.QMainWindow):
    """MainWindow based on Hdf5TreeView
    """

    def __init__(self, app, parent=None, with_ipykernel=False):
        super(MainWindowHdf5Tree, self).__init__(parent=parent)

        self._app = app
        self._with_ipykernel = with_ipykernel
        """Store main application and IPython kernel status"""

        self._menuBar = qt.QMenuBar()
        self.setMenuBar(self._menuBar)
        self._initAppMenu()
        """Add minimal menu bar with Quit action"""

        ico = qt.QIcon(os.path.join(_resourcesPath, "logo",
                                    "xraysloth_logo_04.svg"))
        self.setWindowIcon(ico)
        self.setWindowTitle("sloth-daxs")
        """Set window title and icon"""

        self._view = TreeView(self)
        """Inherited from SILX TreeView view"""

        self._model = TreeModel()
        """Inherited from SILX TreeModel model

        .. note:: in silx.examples.customHdf5TreeModel there are two options:

        - original model::

            # in __init__
            self.__treeview = Hdf5TreeView()
            self.__sourceModel = self.__treeview.model()
            # in __useOriginalModel
            self.__treeview.setModel(self.__sourceModel)

        - custom model::

            # in __init__
            self.__treeview = Hdf5TreeView()
            self.__sourceModel = self.__treeview.model()
            # in __useCustomModel
            customModel = CustomTooltips(self.__treeview)
            # CustomTooltips is qt.QIdentityProxyModel
            customModel.setSourceModel(self.__sourceModel)
            self.__treeview.setModel(customModel)
        """

        self._view.setModel(self._model)
        """Set the model to the view"""

        self._plotArea = PlotArea()
        self.setCentralWidget(self._plotArea)
        """Plot Area storing all plot windows"""

        self._dockWidget = qt.QDockWidget(parent=self)
        self._dockWidget.setObjectName('Data TreeView')
        self._dockWidget.setWidget(self._view)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._dockWidget)
        """TreeView dock widget"""

        if self._with_ipykernel:
            # Initialize internal ipykernel
            self._ipykernel = InternalIPyKernel()
            self._ipykernel.init_kernel(backend='qt')
            """IPython kernel part of the GUI application (= internal)"""

            self._ipykernel.add_to_namespace('app', self)
            self._ipykernel.add_to_namespace('view', self._view)
            self._ipykernel.add_to_namespace('model', self._model)
            self._ipykernel.add_to_namespace('plot', self._plotArea)
            """Namespaces added to the kernel are visible in the consoles"""

            self._initConsoleMenu()
            """Add console menu"""
        else:
            self._ipykernel = None

        if self._ipykernel is not None:
            self._ipykernel.new_qt_console()
            """Open one console"""

        self._plotArea.addPlotWindow()
        """Add one plot window"""

    def showEvent(self, event):
        self.loadSettings()
        super(MainWindowHdf5Tree, self).showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super(MainWindowHdf5Tree, self).closeEvent(event)

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

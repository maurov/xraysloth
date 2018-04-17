#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""sloth main window
====================

..notes

Load designer.ui into python

To directly show in Ipython, simply:

main = uic.loadUi('designer.ui')
main.show()

"""
from __future__ import absolute_import, division, unicode_literals

import os, sys
import math
import numpy as np
import matplotlib.pyplot as plt

from silx.gui import qt
from silx.gui.widgets.PeriodicTable import PeriodicTable

import sloth
_resourcesPath = os.path.join(os.path.split(sloth.__file__)[0], 'resources')

from .widgets.custom_console import customIPythonWidget
from .widgets.custom_plot import customPlotWidget
from .models.list_model import PaletteListModel

class SlothMainWindow(qt.QMainWindow):

    def __init__(self, parent=None):
        super(SlothMainWindow, self).__init__(parent)
        uiPath = os.path.join(_resourcesPath, 'gui', 'uis', 'sloth_main.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')
        logoPath = os.path.join(_resourcesPath, 'logo', 'xraysloth_logo_03.svg')
        self.setWindowTitle('Sloth {0}'.format(sloth.__version__))
        self.setWindowIcon(qt.QIcon(logoPath))
        self.aboutDialog = AboutDialog()
        self.actionAbout.triggered.connect(self.openAboutDialog)

        #EXIT with C-q
        self.actionExit = qt.QAction(('E&xit'), self)
        self.actionExit.setShortcut(qt.QKeySequence("Ctrl+Q"))
        self.addAction(self.actionExit)
        self.actionExit.triggered.connect(self.confirmClose)
        
        #CONSOLE WIDGET
        self.consoleWidget = customIPythonWidget()
        self.consoleLayout.addWidget(self.consoleWidget)
        self.consoleWidget.pushVariables({'os'   : os,
                                          'sys'  : sys,
                                          'np'   : np,
                                          'math' : math,
                                          'plt'  : plt})

        #PLOT WIDGET
        self.plotWidget = customPlotWidget()
        self.plotLayout.addWidget(self.plotWidget)
        self.consoleWidget.pushVariables({'pw' : self.plotWidget})


        #PERIODIC TABLE
        self.periodicTable = PeriodicTable(selectable=True)
        self.periodicTableLayout.addWidget(self.periodicTable)
        self.consoleWidget.pushVariables({'pt' : self.periodicTable})
        
        
        self._fname = None

        red   = qt.QColor(255,0,0)
        green = qt.QColor(0,255,0)
        blue  = qt.QColor(0,0,255)

        rowCount = 4
        columnCount = 6
   
        model = PaletteListModel([red, green, blue])
        model.insertRows(0, 5)

        self.listViewData.setModel(model)

    def openAboutDialog(self):
        self.aboutDialog.show()

    def on_actionOpen_triggered(self):
        fname = qt.QFileDialog.getOpenFileName()
        if fname:
            self._fname = fname
            print('loaded filename: {0}'.format(self._fname))

    def confirmClose(self):
        msg = qt.QMessageBox(self)
        msg.setIcon(qt.QMessageBox.Question)
        msg.setText("You requested closing the application. Is this really what you want?")
        msg.setInformativeText("ALL NOT SAVED DATA WILL BE LOST")
        msg.setWindowTitle("Exit application?")
        msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
        if msg.exec_() == qt.QMessageBox.Ok:
            self.close()

class AboutDialog(qt.QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__()
        uiPath = os.path.join(_resourcesPath, 'gui', 'uis', 'sloth_about.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')
        self.nameLabel.setText('Sloth {0}'.format(sloth.__version__))
            
def main():
    app = qt.QApplication(sys.argv)
    app.setStyle("plastique")
    appli = SlothMainWindow()
    appli.show()
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()

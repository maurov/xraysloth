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
from sloth.gui.widgets.console import (HAS_XRAYLIB, HAS_LARCH,
                                       _pushDict, _pushInfos,
                                       _slothKit)

from sloth.gui.widgets.console import customIPythonWidget
from sloth.gui.widgets.plot1D import customPlotWidget

#from .models.list_model import PaletteListModel

    
#_resourcesPath = os.path.join(os.path.split(sloth.__file__)[0], 'resources')

class SlothMainWindow(qt.QMainWindow):

    def __init__(self, parent=None):
        super(SlothMainWindow, self).__init__(parent)
        uiPath = os.path.join(sloth._resourcesPath, 'gui', 'uis',
                              'sloth_main_common.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')
        logoPath = os.path.join(sloth._resourcesPath, 'logo',
                                'xraysloth_logo_03.svg')
        self.setWindowTitle('Sloth {0}'.format(sloth.__version__))
        self.setWindowIcon(qt.QIcon(logoPath))

        #About dialog
        self.aboutDialog = AboutDialog(parent=self)
        self.actionAbout.triggered.connect(self.openAboutDialog)

        #EXIT with C-q
        #self.actionExit = qt.QAction(('E&xit'), self)
        self.actionExit.setShortcut(qt.QKeySequence("Ctrl+Q"))
        #self.addAction(self.actionExit)
        self.actionExit.triggered.connect(self.confirmClose)

        #OPEN with C-o
        #self.actionOpen = qt.QAction(('Open'), self)
        self.actionOpen.setShortcut(qt.QKeySequence("Ctrl+O"))
        #self.addAction(self.actionOpen)
        self.actionOpen.triggered.connect(self.selectFile)
        
        #CONSOLE WIDGET
        self.consoleWidget = customIPythonWidget()
        self.consoleLayout.addWidget(self.consoleWidget)
        self.consoleWidget.pushVariables(_pushDict)
        for info in _pushInfos:
            self.tabInfoListWidget.addItem(info)
        self.consoleWidget.pushVariables(_slothKit)
        for _key in _slothKit.keys():
            self.slothInfoListWidget.addItem(_key)
            
        #PLOT WIDGET
        self.plotWidget = customPlotWidget()
        self.plotLayout.addWidget(self.plotWidget)
        self.consoleWidget.pushVariables({'p1d' : self.plotWidget})
        self.tabInfoListWidget.addItem('p1d : SILX plot1d widget')

        # #PERIODIC TABLE
        # self.periodicTable = PeriodicTable(selectable=False)
        # self.periodicTableLayout.addWidget(self.periodicTable)
        # self.consoleWidget.pushVariables({'pt' : self.periodicTable})
        # self.tabInfoListWidget.addItem('pt : SILX periodic table widget')
        # self.periodicTable.sigElementClicked.connect(self.click_table)


        # #Load single dataset
        # self._fnames = []
        # self._fname = None
        # self.buttonSelectFname.clicked.connect(self.selectFile)


        # #Loaded data
        
        # red   = qt.QColor(255,0,0)
        # green = qt.QColor(0,255,0)
        # blue  = qt.QColor(0,0,255)

        # rowCount = 4
        # columnCount = 6
   
        #model = PaletteListModel([red, green, blue])
        #model.insertRows(0, 5)
        #self.listViewData.setModel(model)

    def click_table(self, element):
        self.ptInfoListWidget.addItem(element.name)

    def openAboutDialog(self):
        self.aboutDialog.show()

    def selectFile(self):
        fname = qt.QFileDialog.getOpenFileName()
        self._fname = fname[0]
        self.lineSelectedFname.setText(self._fname)
        if fname:
            self._fnames.append(fname[0])
            self.consoleWidget.pushVariables({'fnames' : self._fnames})

    def confirmClose(self):
        msg = qt.QMessageBox(self)
        msg.setIcon(qt.QMessageBox.Question)
        msg.setText("Really close the application?")
        msg.setInformativeText("ALL NOT SAVED DATA WILL BE LOST")
        msg.setWindowTitle("Exit application?")
        msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
        if msg.exec_() == qt.QMessageBox.Ok:
            self.close()
            qt.QApplication.closeAllWindows()

class AboutDialog(qt.QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__()
        uiPath = os.path.join(sloth._resourcesPath, 'gui', 'uis', 'sloth_about.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')
        self.nameLabel.setText('Sloth {0}'.format(sloth.__version__))
            
def sloth_main_gui_app():
    app = qt.QApplication(sys.argv)
    app.setStyle("plastique")
    appli = SlothMainWindow()
    appli.show()
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    sloth_main_gui_app()

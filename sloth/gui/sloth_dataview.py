#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""sloth dataView application
=============================

"""
import os, sys
from silx.gui import qt
import sloth
from sloth.gui.widgets.dataview import DataViewDockWidget

class SlothDataViewMainWindow(qt.QMainWindow):

    def __init__(self, parent=None):
        super(SlothDataViewMainWindow, self).__init__(parent)
        uiPath = os.path.join(sloth._resourcesPath, 'gui', 'uis', 'main_base.ui')
        qt.loadUi(uiPath, baseinstance=self, package='sloth.gui')
        logoPath = os.path.join(sloth._resourcesPath, 'logo',
                                'xraysloth_logo_03.svg')
        self.setWindowTitle('Sloth - dataview')
        self.setWindowIcon(qt.QIcon(logoPath))

        #DATAVIEW DOCK WIDGET
        self.dataviewDockWidget = DataViewDockWidget(parent=self)
        self.addDockWidget(qt.Qt.LeftDockWidgetArea, self.dataviewDockWidget)
        self.dataviewDockWidget.setVisible(True)

def sloth_dataview_app():
    app = qt.QApplication(sys.argv)
    app.setStyle("plastique")
    appli = SlothDataViewMainWindow()
    appli.show()
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    #from silx import sx
    #sx.enable_gui()
    sloth_dataview_app()

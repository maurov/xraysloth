#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""custom version of IPythonWidget (from silx.gui.console)
==========================================================

"""

import os, sys
import numpy as np
import math

from silx.gui import qt
from silx.gui.console import IPythonWidget

import sloth

SLOTH_BANNER = "Sloth console, version {0}\n".format(sloth.__version__)

class customIPythonWidget(IPythonWidget):
    """customized IPythonWidget"""

    def __init__(self, *args, **kwargs):
        super(customIPythonWidget, self).__init__(custom_banner=SLOTH_BANNER,\
                                                  *args, **kwargs)

        self.pushVariables({'os'   : os,
                            'sys'  : sys,
                            'np'   : np,
                            'math' : math})
        
def main():
    """Run a Qt app with an IPython console"""
    app = qt.QApplication([])
    widget = customIPythonWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()

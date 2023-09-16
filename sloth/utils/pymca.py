#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for daily work with PyMca
======================================

"""
import logging
_logger = logging.getLogger('sloth.utils.pymca')

HAS_PYMCA = False
try:
    from PyMca5.PyMcaGui.pymca.PyMcaMain import PyMcaMain
    from PyMca5.PyMcaGui import PyMcaQt as qt
    QTVERSION = qt.qVersion()
    HAS_PYMCA = True
except ImportError:
    from sloth import NullClass
    PyMcaMain = NullClass
else:
    pass
finally:
    pass

### interactive console utils: this works only in the interactive console

def get_average(method="average"):
	"""average the current plotted curves"""

	from sloth.utils.arrays import merge_arrays_1d
	
	curves = plugin.getAllCurves()
    for (x, y, leg, info) in curves:
        plugin.removeCurve(leg)
    avg = merge_arrays_1d(curves, method=method)
    plugin.addCurve(avg[0], avg[1], legend=f"average of {len(curves)}", replace=True)


def getPyMcaMain(fload=None):
    """show PyMcaMain from a shell (e.g. IPython) and return its obj"""
    from matplotlib import rcParams
    rcParams['text.usetex'] = False

    if HAS_PYMCA:
        m = PyMcaMain()
        if fload is not None:
            m.sourceWidget.sourceSelector.openFile(fload)
        m.show()
        return m
    else:
        _logger.error("PyMca not found")
        return 0


class myPyMcaMain(PyMcaMain):
    """customized version of PyMcaMain to run within IPython shell"""

    def __init__(self, fload=None, name="slothPyMca", **kws):
        super(myPyMcaMain, self).__init__(name=name, **kws)

        #self.conf = self.getConfig()

        if fload is not None:
            self.loadFile(fload)
        self.show()

    def loadFile(self, fload):
        """load a file in the sourceWidget"""
        self.sourceWidget.sourceSelector.openFile(fload)


if __name__ == '__main__':
    pass

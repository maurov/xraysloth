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
import numpy as np
import matplotlib.pyplot as plt

from larch.io.mergegroups import index_of

from sloth.utils.arrays import merge_arrays_1d

def get_curves(remove=False):
    """get *ALL* plotted curves from PyMca `plugin`
    
    Parameters
    ----------

    remove: boolean
        to remove the curves from the plot (in case you want to push back something else)
    """
    curves = plugin.getAllCurves()
    if remove:
        for (x, y, leg, info) in curves:
            plugin.removeCurve(leg)
    return curves

def get_average(**kws):
    """average the current plotted curves"""
    curves = get_curves(remove=True)
    avg_legs = [leg for (x, y, leg, info) in curves]
    avg = merge_arrays_1d(curves, **kws)
    avg_leg = " + ".join(avg_legs)
    plugin.addCurve(avg[0][iskip:], avg[1][iskip:], legend=f"AVG OF {len(curves)} [{avg_leg}]", replace=True)

def get_std(estart):
    """get curves (remove) and calculate the std """
    curves = get_curves()
    outcurves = []
    for (x, y, leg, info) in curves:
        plugin.removeCurve(leg)
        if estart is None:
            istart = 1 #skip first energy point
        else:
            istart = index_of(x, estart)
        std = np.std(y[istart:])
        print(f"{std:.4E}: {leg}")
        info["std"] = std
        outcurves.append((x, y, leg, info))  
    return outcurves

def select_curves_by_std(std_frac=None, estart=None, plot=True):
    """push back curves from below std level"""
    print("----- get curves from plot:")
    curves = get_std(estart)
    stds = [info['std'] for (x, y, leg, info) in curves]
    stds = np.array(stds)
    nstds = stds/np.std(stds) #normalized to 
    if plot:
        plt.close("all")
        fig, ax = plt.subplots(num="stds")
        ax.set_title("standard deviations of curves")
        ax.plot(nstds, ls="--", marker="o", color="blue", fillstyle='none')
        ax.hlines(std_frac, 0, len(curves), colors=['red'], ls='-')
        if std_frac is not None:
            ax.set_ylim(nstds.min(), 2*nstds.min())
        ax.set_xlabel("index of curves")
        ax.set_ylabel("stds/std(stds)")
        ax.minorticks_on()
        ax.xaxis.set_tick_params(which='minor', bottom=False)
        ax.grid(True, axis="y", which="both", linewidth=0.5)
    if std_frac is None:
        return
    std_level = (np.std(stds) * std_frac)
    print(f"----- curves with std < {std_level:.4E}:")
    for (x, y, leg, info) in curves:
        std = info["std"]
        if std < std_level:
            print(f"{std:.4E}: {leg}")
            plugin.addCurve(x, y, leg, info)






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

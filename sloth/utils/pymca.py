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


### MOVE TO LARCH
def reject_outliers(data, m=5.189, return_ma=False):
    """Reject outliers

    Modified from: https://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
    See also: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.0)
    mask = s < m
    if return_ma:
        imask = s > m
        return np.ma.masked_array(data=data, mask=imask)
    else:
        return data[mask]


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

def get_average(iskip=1, method="average"):
    """average the current plotted curves"""
    curves = get_curves(remove=True)
    avg_legs = [leg for (x, y, leg, info) in curves]
    avg = merge_arrays_1d(curves, method=method)
    avg_leg = " + ".join(avg_legs)
    plugin.addCurve(avg[0][iskip:], avg[1][iskip:], legend=f"AVG OF {len(curves)} [{avg_leg}]", replace=True)

def get_std(estart):
    """get curves (remove) and calculate the std """
    curves = get_curves(remove=True)
    outcurves = []
    for icurve, (x, y, leg, info) in enumerate(curves):
        if estart is None:
            istart = 1 #skip first energy point
        else:
            istart = index_of(x, estart)
        std = np.std(y[istart:])
        print(f"{icurve}) {std:.4E}: {leg}")
        info["std"] = std
        outcurves.append((x, y, leg, info))  
        #plugin.removeCurve(leg)
    return outcurves


#previous version
#def select_curves_by_std(std_frac=None, estart=None, plot=True):
#    """push back curves from below std level"""
#    print("----- get curves from plot:")
#    curves = get_std(estart)
#    stds = [info['std'] for (x, y, leg, info) in curves]
#    stds = np.array(stds)
#    nstds = stds/np.std(stds) #normalized to 
#    if plot:
#        plt.ion()
#        plt.close("all")
#        fig, ax = plt.subplots(num="stds")
#        ax.set_title("standard deviations of curves")
#        ax.plot(nstds, ls="--", marker="o", color="blue", fillstyle='none')
#        ax.hlines(std_frac, 0, len(curves), colors=['red'], ls='-')
#        if std_frac is not None:
#            ax.set_ylim(nstds.min(), 2*nstds.min())
#        ax.set_xlabel("index of curves")
#        ax.set_ylabel("stds/std(stds)")
#        ax.minorticks_on()
#        ax.xaxis.set_tick_params(which='minor', bottom=False)
#        ax.grid(True, axis="y", which="both", linewidth=0.5)
#    if std_frac is None:
#        return
#    std_level = (np.std(stds) * std_frac)
#    print(f"----- curves with std < {std_level:.4E}:")
#    for (x, y, leg, info) in curves:
#        std = info["std"]
#        if std < std_level:
#            print(f"{std:.4E}: {leg}")
#            plugin.addCurve(x, y, leg, info)



def select_curves_by_std(std_frac=None, estart=None, plot=True, m=6):
    """push back curves from below std level"""
    print("----- get all curves from plot:")
    curves = get_std(estart)
    stds = [info['std'] for (x, y, leg, info) in curves]
    stds = np.array(stds)
    stds2 = reject_outliers(stds, m=m, return_ma=True)  #: detect outliers automagically
    nstds = stds/np.std(stds) #normalized ???
    if plot:
        plt.ion()
        plt.close("all")
        fig, ax = plt.subplots(num="stds")
        ax.set_title("standard deviations of curves")
        #ax.plot(nstds, ls="--", marker="o", color="blue", fillstyle='none')
        ax.plot(stds, ls="--", marker="o", color="blue", fillstyle='none', label="all")
        ax.plot(stds2, ls=" ", marker="o", color="green", label=f"detected")
        ax.hlines(std_frac, 0, len(curves), colors=['red'], ls='-')
        ax.legend()
        if std_frac is not None:
            ax.set_ylim(nstds.min(), 2*nstds.min())
        ax.set_xlabel("index of curves")
        ax.set_ylabel("stds")
        ax.minorticks_on()
        ax.xaxis.set_tick_params(which='minor', bottom=False)
        ax.grid(True, axis="y", which="both", linewidth=0.5)
    #if std_frac is not None:
    #std_level = (np.std(stds) * std_frac)
    print(f"----- selected curves:")
    for icurve, (x, y, leg, info) in enumerate(curves):
        std = info["std"]
        #print(f"{icurve}, {len(curve)}, {stds2.mask[icurve]}, {std}")
    #    if std < std_level:
        if not(stds2.mask[icurve]):
            print(f"{icurve}) {std:.4E}: {leg}")
            plugin.addCurve(x, y, leg, info)
    #return stds2, fig, ax
    





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

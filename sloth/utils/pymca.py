#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for daily work with PyMca
======================================

"""
import copy
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

### interactive console utils: this works only in the interactive console
import numpy as np
import matplotlib.pyplot as plt

from larch.io.mergegroups import index_of, reject_outliers, merge_arrays_1d

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
    curves = get_curves()
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
        plugin.removeCurve(leg)
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
    print("---> get all curves from plot:")
    curves = get_std(estart)
    stds0 = [info['std'] for (x, y, leg, info) in curves]
    stds0 = np.array(stds0)
    mstds0 = np.median(stds0)
    if std_frac is not None:
        max_std = mstds0 * (1 + std_frac)
    else:
        max_std = mstds0
    beststd = stds0.min()
    ibeststd = index_of(stds0, beststd)
    (xbest, ybest, legbest, infobest) = curves[ibeststd]
    print(f"---> *best std* {ibeststd}) {beststd:.4E}: {legbest}")
    yrels = [(y - ybest) for (x, y, leg, info) in curves]
    #stds1 = [np.std(yrel) for yrel in yrels]
    #stds1 = [np.sum(np.abs(yrel)) for yrel in yrels]
    #stds1 = [len(np.extract(yrel > beststd, yrel)) for yrel in yrels]
    stds1 = stds0  #: all previous methods not working! TODO: find a clever way to discriminate curves
    #DEV/DEBUG
    if 0:
        for yrel, (x, y, leg, info) in zip(yrels, curves):
            plugin.addCurve(x, yrel, leg, info)
        import pdb; pdb.set_trace()
        return 
    stds2 = reject_outliers(stds1, m=m, return_ma=True)  #: detect outliers automagically
    for istd, std in enumerate(stds0):
        if std <= mstds0:
            stds2.mask[istd] = False  #: force to keep all curves with std less than median
        if (std_frac is not None) and (std > max_std):
            stds2.mask[istd] = True  #: force to remove if threshold is given
    nstds = stds0/np.std(stds0) #normalized ???
    if plot:
        plt.ion()
        #plt.close("all")
        plt.clf()
        fig, ax = plt.subplots(num="stds")
        ax.set_title("standard deviations of curves")
        ax.plot(stds1, ls="--", marker="o", color="blue", fillstyle='none', label="all")
        ax.plot(stds2, ls=" ", marker="o", color="green", label=f"selected")
        ax.hlines(mstds0, 0, len(curves), colors=['orange'], ls='--', label=f"median: {mstds0:.3E}", linewidth=1)
        if std_frac is not None:
            ax.set_ylim(stds0.min()*0.95, max_std*1.05)
            ax.hlines(max_std, 0, len(curves), colors=['red'], ls='--', label=f"threshold: {max_std:.2E}", linewidth=1)
        ax.legend(fontsize=8)
        ax.set_xlabel("index of curves")
        ax.set_ylabel("stds")
        ax.minorticks_on()
        #ax.xaxis.set_tick_params(which='minor', bottom=False)
        ax.grid(True, axis="both", which="both", linewidth=0.5)
    #if std_frac is not None:
    #std_level = (np.std(stds) * std_frac)
    print(f"---> selected curves:")
    for icurve, (x, y, leg, info) in enumerate(curves):
        std = info["std"]
        #print(f"{icurve}, {len(curve)}, {stds2.mask[icurve]}, {std}")
    #    if std < std_level:
        if not(stds2.mask[icurve]):
            print(f"{icurve}) {std:.4E}: {leg}")
            plugin.addCurve(x, y, leg, info)
    #return stds2, fig, ax
    
def dt_corr(signal, tau):
    """dead time correction"""
    return signal/(1-tau*signal)

def get_tau(counting_time=1, xmax=None, iskip=0, plot=False):
    """get tau for dead time correction"""

    if plot:
        plt.ion()
        plt.close('all')

    from lmfit.models import LinearModel
    
    curves = get_curves()
    taus = []
    figs = []

    print("-> COPY THE FOLLOWING IN BLISS:")
    print("--- blisadm@bm16ctrl: beamline_configuration/counters/fluo_corrections.yml")

    for curve in curves:
        x, y, legend, info = curve

        detn = legend.split("det")[1].split(" ")[0]

        ct = np.ones_like(y) * counting_time

        if xmax is None:
            ixmax = len(x)
        else:
            ixmax = index_of(x, xmax)

        xtofit = copy.deepcopy(x[iskip:ixmax] / ct[iskip:ixmax])
        ytofit = copy.deepcopy(x[iskip:ixmax] / y[iskip:ixmax])

        linmod = LinearModel()
        pars =  linmod.guess(ytofit, x=xtofit)
        linfit = linmod.fit(ytofit, pars, x=xtofit)
        if plot:
            fig = linfit.plot(title=f"det{detn}")
    
        tau = linfit.result.params['slope'].value
        print(f'det{detn}: {tau:.7E}')
        info["tau"] = tau
        taus.append(tau)
        ycorr = dt_corr(y, tau)
        legcorr = f"{legend}_dtcorr"
        if plot:
            plugin.addCurve(x, ycorr, legcorr, info)

    #return taus

def apply_dt_corr(tau: float, remove: bool = False) -> None:
    """apply dead time correction to the current curves
    
    Parameters
    ----------

    tau : float
        time constant
    remove : boolean
        if True, removes the initially plotted curves
    """
    curves = get_curves(remove=remove)

    for curve in curves:
        x, y, legend, info = curve
        ycorr = dt_corr(y, tau)
        legcorr = f"{legend}_dtcorr"
        info["tau"] = tau
        plugin.addCurve(x, ycorr, legcorr, info)



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

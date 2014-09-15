#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""
plots related to dthetaxz
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2013-2014"
__version__ = "0.1.3"
__status__ = "in progress"
__date__ = "Aug 2014"

import sys, os
import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import cm
from matplotlib.ticker import MaxNLocator, AutoLocator, MultipleLocator

from dthetaxz import dThetaXZ, mapCase2Num, mapNum2Case, getMeshMasked, getDthetaDats, writeScanDats
from specfiledata import SpecfileData

def plotEffScatt(xx, zz, wrc=1.25E-4,
                 cases=['Johann', 'Johansson', 'Spherical plate', 'Wittry'], casesLabels=None,
                 angles=[15, 45, 75], xyFigHalfRange=None, xyTicks=0.1, figName='fig1',
                 xFigSize=10*150, yFigSize=6*150, figDpi=150, fontSize=8, nlevels=15, colSpan=2,
                 plotMask=True, absWrc=False, cbarShow=True, cbarTicks=2.5E-5):
    """plots the effective scattering angle given a masked array
    
    Parameters
    ----------
    xx, zz : 2D masked arrays of floats - dThetaXZ() is calculated
             over them
    w : float, maximum accepted angular range [1.25E-4]
    cases : list of str, accepted cases by dThetaXZ (the figure nicely
            shows for 4 items)
    casesLabels : list of str,
                  labels for the cases [None] (if none, it takes cases strings)
    angles : list of floats, theta angles (the figure nicely shows for
             3 items)
    figName : str, name of the figure ['fig1']

    xyFigHalfRange : None or float, if given, set figure dimensions in
                     units of r1p (crystal bending radius) and shows a
                     reference circle with this radius [None]

    xyTicks : float, spacing between major ticks (labels) in x and y - units of r1p [0.05]

    xFigSize, yFigSize : int or float, x, y size of the figure
                         [10*dpi, 6*dpi]
    figDpi : int, figure resolution [150]
    nlevels : int, number of color levels [15]
    colSpan : int, number of columns to span for each subplot [2]
    plotMasks : boolean, to show the mask [True]
    absWrc : boolean, to show absolute $\Delta \theta$ [False]
    cbarShow : boolean, to show the color bar [True]
    cbarTicks : float, spacing between color bar ticks [2.5E-5]

    Returns
    -------
    None

    """
    plt.rcParams['font.size'] = fontSize
    plt.rcParams['text.usetex'] = True
    norm = cm.colors.Normalize(vmin=-2*wrc, vmax=2*wrc)
    extent = (xx.min(), xx.max(), zz.min(), zz.max())
    levels = np.linspace(-wrc, wrc, nlevels)
    fig = plt.figure(num=figName, figsize=(xFigSize/figDpi, yFigSize/figDpi), dpi=figDpi)
    gs = gridspec.GridSpec(len(angles), colSpan*len(cases)+1) #3x3+1 grid +1 is for the colorbar
    ylab = 0.97
    ylabshift = -0.3
    if casesLabels is None:
        casesLabels = cases
    for th, gsx in zip(angles, range(len(angles))):
        for cs, cl, gsy in zip(cases, casesLabels, range(colSpan*len(cases))[::colSpan]):
            dth = dThetaXZ(xx, zz, th, case=cs)
            if absWrc:
                mdth = ma.masked_where(np.abs(dth) > wrc, dth)
            else:
                mdth = ma.masked_where(dth > wrc, dth)
            gsplt = plt.subplot(gs[gsx, gsy:gsy+colSpan])
            if xyFigHalfRange is not None:
                gsplt.set_xlim(-xyFigHalfRange, xyFigHalfRange)
                gsplt.set_ylim(-xyFigHalfRange, xyFigHalfRange)
                refCircle = plt.Circle((0.,0.), xyFigHalfRange, color='w', ec='k', zorder=0)
                gsplt.add_artist(refCircle)
            cntf = gsplt.contourf(xx, zz, mdth, levels, cmap=cm.get_cmap(cm.RdYlGn, len(levels)-1), norm=norm)
            #gsplt.imshow(zz, origin='lower', extent=extent, cmap=cm.RdBu, norm=norm)
            # gsplt.xaxis.set_major_locator(MaxNLocator(4))
            # gsplt.xaxis.set_minor_locator(MaxNLocator(5))
            # gsplt.yaxis.set_major_locator(MaxNLocator(4))
            # gsplt.yaxis.set_minor_locator(MaxNLocator(5))
            gsplt.xaxis.set_major_locator(MultipleLocator(xyTicks))
            gsplt.yaxis.set_major_locator(MultipleLocator(xyTicks))
            if plotMask:
                mm = ma.ones(zz.shape)
                mm.mask = np.logical_not(zz.mask)
                gsplt.contourf(xx, zz, mm, 1, cmap=cm.Greys)
            if gsx == 0:
                gsplt.set_title(cl)
            if gsx == 2:
                gsplt.set_xlabel(r'x, mer. (R$_{m}^{\prime}$)')
            if gsy == 0:
                gsplt.set_ylabel(r'z, sag. (R$_{m}^{\prime}$)')
                gsplt.annotate(r'{0}$^\circ$'.format(th), horizontalalignment='center', verticalalignment='center', fontsize=plt.rcParams['font.size'], bbox=dict(boxstyle="round4", fc="w"), xy=(0.025, ylab), xycoords='figure fraction')
                ylab += ylabshift
    # colorbar
    if cbarShow:
        cplt = plt.subplot(gs[:, -1])
        cb = fig.colorbar(cntf, cax=cplt, use_gridspec=True, orientation='vertical', format='%.1E')
        #cb.set_ticks(AutoLocator())
        cb.set_ticks(MultipleLocator(cbarTicks))
        cb.set_label(r'$|\Delta \theta|$ below given threshold of {:.3E}'.format(wrc))
    plt.tight_layout()
    plt.show()


def plotScanThetaFile(fname, scans, signal='eres', xlims=None, ylims=None, ylog=True,
                      yscale=1, caseScale='Js', plotDeeShells=True, showLegend=True,
                      figName='fig1', figSize=(5,5), figDpi=150, fontSize=10):
    """ plot 1D $\theta_{B}$ scans from SPEC file
    
    Parameters
    ----------
    fname : SPEC file name (refer writeScanDats)
    scans : list of scans
    signal : string, 'eres'
    xlims : tuple, None
    ylims : tuple, None
    ylog : boolean, True
           sets y in log scale
    yscale : int or float, 1
             scale factor for y
    caseScale : str, 'Js'
                case to apply yscale
    plotDeeShells : boolean, True
                    plots the energy resolution for K, L$_{2,3}$ and M$_{4,5}$ shells
    showLegend : boolean, True
                 show the legend on the plot
    figName : str, 'fig1'
    figSize : tuple, (5,5)
    figDpi : int or float, 150
    fontSize : int or float, 10

    Returns
    -------
    None
    """
    plt.rcParams['font.size'] = fontSize
    fig = plt.figure(num=figName, figsize=figSize, dpi=figDpi)
    gs = gridspec.GridSpec(1,1)
    gsplt = plt.subplot(gs[0])
    cls = {'Js' : 'blue',
           'SphJn' : 'red',
           'TorJs' : 'green',
           'JsFocus' : 'violet'}
    d = SpecfileData(fname)
    for scan in scans:
        x, y, mots, infos = d.get_scan(scan, csig=signal)
        lab = d.sd.command()
        if (mots['r1p'] == 1000.0):
            _ms = 5
            _mk = 'v'
        else:
            _ms = 5
            _mk = 'o'
        case = mapNum2Case(mots['case'])
        try:
            cl = cls[case]
        except:
            cl = 'gray'
        if (mapNum2Case(mots['case']) == caseScale):
            ys = yscale
        else:
            ys = 1
        gsplt.plot(x, y*ys, label=lab, color=cl, lw=1, marker=_mk, ms=_ms)
    if plotDeeShells:
        gsplt.axhline(y=2E-4, color='orange', ls='dashed', lw=2, label=r'K')
        gsplt.axhline(y=6E-4, color='gray', ls='dashed', lw=2, label=r'L$_{2,3}$')
        gsplt.axhline(y=8E-4, color='black', ls='dashed', lw=2, label=r'M$_{4,5}$')
    #gsplt.set_title(r'title')
    gsplt.set_xlabel(r'Bragg angle $\theta_B$ (deg)')
    if 'eres' in signal.lower():
        gsplt.set_ylabel(r'Energy resolution, $\Delta$ E/E')
    elif 'sa' in signal.lower():
        gsplt.set_ylabel(r'Effective solid angle (sr)')
    else:
        gsplt.set_ylabel(r'{0}'.format(signal))
    if ylog: gsplt.set_yscale('log')
    if xlims: gsplt.set_xlim(xlims)
    if ylims: gsplt.set_ylim(ylims)
    gsplt.xaxis.set_major_locator(MultipleLocator(5))
    gsplt.xaxis.set_minor_locator(MultipleLocator(1))
    #gsplt.yaxis.set_major_locator(MultipleLocator(1E-4))
    #gsplt.yaxis.set_minor_locator(MultipleLocator(0.25E-4))
    gsplt.grid(True, color='gray', lw=1, alpha=0.5)
    if showLegend:
        gsplt.legend(loc=2, ncol=1, mode="expand", borderaxespad=0., numpoints=1, fancybox=True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # TESTS in xrayspina/examples/dthetaxz_tests.py
    pass


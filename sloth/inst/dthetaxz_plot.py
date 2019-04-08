#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""plots related to dthetaxz"""
import sys, os
import copy
import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator, AutoLocator, MultipleLocator

from sloth.inst.dthetaxz import dThetaXZ, mapCase2Num, mapNum2Case, getMeshMasked, getDthetaDats, writeScanDats
from sloth.io.specfile_reader import SpecfileData

def plotEffScatt(xx, zz, wrc=1.25E-4,\
                 cases=['Johann', 'Johansson', 'Spherical plate', 'Wittry'],\
                 casesLabels=None,\
                 angles=[15, 45, 75], xyFigHalfRange=None, xyTicks=0.1,\
                 xlabel=r'x, mer. (R$_{m}^{\prime}$)',\
                 ylabel=r'z, sag. (R$_{m}^{\prime}$)',\
                 figName='fig1', xyFigSize=(10*150, 6*150), figDpi=150, fontSize=8,\
                 nlevels=15, rowSpan=2, colSpan=2, xylab=(0.025, 0.97), ylabshift=-0.3,\
                 plotMask=True, plotVert=False, absWrc=False, cbarShow=True,\
                 cbarTicks=2.5E-5, cbarOrientation='vertical',\
                 cbarLabel=r'$\Delta \theta$',\
                 figCmap=cm.RdYlGn, figOut=None):
    """plots the effective scattering angle given a masked array

    Parameters
    ----------
    xx, zz : 2D masked arrays of floats
             dThetaXZ() is calculated over them

    wrc : float, 1.25E-4
        maximum accepted angular range

    cases : list of str, ['Johann', 'Johansson', 'Spherical plate', 'Wittry']
            accepted cases by dThetaXZ (tip: nicely shows for 4 items)

    casesLabels : list of str, None
                  labels for the cases (if none, it takes cases
                  strings)

    angles : list of floats, [15, 45, 75]
             theta angles (tip: nicely shows for 3 items)

    figName : str, 'fig1'
              name of the figure

    xyFigHalfRange : float, None
                     set figure dimensions in units of r1p (crystal
                     bending radius) and shows a reference circle with
                     this radius

    xyTicks : float, 0.1
              spacing between major ticks (labels) in x and y - units
              of r1p

    xlabel : str, r'x, mer. (R$_{m}^{\prime}$)'
             label x axis

    ylabel : str, r'z, sag. (R$_{m}^{\prime}$)'
             label y axis

    xyFigSize : list of int or floats, [10*dpi, 6*dpi]
                x, y size of the figure

    figDpi : int, 150
             figure resolution

    figOut : [None]
             figure to save

    fontSize : int, 8


    nlevels : int, 15
              number of color levels

    colSpan : int, 2
              number of columns to span for each subplot (useful if cbarOrientation=='vertical')

    rowSpan : int, 2
              number of row to span for each subplot (useful if cbarOrientation=='horizontal')

    xylab : tuple of floats, (0.025, 0.97)
            position of the angles label (showing theta) in 'figure
            fraction' units

    xylabshift : float, -0.3
                 shift ('figure fraction' units) xylab[1] each subplot

    plotMask : boolean, True
               to show the mask

    plotVert: boolean, False
              plot vertical scattering

    absWrc : boolean, False
             to show absolute $\Delta \theta$

    cbarShow : boolean, True
               to show the color bar

    cbarTicks : float, 2.5E-5
                spacing between color bar ticks

    cbarOrientation : str, 'vertical'
                      orientation of the colorbar: 'vertical' or 'horizontal'

    Returns
    -------
    None

    """
    plt.ion()
    plt.rcParams['font.size'] = fontSize
    plt.rcParams['text.usetex'] = True
    #wrc as multi-values
    if (type(wrc) is list):
        if not (len(wrc) == len(angles)):
            raise NameError('len(wrc) not as angles')
        else:
            wrc_angles = copy.deepcopy(wrc)
    else:
        wrc_angles = np.ones_like(angles)*wrc
    wrc = min(wrc_angles)
    #check if there is a common or separated grid for each case
    if (type(xx) is list) and (type(zz) is list):
        if (len(xx) == len(cases)) and (len(zz) == len(cases)):
            hasMasks = True
            _xx = xx[0]
            _zz = zz[0]
    else:
        hasMasks = False
        _xx = xx
        _zz = zz
    nangles = len(angles)
    ncases = len(cases)
    extent = (_xx.min(), _xx.max(), _zz.min(), _zz.max())
    fig = plt.figure(num=figName, figsize=(xyFigSize[0]/figDpi, xyFigSize[1]/figDpi), dpi=figDpi, constrained_layout=True)
    if cbarOrientation == 'horizontal':
        gs = gridspec.GridSpec(rowSpan*nangles+1, ncases, figure=fig) #iN+1xM grid +1 is for the colorbar
        gsx_rng = range(0, rowSpan*nangles, rowSpan)
        gsy_rng = range(ncases)
        cplt = plt.subplot(gs[-1, :])
    else:
        gs = gridspec.GriSpec(nangles, colSpan*ncases+1, figure=fig) #NxjM+1 grid +1 is for the colorbar
        gsx_rng = range(nangles)
        gsy_rng = range(0, colSpan*ncases, colSpan)
        cplt = plt.subplot(gs[:, -1])
    xlab = xylab[0]
    ylab = xylab[1]
    if casesLabels is None:
        casesLabels = cases
    for th, gsx, _wrc in zip(angles, gsx_rng, wrc_angles):
        for ic, (cs, cl, gsy) in enumerate(zip(cases, casesLabels, gsy_rng)):
            if hasMasks:
                _xx = xx[ic]
                _zz = zz[ic]
            dth = dThetaXZ(_xx, _zz, th, case=cs)
            mdth = ma.masked_where(np.abs(dth) > _wrc, dth)
            if absWrc: mdth = np.abs(mdth)
            if cbarOrientation == 'horizontal':
                gsplt = fig.add_subplot(gs[gsx:gsx+rowSpan, gsy])
            else:
                gsplt = fig.add_subplot(gs[gsx, gsy:gsy+colSpan])
            if xyFigHalfRange is not None:
                gsplt.set_xlim(-xyFigHalfRange, xyFigHalfRange)
                gsplt.set_ylim(-xyFigHalfRange, xyFigHalfRange)
                refCircle = plt.Circle((0.,0.), xyFigHalfRange, color='w', ec='k', zorder=0)
                gsplt.add_artist(refCircle)
            if plotVert:
                _xxplot = _zz
                _zzplot = _xx
            else:
                _xxplot = _xx
                _zzplot = _zz
            norm = cm.colors.Normalize(vmin=-2*wrc, vmax=2*wrc) #NOT WORKING (NOT USED)!!!
            if absWrc:
                levels = np.linspace(0, wrc, nlevels)
            else:
                levels = np.linspace(-wrc, wrc, nlevels)
            #cntf = gsplt.contourf(_xxplot, _zzplot, mdth, levels, cmap=cm.get_cmap(figCmap, len(levels)-1), norm=norm)
            #cntf = gsplt.contourf(_xxplot, _zzplot, mdth, levels, cmap=cm.get_cmap(figCmap, len(levels)-1))
            cntf = gsplt.contourf(_xxplot, _zzplot, mdth, nlevels, cmap=cm.get_cmap(figCmap, nlevels-1))
            #gsplt.imshow(_zzplot, origin='lower', extent=extent, cmap=cm.get_cmap(figCmap), norm=norm)
            # gsplt.xaxis.set_major_locator(MaxNLocator(4))
            # gsplt.xaxis.set_minor_locator(MaxNLocator(5))
            # gsplt.yaxis.set_major_locator(MaxNLocator(4))
            # gsplt.yaxis.set_minor_locator(MaxNLocator(5))
            gsplt.xaxis.set_major_locator(MultipleLocator(xyTicks))
            gsplt.yaxis.set_major_locator(MultipleLocator(xyTicks))
            if plotMask:
                mm = ma.ones(_zzplot.shape)
                mm.mask = np.logical_not(_zzplot.mask)
                gsplt.contourf(_xxplot, _zzplot, mm, 1, cmap=cm.Greys)
            if gsx == 0:
                gsplt.set_title(cl)
            if gsx == 2:
                gsplt.set_xlabel(xlabel)
            if gsy == 0:
                gsplt.set_ylabel(ylabel)
                gsplt.annotate(r'{0}$^\circ$'.format(th),
                               horizontalalignment='center',
                               verticalalignment='center',
                               fontsize=fontSize+2,
                               bbox=dict(boxstyle="round4", fc="w"),
                               xy=(xlab, ylab), xycoords='figure fraction')
                ylab += ylabshift
    # colorbar
    if cbarShow:
        cb = fig.colorbar(cntf, cax=cplt, use_gridspec=True, orientation=cbarOrientation, format='%.1E')
        #cb.set_ticks(AutoLocator())
        cb.set_ticks(MultipleLocator(cbarTicks))
        cb.set_label(cbarLabel)
    plt.tight_layout()
    plt.show()
    if figOut:
        plt.savefig('{0}.pdf'.format(figOut), bbox_inches='tight')
        plt.savefig('{0}.png'.format(figOut), bbox_inches='tight')
        plt.savefig('{0}.svg'.format(figOut), bbox_inches='tight')


def plotScanThetaFile(fname, scans, signal='eres', xlims=None, ylims=None, ylog=True,
                      yscale=1, caseScale='Js', plotDeeShells=True, showLegend=True,
                      figName='fig1', figSize=(5,5), figDpi=150, fontSize=10):
    """plot 1D $\theta_{B}$ scans from SPEC file

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
    gs = fig.gridspec.GridSpec(1,1)
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
        gsplt.legend(loc=2, ncol=1, mode="expand", borderaxespad=0.,
                     numpoints=1, fancybox=True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # TESTS in xraysloth/examples/dthetaxz_tests.py
    pass

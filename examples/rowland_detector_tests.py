#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for sloth.inst.rowland (detector movements part)
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"

import os, sys
import math

import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib import rc, cm, gridspec
from matplotlib.ticker import MultipleLocator

### SLOTH ###
try:
    from sloth import __version__ as sloth_version
    from sloth.inst.rowland import cs_h, acenx, det_pos_rotated, RcHoriz, RcVert
    from sloth.utils.genericutils import colorstr
    from sloth.utils.bragg import d_cubic, d_hexagonal
except:
    raise ImportError('sloth is not installed (required version >= 0.2.0)')

def testDetMove(Rm=510):
    """test detector position in two ref frames"""
    ths = np.linspace(35., 85., 51)
    dres = {'th' : [],
            'dy' : [],
            'dz' : [],
            'dpar' : [],
            'dper' : []}
    for th in ths:
        r = RcHoriz(Rm, theta0=th, showInfos=False)
        d0 = r.get_det_pos()
        d1 = det_pos_rotated(d0, drot=35.)
        dres['th'].append(th)
        dres['dy'].append(d0[1])
        dres['dz'].append(d0[2])
        dres['dpar'].append(d1[0])
        dres['dper'].append(d1[1])
    return dres

def fig2DetMove(thTot, thStops=None, figName='spectroTravelYZ',
                drot=35., figSize=(6,6), figDpi=150, replace=True,
                plotLegend=True, plotGrid=True, figTitle=None,
                xMajTicks=100, xMinTicks=10, yMajTicks=100,
                yMinTicks=10, figSaveName=None):
    """figure showing detector trajectories in two reference systems:
    
    1) global [Y,Z]
    2) local [dpar,dper]

    the local reference system is rotated counter clock-wise around X by drot (deg)

    Parameters
    ----------

    thTot : full angular range for calculating the detector positions, deg

    thStops : list of angles where to show a stop indicator

    """
    
    ### FIGURE LAYOUT ###
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size':'12'})
    rc('text', usetex=True)

    fig, (top, bot) = plt.subplots(num=figName, nrows=2, ncols=1, figsize=figSize, dpi=figDpi)

    #plot setup
    radii =    [490.,   500.,               510.,   240.,    250.,              260.]
    rmasks =   [1,      1,                  1,      1,       1,                 1]
    rthstops = [0,      1,                  0,      0,       1,                 0] 
    labels =   [None,   '1000 $\pm$ 20 mm', None,   None,    '500 $\pm$ 20 mm', None]
    lcs =      ['blue', 'blue',             'blue', 'green', 'green',           'green']
    lss =      ['--',   '-',                '--',   '--',    '-',               '--']
    alphas =   [0.5,    None,               0.5,    0.5,     None,              0.5]

    #detector scan
    for irm, rm in enumerate(radii):
        if not rmasks[irm]:
            continue
        r = RcHoriz(Rm=rm, showInfos=False)
        yD = np.zeros_like(thTot)
        zD = np.zeros_like(thTot)
        dyD = np.zeros_like(thTot)
        dzD = np.zeros_like(thTot)
        for ith, th in enumerate(thTot):
            r.set_theta0(th)
            dpos = r.get_det_pos()
            dpos2 = det_pos_rotated(dpos, drot=drot)
            yD[ith] = dpos[1]
            zD[ith] = dpos[2]
            dyD[ith] = dpos2[0]
            dzD[ith] = dpos2[1]
        top.plot(yD, zD, lw=2, color=lcs[irm], ls=lss[irm], alpha=alphas[irm], label=labels[irm])
        bot.plot(dyD, dzD, lw=2, color=lcs[irm], ls=lss[irm], alpha=alphas[irm], label=labels[irm])


    #th stops indicators (vertical line)
    if thStops is not None:
        for irm, rm in enumerate(radii):
            if not rthstops[irm]:
                continue
            r = RcHoriz(Rm=rm, showInfos=False)
            for th in thStops:
                r.set_theta0(th)
                dpos = r.get_det_pos()
                dpos2 = det_pos_rotated(dpos, drot=drot)
                top.vlines(x=dpos[1], ymin=dpos[2]-yMajTicks, ymax=dpos[2]+yMajTicks, linewidth=2, color=lcs[irm], alpha=0.5)
                bot.vlines(x=dpos2[0], ymin=dpos2[1]-yMajTicks, ymax=dpos2[1]+yMajTicks, linewidth=2, color=lcs[irm], alpha=0.5)
            
    if figTitle is None:
        figTitle = r'Detector travel in {0}-{1} deg range'.format(int(thTot[-1]), int(thTot[0]))

    for p, ref, xlab, ylab in zip((top, bot), ('global', 'local'), ('y', 'dpar/dy'), ('z', 'dper/dz')):
        p.set_title('{0} - {1} ref'.format(figTitle, ref))
        p.set_xlabel(r'{0} (mm)'.format(xlab))
        p.set_ylabel(r'{0} (mm)'.format(ylab))
        p.xaxis.set_major_locator(MultipleLocator(xMajTicks))
        p.xaxis.set_minor_locator(MultipleLocator(xMinTicks))
        p.yaxis.set_major_locator(MultipleLocator(yMajTicks))
        p.yaxis.set_minor_locator(MultipleLocator(yMinTicks))

        if plotGrid:
            p.grid(True, color='gray', lw=1, alpha=0.5)
        if plotLegend and (ref == 'global'):
            p.legend(loc='lower right', numpoints=1, fancybox=True)

    plt.tight_layout()
    plt.ion()
    plt.draw()
    plt.show()

    if figSaveName:
        print('Saving plot to {0}.pdf/.png/.svg'.format(figSaveName))
        plt.savefig('{0}.pdf'.format(figSaveName), bbox_inches='tight')
        plt.savefig('{0}.png'.format(figSaveName), bbox_inches='tight')
        plt.savefig('{0}.svg'.format(figSaveName), bbox_inches='tight')
    
    return fig

if __name__ == "__main__":
    plt.close('all')

    if 0:
        print("Detector positions continous plot with theta stops")
        thMin = 35
        thMax = 85
        thPts = 1000
        thTot = np.linspace(thMin, thMax, thPts) #better linspace includes limits
        thStops = np.arange(40, 85, 5)
        figOut = None
        #figOut = 'spectrotravel_20170404'
        figTitle = 'Detector travel {0}--{1} deg (stops every 5 deg)'.format(thMin, thMax)
        fig = fig2DetMove(thTot, thStops=thStops, figTitle=figTitle, figSaveName=figOut)
    if 1:
        print("Detector positions plot with theta intevals")
        thsEnds = [35., 40., 45., 50., 55., 60., 65., 70., 75., 80., 85.]
        thsStarts = [34.4283, 39.2352, 44.0020, 48.7192, 53.3720,
                     57.9369, 62.3748, 66.6179, 70.5431, 73.9200, 76.3397]
        thsTot = np.array([])
        for idx, (ts, te) in enumerate(zip(thsStarts, thsEnds)):
            lsp = np.linspace(ts, te, 20)
            thsTot = np.append(thsTot, lsp)
            n = np.zeros_like(lsp)
            n *= np.nan
            thsTot = np.append(thsTot, n)
        figOut = None
        #figOut = 'spectrotravel_20170403'
        fig = fig2DetMove(thsTot, figTitle='Detector travel in 50 eV scans', figSaveName=figOut)
    if 0:
        dres = testDetMove()

    pass

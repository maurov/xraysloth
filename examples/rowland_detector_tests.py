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


def figDetMoveYZ(thTot, figName='spectroTravelYZ', figSize=(6,4),
                 figDpi=150, replace=True, plotLegend=True,
                 plotGrid=True):
    
    ### FIGURE LAYOUT ###
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size':'12'})
    rc('text', usetex=True)
    if replace: plt.close(figName)
    fig = plt.figure(num=figName, figsize=figSize, dpi=figDpi)
    gsplt = fig.add_subplot(111)

    #plot setup
    radii =  [490.,   500.,               510.,   240.,    250.,              260.]
    rmasks = [1,      1,                  1,      1,       1,                 1] 
    labels = [None,   '1000 $\pm$ 20 mm', None,   None,    '500 $\pm$ 20 mm', None]
    lcs =    ['blue', 'blue',             'blue', 'green', 'green',           'green']
    lss =    ['--',   '-',                '--',   '--',    '-',               '--']
    alphas = [0.5,    None,               0.5,    0.5,     None,              0.5]

    #detector scan
    for irm, rm in enumerate(radii):
        if not rmasks[irm]:
            continue
        r = RcHoriz(Rm=rm, showInfos=False)
        yD = np.zeros_like(thTot)
        zD = np.zeros_like(thTot)
        for ith, th in enumerate(thTot):
            r.set_theta0(th)
            dpos = r.get_det_pos()
            yD[ith] = dpos[1]
            zD[ith] = dpos[2]
        gsplt.plot(yD, zD, lw=2, color=lcs[irm], ls=lss[irm],
                   alpha=alphas[irm], label=labels[irm])
        
    gsplt.set_title(r'Detector travel in {0}-{1} deg range'.format(int(thTot[-1]), int(thTot[0])))
    gsplt.set_xlabel(r'y (mm)')
    gsplt.set_ylabel(r'z (mm)')
    
    #gsplt.set_xlim(emin, emax)
    #gsplt.set_ylim(angmin, angmax)
    gsplt.xaxis.set_major_locator(MultipleLocator(50))
    gsplt.xaxis.set_minor_locator(MultipleLocator(5))
    gsplt.yaxis.set_major_locator(MultipleLocator(50))
    gsplt.yaxis.set_minor_locator(MultipleLocator(5))

    if plotGrid:
        gsplt.grid(True, color='gray', lw=1, alpha=0.5)
    if plotLegend:
        gsplt.legend(loc='lower right', numpoints=1, fancybox=True)

    plt.tight_layout()
    plt.ion()
    plt.draw()
    plt.show()
    return fig

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

if __name__ == "__main__":
    plt.close('all')

    if 1:
        thMin = 35
        thMax = 85
        thPts = 1000
        thTot = np.linspace(thMin, thMax, thPts) #better linspace includes limits
        #thSteps(thTot, eStep=0.05, eScan=50.)
        fig = figDetMoveYZ(thTot)
        #pass

    if 0:
        dres = testDetMove()

    pass

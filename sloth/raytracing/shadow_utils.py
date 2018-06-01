#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_utils: simple various utilities for SHADOW3_

.. _SHADOW3: https://github.com/srio/shadow3

"""

import sys, os
import math
import numpy as np

HAS_SHADOW = False
try:
    import Shadow
    Shadow.ShadowTools.plt.ion()
    HAS_SHADOW = True
except:
    print("WARNING: {0}\n => this test will probably fail!".format(sys.exc_info()[1]))
    pass

from sloth.fit.peakfit import fit_splitpvoigt

def get_src_hdiv(oe_xhw, oe_ydist):
    """get source horizontal divergence

    :param oe_xhw: optical element X half width
    :param oe_ydist: optical element distance from source
    
    """
    return math.atan(oe_xhw/oe_ydist)

def get_src_vdiv(oe_yhw, oe_ydist, oe_th):
    """get source vertical divergence

    :param oe_yhw: optical element Y half width
    :param oe_ydist: optical element distance from source
    :param oe_th: optical element grazing angle in degrees (e.g. Bragg angle)

    """
    _rth = math.radians(oe_th)
    _h = oe_yhw * math.sin(_rth)
    _d = oe_ydist + oe_yhw * math.cos(_rth)
    return math.atan(_h/_d)

#############
### PLOTS ###
#############

def plot_close_all():
    """close all plots

    :returns: None
    """
    Shadow.ShadowTools.plt.close('all')

def plot_energy_histo(beam, fit=False, return_tkt=False):
    """plot rays energy distribution weighted by intensity

    :param beam: Shadow.Beam() instance
    :param fit: boolean fit the data with split-PseudoVoigt [False]
    :param return_tkt: boolean if return Matplotlib ticket

    """
    tkt = Shadow.ShadowTools.histo1(beam, 11, ref=23, nbins=101)
    if fit:
        x = tkt['bin_path']
        y = tkt['histogram_path']
        fit = fit_splitpvoigt(x,y)
    if return_tkt: return tkt

def plot_footprint(return_tkt=False, **h2args):
    """plot lost rays on the optical element to check correct overfill

    :param return_tkt: boolean if return Matplotlib ticket

    """
    #avoid duplicate kwargs
    _popnolost = h2args.pop('nolost', None)
    _popref = h2args.pop('ref', None)
    _poptitle = h2args.pop('title', None)
    try:
        tkt = Shadow.ShadowTools.plotxy('mirr.01', 2, 1, nolost=2, ref=0,\
                                        title='Footprint', **h2args)
    except:
        print('ERROR: probably "mirr.XX" file does not exist!')
        tkt = 0
    if return_tkt: return tkt
    
def plot_image(beam, return_tkt=False, **h2args):
    """plot image at the detector weighted by intensity

    :param beam: Shadow.Beam() instance
    :param return_tkt: boolean if return Matplotlib ticket

    """
    #avoid duplicate kwargs
    _popnolost = h2args.pop('nolost', None)
    _popref = h2args.pop('ref', None)
    _popcalcw = h2args.pop('calculate_widths', None)
    tkt = Shadow.ShadowTools.plotxy(beam, 1, 3, ref=23, nolost=1,\
                                    calculate_widths=2, **h2args)
    if return_tkt: return tkt



if __name__ == '__main__':
    pass

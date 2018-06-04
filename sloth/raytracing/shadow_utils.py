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
    pass

from sloth.fit.peakfit import fit_splitpvoigt
from sloth.inst.rowland import RcHoriz, RcVert

###############
### SOURCES ###
###############

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
### BEAMS ###
#############

def merge_beams(beams):
    """merge a list of beams

    :param beams: list of Shadow.Beam() instances
    :returns: merged beams
    :rtype: Shadow.Beam()

    """
    beam_mrg = Shadow.Beam()
    beam_mrg.rays = beams[0].rays
    for ibeam, beam in enumerate(beams):
        if ibeam == 0: continue
        beam_mrg.rays = np.append(beam_mrg.rays, beam.rays, axis=0)
    return beam_mrg

######################
### ROWLAND CIRCLE ###
######################

def get_moverc(Rm, theta0, chi, geom='vertical'):
    """get optical element movement

    .. note:: optical element local coordinate system is used

    :param Rm: radius of the Rowland circle in mm
    :param theta0: incidence angle in deg (= Bragg angle)
    :param chi: sagittal angle in deg
                (= rotation on the sagittal plane around the sample-detector axis)
    :param geom: Rowland geometry, 'vertical' or 'horizontal'
    :returns: [OFFX, OFFY, OFFZ, X_ROT, Y_ROT, Z_ROT]
    :rtype: list of floats
    
    """
    offx, offy, offz, xrot, yrot, zrot = 0, 0, 0, 0, 0, 0
    if 'vert' in geom.lower():
        rc = RcVert(Rm, theta0, showInfos=False)
    elif 'hor' in geom.lower():
        rc = RcHoriz(Rm, theta0, showInfos=False)
    else:
        print("ERROR: geometry not known")
        return [offx, offy, offz, xrot, yrot, zrot]
    apos0 = rc.get_ana_pos(0)
    apos1 = rc.get_ana_pos(chi)
    aoff = apos1 - apos0
    #
    offx = aoff[0]
    offy = aoff[2]
    offz = -1*aoff[1]
    yrot = chi
    #
    return [offx, offy, offz, xrot, yrot, zrot]

def get_chi_TEXS(Rm, theta0):
    """get chi angles (deg) for TEXS spectrometer (Rovezzi et al.)

    :param Rm: radius of the Rowland circle in mm
    :param theta0: incidence angle in deg (= Bragg angle)
    :returns: [chi0, chi1, chi2, chi3, chi4, chi5]
    :rtype: list of floats

    """
    rc = RcHoriz(Rm, theta0, aW=25., aWext=32, rSext=10., aL=97.,
                 bender_version=1, bender=(40., 60., 28.),
                 actuator=(300, 120), showInfos=False)
    chis = []
    for ana in [0, 1, 2, 3, 4, 5]:
        chi = rc.get_chi2(ana)
        chis.append(chi)
    return chis

#############
### PLOTS ###
#############

def plot_close_all():
    """close all plots

    :returns: None
    """
    Shadow.ShadowTools.plt.close('all')

def plot_energy_histo(beam, fit=False, return_tkt=False, **h1args):
    """plot rays energy distribution weighted by intensity

    :param beam: Shadow.Beam() instance
    :param fit: boolean fit the data with split-PseudoVoigt [False]
    :param return_tkt: boolean if return Matplotlib ticket

    """
    tkt = Shadow.ShadowTools.histo1(beam, 11, ref=23, **h1args)
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

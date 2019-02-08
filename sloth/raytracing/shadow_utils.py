#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_utils: simple various utilities for SHADOW3_

.. _SHADOW3: https://github.com/srio/shadow3

"""

import sys, os, logging
import math
import numpy as np
from scipy.interpolate import splrep, sproot, splev

from silx.gui.plot.StackView import StackViewMainWindow

HAS_SHADOW = False
try:
    import Shadow
    from Shadow import ShadowLibExtensions
    Shadow.ShadowTools.plt.ion()
    HAS_SHADOW = True
except:
    pass

from sloth.fit.peakfit import fit_splitpvoigt
from sloth.inst.rowland import RcHoriz, RcVert

_logger = logging.getLogger(__name__)

############
### MATH ###
############

def fwhm_spl(x, y, threshold=0.5, k=10):
    """Determine full-with-half-maximum of a peaked set of points, x and y.

    Assumes that there is only one peak present in the datasset. The
    function uses a spline interpolation of order k.

    .. note: code taken from StackOverFlow (TODO: put link!!!)
    
    Parameters
    ==========

    x, y : arrays of floats
        dataset

    threshold : float
        at which level to get the full-width, half-maximum by default [0.5]

    k : int
       order of spline
    
    Returns
    =======

    fw : float
        full-width-at-threshold/half_maximum

    """
    class MultiplePeaks(Exception): pass
    class NoPeaksFound(Exception): pass

    half_max = np.amax(y) * threshold
    s = splrep(x, y - half_max)
    roots = sproot(s)

    if len(roots) > 2:
        raise MultiplePeaks("The dataset appears to have multiple peaks, and thus the FWHM can't be determined.")
    elif len(roots) < 2:
        raise NoPeaksFound("No proper peaks were found in the data set; likely the dataset is flat (e.g. all zeros).")
    else:
        return abs(roots[1] - roots[0])

def fwhm_cross(x, y, threshold=0.5):
    """Determine full-with-half-maximum of a peaked set of points X,Y.

    (alternative method)
    
    .. note: code taken from StackOverFlow (TODO: put link!!!)

    Parameters
    ==========

    x, y : arrays of floats
        dataset

    threshold : float
        at which level to get the full-width, half-maximum by default [0.5]

    Returns
    =======

    fw : float
        full-width-at-threshold/half_maximum

    """
    half_max = max(y) * threshold
    #find when function crosses line half_max (when sign of diff flips)
    #take the 'derivative' of signum(half_max - y[])
    d = np.sign(half_max - np.array(y[0:-1])) - np.sign(half_max - np.array(y[1:]))
    #plot(x,d) #if you are interested
    #find the left and right most indexes
    left_idx = np.where(d > 0)[0]
    right_idx = np.where(d < 0)[-1]
    return x[right_idx] - x[left_idx] #return the difference (full width)

def fwhm_bin(x, y, threshold=0.5):
    """Determine full-width-at-threshold (default: half-maximum)

    Parameters
    ==========

    x, y : arrays of floats
        dataset

    threshold : float
        at which level to get the full-width, half-maximum by default [0.5]

    Returns
    =======

    fw : float
        full-width-at-threshold/half_maximum

    """
    tt = np.where(y>=max(y)*threshold)
    if y[tt].size > 1:
        binSize = x[1] - x[0]
        fw = binSize * (tt[0][-1] - tt[0][0])
    else:
        fw = 0
    return fw

def fwhm(x, y, method='all', **kwargs):
    """get full-width-at-threshold for a x,y dataset

    Parameters
    ==========

    x, y : arrays of floats
        dataset

    method : string
       which method to use:
       - 'spl'   -> .. seealso:: :func:`fwhm_spl`
       - 'cross' -> .. seealso:: :func:`fwhm_cross`
       - 'bin'   -> .. seealso:: :func:`fwhm_bin`
       - 'all'   -> all previous, returns a list [default]
    
    threshold : float
        at which level to get the full-width, half-maximum by default [0.5]

    Returns
    =======

    fw : float or list of floats
        full-width-at-threshold/half_maximum
        if method='all' returns [fwhm_bin, fwhm_cross, fwhm_spl]
    """
    methods = ('spl', 'cross', 'bin', 'all')
    if not method in methods:
        _logger.warning('given method not understood!')
        return 0
    try:
        _spl = fwhm_spl(x, y, **kwargs)[0]
    except:
        _spl = 0
    try:
        _bin = fwhm_bin(x, y, **kwargs)
    except:
        _bin = 0
    try:
        _cross = fwhm_cross(x, y, **kwargs)[0]
    except:
        _cross = 0
    if method == 'spl'  : return _spl
    if method == 'bin'  : return _bin
    if method == 'cross': return _cross
    if method == 'all'  : return [_bin, _cross, _spl]

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

def get_beam_from_file(bin_fname):
    """get Shadow.Beam() from SHADOW binary file

    :param bin_fname: SHADOW binary file (e.g. `mirr.01`)
    :returns: beam
    :rtype: Shadow.Beam() instance

    """
    beam = ShadowLibExtensions.Beam()
    try:
        beam.load(bin_fname)
    except:
        print('ERROR: get_beam_from_file cannot load {0}'.format(bin_fname))
        beam = None
    return beam
        
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

def plot_fpstack(fps):
    """plot a stack of footprints using silx.gui.plot.StackViewMainWindow

    Parameters
    ==========

    fps : list of histo2 instances

    Returns
    =======

    sv : class:`StackViewMainWindow`

    """
    fpStack = np.array([i['histogram'] for i in fps])
    sv = StackViewMainWindow()
    sv.setWindowTitle('footprints (= lost rays at OE)')
    sv.setColormap('viridis')
    sv.setKeepDataAspectRatio(True)
    sv.setGraphXLabel('X')
    sv.setGraphXLabel('Y')
    sv.setStack(fpStack)
    sv.show()
    return sv

####################
### HISTO2 HACKS ###
####################

def get_origin_scale(h2tkt):
    """get origin and scale from a Shadow.Beam.histo2() instance

    #######################################
    .. warning:: TEMPORARY, WILL BE REMOVED
    #######################################
   
    :param h2tkt: Shadow.Beam.histo2()
    :returns: origin, scale
    :rtype: tuples of floats

    """
    xx = h2tkt['bin_h_edges']
    yy = h2tkt['bin_v_edges']
    
    xmin, xmax = xx.min(), xx.max()
    ymin, ymax = yy.min(), yy.max()
    
    origin = (xmin, ymin)
    scale = (abs((xmax-xmin)/h2tkt['nbins_h']), abs((ymax-ymin)/h2tkt['nbins_v']))
    return (origin, scale)

def histo2_normed(beam, col_h, col_v, nbins=25, ref=23, nbins_h=None,
                  nbins_v=None, nolost=0, xrange=None, yrange=None,
                  normed=False, calculate_widths=1):
    """Performs 2d histogram to prepare data for a plotxy plot

    #######################################
    .. warning:: TEMPORARY, WILL BE REMOVED
    #######################################

    
    It uses histogram2d for calculations
    
    .. note:: this Shadow.Beam.histo2 was previously called Shadow.Beam.plotxy

    :param col_h: the horizontal column
    :param col_v: the vertical column
    :param nbins: number of bins
    :param ref:
               0, None, "no", "NO" or "No":   only count the rays
               23, "Yes", "YES" or "yes": weight with intensity (look
               at col=23 |E|^2 total intensity)
               other value: use that column as weight
    :param nbins_h: number of bins in H
    :param nbins_v: number of bins in V
    :param nolost: 0 or None: all rays, 1=good rays, 2=only losses
    :param xrange: range for H
    :param yrange: range for V
    :param normed: normed parameter for numpy.histogram2d
    :param calculate_widths: 0=No, 1=calculate FWHM (default),
                             2=Calculate FWHM and FW at 25% and 75% if
                             Maximum

    :return: a dictionary with all data needed for plot

    """
    ticket = {'error':1}
    
    if ref == None: ref = 0
    if ref == "No": ref = 0
    if ref == "NO": ref = 0
    if ref == "no": ref = 0
    
    if ref == "Yes": ref = 23
    if ref == "YES": ref = 23
    if ref == "yes": ref = 23

    if ref == 1:
        print("Shadow.Beam.histo2: Warning: weighting with column 1 (X) [not with\
               intensity as may happen in old versions]")
    
    if nbins_h == None: nbins_h = nbins
    if nbins_v == None: nbins_v = nbins

    # copy the inputs
    ticket['col_h'] = col_h
    ticket['col_v'] = col_v
    ticket['nolost'] = nolost
    ticket['nbins_h'] = nbins_h
    ticket['nbins_v'] = nbins_v
    ticket['ref'] = ref
    
    (col1,col2) = beam.getshcol((col_h,col_v),nolost=nolost)

    if xrange==None: xrange = beam.get_good_range(col_h,nolost=nolost)
    if yrange==None: yrange = beam.get_good_range(col_v,nolost=nolost)

    if ref == 0:
        weights = col1*0+1
    else:
        weights = beam.getshonecol(ref,nolost=nolost)

    (hh,xx,yy) = np.histogram2d(col1, col2, bins=[nbins_h,nbins_v],\
                                range=[xrange,yrange],\
                                normed=normed, weights=weights)

    ticket['xrange'] = xrange
    ticket['yrange'] = yrange
    ticket['bin_h_edges'] = xx
    ticket['bin_v_edges'] = yy
    ticket['bin_h_left'] = np.delete(xx,-1)
    ticket['bin_v_left'] = np.delete(yy,-1)
    ticket['bin_h_right'] = np.delete(xx,0)
    ticket['bin_v_right'] = np.delete(yy,0)
    ticket['bin_h_center'] = 0.5*(ticket['bin_h_left']+ticket['bin_h_right'])
    ticket['bin_v_center'] = 0.5*(ticket['bin_v_left']+ticket['bin_v_right'])
    ticket['histogram'] = hh
    ticket['histogram_h'] = hh.sum(axis=1)
    ticket['histogram_v'] = hh.sum(axis=0)
    ticket['intensity'] = beam.intensity(nolost=nolost)
    ticket['nrays'] = beam.nrays(nolost=0)
    ticket['good_rays'] = beam.nrays(nolost=1)

    
    # CALCULATE fwhm
    if calculate_widths > 0:
        h = ticket['histogram_h']
        tt = np.where(h>=max(h)*0.5)
        if h[tt].size > 1:
            binSize = ticket['bin_h_center'][1]-ticket['bin_h_center'][0]
            ticket['fwhm_h'] = binSize*(tt[0][-1]-tt[0][0])
            ticket['fwhm_coordinates_h'] = (ticket['bin_h_center'][tt[0][0]],ticket['bin_h_center'][tt[0][-1]])
        else:
            ticket["fwhm_h"] = None

        h = ticket['histogram_v']
        tt = np.where(h>=max(h)*0.5)
        if h[tt].size > 1:
            binSize = ticket['bin_v_center'][1]-ticket['bin_v_center'][0]
            ticket['fwhm_v'] = binSize*(tt[0][-1]-tt[0][0])
            ticket['fwhm_coordinates_v'] = (ticket['bin_v_center'][tt[0][0]],ticket['bin_v_center'][tt[0][-1]])
        else:
            ticket["fwhm_v"] = None

    if calculate_widths == 2:
        # CALCULATE FW at 25% HEIGHT
        h = ticket['histogram_h']
        tt = np.where(h>=max(h)*0.25)
        if h[tt].size > 1:
            binSize = ticket['bin_h_center'][1]-ticket['bin_h_center'][0]
            ticket['fw25%m_h'] = binSize*(tt[0][-1]-tt[0][0])
        else:
            ticket["fw25%m_h"] = None

        h = ticket['histogram_v']
        tt = np.where(h>=max(h)*0.25)
        if h[tt].size > 1:
            binSize = ticket['bin_v_center'][1]-ticket['bin_v_center'][0]
            ticket['fw25%m_v'] = binSize*(tt[0][-1]-tt[0][0])
        else:
            ticket["fw25%m_v"] = None

        # CALCULATE FW at 75% HEIGHT
        h = ticket['histogram_h']
        tt = np.where(h>=max(h)*0.75)
        if h[tt].size > 1:
            binSize = ticket['bin_h_center'][1]-ticket['bin_h_center'][0]
            ticket['fw75%m_h'] = binSize*(tt[0][-1]-tt[0][0])
        else:
            ticket["fw75%m_h"] = None

        h = ticket['histogram_v']
        tt = np.where(h>=max(h)*0.75)
        if h[tt].size > 1:
            binSize = ticket['bin_v_center'][1]-ticket['bin_v_center'][0]
            ticket['fw75%m_v'] = binSize*(tt[0][-1]-tt[0][0])
        else:
            ticket["fw75%m_v"] = None

    return ticket


if __name__ == '__main__':
    pass

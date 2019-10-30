#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Arrays manipulation utilities
================================

Basic array manipulation using Numpy & Scipy
"""
import numpy as np
from scipy.interpolate import interp1d

from .logging import getLogger
_logger = getLogger('sloth.utils.arrays')


def imin(arr, debug=False):
    """index of minimum value"""
    _im = np.argmin(arr)
    if debug:
        _logger.debug('Check: {0} = {1}'.format(np.min(arr), arr[_im]))
    return _im


def imax(arr, debug=False):
    """index of maximum value"""
    _im = np.argmax(arr)
    if debug:
        _logger.debug('Check: {0} = {1}'.format(np.max(arr), arr[_im]))
    return _im


def sum_arrays_1d(xdats, zdats, axis=None):
    """Sum list of 1D arrays by interpolation on a reference axis

    Parameters
    ----------
    xdats, zdats : lists of 1D arrays
        data to sum
    axis : array 1D (optional)
        a reference axis used for the interpolation [None -> xdats[0]]

    Returns
    -------
    axis, zsum : 1D arrays
        sum(zdats)
    """
    if axis is None:
        axis = xdats[0]
    try:
        #: sum element-by-element
        arr_zdats = np.array(zdats)
        return axis, np.sum(arr_zdats, 0)
    except Exception:
        #: sum by interpolation
        zsum = np.zeros_like(axis)
        for xdat, zdat in zip(xdats, zdats):
            fdat = interp1d(xdat, zdat)
            zsum += fdat(axis)
        return axis, zsum


def rebin_piecewise_constant(x1, y1, x2):
    """Rebin histogram values y1 from old bin edges x1 to new edges x2.

    Code taken from: https://github.com/jhykes/rebin/blob/master/rebin.py

    It follows the procedure described in Figure 18.13 (chapter 18.IV.B.
    Spectrum Alignment, page 703) of Knoll [1]

    References
    ----------
    [1] Glenn Knoll, Radiation Detection and Measurement, third edition,
        Wiley, 2000.

    Parameters
    ----------
     - x1 : m+1 array of old bin edges.
     - y1 : m array of old histogram values.
            This is the total number in each bin, not an average.
     - x2 : n+1 array of new bin edges.

    Returns
    -------
     - y2 : n array of rebinned histogram values.
    """
    x1 = np.asarray(x1)
    y1 = np.asarray(y1)
    x2 = np.asarray(x2)

    # the fractional bin locations of the new bins in the old bins
    i_place = np.interp(x2, x1, np.arange(len(x1)))

    cum_sum = np.r_[[0], np.cumsum(y1)]

    # calculate bins where lower and upper bin edges span
    # greater than or equal to one original bin.
    # This is the contribution from the 'intact' bins (not including the
    # fractional start and end parts.
    whole_bins = np.floor(i_place[1:]) - np.ceil(i_place[:-1]) >= 1.
    start = cum_sum[np.ceil(i_place[:-1]).astype(int)]
    finish = cum_sum[np.floor(i_place[1:]).astype(int)]

    y2 = np.where(whole_bins, finish - start, 0.)

    bin_loc = np.clip(np.floor(i_place).astype(int), 0, len(y1) - 1)

    # fractional contribution for bins where the new bin edges are in the same
    # original bin.
    same_cell = np.floor(i_place[1:]) == np.floor(i_place[:-1])
    frac = i_place[1:] - i_place[:-1]
    contrib = (frac * y1[bin_loc[:-1]])
    y2 += np.where(same_cell, contrib, 0.)

    # fractional contribution for bins where the left and right bin edges are in
    # different original bins.
    different_cell = np.floor(i_place[1:]) > np.floor(i_place[:-1])
    frac_left = np.ceil(i_place[:-1]) - i_place[:-1]
    contrib = (frac_left * y1[bin_loc[:-1]])

    frac_right = i_place[1:] - np.floor(i_place[1:])
    contrib += (frac_right * y1[bin_loc[1:]])

    y2 += np.where(different_cell, contrib, 0.)

    return y2


def reject_outliers(data, m=2.0, return_mask=False):
    """Reject outliers

    Modified from: https://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.0)
    mask = s < m
    if return_mask:
        return data[mask], mask
    else:
        return data[mask]


if __name__ == '__main__':
    pass

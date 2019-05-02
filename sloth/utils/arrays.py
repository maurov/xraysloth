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
    zsum = np.zeros_like(axis)
    for xdat, zdat in zip(xdats, zdats):
        fdat = interp1d(xdat, zdat)
        zsum += fdat(axis)
    return axis, zsum


if __name__ == '__main__':
    pass

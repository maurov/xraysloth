#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Deglitch utilities
=====================

"""
import numpy as np

HAS_PANDAS = False
try:
    import pandas as pd
    HAS_PANDAS = True
except:
    pass

def remove_spikes(x, y, window=3, threshold=3):
    """remove spikes using pandas

    .. note:: this will not work in pandas > 0.17 one could simply do
              `df.rolling(3, center=True).median()`; also
              df.as_matrix() is deprecated, use df.values instead

    Parameters
    ==========

    x, y : data arrays

    window : int, [3]
             window in rolling
    
    threshold : int, [3]
                number of sigma

    Return
    ======

    ynew : array like x/y

    """
    ynew = np.zeros_like(y)
    if (not HAS_PANDAS):
        print('ERROR: pandas not found (required for this function)')
        return ynew
    df = pd.DataFrame(y)
    try:
        yf = pd.rolling_median(df, window=3, center=True).fillna(method='bfill').fillna(method='ffill')
        diff = yf.as_matrix()-y
        mean = diff.mean()
        sigma = (y - mean)**2
        sigma = np.sqrt(sigma.sum()/float(len(sigma)))
        ynew = np.where(abs(diff) > threshold * sigma, yf.as_matrix(), y)
    except:
        yf = df.rolling(window, center=True).median().fillna(method='bfill').fillna(method='ffill')
        ynew = np.array(yf.values).reshape(len(x))
    return ynew

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

def remove_spikes(x, y, threshold=3):
    """remove spikes using pandas

    .. note:: this will not work in pandas > 0.17 one could simply do
              `df.rolling(3, center=True).median()`; also
              df.as_matrix() is deprecated, use df.values instead

    Parameters
    ==========

    x, y : data arrays

    threshold : int [3]
                number of sigma

    Return
    ======

    ynew : array like x/y

    """
    if (not HAS_PANDAS):
        return np.zeros_like(y)
    df = pd.DataFrame(y)
    df['filtered'] = rolling_median(df, window=3, center=True).fillna(method='bfill').fillna(method='ffill')
    diff = df['filtered'].as_matrix()-y
    mean = diff.mean()
    sigma = (y - mean)**2
    sigma = np.sqrt(sigma.sum()/float(len(sigma)))
    ynew = np.where(abs(diff) > threshold * sigma, df['filtered'].as_matrix(), y)	
    return ynew

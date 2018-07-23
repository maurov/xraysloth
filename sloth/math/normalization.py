#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Normalization schemes
========================

"""
import numpy as np

def norm1D(y, norm=None, **kws):
    """collection of simple normalization methods

    Parameters
    ==========
    y : array of float, to normalize
    norm : string, available options
           "max"     -> y / np.max(y)
           "max-min" -> (y - np.min(y)) / (np.max(y) - np.min(y))
           "area"    -> (y - np.min(y)) / np.trapz(y, x=kws.get('x'))
           "sum"     ->  (y - np.min(y)) / np.sum(y)
           "larch"   -> TODO!!!

    Returns
    =======
    ynorm : array of float

    """
    if norm == "max":
        return y / np.max(y)
    elif norm == "max-min":
        return (y - np.min(y)) / (np.max(y) - np.min(y))
    elif norm == "area":
        try:
            return (y - np.min(y)) / np.trapz(y, x=kws.get('x'))
        except:
            return (y - np.min(y)) / np.trapz(y)
    elif norm == "sum":
        return (y - np.min(y)) / np.sum(y)
    elif norm == "larch":
        print("TODO!")
        return y
        # try:
        #     d = DataGroupXanes()
        #     d.gs.append(Group(_larch=d._larch))
        #     d.gs[-1].x = kws.get('x')
        #     d.gs[-1].y = y
        #     d.norxafs(d.gs[-1], xattr='x', yattr='y', outattr='flat', **kws)
        #     return d.gs[-1].flat
        # except:
        #     print('ERROR: Larch normalization failed')
        #     return y
    else:
        print("WARNING: normalization method not known")
        return y

if __name__ == '__main__':
    pass

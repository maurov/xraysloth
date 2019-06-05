#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities related to Matplotlib
-------------------------------
"""
import numpy as np

##############
# Matplotlib #
##############


def mplSetPubFont(size=8, usetex=True):
    """very basic mpl set font for publication-quality figures"""
    from matplotlib import rc
    rc('font', **{'family': 'sans-serif',
                  'sans-serif': ['Helvetica'],
                  'size': size})
    rc('text', usetex=usetex)


def get_colors(nlevels, colormap=None):
    """get a given number of colors from a colormap"""
    if colormap is None:
        from matplotlib.pyplot import cm
        colormap = cm.rainbow
    return colormap(np.linspace(0, 1, nlevels))

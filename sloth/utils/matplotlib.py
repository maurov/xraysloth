#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities related to Matplotlib
-------------------------------
"""

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

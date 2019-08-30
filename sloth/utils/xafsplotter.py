#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Matplotlib plotter for XAFS data
=======================================

This utility is a pure matplotlib visualizer/plotter (no interaction!, no
widgets) for XAFS (x-ray absorption fine structure) data. It is intended to be
used in Jupyter notebooks with Larch.

"""
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt
from sloth.utils.logging import getLogger

class XAFSPlotter(object):

    #: default colors palette
    _colors = cycle(['#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78',
                     '#2CA02C', '#98DF8A', '#D62728', '#FF9896',
                     '#9467BD', '#C5B0D5', '#8C564B', '#C49C94',
                     '#E377C2', '#F7B6D2', '#7F7F7F', '#C7C7C7',
                     '#BCBD22', '#DBDB8D', '#17BECF', '#9EDAE5'])

    #: default plot labels
    _labels = dict(k=r'$k \rm\,(\AA^{-1})$',
                   r=r'$R \rm\,(\AA)$',
                   energy=r'$E\rm\,(eV)$',
                   mu=r'$\mu(E)$',
                   norm=r'normalized $\mu(E)$',
                   flat=r'flattened $\mu(E)$',
                   deconv=r'deconvolved $\mu(E)$',
                   dmude=r'$d\mu(E)/dE$',
                   dnormde=r'$d\mu_{\rm norm}(E)/dE$',
                   chie=r'$\chi(E)$',
                   chikw=r'$k^{{{0:g}}}\chi(k) \rm\,(\AA^{{-{0:g}}})$',
                   chir=r'$\chi(R) \rm\,(\AA^{{-{0:g}}})$',
                   chirmag=r'$|\chi(R)| \rm\,(\AA^{{-{0:g}}})$',
                   chirre=r'${{\rm Re}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                   chirim=r'${{\rm Im}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                   chirpha=r'${{\rm Phase}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                   e0color='#B2B282',
                   chirlab=None)

    def __init__(self, data_group=None, name='XAFSplotter',
                 dpi=150, figsize=(10, 10), ncols=1, nrows=1, title=None,
                 logger=None):

        self._name = name
        self._logger = logger or getLogger(self._name)

        #: figure/axes parameters
        self._dpi = dpi
        self._figsize = figsize
        self._ncols = ncols
        self._nrows = nrows

        self._data = data_group

        self._fig, _axs = plt.subplots(num=self._name,
                                       ncols=self._ncols,
                                       nrows=self._nrows,
                                       dpi=self._dpi,
                                       figsize=self._figsize)

        #: reshape Axes as list
        self._nplots = self._nrows*self._ncols
        self._axs = np.array(_axs).reshape(self._nplots)
        self._initPlotsTitle(title)

    def _getNewColor(self):
        return next(self._colors)

    def _initPlotsTitle(self, title=None):
        """init title for all subplots"""
        if title is None:
            self._ptitles = ['win={0}'.format(i) for i in range(self._nplots)]
        else:
            assert type(title) is list, 'title should be a list'
            assert len(title) == self._nplots, 'title length should correspond to number of plot windows'
            self._ptitles = title
        for iax, ax in enumerate(self._axs):
            ax.set_title(self._ptitles[iax])

    def getAxis(self, win):
        """get the matplotlib.axes._subplots.AxesSubplot at given index"""
        try:
            return self._axs[win]
        except IndexError:
            self._logger.error('Wrong plot index')
            return None

    def plot(self, x, y, label=None, win=0, color=None, side='left', **kws):
        """plot in given axis"""
        ax = self.getAxis(win)
        if color is None:
            color = self._getNewColor()
        if side == 'right':
            ax = ax.twinx()
        ax.plot(x, y, label=label, color=color)
        self._fig.tight_layout()

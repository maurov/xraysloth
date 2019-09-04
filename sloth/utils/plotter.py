#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Matplotlib plotter
==================

This utility is a pure matplotlib visualizer/plotter (no interaction!, no
widgets). It is intended to be used in Jupyter notebooks (%inline or %notebook).

"""
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sloth.utils.logging import getLogger


class Plotter(object):

    #: default colors palette
    _colors = cycle(['#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78',
                     '#2CA02C', '#98DF8A', '#D62728', '#FF9896',
                     '#9467BD', '#C5B0D5', '#8C564B', '#C49C94',
                     '#E377C2', '#F7B6D2', '#7F7F7F', '#C7C7C7',
                     '#BCBD22', '#DBDB8D', '#17BECF', '#9EDAE5'])

    #: default plot labels
    _labels = dict(x='X',
                   y='Y')

    def __init__(self, name='plotter',
                 dpi=150, figsize=(10, 10),
                 ncols=1, nrows=1,
                 font_size=6,
                 axes_linewidth=0.5,
                 lines_linewidth=1.5,
                 title=None, titles=None,
                 logger=None):
        """Logger Constructor

        Parameters
        ----------

        name : str
            name of the figure ['plotter']
        dpi : int
            figure dpi [150]
        figsize : tuple
            sigure size [(10, 10)]
        font_size : int
            base font size [6]
        axes_linewidth : float
            base axes width [0.5]
        lines_linewidth : float
            base lines width [1.5]
        title : None or str
            figure main title [None -> use self._name]
        titles : None or list
            list of titles for the subplots [None -> 'win=#']
        """

        #: general
        self._name = name
        self._logger = logger or getLogger(self._name)
        self._title = title or self._name
        self._titles = titles

        #: matplotlib rcParams
        self._text_usetex = False
        self._font_size = font_size
        self._axes_linewidth = axes_linewidth
        self._lines_linewidth = lines_linewidth

        #: figure/axes parameters
        self._dpi = dpi
        self._figsize = figsize
        self._ncols = ncols
        self._nrows = nrows
        self._nplots = self._nrows*self._ncols

        self._initRcParams()
        self._initPlots()

    def _initRcParams(self, style='seaborn-ticks'):
        """init default Matplotlib parameters"""
        plt.style.use(style)
        rcParams['text.usetex'] = self._text_usetex
        rcParams['font.size'] = self._font_size
        rcParams['axes.titlesize'] = 'large'
        rcParams['axes.linewidth'] = self._axes_linewidth
        rcParams['xtick.major.width'] = self._axes_linewidth
        rcParams['ytick.major.width'] = self._axes_linewidth/2.
        rcParams['figure.dpi'] = self._dpi
        rcParams['figure.figsize'] = self._figsize
        rcParams['grid.alpha'] = 0.5
        rcParams['lines.linewidth'] = self._lines_linewidth

    def _initPlots(self, sharex=False, sharey=False):
        """instantiate figure and subplots"""
        plt.close(self._name)
        self._fig, _axs = plt.subplots(num=self._name,
                                       ncols=self._ncols,
                                       nrows=self._nrows,
                                       dpi=self._dpi,
                                       figsize=self._figsize,
                                       sharex=sharex,
                                       sharey=sharey)
        #: reshape Axes as list
        self._axs = np.array(_axs).reshape(self._nplots)
        # self._axs2 = np.full_like(self._axs, None)
        self._fig.suptitle(f"Fig: {self._title}", fontsize=self._font_size+4)
        self._initPlotsTitle(self._titles)

    def _initPlotsTitle(self, titles=None):
        """init title for all subplots"""
        if titles is None:
            self._titles = ['win={0}'.format(i) for i in range(self._nplots)]
        else:
            assert type(titles) is list, 'titles should be a list'
            assert len(titles) == self._nplots, 'titles length should correspond to number of plot windows'
            self._titles = titles
        for iax, ax in enumerate(self._axs):
            ax.set_title(self._titles[iax])

    def _getNewColor(self):
        return next(self._colors)

    def getAxis(self, win):
        """get the matplotlib.axes._subplots.AxesSubplot at given index"""
        try:
            return self._axs[win]
        except IndexError:
            self._logger.error('Wrong plot index')
            return None

    def subplots_adjust(self, **kws):
        return self._fig.subplots_adjust(**kws)

    def plot(self, x, y, label=None, win=0, color=None,
             side='left', show_legend=None,
             **kws):
        """plot in given axis

        Parameters
        ==========
        x, y : arrays to plot
        label : str
            label for the legend [None]
        win : int
            index of self._axs (subplot to use for plot) [0]
        color : str
            line color [cycle(self._colors)]
        side : str
            ['left']
            'right' -> sharex
            'top' -> sharey
        show_legend : None or dict
            if given, it should be a dictonary of parmeters for ax.legend()
        """
        ax = self.getAxis(win)
        if color is None:
            color = self._getNewColor()
        if side == 'right':
            ax = ax.twinx()
            # np.append(self._axs, ax)
        if side == 'top':
            raise NotImplementedError()
        ax.plot(x, y, label=label, color=color)
        if show_legend is not None:
            assert type(show_legend) is dict, 'show_legend: None or dict'
            ax.legend(**show_legend)
        self._fig.tight_layout()

    def legend(self, win=0,
               loc='center right',
               bbox_to_anchor=(0.95, 0.4),
               borderaxespad=0.1,
               title='Legend',
               frameon=True,
               fancybox=True):
        """add a common figure legend"""
        handlers, labels = [], []
        for ax in self._axs:
            _handlers, _labels = ax.get_legend_handles_labels()
            handlers.extend(_handlers)
            labels.extend(_labels)
        self._fig.legend(handlers,
                         labels,
                         loc=loc,
                         bbox_to_anchor=bbox_to_anchor,
                         borderaxespad=borderaxespad,
                         title=title,
                         frameon=frameon,
                         fancybox=fancybox)
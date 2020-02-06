#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Matplotlib (inline) plotter
===========================

This utility is a pure matplotlib visualizer/plotter (no interaction!, no
widgets). It is intended to be used in Jupyter notebooks (%inline or %notebook).

"""
from itertools import cycle
from copy import deepcopy
from os import path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sloth.utils.logging import getLogger


class Plotter(object):

    #: default colors palette
    _DEFAULT_COLORS = (
        "#1F77B4",
        "#AEC7E8",
        "#FF7F0E",
        "#FFBB78",
        "#2CA02C",
        "#98DF8A",
        "#D62728",
        "#FF9896",
        "#9467BD",
        "#C5B0D5",
        "#8C564B",
        "#C49C94",
        "#E377C2",
        "#F7B6D2",
        "#7F7F7F",
        "#C7C7C7",
        "#BCBD22",
        "#DBDB8D",
        "#17BECF",
        "#9EDAE5",
    )

    #: default plot labels
    _labels = dict(x="X", y="Y")

    def __init__(
        self,
        name="plotter",
        dpi=150,
        figsize=(10, 10),
        ncols=1,
        nrows=1,
        fontsize=6,
        axes_linewidth=1,
        lines_linewidth=1.5,
        style="seaborn-paper",
        usetex=False,
        title=None,
        titles=None,
        logger=None,
        outdir=None,
    ):
        """Logger Constructor

        Parameters
        ----------

        name : str
            name of the figure ['plotter']
        dpi : int
            figure dpi [150]
        figsize : tuple
            sigure size [(10, 10)]
        fontsize : int
            base font size [6]
        axes_linewidth : float
            base axes width [0.5]
        lines_linewidth : float
            base lines width [1.5]
        style : str
            https://matplotlib.org/gallery/style_sheets/style_sheets_reference.html
        usetex : bool
            use TeX
        title : None or str
            figure main title [None -> use self._name]
        titles : None or list
            list of titles for the subplots [None -> 'win=#']
        logger : instance of getLogger
        outdir : str
            path for saving figures [None]
        """

        #: general
        self._name = name
        self._logger = logger or getLogger(self._name)
        self._title = title or self._name
        self._suptitle = title or f"Fig: {self._title}"
        self._titles = titles

        #: matplotlib rcParams
        self._usetex = usetex
        self._fontsize = fontsize
        self._axes_linewidth = axes_linewidth
        self._lines_linewidth = lines_linewidth
        self._style = style

        #: figure/axes parameters
        self._dpi = dpi
        self._figsize = figsize
        self._ncols = ncols
        self._nrows = nrows
        self._nplots = self._nrows * self._ncols

        #: input/output
        self._outdir = outdir

        self.set_style(self._style)
        self._init_matplotlib()
        self._init_subplots()

    def _init_matplotlib(self, **kws):
        """init default Matplotlib parameters"""
        plt.ion()
        self._rc = {
            "text.usetex": self._usetex,
            "figure.dpi": self._dpi,
            "figure.figsize": self._figsize,
            "font.size": self._fontsize,
            "axes.titlesize": "medium",
            "axes.linewidth": self._axes_linewidth,
            "xtick.major.width": self._axes_linewidth,
            "ytick.major.width": self._axes_linewidth,
            "lines.linewidth": self._lines_linewidth,
            "grid.alpha": 0.5,
        }
        rcParams.update(self._rc)
        self._rc = deepcopy(rcParams)

    def set_style(self, style=None):
        """Set matplotlib style (reset to default if not given)"""
        plt.rcdefaults()
        if style is not None:
            plt.style.use(style)

    def _update_matplotlib(self, rcpars):
        """Update matplotlib base settings

        Parameters
        ----------
        rcpars : dict
            dictionary to update matplotlib.rcParams
        """
        self._init_matplotlib()  #: first reset to defaults
        if rcpars is not None:
            assert type(rcpars) is dict, "'rcpars' should be a dictionary"
            rcParams.update(rcpars)
        #: store updated parameters
        self._rc = deepcopy(rcParams)

    def _init_subplots(self, sharex=False, sharey=False):
        """instantiate figure and subplots"""
        plt.close(self._name)
        self._fig, _axs = plt.subplots(
            num=self._name,
            ncols=self._ncols,
            nrows=self._nrows,
            dpi=self._dpi,
            figsize=self._figsize,
            sharex=sharex,
            sharey=sharey,
        )
        #: reshape Axes as list
        self._axs = np.array(_axs).reshape(self._nplots)
        # self._axs2 = np.full_like(self._axs, None)
        self._fig.suptitle(self._suptitle, fontsize=self._fontsize + 4)
        self._initPlotsTitle(self._titles)

    def _initPlotsTitle(self, titles=None):
        """init title for all subplots"""
        if titles is None:
            self._titles = ["win={0}".format(i) for i in range(self._nplots)]
        else:
            assert type(titles) is list, "titles should be a list"
            assert (
                len(titles) == self._nplots
            ), "titles length should correspond to number of plot windows"
            self._titles = titles
        for iax, ax in enumerate(self._axs):
            ax.set_title(self._titles[iax])

    def _initColors(self):
        self._colors = cycle(self._DEFAULT_COLORS)

    def _getNextColor(self):
        return next(self._colors)

    def getAxis(self, win):
        """get the matplotlib.axes._subplots.AxesSubplot at given index"""
        try:
            return self._axs[win]
        except IndexError:
            self._logger.error("Wrong plot index")
            return None

    def subplots_adjust(self, **kws):
        return self._fig.subplots_adjust(**kws)

    def newplot(self, *args, **kwargs):
        """Plot command with forced replace=True"""
        _ = kwargs.pop("replace", True)
        return self.plot(*args, replace=True, **kwargs)

    def plot(
        self,
        x,
        y,
        label=None,
        win=0,
        color=None,
        side="left",
        show_legend=None,
        replace=False,
        xscale="linear",
        yscale="linear",
        xlabel=None,
        ylabel=None,
        xlim=None,
        ylim=None,
        **plotkws,
    ):
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
        **plotkws
            keyword arguments for ax.plot()
        replace : bool
            if True, forces axis update
        xscale, yscale : str
            "linear", "log", "symlog", "logit", ...
            The axis scale type to apply. -> https://matplotlib.org/api/axes_api.html
        xlabel, ylabel : str
            x, y labels
        xlim, ylim: tuples
            tuple for x, y limits [(None, None)]
        """
        ax = self.getAxis(win)
        #: override axis settings
        if replace:
            ax.set_xscale(xscale)
            ax.set_yscale(yscale)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            if xlim is not None:
                ax.set_xlim(xlim)
            if ylim is not None:
                ax.set_ylim(ylim)

        if color is None:
            color = self._getNextColor()

        if side == "right":
            ax = ax.twinx()
            # np.append(self._axs, ax)
        if side == "top":
            raise NotImplementedError()

        #: main wrapped method
        ax.plot(x, y, label=label, color=color, **plotkws)

        if show_legend is not None:
            assert type(show_legend) is dict, "show_legend: None or dict"
            ax.legend(**show_legend)

        if replace:
            self._fig.tight_layout()

    def legend(
        self,
        win=0,
        loc="upper right",
        bbox_to_anchor=(1.3, 0.95),
        borderaxespad=0.1,
        title="Legend",
        frameon=True,
        fancybox=True,
    ):
        """add a common figure legend"""
        handlers, labels = [], []
        for ax in self._axs:
            _handlers, _labels = ax.get_legend_handles_labels()
            handlers.extend(_handlers)
            labels.extend(_labels)
        self._fig.legend(
            handlers,
            labels,
            loc=loc,
            bbox_to_anchor=bbox_to_anchor,
            borderaxespad=borderaxespad,
            title=title,
            frameon=frameon,
            fancybox=fancybox,
        )

    def savefig(self, fig_out=None, dpi_out=300):
        """Save figure to .pdf/.png/.svg files"""
        if fig_out is None:
            return None
        if self._outdir is not None:
            fig_out = path.join(self._outdir, fig_out)
        self._fig.savefig("{0}.pdf".format(fig_out), dpi=dpi_out, bbox_inches="tight")
        self._fig.savefig("{0}.png".format(fig_out), dpi=dpi_out, bbox_inches="tight")
        self._fig.savefig("{0}.svg".format(fig_out), dpi=dpi_out, bbox_inches="tight")
        self._logger.info("Saved figures .pdf/.png/.svg figures to: %s", fig_out)


if __name__ == "__main__":
    pass

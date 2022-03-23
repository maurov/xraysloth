#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DataGroupXes: work with XES data sets
========================================

- DataGroup
  - DataGroup1D
    - DataGroupXes
"""
import numpy as np
from datetime import datetime
from larch import Group
from .datagroup import MODNAME, HAS_PYMCA
from .datagroup1D import DataGroup1D

class DataGroupXes(DataGroup1D):
    """DataGroup for XES scans"""
    def __init__(self, kwsd=None, _larch=None):
        super(DataGroupXes, self).__init__(kwsd=kwsd, _larch=_larch)

    def mkiads(self, ref=0, plot=False, **kws):
        """IAD analysis for XES

        Keyword arguments
        -----------------
        ref : reference spectrum (in gs list)
        plot : to show the results in a plot

        Returns
        -------
        None -- output written to 'iads' group
        """
        _debug =  kws.get('DEBUG', False)
        self.iads = Group()
        self.iads.__name__ = 'IAD analysis'
        self.iads.header = [self.iads.__name__,
                            'Saved on {0}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        self.iads.id = []
        self.iads.lab = []
        self.iads.area = []
        self.iads.max = []
        if not (hasattr(self.gs[ref], 'xnew') or hasattr(self.gs[ref], 'ynew')):
            raise AttributeError("First interpolate the data with 'mkinterpxy()'!")
        for _n, _g in enumerate(self.gs):
            yda = self.norint(_g.ynew, x=_g.xnew) - self.norint(self.gs[ref].ynew, x=self.gs[ref].xnew)
            ydm = self.normax(_g.ynew) - self.normax(self.gs[ref].ynew)
            iad_area = np.trapz(np.abs(yda), x=_g.xnew)
            iad_max = np.trapz(np.abs(ydm), x=_g.xnew)
            if _debug:
                try:
                    setattr(_g, 'iad_area', iad_area)
                    setattr(_g, 'iad_max', iad_max)
                    print('DEBUG: {0}: area {1}\t max {2}'.format(_n, iad_area, iad_max))
                    setattr(_g, 'iad_yda', yda)
                    setattr(_g, 'iad_ydm', ydm)
                except AttributeError:
                    pass
            self.iads.id.append(_n)
            self.iads.lab.append(_g.label)
            self.iads.area.append(iad_area)
            self.iads.max.append(iad_max)
        if _debug:
            print("DEBUG: written attributes 'iad_yda' and 'iad_ydm' for fine check")
        if plot:
            self.plotiads()

    def plotiads(self, order=None, xlist=None, **kws):
        """custom plot for IAD analysis"""
        # as in self.plotxy()
        replace = kws.get('replace', True)
        win = kws.get('win', 2)
        show_legend = kws.get('show_legend', self.kwsd['plot']['show_legend'])
        legend_loc = kws.get('legend_loc', self.kwsd['plot']['legend_loc'])
        xlabel = kws.get('xlabel', 'index')
        ylabel = kws.get('ylabel', 'IAD_area (arb. units)')
        title = kws.get('title', 'IAD analysis')
        xmin = kws.get('xmin', None)
        xmax = kws.get('xmax', None)
        ymin = kws.get('ymin', None)
        ymax = kws.get('ymax', None)
        # specific self.plotiads()
        show_labs =  kws.get('show_labs', True)
        labs_rot = kws.get('labs_rot', 45)
        labs_xoff = kws.get('labs_xoff', 0)
        labs_yoff = kws.get('labs_yoff', 0)
        labs_ha = kws.get('labs_ha', 'center')
        labs_va = kws.get('labs_va', 'center')
        
        if xlist is None:
            xlist = self.iads.id

        if order:
            _ids = []
            _iads = []
            _labs = []
            for _id in order:
                _ids.append(xlist[_id])
                _iads.append(self.iads.area[_id])
                _labs.append(self.iads.lab[_id])
        else:
            _ids = xlist
            _iads = self.iads.area
            _labs = self.iads.lab

        if self._inlarch:
            # plot with Larch
            from larch.wxlib.plotter import _scatterplot, _plot_text
            _scatterplot(_ids, _iads, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                         xlabel=xlabel, ylabel=ylabel,
                         win=win, new=replace, _larch=self._larch)
            if show_labs:
                for _lab, _x, _y in zip(_labs, _ids, _iads):
                    _plot_text(_lab, _x+labs_xoff, _y+labs_yoff, win=win, rotation=labs_rot,
                               ha=labs_ha, va=labs_va, _larch=self._larch)
        elif HAS_PYMCA:
            # plot with PyMca
            if not hasattr(self, 'pw'):
                from PyMca5 import ScanWindow
                self.pw = ScanWindow.ScanWindow()
                self.pw.setGraphTitle(title)
                try:
                    self.pw.setGraphXLabel(xlabel)
                except:
                    self.pw.setGraphXTitle(xlabel)
                try:
                    self.pw.setGraphYLabel(ylabel)
                except:    
                    self.pw.setGraphYTitle(ylabel)
                if (xmin and xmax):
                    self.pw.setGraphXLimits(xmin, xmax)
                if (ymin and ymax):
                    self.pw.setGraphYLimits(ymin, ymax)
                # geometry good for >1280x800 resolution
                self.pw.setGeometry(50, 50, 700, 700)
                self.pw._plotPoints = True
                self.pw.showGrid()
                self.pw.show()
            x = np.array(_ids)
            y = np.array(_iads)
            self.pw.addCurve(x, y, legend='IADs', replace=True)
        else:
            print('plotting with matplotlib not implemented yet. do it yourself!')

        
### LARCH ###
def datagroup_xes(kwsd=None, _larch=None):
    """utility to perform wrapped operations on a list of XES data
    groups"""
    return DataGroupXes(kwsd=kwsd, _larch=_larch)

def registerLarchPlugin():
    return (MODNAME, {'datagroup_xes' : datagroup_xes})

if __name__ == '__main__':
    pass

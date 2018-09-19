#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DataGroup1D: work with 1D data sets (line scans)
===================================================

"""
### IMPORTS ###
import os, sys
import numpy as np
from datetime import datetime

# Larch
HAS_LARCH = False
try:
    import larch
    from larch import use_plugin_path, Group
    # Larch Plugins
    use_plugin_path('io')
    from columnfile import _read_ascii
    from larch_plugins.io import write_ascii
    use_plugin_path('wx')
    from plotter import _plot, _scatterplot, _plot_text
    use_plugin_path('math')
    from mathutils import _interp
    from fitpeak import fit_peak
    use_plugin_path('xafs')
    from xafsft import xftf, xftr, xftf_prep, xftf_fast, xftr_fast, ftwindow
    from pre_edge import pre_edge
    HAS_LARCH = True
except ImportError:
    pass
    
from ..io.specfile_reader import _str2rng as str2rng
from ..io.specfile_reader import spec_getmap2group, spec_getmrg2group
from .datagroup import DataGroup, _norm, MODNAME

# PyMca
HAS_PYMCA = False
try:
    from PyMca5.PyMcaGui import ScanWindow
    HAS_PYMCA = True
except ImportError:
    try:
        from PyMca import ScanWindow
        HAS_PYMCA = True
    except ImportError:
        pass

# DEBUG
if 'DEBUG' in globals():
    pass
else:
    DEBUG = False

class DataGroup1D(DataGroup):
    """1D version of DataGroup"""
    
    def __init__(self, kwsd=None, _larch=None):
        super(DataGroup1D, self).__init__(kwsd=kwsd, _larch=_larch)

    def read_ascii(self, fname, labels=None, sort=False, sort_column=0):
        """see 'read_ascii' in Larch"""
        return _read_ascii(fname, labels=labels,
                           sort=sort, sort_column=sort_column,
                           _larch=self._larch)

    def write_ascii_xy(self, fname, g, xattr='x', yattr='y', label=None):
        """write a two-columns ascii file

        Parameters
        ==========

        fname : str
                output file name

        xattr, yattr: str
                      attributes to use as X/Y columns to write
        """
        _x = getattr(self.gs[g], xattr)
        _y = getattr(self.gs[g], yattr)
        if label is None:
            try:
                _lab = self.gs[g].label
            except:
                _lab = 'Unknown'
        return write_ascii(fname, _x, _y, label=_lab, _larch=self._larch)
        

    def getxy(self, fname, xattr='x', yattr='y', scanlab=None, **kws):
        """load two colums ascii data """
        g = _read_ascii(fname, labels='{0} {1}'.format(xattr, yattr),
                        _larch=self._larch)
        g.norint = self.norint(getattr(g, yattr))#, x=getattr(g, xattr))
        g.normax = self.normax(getattr(g, yattr))
        g.label = str(scanlab)
        return g

    def getspecscan(self, fname, scans, scanlab=None, **kws):
        """load two colums data from SPEC file"""
        cntx = kws.get('cntx', self.kwsd['spec']['cntx'])
        cnty = kws.get('cnty', self.kwsd['spec']['cnty'])
        csig = kws.get('csig', self.kwsd['spec']['csig'])
        cmon = kws.get('cmon', self.kwsd['spec']['cmon'])
        csec = kws.get('csec', self.kwsd['spec']['csec'])
        norm = kws.get('norm', self.kwsd['spec']['norm'])
        action = kws.get('action', self.kwsd['spec']['action'])
        g = spec_getmrg2group(fname,
                              scans=scans,
                              cntx=cntx,
                              csig=csig,
                              cmon=cmon,
                              csec=csec,
                              norm=norm,
                              action=action,
                              _larch=self._larch)
        g.label = str(scanlab)
        return g

    def getcom(self, g, xattr='x', yattr='y'):
        """center of mass (com) for the given group and x,w attributes"""
        return np.average(getattr(self.gs[g], xattr), weights=getattr(self.gs[g], yattr))

    def norint(self, y, x=None):
        """simple normalization by area"""
        return _norm(y, norm="area", x=x)
        
    def normax(self, y):
        """simple normalization by maximum minus offset"""
        return _norm(y, norm="max-min")

    def norxafs(self, g, xattr='x', yattr='y', outattr=None, **kws):
        """XAFS normalization on a given group (g)

        Keyword arguments
        -----------------
        xattr : ['x'] attribute for the energy array
        yattr : ['y'] attribute for the mu array
        outattr : ['flat'] attribute for output normalize array
        
        **kws : [''self.kwsd[pre_edge][*]''] as in pre_edge()
        """
        e0 = kws.get('e0', self.kwsd['pre_edge']['e0'])
        pre1 = kws.get('pre1', self.kwsd['pre_edge']['pre1'])
        pre2 = kws.get('pre2', self.kwsd['pre_edge']['pre2'])
        norm1 = kws.get('norm1', self.kwsd['pre_edge']['norm1'])
        norm2 = kws.get('norm2', self.kwsd['pre_edge']['norm2'])
        nvict = kws.get('nvict', self.kwsd['pre_edge']['nvict'])
        nnorm = kws.get('nnorm', self.kwsd['pre_edge']['nnorm'])
        pre_edge(getattr(g, xattr), getattr(g, yattr), group=g,
                 nnorm=nnorm, nvict=nvict, pre1=pre1, pre2=pre2,
                 norm1=norm1, norm2=norm2, _larch=self._larch)
        if outattr == 'flat':
            return g.flat
        elif outattr == 'norm':
            return g.norm

    def xcalib(self, g, ref=0, method='com', set_attr=False):
        """find the x-shift to calibrate two spectra

        Keyword arguments
        -----------------
        g : spectrum to shift (index in datagroup)
        ref : reference spectrum (in datagroup)
        method : the method to perform this task
                 'com' -> overlap the center of mass
        set_attr : [False] write 'xcalib' attr for the calibrated group

        """
        if method == 'com':
            xmin = max(min(self.gs[g].x), min(self.gs[ref].x))
            xmax = min(max(self.gs[g].x), max(self.gs[ref].x))
            self.mkinterpxy(xmin=xmin, xmax=xmax)
            cmdiff = self.getcom(ref, xattr='xnew', yattr='ynew') - self.getcom(g, xattr='xnew', yattr='ynew')
            self.gs[g].x = self.gs[g].x + cmdiff
            print('{0}.x shifted by {1}'.format(self.gs[g].label, cmdiff))
            if set_attr:
                self.gs[g].xcalib = cmdiff
        else:
            pass

    def xshift(self, g, xshift, xattr='x'):
        """simply apply the shift to group g"""
        _x = getattr(self.gs[g], xattr)
        setattr(self.gs[g], xattr, _x + xshift)

    def mkinterpxy(self, ref=0, sel='*', **kws):
        """interpolate (xattr, yattr) to (xnew, ynew) on a selected list of
        groups (sel); xnew is taken from the reference group or as
        linear space -- xnew = np.linspace(xmin, xmax,
        (xmax-xmin)/xstep) -- if xmin,xmax,xstep are given as input

        Keyword arguments
        -----------------
        ref : reference group [0]
        sel : list of groups to interpolate ['*']
        xmin, xmax, xstep : extracted from ref group if not given
        kind : type of interpolation method

        Returns
        -------
        None -- output written to attributes: 'xnew', 'ynew'

        """
        xattr = kws.get('xattr', 'x')
        yattr = kws.get('yattr', 'y')
        xref = self.get(xattr, sel=[ref])[0]
        yref = self.get(yattr, sel=[ref])[0]
        xmin = kws.get('xmin', None)
        xmax = kws.get('xmax', None)
        xstep = kws.get('xstep', None)
        kind =  kws.get('kind', self.kwsd['interp']['kind'])
        if (xmin is None) or (xmax is None) or (xstep is None):
            xnew = xref
        else:
            if (xmin is None):
                xmin = xref.min()
            if (xmax is None):
                xmax = xref.max()
            if (xstep is None):
                xstep = min(np.diff(xref))
            xnew = np.linspace(xmin, xmax, (xmax-xmin)/xstep)
        if DEBUG:
            print('DEBUG: {0} interp, {1} to {2}, {3} xstep = {4} points'.format(kind, xmin, xmax, xstep, len(xnew)))
        self.selector(sel)
        for _n, _g in enumerate(self.gs_sel):
            try:
                setattr(_g, 'xnew', xnew)
                setattr(_g, 'ynew', _interp(getattr(_g, xattr), getattr(_g, yattr), xnew, kind=kind))
                if DEBUG:
                    print('DEBUG: group {0} interpolated'.format(_n))
            except AttributeError:
                pass

    def mksum(self, sel, **kws):
        """make a new group as sum of selected groups
        
        Keyword arguments
        -----------------
        sel : an ordered list of selected groups
              sel[0] is the reference for the interpolation
        xattr : attribute for x-axis ['x']
        yattr : attribute for y-axis ['y']
        label : the label for the new sum group ['sum_sel_indx']

        Returns
        -------
        None -- output written to given attributes: 'xattr', 'yattr'
                of a new group in datagroup
        """
        iref = sel[0]
        xattr = kws.get('xattr', 'x')
        yattr = kws.get('yattr', 'y')
        xref = self.get(xattr, sel=[iref])[0]
        yref = self.get(yattr, sel=[iref])[0]
        label = kws.get('label', 'sum_of_{}'.format(sel))
        self.gs.append(Group())
        gsum = self.gs[-1]
        gsum.label = label
        self.mkinterpxy(ref=iref, sel=sel, xattr=xattr, yattr=yattr)
        for s in sel:
            if (s == iref):
                setattr(gsum, str(xattr), self.gs[s].xnew)
                ysum = self.gs[s].ynew
            else:
                ysum = ysum + self.gs[s].ynew
        setattr(gsum, str(yattr), ysum)

    def plotxy(self, **kws):
        """wrap to plot() in Larch (if available) otherwise PyMca is
        used (if available)
        
        Keyword arguments
        -----------------
        sel : a list of selected groups
        xattr : attribute for x-axis 
        yattr : attribute for y-axis
        replace : True acts as newplot()
        norm : type of normalization to apply
               'area', 'max-min', 'xflat'
        **kws : as in plot()
        """
        # init keyword arguments with educated guesses
        sel = kws.get('sel', self.sel)
        xattr = kws.get('xattr', self.kwsd['plot']['xattr'])
        yattr = kws.get('yattr', self.kwsd['plot']['yattr'])
        norm =  kws.get('norm', self.kwsd['plot']['norm'])
        replace = kws.get('replace', self.kwsd['plot']['replace'])
        win = kws.get('win', self.kwsd['plot']['win'])
        title = kws.get('title', self.kwsd['plot']['title'])
        show_legend = kws.get('show_legend', self.kwsd['plot']['show_legend'])
        legend_loc = kws.get('legend_loc', self.kwsd['plot']['legend_loc'])
        xlabel = kws.get('xlabel', self.kwsd['plot']['xlabel'])
        ylabel = kws.get('ylabel', self.kwsd['plot']['ylabel'])
        xmin = kws.get('xmin', self.kwsd['plot']['xmin'])
        xmax = kws.get('xmax', self.kwsd['plot']['xmax'])
        ymin = kws.get('ymin', self.kwsd['plot']['ymin'])
        ymax = kws.get('ymax', self.kwsd['plot']['ymax'])
        xshift = kws.get('xshift', self.kwsd['plot']['xshift'])
        ystack = kws.get('ystack', self.kwsd['plot']['ystack'])
        xscale = kws.get('xscale', self.kwsd['plot']['xscale'])
        yscale = kws.get('yscale', self.kwsd['plot']['yscale'])
        ###
        if (HAS_PYMCA and ( not self._inlarch )):
            if not hasattr(self, 'pw'):
                self.pw = ScanWindow.ScanWindow()
                # geometry good for >1280x800 resolution
                self.pw.setGeometry(50, 50, 700, 700)
                self.pw.show()
            if title:
                self.pw.setGraphTitle(title)
            if xlabel:
                self.pw.setGraphXTitle(xlabel)
            if ylabel:
                self.pw.setGraphYTitle(ylabel)
            if (xmin and xmax):
                self.pw.setGraphXLimits(xmin, xmax)
            if (ymin and ymax):
                print(ymin, ymax)
                self.pw.setGraphYLimits(ymin, ymax)
            # force replot
            self.pw.replot()
        if sel == '*':
            print('Plotting all...')
            self.show()
            sel = range(len(self.gs))
        if replace:
            _n = 0
        else:
            _n = 1
        _m = 0
        for _s in sel:
            # assign x,y
            x = getattr(self.gs[_s], xattr)
            y = getattr(self.gs[_s], yattr)
            # normalize y
            if norm == 'area':
                y = self.norint(y, x=x)
            elif norm == 'max-min':
                y = self.normax(y)
            elif norm == 'xflat':
                y = self.norxafs(self.gs[_s], outattr='flat', **kws)
            elif norm == 'xnorm':
                y = self.norxafs(self.gs[_s], outattr='norm', **kws)
            # plot
            if _n == 0:
                if self._inlarch:
                    _plot(x * xscale + xshift,
                          y * yscale + ystack * _m,
                          label=self.gs[_s].label, title=title, win=win,
                          xlabel=xlabel, ylabel=ylabel,
                          xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                          show_legend=show_legend, legend_loc=legend_loc,
                          new=True, _larch=self._larch)
                if (HAS_PYMCA and ( not self._inlarch )):
                    self.pw.addCurve(x * xscale + xshift,
                                     y * yscale + ystack * _m,
                                     legend=self.gs[_s].label,
                                     replace=True)
                _n += 1
                _m += 1
            else:
                if self._inlarch:
                    _plot(x * xscale + xshift,
                          y * yscale + ystack * _m,
                          label=self.gs[_s].label, title=title, win=win,
                          show_legend=show_legend, legend_loc=legend_loc,
                          new=False, _larch=self._larch)
                if (HAS_PYMCA and ( not self._inlarch )):
                    self.pw.addCurve(x * xscale + xshift,
                                     y * yscale + ystack * _m,
                                     legend=self.gs[_s].label,
                                     replace=False)
                _m += 1


        
### LARCH ###    
def datagroup1D(kwsd=None, _larch=None):
    """utility to perform wrapped operations on a list of 1D data
    groups"""
    return DataGroup1D(kwsd=kwsd, _larch=_larch)

def registerLarchPlugin():
    return (MODNAME, {'datagroup1D' : datagroup1D})

if __name__ == '__main__':
    pass

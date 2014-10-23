#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GsList1D: work with 1D data sets (scans)

TODO
----
- [] mksum
- [] plotxy: self.pw.setGeometry(700, 50, 900, 900), use config!
- [] 

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__owner__ = "Mauro Rovezzi"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2013"
__version__ = "0.0.1"
__status__ = "Alpha"
__date__ = "Dec 2013"

### IMPORTS ###
import os, sys
import numpy as np
# Larch
from larch import use_plugin_path, Group
# Larch Plugins
use_plugin_path('io')
from columnfile import _read_ascii
use_plugin_path('wx')
from plotter import _plot, _scatterplot, _plot_text
use_plugin_path('math')
from mathutils import _interp
from fitpeak import fit_peak
use_plugin_path('xafs')
from xafsft import xftf, xftr, xftf_prep, xftf_fast, xftr_fast, ftwindow
from pre_edge import pre_edge
# Mauro's Larch Plugins (https://github.com/maurov/larch_plugins)
from specfiledata import _str2rng as str2rng
from specfiledata import spec_getmap2group, spec_getmrg2group
from rixsdata_plotter import RixsDataPlotter
from gsutils import GsList

# PyMca
HAS_PYMCA = False
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

class GsList1D(GsList):
    """ 1D version of GsList """
    def __init__(self, kwsd=None, _larch=None):
        GsList.__init__(self, kwsd=kwsd, _larch=_larch)

    def read_ascii(self, fname, labels=None, sort=False, sort_column=0):
        """ see 'read_ascii' in Larch """
        return _read_ascii(fname, labels=labels,
                           sort=sort, sort_column=sort_column,
                           _larch=self._larch)

    def getxy(self, fname, xattr='x', yattr='y', scanlab=None, **kws):
        """ load two colums ascii data """
        g = _read_ascii(fname, labels='{0} {1}'.format(xattr, yattr),
                        _larch=self._larch)
        g.norint = self.norint(getattr(g, yattr))#, x=getattr(g, xattr))
        g.normax = self.normax(getattr(g, yattr))
        g.label = str(scanlab)
        return g

    def getspecscan(self, fname, scans, scanlab=None, **kws):
        """ load two colums data from SPEC file """
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
        """ center of mass (com) for the given group and x,w
        attributes"""
        return np.average(getattr(self.gs[g], xattr), weights=getattr(self.gs[g], yattr))

    def norint(self, y, x=None):
        """ simple normalization by area """
        return (y-np.min(y))/np.trapz(y, x=x)
        
    def normax(self, y):
        """ simple normalization by maximum minus offset """
        return (y-np.min(y))/(np.max(y)-np.min(y))

    def norxafs(self, g, xattr='x', yattr='y', outattr=None, **kws):
        """ XAFS normalization on a given group (g)

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
        """ find the x-shift to calibrate two spectra

        Keyword arguments
        -----------------
        g : spectrum to shift (index in gslist)
        ref : reference spectrum (in gslist)
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
            print '{0}.x shifted by {1}'.format(self.gs[g].label, cmdiff)
            if set_attr:
                self.gs[g].xcalib = cmdiff
        else:
            pass

    def mkinterpxy(self, ref=0, sel='*', **kws):
        """ interpolate (xattr, yattr) to (xnew, ynew) on a selected
        list of groups (sel); xnew is taken from the reference group
        or as linear space -- xnew = np.linspace(xmin, xmax,
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
            print 'DEBUG: {0} interp, {1} to {2}, {3} xstep = {4} points'.format(kind, xmin, xmax, xstep, len(xnew))
        self.selector(sel)
        for _n, _g in enumerate(self.gs_sel):
            try:
                setattr(_g, 'xnew', xnew)
                setattr(_g, 'ynew', _interp(getattr(_g, xattr), getattr(_g, yattr), xnew, kind=kind))
                if DEBUG:
                    print 'DEBUG: group {0} interpolated'.format(_n)
            except AttributeError:
                pass

    def mksum(self, sel, **kws):
        """ make a new group as sum of selected groups
        
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
                of a new group in gslist
             
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
        """ wrap to plot() in Larch (if available)
        otherwise PyMca is used (if available)
        
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
                if title:
                    self.pw.setGraphTitle(title)
                if xlabel:
                    self.pw.setGraphXTitle(xlabel)
                if ylabel:
                    self.pw.setGraphYTitle(ylabel)
                if (xmin and xmax):
                    self.pw.setGraphXLimits(xmin, xmax)
                if (ymin and ymax):
                    self.pw.setGraphYLimits(ymin, ymax)
                # geometry good for >1280x800 resolution
                self.pw.setGeometry(50, 50, 700, 700)
                self.pw.show()
        if sel == '*':
            print 'Plotting all...'
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

class GsListXanes(GsList1D):
    """ GsList for XANES scans """
    def __init__(self, kwsd=None, _larch=None):
        GsList1D.__init__(self, kwsd=kwsd, _larch=_larch)

class GsListExafs(GsList1D):
    """ GsList for EXAFS scans """
    def __init__(self, kwsd=None, _larch=None):
        GsList1D.__init__(self, kwsd=kwsd, _larch=_larch)

    def mkchikw(self, kws=[1,2,3]):
        """makes kws-weighted groups

        Returns
        -------
        None -- output written to attributes: 'chik[1,2,3]'
        """
        for kw in kws:
            _attr = 'chik'+str(kw)
            for _n, _g in enumerate(self.gs):
                try:
                    setattr(_g, _attr, _g.chi*_g.k**int(kw))
                except AttributeError:
                    print "group {0} ({1}): attr {3} does not exist".format(_n, _g.label, _attr)

    def mkftf(self, **kws):
        """ forward Fourier transform

        Returns
        -------
        None -- output written to attributes: (see xftf doc)
        """
        # sel = kws.get('sel', self.sel)
        xattr = kws.get('xattr', self.kwsd['xftf']['xattr'])
        yattr = kws.get('yattr', self.kwsd['xftf']['yattr'])
        kmin = kws.get('kmin', self.kwsd['xftf']['kmin'])
        kmax = kws.get('kmax', self.kwsd['xftf']['kmax'])
        dk = kws.get('dk', self.kwsd['xftf']['dk'])
        window = kws.get('window', self.kwsd['xftf']['window'])
        kweight = kws.get('kweight', self.kwsd['xftf']['kweight'])
        ###
        for _n, _g in enumerate(self.gs):
            try:
                _k = getattr(_g, xattr)
                _chi = getattr(_g, yattr)
            except AttributeError:
                print "group {0} ({1}): attr {3} does not exist".format(_n, _g.label, _attr)
                continue
            
            xftf(_k, _chi, group=_g, kmin=kmin, kmax=kmax, dk=dk,
                 window=window, kweight=kweight, _larch=self._larch)

    def scale_kwin(self, gchikw):
        """ returns a scale parameter to amplify the FT transform
        window"""
        return int(10.2*max(abs(gchikw)))/10.0

    def plotexa(self, space='E, K, R, Q', **kws):
        """ EXAFS default plots """
        sel = kws.get('sel', self.sel)
        replace = kws.get('replace', self.kwsd['plot']['replace'])
        xshift = kws.get('xshift', self.kwsd['plot']['xshift'])
        ystack = kws.get('ystack', self.kwsd['plot']['ystack'])
        xscale = kws.get('xscale', self.kwsd['plot']['xscale'])
        yscale = kws.get('yscale', self.kwsd['plot']['yscale'])
        ###
        if 'E' in space.upper():
            self.plotxy(sel=sel, xattr='ene', yattr='norm', win=1, replace=replace,
                        xshift=xshift, ystack=ystack, xscale=xscale, yscale=yscale,
                        xlabel=self.kwsd['plot']['xlabelE'], ylabel=self.kwsd['plot']['ylabelE'])
            if len(sel) == 1 and replace and not sel == '*':
                self.plotxy(sel=sel, xattr='ene', yattr='bkg', win=1, replace=replace,
                            xshift=xshift, ystack=ystack, xscale=xscale, yscale=yscale,
                            color='red', label='bkg')
        if 'K' in space.upper():
            self.plotxy(sel=sel, xattr='k', yattr='chik2', win=2, replace=replace,
                        show_legend=False,
                        xshift=xshift, ystack=ystack, xscale=xscale, yscale=yscale,
                        xlabel=self.kwsd['plot']['xlabelK'], ylabel=self.kwsd['plot']['ylabelK'])
            if len(sel) == 1 and replace and not sel == '*':
                _plot(self.gs[sel[0]].k, self.gs[sel[0]].kwin*self.scale_kwin(self.gs[sel[0]].chik2), color='red', win=2, _larch=self._larch)
        if 'R' in space.upper():
            self.plotxy(sel=sel, xattr='r', yattr='chir_mag', win=3, replace=replace,
                        show_legend=True,
                        xshift=xshift, ystack=ystack, xscale=xscale, yscale=yscale,
                        xmin=0, xmax=8, xlabel=self.kwsd['plot']['xlabelR'], ylabel=self.kwsd['plot']['ylabelR'])
        if 'Q' in space.upper():
            print 'to do'

class GsListXes(GsList1D):
    """ GsList for XES scans """
    def __init__(self, kwsd=None, _larch=None):
        GsList1D.__init__(self, kwsd=kwsd, _larch=_larch)

    def mkiads(self, ref=0, plot=False, **kws):
        """ IAD analysis for XES

        Keyword arguments
        -----------------
        ref : reference spectrum (in gs list)
        plot : to show the results in a plot

        Returns
        -------
        None -- output written to 'iads' group
        """
        _debug =  kws.get('DEBUG', DEBUG)
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
                    print 'DEBUG: {0}: area {1}\t max {2}'.format(_n, iad_area, iad_max)
                    setattr(_g, 'iad_yda', yda)
                    setattr(_g, 'iad_ydm', ydm)
                except AttributeError:
                    pass
            self.iads.id.append(_n)
            self.iads.lab.append(_g.label)
            self.iads.area.append(iad_area)
            self.iads.max.append(iad_max)
        if _debug:
            print "DEBUG: written attributes 'iad_yda' and 'iad_ydm' for fine check"
        if plot:
            self.plotiads()

    def plotiads(self, order=None, xlist=None, **kws):
        """ custom plot for IAD analysis """
        # as in self.plotxy()
        replace = kws.get('replace', True)
        win = kws.get('win', 2)
        show_legend = kws.get('show_legend', self.kwsd['plot']['show_legend'])
        legend_loc = kws.get('legend_loc', self.kwsd['plot']['legend_loc'])
        xlabel = kws.get('xlabel', None)
        ylabel = kws.get('ylabel', 'IAD (arb. units)')
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
        if order:
            if xlist:
                _ids = xlist
            else:
                _ids = range(len(order))
            _iads = []
            _labs = []
            for _id in order:
                _iads.append(self.iads.area[_id])
                _labs.append(self.iads.lab[_id])
        else:
            _ids = self.iads.id
            _iads = self.iads.area
            _labs = self.iads.lab
        
        _scatterplot(_ids, _iads, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                     xlabel=xlabel, ylabel=ylabel,
                     win=win, new=replace, _larch=self._larch)                

        if show_labs:
            for _lab, _x, _y in zip(_labs, _ids, _iads):
                _plot_text(_lab, _x+labs_xoff, _y+labs_yoff, win=win, rotation=labs_rot,
                           ha=labs_ha, va=labs_va, _larch=self._larch)

### LARCH ###    
def gslist_xan(kwsd=None, _larch=None):
    """ utility to perform common operations on a list of XANES data groups """
    return GsListXanes(kwsd=kwsd, _larch=_larch)

def gslist_exa(kwsd=None, _larch=None):
    """ utility to perform common operations on a list of EXAFS data groups """
    return GsListExafs(kwsd=kwsd, _larch=_larch)

def gslist_xes(kwsd=None, _larch=None):
    """ utility to perform common operations on a list of XES data groups """
    return GsListXes(kwsd=kwsd, _larch=_larch)

def registerLarchPlugin():
    return (MODNAME, {'gslist_xan' : gslist_xan,
                      'gslist_exa' : gslist_exa,
                      'gslist_xes' : gslist_xes})

if __name__ == '__main__':
    pass

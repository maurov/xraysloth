#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DataGroupExafs: work with EXAFS data sets
============================================

- DataGroup
  - DataGroup1D
    - DataGroupExafs
"""
from .datagroup import MODNAME
from .datagroup1D import DataGroup1D

class DataGroupExafs(DataGroup1D):
    """DataGroup for EXAFS scans"""
    def __init__(self, kwsd=None, _larch=None):
        super(DataGroupExafs, self).__init__(kwsd=kwsd, _larch=_larch)

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
                    print("group {0} ({1}): attr {3} does not exist".format(_n, _g.label, _attr))

    def mkftf(self, **kws):
        """forward Fourier transform

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
                print("group {0} ({1}): attr {3} does not exist".format(_n, _g.label, _attr))
                continue
            
            xftf(_k, _chi, group=_g, kmin=kmin, kmax=kmax, dk=dk,
                 window=window, kweight=kweight, _larch=self._larch)

    def scale_kwin(self, gchikw):
        """returns a scale parameter to amplify the FT transform
        window"""
        return int(10.2*max(abs(gchikw)))/10.0

    def plotexa(self, space='E, K, R, Q', **kws):
        """EXAFS default plots"""
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
            print('Not implemented yet.')

### LARCH ###    
def datagroup_exa(kwsd=None, _larch=None):
    """utility to perform wrapped operations on a list of EXAFS data
    groups"""
    return DataGroupExafs(kwsd=kwsd, _larch=_larch)

def registerLarchPlugin():
    return (MODNAME, {'datagroup_xan' : datagroup_exa})

if __name__ == '__main__':
    pass

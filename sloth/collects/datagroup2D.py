#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DataGroup2D: work with 2D data sets (planes/maps)

TODO
----
- [] REFACTOR THE WHOLE THING!!!
- [] MOVE TECHNIQUE-BASED DATAGROUPS TO "sloth.technique"!!!
- [] 
- []

"""
from .datagroup import DataGroup
from ..rixs.rixsdata_plotter import RixsDataPlotter

class DataGroup2D(DataGroup):
    """ 2D version of DataGroup """
    def __init__(self, kwsd=None, _larch=None):
        DataGroup.__init__(self, kwsd=kwsd, _larch=_larch)

class DataGroupRixs(DataGroup2D):
    """DataGroup for RIXS planes"""
    def __init__(self, kwsd=None, _larch=None):
        DataGroup2D.__init__(self, kwsd=kwsd, _larch=_larch)

    def getspecmap(self, fname, scans, scanlab=None, **kws):
        """ 2D map from a list of scans read from SPEC data files"""
        cntx = kws.get('cntx', self.kwsd['spec']['cntx'])
        cnty = kws.get('cnty', self.kwsd['spec']['cnty'])
        csig = kws.get('csig', self.kwsd['spec']['csig'])
        cmon = kws.get('cmon', self.kwsd['spec']['cmon'])
        csec = kws.get('csec', self.kwsd['spec']['csec'])
        norm = kws.get('norm', self.kwsd['spec']['norm'])
        xystep = kws.get('xystep', self.kwsd['spec']['xystep'])
        g = spec_getmap2group(fname, scans=scans,
                              cntx=cntx,
                              cnty=cnty,
                              csig=csig,
                              cmon=cmon,
                              csec=csec,
                              xystep=xystep,
                              norm=norm,
                              _larch=self._larch)
        g.label = str(scanlab)
        return g

    def plotmap(self, imap, **kws):
        """plot for 2D map (e.g. RIXS plane)

        imap : index in gs list

        """
        p = RixsDataPlotter(self.gs[imap])
        p.plot()
        return

if __name__ == '__main__':
    pass

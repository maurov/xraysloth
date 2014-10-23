#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GsList2D: work with 2D data sets (planes/maps)

TODO
----
- [] 
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

from gsutils import GsList

class GsList2D(GsList):
    """ 2D version of GsList """
    def __init__(self, kwsd=None, _larch=None):
        GsList.__init__(self, kwsd=kwsd, _larch=_larch)

class GsListRixs(GsList2D):
    """ GsList for RIXS planes """
    def __init__(self, kwsd=None, _larch=None):
        GsList2D.__init__(self, kwsd=kwsd, _larch=_larch)

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
        """ plot for 2D map (e.g. RIXS plane)

        imap : index in gs list
        """
        p = RixsDataPlotter(self.gs[imap])
        p.plot()
        return

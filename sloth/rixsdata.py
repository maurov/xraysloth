#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resonant Inelastic X-ray Scattering (RIXS) data objects (2D maps)

TODO
----
- move self.getkwsd() to ConfigParser

"""

from __future__ import division

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__owner__ = "Mauro Rovezzi"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2011-2014"
__version__ = "0.0.1"
__status__ = "Alpha"
__date__ = "Oct 2014"

import os, sys
import numpy as np
from matplotlib import cm

# Larch & friends
from gridutils import _gridxyz
from specfiledata import _str2rng as str2rng
from specfiledata import SpecfileData

class RixsData(object):
    """ RIXS plane object """
    def __init__(self, label=None, kwsd=None):
        "initialize with keyword arguments dictionaries"
        if kwsd is None:
            kwsd = self.getkwsd()
        self.kwsd = kwsd
        if label is None:
            label = 'rd{0}'.format(hex(id(self)))
        self.label = label

    def getkwsd(self):
        """ return a dictionary of dictionaries with keywords arguments:
        
        kwsd['exp']['expdir'] : main working directory (experiment directory)
        ...........['datdir'] : directory where the raw data (e.g. SPEC data) are stored
        ...........['evaldir'] : directory where evaluated data are saved
        ...........['mater'] : material
        ...........['sample'] : sample name
        ...........['explab'] : label to identify the experiment
        ...........['geom'] : data collection geometry (VGI or V## / HGI or H##)
        ...........['scnt'] : type of scan (EXA, XAN, PRE, RIXS, RIXS_ET)
        ...........['mode'] : data collection mode ???
        
        kwsd['spec']['fname'] : file name to load (full path)
        ............['rngstr'] : string to identify the range of loaded scans
        ............['cntx'] : name of x-axis counter/motor
        ............['cnty'] : name of y-axis counter/motor
        ............['csig'] : name for signal
        ............['cmon'] : name for monitor (e.g. incoming beam monitor, I0)
        ............['cmon2'] : name for a second monitor (e.g. total fluo yield, IF2)
        ............['csec'] : name for seconds
        ............['norm'] : normalization type ( 
        ............['xystep'] : step in meshgrid
        
        kwsd['plot']['...']
        ............
        """
        kwsd = {'exp' : {'expdir' : None,
                         'datdir' : None,
                         'evaldir' : None,
                         'mater' : None,
                         'sample' : None,
                         'explab' : None,
                         'geom' : None,
                         'scnt' : None,
                         'mode' : None},
                'spec' : {'fname': None,
                          'rngstr' : None,
                          'cntx' : 1,
                          'cnty' : None,
                          'csig' : None,
                          'cmon' : None,
                          'cmon2' : None,
                          'csec' : None,
                          'norm' : None,
                          'xystep' : 0.02},
                'grid' : {'xystep' : 0.02,
                          'method' : 'nn',
                          'lib' : 'matplotlib'},
                'plot' : {'replace' : True,
                          'figname' : 'RixsPlotter',
                          'figsize' : (5,5),
                          'figdpi' : 100,
                          'title' : None,
                          'xlabel' : None,
                          'ylabel' : None,
                          'x_nticks': 0,
                          'y_nticks': 0,
                          'z_nticks': 0,
                          'xlabelE' : r'Incoming Energy (eV)',
                          'ylabelE' : r'Emitted Energy (eV)',
                          'ylabelEt' : r'Energy transfer (eV)',
                          'zlabel' : r'Intensity (a.u)',
                          'xystep' : 0.02,
                          'xmin' : None,
                          'xmax' : None,
                          'ymin' : None,
                          'ymax' : None,
                          'xshift' : 0,
                          'ystack' : 0,
                          'xscale' : 1,
                          'yscale' : 1,
                          'cbar_show' : False,
                          'cbar_pos': 'vertical',
                          'cbar_nticks' : 0,
                          'cbar_label' : 'Counts/s',
                          'cbar_norm0' : False,
                          'cmap': cm.gist_heat_r,
                          'cmap2' : cm.RdBu,
                          'cmap_linlog': 'linear',
                          'cont_imshow' : True,
                          'cont_type': 'line',
                          'cont_lwidths': 0.25,
                          'cont_levels': 100,
                          'cont_labels': None,
                          'cont_labelformat': '%.3f',
                          'origin': 'lower',
                          'lcuts' : False,
                          'xcut' : None,
                          'ycut' : None,
                          'dcut' : None,
                          'lc_dticks' : 2,
                          'lc_color' : 'red',
                          'lc_lw': 3}}
        return kwsd

    def loadxyz(self, fname, **kws):
        """ load data from a 3 columns ASCII file assuming the format:
        e_in, e_out, signal"""
      
        try:
            self.dat = np.loadtxt(fname)
            print 'Loaded {0}'.format(fname)
        except:
            print 'Error in loading {0}'.format(fname)
            return
        
        self.xcol = self.dat[:,0]
        #decide if dat[:,1] is e_out or e_in-e_out
        if np.max(self.dat[:,1])/np.max(self.dat[:,0]) < 0.5:
            self.ycol = self.dat[:,0] - self.dat[:,1]
            self.etcol = self.dat[:,1]
        else:
            self.ycol = self.dat[:,1]
            self.etcol = self.dat[:,0] - self.dat[:,1] # energy transfer
        self.zcol = self.dat[:,2]

    def gridxyz(self, **kws):
        """ create gridded standard groups """
        xystep = kws.get('xystep', self.kwsd['grid']['xystep'])
        method = kws.get('method', self.kwsd['grid']['method'])
        lib = kws.get('lib', self.kwsd['grid']['lib'])

        self.x, self.y, self.zz = _gridxyz(self.xcol,
                                           self.ycol,
                                           self.zcol,
                                           xystep=xystep,
                                           method=method,
                                           lib=lib)
        self.ex, self.et, self.ezz = _gridxyz(self.xcol,
                                              self.etcol,
                                              self.zcol,
                                              xystep=xystep,
                                              method=method,
                                              lib=lib)
        
    def load_spec_map(self, **kws):
        """ load the plane from SPEC file

        TODO: merge this in the previous load_xyz and the SPEC part in
        specfile
        """
        datdir = kws.get('datdir', self.kwsd['spec']['datdir'])
        fname = kws.get('fname', self.kwsd['spec']['fname'])
        scans = kws.get('scans', self.kwsd['spec']['rngstr'])
        scnt = kws.get('scnt', self.kwsd['exp']['scnt'])
        cntx = kws.get('cntx', self.kwsd['spec']['cntx'])
        cnty = kws.get('cnty', self.kwsd['spec']['cnty'])
        csig = kws.get('csig', self.kwsd['spec']['csig'])
        cmon = kws.get('cmon', self.kwsd['spec']['cmon'])
        csec = kws.get('csec', self.kwsd['spec']['csec'])
        norm = kws.get('norm', self.kwsd['spec']['norm'])
        xystep = kws.get('xystep', self.kwsd['grid']['xystep'])
        method = kws.get('method', self.kwsd['grid']['method'])
        lib = kws.get('lib', self.kwsd['grid']['lib'])
        
        self.sfd = SpecfileData(os.path.join(datdir, fname))
        _x, _y, self.zcol = self.sfd.get_map(scans=scans,
                                             cntx=cntx,
                                             cnty=cnty,
                                             csig=csig,
                                             cmon=cmon,
                                             csec=csec,
                                             norm=norm)
        # in case of rixs_et we swap x<->y
        if 'rixs_et' in scnt.lower():
            self.xcol, self.ycol = _y, _x
        else:
            self.xcol, self.ycol = _x, _y
        self.etcol = self.xcol-self.ycol # energy transfer

    def crop(self, x1, y1, x2, y2, **kws):
        """ crop the plane in given range (x1, y1) -> (x2, y2) """
        xystep = kws.get('xystep', self.kwsd['spec']['xystep'])
        from matplotlib.mlab import griddata
        self.xcrop = np.arange(x1, x2, xystep)
        self.ycrop = np.arange(y1, y2, xystep)
        _xx, _yy = np.meshgrid(self.xcrop, self.ycrop)
        self.excrop = np.arange(x1, x2, xystep)
        self.etcrop = np.arange(x2-y2, x1-y1, xystep)
        _exx, _et = np.meshgrid(self.excrop, self.etcrop)
        self.zzcrop = griddata(self.xcol, self.ycol, self.zcol, _xx, _yy)
        self.ezzcrop = griddata(self.xcol, self.etcol, self.zcol, _exx, _et)
        return

    def norm(self, zz):
        """ normalization to max-min """
        return zz/(np.nanmax(zz)-np.nanmin(zz))

if __name__ == '__main__':
    pass
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DataGroupRixs: work with  RIXS data sets (2D maps)
=====================================================

.. note: RIXS stands for Resonant Inelastic X-ray Scattering

- DataGroup
  - DataGroup2D
    - DataGroupRixs
"""

from __future__ import print_function, division

import os
import copy
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import cm
from matplotlib.ticker import MaxNLocator, AutoLocator

# sloth
from ..io.specfile_reader import spec_getmap2group
from .datagroup2D import DataGroup2D
from ..math.gridxyz import gridxyz
from sloth.io.specfile_reader import SpecfileData

from sloth.utils.logging import getLogger

_logger = getLogger(__name__)  #: module logger, used as self._logger if not given

class DataGroupRixs(DataGroup2D):
    """DataGroup for RIXS planes"""

    def __init__(self, kwsd=None, _larch=None):
        super(DataGroupRixs, self).__init__(self, kwsd=kwsd, _larch=_larch)

        _logger.warning("!!!DEPRECATED!!!: use `from larch.io.rixdata import RixsData`")

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


class RixsData(object):
    """RIXS plane object"""

    def __init__(self, label=None, kwsd=None, logger=None):
        """initialize with keyword arguments dictionaries"""

        _logger.warning("DEPRECATED: use `from larch.io.rixdata import RixsData`")

        if logger is not None:
            self._logger = logger
        else:
            self._logger = _logger

        if kwsd is None:
            kwsd = self.get_kwsd()
        self.kwsd = kwsd

        if label is None:
            label = 'rd{0}'.format(hex(id(self)))
        self.label = label

        self.plotter = None

    def get_kwsd(self):
        """return a dictionary of dictionaries with keywords arguments:

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
                          'method' : 'cubic',
                          'lib'    : 'scipy'},
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


    def load_from_dict(self, rxdict):
        """Load RIXS data from a dictionary

        Parameters
        ----------
        rxdict : dict
            Required structure
            {
             'sample_name': str,
             'ene_in': 1D array,
             'ene_out': 1D array,
             'rixs': 2D array,
            }

        Return
        ------
        None, set attributes: self.x, self.y, self.zz, self.label
        """
        self.label = rxdict['sample_name']
        self.x = rxdict['ene_in']
        self.y = rxdict['ene_out']
        self.zz = rxdict['rixs']


    def load_from_h5(self, fname):
        """Load RIXS from HDF5 file"""
        from silx.io.dictdump import h5todict
        rxdict = h5todict(fname)
        rxdict['sample_name'] = rxdict['sample_name'].tostring().decode()
        self.load_from_dict(rxdict)


    def loadxyz(self, fname, **kws):
        """load data from a 3 columns ASCII file assuming the format: e_in,
        e_out, signal

        """

        try:
            self.dat = np.loadtxt(fname)
            print('Loaded {0}'.format(fname))
        except Exception:
            print('Error in loading {0}'.format(fname))
            return

        self.xcol = self.dat[:, 0]
        # decide if dat[:,1] is e_out or e_in-e_out
        if np.max(self.dat[:, 1]) / np.max(self.dat[:, 0]) < 0.5:
            self.ycol = self.dat[:, 0] - self.dat[:, 1]
            self.etcol = self.dat[:, 1]
        else:
            self.ycol = self.dat[:, 1]
            self.etcol = self.dat[:, 0] - self.dat[:, 1]  # energy transfer
        self.zcol = self.dat[:, 2]

    def gridxyz(self, **kws):
        """create gridded standard groups"""
        xystep = kws.get('xystep', self.kwsd['grid']['xystep'])
        method = kws.get('method', self.kwsd['grid']['method'])
        lib = kws.get('lib', self.kwsd['grid']['lib'])

        self.x, self.y, self.zz = gridxyz(self.xcol,
                                          self.ycol,
                                          self.zcol,
                                          xystep=xystep,
                                          method=method,
                                          lib=lib)
        self.ex, self.et, self.ezz = gridxyz(self.xcol,
                                             self.etcol,
                                             self.zcol,
                                             xystep=xystep,
                                             method=method,
                                             lib=lib)

    def load_spec_map(self, **kws):
        """load the plane from SPEC file

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

    def crop_old(self, x1, y1, x2, y2, yet=False, **kws):
        """crop the plane in a given range

        Parameters
        ==========

        x1, y1, x2, y2 : floats
                         X/Y initial and new coordinates

        yet : boolean, False
              defines if the Y coordinates are given in emission or
              energy transfer

        """
        _xystep = kws.get('xystep', self.kwsd['grid']['xystep'])
        _method = kws.get('method', self.kwsd['grid']['method'])

        _nxpts = int((x2-x1)/_xystep)
        self.xcrop = np.linspace(x1, x2, num=_nxpts)

        if yet:
            _netpts = int((y2-y1)/_xystep)
            _ymin = x2-y2
            _ymax = x1-y1
            _nypts = int((_ymax-_ymin)/_xystep)
            self.etcrop = np.linspace(y1, y2, num=_netpts)
            self.ycrop = np.linspace(_ymin, _ymax, num=_nypts)
        else:
            _nypts = int((y2-y1)/_xystep)
            _etmin = x1-y2
            _etmax = x2-y1
            _netpts = int((_etmax-_etmin)/_xystep)
            self.etcrop = np.linspace(_etmin, _etmax, num=_netpts)
            self.ycrop = np.linspace(y1, y2, num=_nypts)

        _xx, _yy = np.meshgrid(self.xcrop, self.ycrop)
        _exx, _et = np.meshgrid(self.xcrop, self.etcrop)

        self.zzcrop = griddata((self.xcol, self.ycol), self.zcol, (_xx, _yy), method=_method)

        self.ezzcrop = griddata((self.xcol, self.etcol), self.zcol, (_exx, _et), method=_method)

        return

    def crop(self, x1, y1, x2, y2, yet=False, **kws):
        """crop the plane in a given range / matrix approach (current)

        Parameters
        ==========
        x1, y1, x2, y2 : floats
            X/Y initial and new coordinates

        yet : boolean, False
            defines if the Y coordinates are given in emission or
            energy transfer
        """
        if yet == True:
            print('Not implemented!')
            return
        ix1 = np.abs(self.x-x1).argmin()
        iy1 = np.abs(self.y-y1).argmin()
        ix2 = np.abs(self.x-x2).argmin()
        iy2 = np.abs(self.y-y2).argmin()
        self._crop_area = (x1, y1, x2, y2)
        self.xcrop = self.x[ix1:ix2]
        self.ycrop = self.y[iy1:iy2]
        self.zzcrop = self.zz[iy1:iy2, ix1:ix2]

    def norm(self, zz):
        """normalization to max-min"""
        return zz/(np.nanmax(zz)-np.nanmin(zz))

    def getPlotter(self):
        """Get a default plotter"""
        if self.plotter is None:
            from sloth.gui.plot.plotrixs import RixsPlot2D
            self.plotter = RixsPlot2D(logger=self._logger)
        return self.plotter

    def plot(self, plotter=None, nlevels=50, crop=False):
        """Data plotter"""
        if plotter is None:
            p = self.getPlotter()
        p.clear()
        if type(crop) is tuple:
            self.crop(*crop)
        if crop:
            _title = f"{self.label} [CROP: {self._crop_area}]"
            p.addImage(self.zzcrop, x=self.xcrop, y=self.ycrop, title=_title,
                       xlabel='Ene_in', ylabel='Ene_out')
        else:
            p.addImage(self.zz, x=self.x, y=self.y, title=self.label,
                       xlabel='Ene_in', ylabel='Ene_out')
        p.addContours(nlevels)
        p.show()



class RixsDataPlotter(object):
    """ plotter for a RixsData object """
    def __init__(self, rd):
        "initialize with keyword arguments dictionaries"
        if not 'RixsData' in str(type(rd)):
            _logger.error('I can only plot "RixsData" objects!')
            return
        try:
            self.kwsd = copy.deepcopy(rd.kwsd['plot'])
        except Exception:
            self.kwsd = self.get_plot_kwsd()
        self.rd = rd

    def get_plot_kwsd(self):
        """return a dictionary of dictionaries with default keywords arguments"""
        kwsd = {'replace' : True,
                          'figname' : 'RixsPlotter',
                          'figsize' : (10,10),
                          'figdpi' : 150,
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
                          'cont_levels': 50,
                          'cont_labels': None,
                          'cont_labelformat': '%.3f',
                          'origin': 'lower',
                          'lcuts' : False,
                          'xcut' : None,
                          'ycut' : None,
                          'dcut' : None,
                          'lc_dticks' : 2,
                          'lc_color' : 'red',
                          'lc_lw': 3}
        return kwsd


    def plot(self, x=None, y=None, zz=None, **kws):
        """ make the plot """
        if x is None:
            x = self.rd.ex
            x0 = self.rd.x
        if y is None:
            y = self.rd.et
            y0 = self.rd.y
        if zz is None:
            zz = self.rd.ezz
            zz0 = self.rd.zz

        self.kwsd.update(**kws)

        # check if x and y are 1D or 2D arrays
        if ( (len(x.shape) == 1) and (len(y.shape) == 1) ):
            _xyshape = 1
        elif ( (len(x.shape) == 2) and (len(y.shape) == 2) ):
            _xyshape = 2

        lcuts = kws.get('lcuts', self.kwsd['lcuts'])
        xcut = kws.get('xcut', self.kwsd['xcut'])
        ycut = kws.get('ycut', self.kwsd['ycut'])
        dcut = kws.get('dcut', self.kwsd['dcut'])

        lc_dticks = kws.get('lc_dticks', self.kwsd['lc_dticks'])
        lc_color = kws.get('lc_color', self.kwsd['lc_color'])
        lc_lw = kws.get('lc_lw', self.kwsd['lc_lw'])

        replace = kws.get('replace', self.kwsd['replace'])
        figname = kws.get('figname', self.kwsd['figname'])
        figsize = kws.get('figsize', self.kwsd['figsize'])
        figdpi = kws.get('figdpi', self.kwsd['figdpi'])
        title = kws.get('title', self.kwsd['title'])
        xlabel = kws.get('xlabel', self.kwsd['xlabelE'])
        if (y.max()/x.max() < 0.5):
            ylabel = kws.get('ylabel', self.kwsd['ylabelEt'])
        else:
            ylabel = kws.get('ylabel', self.kwsd['ylabelE'])
        zlabel = kws.get('zlabel', self.kwsd['zlabel'])
        xmin = kws.get('xmin', self.kwsd['xmin'])
        xmax = kws.get('xmax', self.kwsd['xmax'])
        ymin = kws.get('ymin', self.kwsd['ymin'])
        ymax = kws.get('ymax', self.kwsd['ymax'])
        x_nticks = kws.get('x_nticks', self.kwsd['x_nticks'])
        y_nticks = kws.get('y_nticks', self.kwsd['y_nticks'])
        z_nticks = kws.get('z_nticks', self.kwsd['z_nticks'])
        cmap = kws.get('cmap', self.kwsd['cmap'])

        cbar_show = kws.get('cbar_show', self.kwsd['cbar_show'])
        cbar_pos = kws.get('cbar_pos', self.kwsd['cbar_pos'])
        cbar_nticks = kws.get('cbar_nticks', self.kwsd['cbar_nticks'])
        cbar_label = kws.get('cbar_label', self.kwsd['cbar_label'])
        cbar_norm0 = kws.get('cbar_norm0', self.kwsd['cbar_norm0'])

        cont_imshow = kws.get('cont_imshow', self.kwsd['cont_imshow'])
        cont_type = kws.get('cont_type', self.kwsd['cont_type'])
        cont_levels = kws.get('cont_levels', self.kwsd['cont_levels'])
        cont_lwidths = kws.get('cont_lwidths', self.kwsd['cont_lwidths'])

        # NOTE: np.nanmin/np.nanmax fails with masked arrays! better
        #       to work with MaskedArray for zz

        #if not 'MaskedArray' in str(type(zz)):
        #    zz = np.ma.masked_where(zz == np.nan, zz)

        # NOTE2: even with masked arrays min()/max() fail!!!  I do a
        #        manual check against 'nan' instead of the masked
        #        array solution

        try:
            zzmin, zzmax = np.nanmin(zz), np.nanmax(zz)
        except:
            zzmin, zzmax = np.min(zz), np.max(zz)

        if cbar_norm0:
            # normalize colors around 0
            if abs(zzmin) > abs(zzmax):
                vnorm = abs(zzmin)
            else:
                vnorm = abs(zzmax)
            norm = cm.colors.Normalize(vmin=-vnorm, vmax=vnorm)
        else:
            # normalize colors from min to max
            norm = cm.colors.Normalize(vmin=zzmin, vmax=zzmax)

        extent = (x.min(), x.max(), y.min(), y.max())
        levels = np.linspace(zzmin, zzmax, cont_levels)

        ### FIGURE LAYOUT ###
        if replace:
            plt.close(figname)
        self.fig = plt.figure(num=figname, figsize=figsize, dpi=figdpi)
        if replace:
            self.fig.clear()

        # 1 DATA SET WITH OR WITHOUT LINE CUTS
        if lcuts:
            gs = gridspec.GridSpec(3,3) #3x3 grid
            self.plane = plt.subplot(gs[:,:-1]) # plane
            self.lxcut = plt.subplot(gs[0,2]) # cut along x-axis
            self.ldcut = plt.subplot(gs[1,2]) # cut along d-axis (diagonal)
            self.lycut = plt.subplot(gs[2,2]) # cut along y-axis
        else:
            self.plane = self.fig.add_subplot(111) #plot olny plane

        # plane
        if title:
            self.plane.set_title(title)
        self.plane.set_xlabel(xlabel)
        self.plane.set_ylabel(ylabel)
        if xmin and xmax:
            self.plane.set_xlim(xmin, xmax)
        if ymin and ymax:
            self.plane.set_ylim(ymin, ymax)

        # contour mode: 'contf' or 'imshow'
        if cont_imshow:
            self.contf = self.plane.imshow(zz, origin='lower', extent=extent, cmap=cmap, norm=norm)
        else:
            self.contf = self.plane.contourf(x, y, zz, levels, cmap=cm.get_cmap(cmap, len(levels)-1), norm=norm)

        if 'line' in cont_type.lower():
            self.cont = self.plane.contour(x, y, zz, levels, colors = 'k', hold='on', linewidths=cont_lwidths)
        if x_nticks:
            self.plane.xaxis.set_major_locator(MaxNLocator(int(x_nticks)))
        else:
            self.plane.xaxis.set_major_locator(AutoLocator())
        if y_nticks:
            self.plane.yaxis.set_major_locator(MaxNLocator(int(y_nticks)))
        else:
            self.plane.yaxis.set_major_locator(AutoLocator())

        # colorbar
        if cbar_show:
            self.cbar = self.fig.colorbar(self.contf, use_gridspec=True, orientation=cbar_pos)
            if cbar_nticks:
                self.cbar.set_ticks(MaxNLocator(int(y_nticks)))
            else:
                self.cbar.set_ticks(AutoLocator())
            self.cbar.set_label(cbar_label)

        # xcut plot
        if lcuts and xcut:
            xpos = np.argmin(np.abs(xcut-x))
            if _xyshape == 1:
                self.lxcut.plot(y, zz[:,xpos], label=str(x[xpos]),
                                color=lc_color, linewidth=lc_lw)
            elif _xyshape == 2:
                self.lxcut.plot(y[:,xpos], zz[:,xpos], label=str(x[:,xpos][0]),
                                color=lc_color, linewidth=lc_lw)
            if y_nticks:
                self.lxcut.xaxis.set_major_locator(MaxNLocator(int(y_nticks/lc_dticks)))
            else:
                self.lxcut.xaxis.set_major_locator(AutoLocator())
            if z_nticks:
                self.lxcut.yaxis.set_major_locator(MaxNLocator(int(z_nticks/lc_dticks)))
            else:
                self.lxcut.yaxis.set_major_locator(AutoLocator())
            self.lxcut.set_yticklabels([])
            self.lxcut.set_ylabel(zlabel)
            self.lxcut.set_xlabel(ylabel)
            if ymin and ymax:
                self.lxcut.set_xlim(ymin, ymax)

        # ycut plot
        if lcuts and ycut:
            ypos = np.argmin(np.abs(ycut-y))
            if _xyshape == 1:
                self.lycut.plot(x, zz[ypos,:], label=str(y[ypos]),
                                color=lc_color, linewidth=lc_lw)
            elif _xyshape == 2:
                self.lycut.plot(x[ypos,:], zz[ypos,:], label=str(y[ypos,:][0]),
                                color=lc_color, linewidth=lc_lw)
            if x_nticks:
                self.lycut.xaxis.set_major_locator(MaxNLocator(int(x_nticks/lc_dticks)))
            else:
                self.lycut.xaxis.set_major_locator(AutoLocator())
            if z_nticks:
                self.lycut.yaxis.set_major_locator(MaxNLocator(int(z_nticks/lc_dticks)))
            else:
                self.lycut.yaxis.set_major_locator(AutoLocator())
            self.lycut.set_yticklabels([])
            self.lycut.set_ylabel(zlabel)
            self.lycut.set_xlabel(xlabel)
            if xmin and xmax:
                self.lycut.set_xlim(xmin, xmax)

        # dcut plot => equivalent to ycut plot for (zz0, x0, y0)
        if lcuts and dcut:
            ypos0 = np.argmin(np.abs(dcut-y0))
            if _xyshape == 1:
                self.ldcut.plot(x0, zz0[ypos0,:], label=str(y0[ypos0]),
                                color=lc_color, linewidth=lc_lw)
            elif _xyshape == 2:
                self.ldcut.plot(x0[ypos0,:], zz0[ypos0,:], label=str(y0[ypos0,:][0]),
                                color=lc_color, linewidth=lc_lw)
            if x_nticks:
                self.ldcut.xaxis.set_major_locator(MaxNLocator(int(x_nticks/lc_dticks)))
            else:
                self.ldcut.xaxis.set_major_locator(AutoLocator())
            if z_nticks:
                self.ldcut.yaxis.set_major_locator(MaxNLocator(int(z_nticks/lc_dticks)))
            else:
                self.ldcut.yaxis.set_major_locator(AutoLocator())
            self.ldcut.set_yticklabels([])
            self.ldcut.set_ylabel(zlabel)
            self.ldcut.set_xlabel(xlabel)
            if xmin and xmax:
                self.ldcut.set_xlim(xmin, xmax)
        plt.draw()
        plt.show()

if __name__ == '__main__':
    pass

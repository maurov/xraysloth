#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RixsDataPlotter : Matplotlib-based plotter for RIXS planes
==========================================================
"""

import sys, os, copy
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import cm
from matplotlib.ticker import MaxNLocator, AutoLocator
import numpy as np

class RixsDataPlotter(object):
    """ plotter for a RixsData object """
    def __init__(self, rd):
        "initialize with keyword arguments dictionaries"
        if not 'RixsData' in str(type(rd)):
            print('I can only plot "RixsData" objects!')
            return
        self.kwsd = copy.deepcopy(rd.kwsd)
        self.rd = rd

    def updatekwsd(self, kwsd):
        """ update plot parameters """
        return self.kwsd['plot'].update(kwsd)
 
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

        # check if x and y are 1D or 2D arrays
        if ( (len(x.shape) == 1) and (len(y.shape) == 1) ):
            _xyshape = 1
        elif ( (len(x.shape) == 2) and (len(y.shape) == 2) ):
            _xyshape = 2

        lcuts = kws.get('lcuts', self.kwsd['plot']['lcuts'])
        xcut = kws.get('xcut', self.kwsd['plot']['xcut'])
        ycut = kws.get('ycut', self.kwsd['plot']['ycut'])
        dcut = kws.get('dcut', self.kwsd['plot']['dcut'])
        
        lc_dticks = kws.get('lc_dticks', self.kwsd['plot']['lc_dticks'])
        lc_color = kws.get('lc_color', self.kwsd['plot']['lc_color'])
        lc_lw = kws.get('lc_lw', self.kwsd['plot']['lc_lw'])
        
        replace = kws.get('replace', self.kwsd['plot']['replace'])
        figname = kws.get('figname', self.kwsd['plot']['figname'])
        figsize = kws.get('figsize', self.kwsd['plot']['figsize'])
        figdpi = kws.get('figdpi', self.kwsd['plot']['figdpi'])
        title = kws.get('title', self.kwsd['plot']['title'])
        xlabel = kws.get('xlabel', self.kwsd['plot']['xlabelE'])
        if (y.max()/x.max() < 0.5):
            ylabel = kws.get('ylabel', self.kwsd['plot']['ylabelEt'])
        else:
            ylabel = kws.get('ylabel', self.kwsd['plot']['ylabelE'])
        zlabel = kws.get('zlabel', self.kwsd['plot']['zlabel'])
        xmin = kws.get('xmin', self.kwsd['plot']['xmin'])
        xmax = kws.get('xmax', self.kwsd['plot']['xmax'])
        ymin = kws.get('ymin', self.kwsd['plot']['ymin'])        
        ymax = kws.get('ymax', self.kwsd['plot']['ymax'])
        x_nticks = kws.get('x_nticks', self.kwsd['plot']['x_nticks'])
        y_nticks = kws.get('y_nticks', self.kwsd['plot']['y_nticks'])
        z_nticks = kws.get('z_nticks', self.kwsd['plot']['z_nticks'])
        cmap = kws.get('cmap', self.kwsd['plot']['cmap'])
        
        cbar_show = kws.get('cbar_show', self.kwsd['plot']['cbar_show'])
        cbar_pos = kws.get('cbar_pos', self.kwsd['plot']['cbar_pos'])
        cbar_nticks = kws.get('cbar_nticks', self.kwsd['plot']['cbar_nticks'])
        cbar_label = kws.get('cbar_label', self.kwsd['plot']['cbar_label'])
        cbar_norm0 = kws.get('cbar_norm0', self.kwsd['plot']['cbar_norm0'])

        cont_imshow = kws.get('cont_imshow', self.kwsd['plot']['cont_imshow'])
        cont_type = kws.get('cont_type', self.kwsd['plot']['cont_type'])
        cont_levels = kws.get('cont_levels', self.kwsd['plot']['cont_levels'])
        cont_lwidths = kws.get('cont_lwidths', self.kwsd['plot']['cont_lwidths'])

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SpecfileData object mapped with a stack of EDF images

Description
===========

Utility object to connect a given scan in a SPEC file with a series
(stack) of EDF (ESRF data format) images, usually collected with a
two-dimensional detector (2D detector) during a scan
(e.g. monochromator energy scan).


STATUS
======

The current version is not generic nor stable. It should not be used
as it is, but only considered as an example. Here an elastic peak scan
from a crystal analyzer is evaluated. It permits to make/plot/save an
animation with Matplotlib.

Related
=======

- XRStools

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = "Thomas Vincent (ESRF)"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import os, sys
import copy
import numpy as np
import weakref

### Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib import cm, animation
from matplotlib import gridspec

### PyMca5 imports
from PyMca5.PyMcaIO import EdfFile
from PyMca5.PyMcaGui import PyMcaQt as qt
from PyMca5.PyMcaGui.plotting import MaskImageWidget, ImageView

### local imports
from specfiledata import SpecfileData

### UTIL CLASS ###
class RadarViewWithOverlay(ImageView.RadarView):
    """RadarView subclass adding a text overlay and a limitsChanged
listener."""

    def __init__(self, imageView, *args, **kwargs):
        self._imageView = weakref.proxy(imageView)
        self._text = ''
        self._imageView._imagePlot.sigPlotSignal.connect(self.limitsChanged)

        super(RadarViewWithOverlay, self).__init__(*args, **kwargs)

    def limitsChanged(self, event):
        if event['event'] != 'limitsChanged':
            return

        # Get histogram info for each axis
        histoX = self._imageView.getHistogram('x')
        xHisto = histoX['data']  # histogram
        xStart = histoX['extent'][0]  # Start column
        xEnd = histoX['extent'][1]  # End column

        histoY = self._imageView.getHistogram('y')
        yHisto = histoY['data']  # histogram
        yStart = histoY['extent'][0]  # Start row
        yEnd = histoY['extent'][1]  # End row

        # InfoBox
        self._text = """X: [%d, %d[
\tmin: %g
\tmax: %g

Y: [%d, %d[
\tmin: %g
\tmax: %g""" % (xStart, xEnd, xHisto.min(), xHisto.max(),
                yStart, yEnd, yHisto.min(), yHisto.max())

        self.update()

    def drawForeground(self, painter, rect):
        painter.save()
        painter.setWorldMatrixEnabled(False)
        painter.setPen(qt.QPen(qt.Qt.black, 2))
        painter.drawText(painter.viewport(),
                         qt.Qt.AlignHCenter | qt.Qt.AlignTop,
                         self._text)
        painter.setWorldMatrixEnabled(True)
        painter.restore()

### MAIN CLASS ###
class SpecWithEdfStack(SpecfileData):
    """scan data as a SPEC file plus a stack of EDF images"""

    def __init__(self, spec_fname, spec_scanno, anim_title=None,\
                 edf_root=None, edf_dir=None, edf_ext=None,
                 noisy_pxs=None, **kws):
        """load SPEC and EDF data

        Parameters
        ==========

        spec_fname : string, SPEC file name with path

        spec_scanno : int, the scan number corresponding to the edf stack to load

        anim_title : string, title shown on the animation plot

        edf_root : string, the root name of the images, before the _####.edf
                   if None, {spec_fname}_{spec_scanno} is used by default
        
        edf_dir : string, directory path where EDF images are stored
                  if None, {spec_dirname}/edf is used as default

        edf_ext : string, images extension
                  if None, '.edf' is taken as default

        noisy_pxs : list of tuples, (X,Y) coordinates of noisy pixels
                    to set to 0

        **kws : as in SpecfileData

        """
        super(SpecWithEdfStack, self).__init__(spec_fname, **kws)

        # init image plot window
        #self.miw = MaskImageWidget.MaskImageWidget()
        self.miw = ImageView.ImageViewMainWindow()
        _radarview = RadarViewWithOverlay(self.miw.imageView)
        self.miw.imageView.setRadarView(_radarview)
        self.keep_aspect_ratio(True)
        
        # animation figure layout
        self.anim_fig = plt.figure(num='SpecWithEdfStack', figsize=(5,5), dpi=150)
        gs = gridspec.GridSpec(3, 2)
        self.anim_img = plt.subplot(gs[:-1, :])
        self.anim_int = plt.subplot(gs[2, :])
        if anim_title is not None:
            self.anim_img.set_title(anim_title)
        self.anim_img.set_xlabel('Sagittal direction (pixel)')
        self.anim_img.set_ylabel('Dispersive direction (pixel)')
        self.anim_int.set_xlabel('Energy (eV)')
        self.anim_int.set_ylabel('Integrated intesity')
        self.anim_int.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        plt.ion()
        self.anim = None

        # load scan
        self.sd = self.sf.select(str(spec_scanno))
        self.mots = dict(zip(self.sf.allmotors(), self.sd.allmotorpos()))
        cntx = kws.get('cntx', self.sd.alllabels()[0])
        self.x = self.sd.datacol(cntx)
        
        if self.cmon is not None:
            self.mon = self.sd.datacol(self.cmon)
        if self.csec is not None:
            self.sec = self.sd.datacol(self.csec)

        # load images stack
        if edf_root is None:
            self.edf_root = '{0}_{1}_'.format(self.fname.split(os.sep)[-1],
                                              spec_scanno)
        else:
            self.edf_root = edf_root
        if edf_dir is None:
            self.edf_dir = os.path.join(os.path.dirname(self.fname), 'edf')
        else:
            self.edf_dir = edf_dir
        if edf_ext is None:
            self.edf_ext = '.edf'
        else:
            self.edf_ext = edf_ext
        self.load_imgs(noisy_pxs=noisy_pxs)

    def load_imgs(self, **kws):
        """load images in self.imgs list"""
        noisy_pxs = kws.get('noisy_pxs', None)
        _iload = 0
        self.imgs = []
        self.imgs_head = []
        self.imgs_int = []
        self.imgs_fname = []
        for idx, x in enumerate(self.x):
            _fname = '{0}{1}{2}{3:04d}{4}'.format(self.edf_dir,
                                                  os.sep,
                                                  self.edf_root, idx,
                                                  self.edf_ext)
            #print(_fname)
            try:
                edf = EdfFile.EdfFile(_fname, "rb")
                self.imgs_fname.append(_fname)
                _iload += 1
            except:
                print("WARNING: {0} not found => NOT LOADED!".format(_fname))
                continue
            data = edf.GetData(0)
            header = edf.GetHeader(0)
            if (noisy_pxs is not None) and type(noisy_pxs == list):
                for px in noisy_pxs:
                    try:
                        data[px[1], px[0]] = 0
                    except:
                        print("WARNING: something wrong with 'noisy_pxs'")
                        continue
            _int = np.trapz(np.trapz(data))
            self.imgs.append(data)
            self.imgs_head.append(header)
            self.imgs_int.append(_int)
        edf = None
        print('Loaded {0} images'.format(_iload))

    def keep_aspect_ratio(self, flag=True):
        """wrapper to self.miw.imageView._imagePlot.keepDataAspectRatio"""
        self.miw.imageView._imagePlot.keepDataAspectRatio(flag)
        
    def slice_stack(self, rowmin, rowmax, colmin, colmax):
        """crop the stack"""
        for idx, img in enumerate(self.imgs):
            shp = img.shape
            try:
                self.imgs[idx] = img[rowmin:rowmax, colmin:colmax]
                _int = np.trapz(np.trapz(self.imgs[idx]))
                self.imgs_int[idx] = _int
            except:
                print('Error slicing image {0}, shape is {1}'.format(idx, shp))
        
    def plot_image(self, idx, cmap_min=0, cmap_max=10):
        """show given image index"""
        #with MaskImageWidget
        #self.miw.setImageData(self.imgs[idx])
        #self.miw.colormap = [1, False, cmap_min, cmap_max,\
        #                  self.imgs[idx].min(), self.imgs[idx].max(), 0]
        #self.miw.plotImage(update=True)
        #with ImageView
        self.miw.setImage(self.imgs[idx])
        cmapdict = {'name' : 'Blues',
                    'normalization' : 'linear',
                    'autoscale' : False,
                    'vmin' : cmap_min,
                    'vmax' : cmap_max}
        self.miw.imageView.setColormap(cmapdict)
        self.miw.imageView.replot()
        self.miw.show()

    def plot_set_limits(self, xmin, xmax, ymin, ymax):
        """set limits on the imageView and replot"""
        self.miw.imageView.setLimits(xmin, xmax, ymin, ymax)
        self.miw.imageView.replot()
        
    def make_animation(self, cmap_min=0, cmap_max=10, cmap=cm.Blues):
        """animation with matplotlib"""
        self.imgs_mpl = []
        norm = cm.colors.Normalize(vmin=cmap_min, vmax=cmap_max)
        for idx, (img, _x, _int) in enumerate(zip(self.imgs, self.x, self.imgs_int)):
            impl = self.anim_img.imshow(img, norm=norm, cmap=cmap, origin='lower')
            iint_ln, = self.anim_int.plot(self.x*1000, self.imgs_int,\
                                          linestyle='-', linewidth=1.5,\
                                          color='gray')
            iint_mk, = self.anim_int.plot(_x*1000, _int, linestyle='',\
                                          marker='o', markersize=5,\
                                          color='black')
            self.imgs_mpl.append([impl, iint_ln, iint_mk])

    def plot_animation(self):
        """plot the animation"""
        # blit=True updates only what is really changed
        #THIS WILL NOT WORK TO SAVE THE VIDEO!!!
        self.anim = animation.ArtistAnimation(self.anim_fig,\
                                              self.imgs_mpl,\
                                              interval=100,\
                                              blit=False,\
                                              repeat_delay=1000)
        #plt.subplots_adjust()
        plt.show()

    def save_animation(self, anim_save, writer=None, fps=30,\
                       extra_args=['-vcodec', 'libx264']):
        """save the animation to {anim_save}"""

        if writer is None:
            writer = animation.FFMpegWriter()
        print('saving animation... (NOTE: may take a while!)')
        self.anim.save(anim_save, writer=writer, fps=fps, extra_args=extra_args)

if __name__ == '__main__':
    pass

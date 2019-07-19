#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RIXS data object
================

"""
import numpy as np

from sloth.utils.logging import getLogger
_logger = getLogger('rixsdata')  #: module logger

class RixsData(object):
    """RIXS plane object"""

    _x, _y, _zz = None, None, None
    _xc, _yc, _zzc = None, None, None

    _xlabel = 'Incoming energy (eV)'
    _ylabel = 'Emitted energy (eV)'
    _etlabel = 'Energy transfer (eV)'


    def __init__(self, label=None, logger=None):
        """Constructor"""

        if label is None:
            label = 'rd{0}'.format(hex(id(self)))
        self.label = label

        if logger is None:
            logger = _logger
        self._logger = _logger

        self._plotter = None


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
        self._x = rxdict['ene_in']
        self._y = rxdict['ene_out']
        self._zz = rxdict['rixs']


    def load_from_h5(self, fname):
        """Load RIXS from HDF5 file"""
        from silx.io.dictdump import h5todict
        rxdict = h5todict(fname)
        rxdict['sample_name'] = rxdict['sample_name'].tostring().decode()
        self.load_from_dict(rxdict)
        self._logger.info(f"RIXS map loade from {fname}")


    def crop(self, crop_area):
        """Crop the plane in a given range / matrix approach (current)

        Parameters
        ----------
        crop_area : tuple
            (x1, y1, x2, y2) : floats
            x1 < x2 (ene_in)
            y1 < y2 (ene_out)

        """
        x1, y1, x2, y2 = crop_area
        ix1 = np.abs(self._x-x1).argmin()
        iy1 = np.abs(self._y-y1).argmin()
        ix2 = np.abs(self._x-x2).argmin()
        iy2 = np.abs(self._y-y2).argmin()
        self._crop_area = crop_area
        self._xc = self._x[ix1:ix2]
        self._yc = self._y[iy1:iy2]
        self._zzc = self._zz[iy1:iy2, ix1:ix2]

    def norm(self):
        """Simple map normalization to max-min"""
        self._zzn = self._zz/(np.nanmax(self._zz)-np.nanmin(self._zz))


    def getPlotter(self):
        """Get a default plotter"""
        if self._plotter is None:
            from sloth.gui.plot.plotrixs import RixsPlot2D
            self._plotter = RixsPlot2D(logger=self._logger)
        return self._plotter

    def plot(self, plotter=None, nlevels=50, crop=False):
        """Data plotter"""
        if plotter is None:
            plotter = self.getPlotter()
        else:
            self._plotter = plotter
        plotter.clear()
        if type(crop) is tuple:
            self.crop(*crop)
        if crop:
            _title = f"{self.label} [CROP: {self._crop_area}]"
            plotter.addImage(self._zzc, x=self._xc, y=self._yc, title=_title,
                             xlabel=self._xlabel, ylabel=self._ylabel)
        else:
            plotter.addImage(self._zz, x=self._x, y=self._y, title=self.label,
                             xlabel=self._xlabel, ylabel=self._ylabel)
        plotter.addContours(nlevels)
        plotter.show()

if __name__ == '__main__':
    pass

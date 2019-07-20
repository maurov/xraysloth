#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RIXS data object
================

"""
import numpy as np

from silx.io.dictdump import dicttoh5, h5todict

from sloth.utils.logging import getLogger
_logger = getLogger('rixsdata')  #: module logger

class RixsData(object):
    """RIXS plane object"""

    sample_name = 'Unknown'

    ein, eout, rmap = None, None, None
    ein_c, eout_c, rmap_c = None, None, None

    ein_label = 'Incoming energy (eV)'
    eout_label = 'Emitted energy (eV)'
    et_label = 'Energy transfer (eV)'

    _plotter = None

    def __init__(self, name=None, logger=None):
        """Constructor"""

        self.__name__ = name or 'RixsData_{0}'.format(hex(id(self)))
        self._logger = logger or _logger


    def load_from_dict(self, rxdict):
        """Load RIXS data from a dictionary

        Parameters
        ----------
        rxdict : dict
            Required structure
            {
             'sample_name': str,
             'ein': 1D array,
             'eout': 1D array,
             'rmap': 2D array,
            }

        Return
        ------
        None, set attributes: self.x, self.y, self.zz, self.label
        """
        self.__dict__.update(rxdict)


    def load_from_h5(self, fname):
        """Load RIXS from HDF5 file"""
        rxdict = h5todict(fname)
        rxdict['sample_name'] = rxdict['sample_name'].tostring().decode()
        self.load_from_dict(rxdict)
        self._logger.info(f"RIXS map loaded from {fname}")


    def save_to_h5(self, fname):
        """Dump dictionary representation to HDF5 file"""
        dicttoh5(self.__dict__)
        self._logger.info(f"RixsData saved to {fname}")


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
        ix1 = np.abs(self.ein-x1).argmin()
        iy1 = np.abs(self.eout-y1).argmin()
        ix2 = np.abs(self.ein-x2).argmin()
        iy2 = np.abs(self.eout-y2).argmin()
        self._crop_area = crop_area
        self.ein_c = self.ein[ix1:ix2]
        self.eout_c = self.eout[iy1:iy2]
        self.rmap_c = self.rmap[iy1:iy2, ix1:ix2]


    def norm(self):
        """Simple map normalization to max-min"""
        self.rmap_norm = self.rmap/(np.nanmax(self.rmap)-np.nanmin(self.rmap))


    def getPlotter(self):
        """Get a default plotter"""
        if self._plotter is None:
            from sloth.gui.plot.plotrixs import RixsPlot2D
            self._plotter = RixsPlot2D(logger=self._logger)
        return self._plotter


    def plot(self, plotter=None, crop=False, nlevels=50):
        """Data plotter"""
        if plotter is None:
            plotter = self.getPlotter()
        else:
            self._plotter = plotter
        plotter.clear()
        if type(crop) is tuple:
            self.crop(crop)
        if crop:
            _title = f"{self.sample_name} [CROP: {self._crop_area}]"
            plotter.addImage(self.rmap_c, x=self.ein_c, y=self.eout_c, title=_title,
                             xlabel=self.ein_label, ylabel=self.eout_label)
        else:
            plotter.addImage(self.rmap, x=self.ein, y=self.eout, title=self.sample_name,
                             xlabel=self.ein_label, ylabel=self.eout_label)
        plotter.addContours(nlevels)
        plotter.show()

if __name__ == '__main__':
    pass

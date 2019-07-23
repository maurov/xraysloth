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

def get_rixs_et(rixs_map, ene_in, ene_out):
    """Rotate a RIXS map to energy transfer


    """
    assert type(ene_in) is np.ndarray and (len(rixs_map.shape)==1), "'ene_in' should be 1D Numpy array"
    assert type(ene_out) is np.ndarray and (len(rixs_map.shape)==1), "'ene_out' should be 1D Numpy array"
    assert (type(rixs_map) is np.ndarray) and (len(rixs_map.shape)==2), "'rixs_map' should be 2D Numpy array"
    ene_et = ene_in - ene_out
    # TODO
    return


class RixsData(object):
    """RIXS plane object"""

    sample_name = 'Unknown'

    counter_all, counter_signal, counter_norm = None, None, None

    ene_in, ene_out, rixs_map = None, None, None
    ene_et, rixs_et_map = None, None
    ene_in_crop, ene_out_crop, rixs_map_crop = None, None, None
    ene_grid, ene_unit = None, None

    ene_in_label = 'Incoming energy (eV)'
    ene_out_label = 'Emitted energy (eV)'
    ene_et_label = 'Energy transfer (eV)'

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
            Minimal required structure
            {
             'sample_name': str,
             'ene_in': 1D array,
             'ene_out': 1D array,
             'rixs_map': 2D array,
            }

        Return
        ------
        None, set attributes: self.*
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
        ix1 = np.abs(self.ene_in-x1).argmin()
        iy1 = np.abs(self.ene_out-y1).argmin()
        ix2 = np.abs(self.ene_in-x2).argmin()
        iy2 = np.abs(self.ene_out-y2).argmin()
        self._crop_area = crop_area
        self.ene_in_crop = self.ene_in[ix1:ix2]
        self.ene_out_crop = self.ene_out[iy1:iy2]
        self.rixs_map_crop = self.rixs_map[iy1:iy2, ix1:ix2]


    def norm(self):
        """Simple map normalization to max-min"""
        self.rixs_map_norm = self.rixs_map/(np.nanmax(self.rixs_map)-np.nanmin(self.rixs_map))


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
            plotter.addImage(self.rixs_map_crop,
                             x=self.ene_in_crop,
                             y=self.ene_out_crop,
                             title=_title,
                             xlabel=self.ene_in_label,
                             ylabel=self.ene_out_label)
        else:
            plotter.addImage(self.rixs_map,
                             x=self.ene_in,
                             y=self.ene_out,
                             title=self.sample_name,
                             xlabel=self.ene_in_label,
                             ylabel=self.ene_out_label)
        plotter.addContours(nlevels)
        plotter.show()

if __name__ == '__main__':
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RIXS data reader for beamline BM16 @ ESRF
=========================================

.. note: RIXS stands for Resonant Inelastic X-ray Scattering

.. note: BM16 is FAME-UHD, French CRG beamline

"""
import os
import time
import glob
import numpy as np
from silx.io.dictdump import dicttoh5

from larch.io.specfile_reader import DataSourceSpecH5, _mot2array
from larch.io.rixs_esrf_fame import get_rixs_bm16

from sloth.fit.peakfit_silx import fit_splitpvoigt
from sloth.utils.logging import getLogger
_logger = getLogger('io_rixs_bm16')

def get_xyz_bm16(logobj, specobj, fit_elastic=False):
    """function to get 3 arrays representing the RIXS plane

    .. note: this scheme is currently used at FAME-UHD beamline (ESRF/BM16) and
             requires a SPEC file and log file

    Parameters
    ----------
    logobj : numpy.ndarray or str
        2lD columns array (scanN, eneKeV) or RIXS log file name
    specobj : SpecfileData object
    fit_elastic : [False] controls if the elastic peak should be fitted
                  if True:
                      - fits the elastic peak with a SplitPseudoVoigt
                        function
                      - substract the fitted function from the data
                      - reset the energy array to the mono energy at the
                        center of FWHM
    Returns
    -------
    xcol, ycol, zcol: 1D arrays

    """
    
    _logger.warning("!!!DEPRECATED!!! -> use `get_rixs_bm16` from larch.io.rixs_esrf_fame")

    if isinstance(logobj, str):
        logobj = np.genfromtxt(logobj, delimiter=',', comments='#')
    scans = logobj[:, 0]  # list of scan numers
    enes = logobj[:, 1] * 1000  # in eV
    _counter = 0
    for scan, ene in zip(scans, enes):
        try:
            x, z, mot, info = specobj.get_scan('{0}.2'.format(int(scan)))
        except KeyError:
            x, z, mot, info = specobj.get_scan('{0}.1'.format(int(scan)))
        print("INFO: loaded scan {0}".format(int(scan)))
        y = _mot2array(ene, x)
        # perform some data treatment -> TODO: move elsewhere!!!
        if fit_elastic is True:
            fit, pw = fit_splitpvoigt(x, z, bkg='No Background', plot=False)
            x = x - fit.resdict['position'] + ene
            # z = fit.residual
        if _counter == 0:
            xcol = x
            ycol = y
            zcol = z
        else:
            xcol = np.append(xcol, x)
            ycol = np.append(ycol, y)
            zcol = np.append(zcol, z)
        _counter += 1
    return xcol, ycol, zcol

if __name__ == '__main__':
    pass

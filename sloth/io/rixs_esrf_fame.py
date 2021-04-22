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
from sloth.io.specfile_reader import _mot2array
from sloth.fit.peakfit_silx import fit_splitpvoigt
from sloth.io.datasource_spech5 import DataSourceSpecH5
from silx.io.dictdump import dicttoh5

from sloth.utils.logging import getLogger
_logger = getLogger('io_rixs_bm16')

def _parse_header(fname):
    """Get parsed header for the RIXS_###.log file
    Return
    ------
    header : dict
    """
    with open(fname) as f:
        lines = f.read().splitlines()
    header_lines = [line[1:] for line in lines if line[0] == '#']
    header = {}
    for line in header_lines:
        ls = line.split(": ")
        try:
            k, v = ls[0], ls[1]
        except IndexError:
            pass
        for s in ('START', 'END', 'STEP'):
            if s in k:
                v = float(v)
        header[k] = v
    return header

def get_rixs_bm16(rixs_logfn, sample_name='UNKNOWN_SAMPLE', out_dir=None, counter_signal='absF1', counter_norm=None, interp_ene_in=True, save_rixs=False):
    """Build RIXS map as X,Y,Z 1D arrays
    Parameters
    ----------
    rixs_logfn : str
        path to the RIXS_###.log file
    sample_name : str, optional ['UNKNOWN_SAMPLE']
    out_dir : str, optional
        path to save the data [None -> data_dir]
    counter_signal : str
        name of the data column to use as signal
    counter_norm : str
        name of the data column to use as normaliztion
    interp_ene_in: bool
        perform interpolation ene_in to the energy step of ene_out [True]
    save_rixs : bool
        if True -> save outdict to disk (in 'out_dir')
    Returns
    -------
    outdict : dict
        {
        '_x': array, energy in
        '_y': array, energy out
        '_z': array, signal
        'writer_name': str,
        'writer_version': str,
        'writer_timestamp': str,
        'filename_all' : list,
        'filename_root': str,
        'name_sample': str,
        'name_scan': str,
        'counter_all': str,
        'counter_signal': str,
        'counter_norm': str,
        'ene_grid': float,
        'ene_unit': str,
        }
    """
    _writer = 'get_rixs_bm16'
    _writer_version = '2021-04'  #: used for reading back in RixsData.load_from_h5()
    _writer_timestamp = '{0:04d}-{1:02d}-{2:02d}_{3:02d}{4:02d}'.format(*time.localtime())
    header = _parse_header(rixs_logfn)
    sfn = header["DATAFILE"]
    scntype = header["RIXS_SCAN_TYPE"]
    data_dir = os.path.join(os.sep, *sfn.split('/')[1:-1])
    if out_dir is None:
        out_dir = data_dir
    ds = DataSourceSpecH5(sfn, logger=_logger)

    logobj = np.genfromtxt(logobj, delimiter=',', comments='#')
    scans = logobj[:, 0]  # list of scan numers
    enes = logobj[:, 1] * 1000  # in eV

    _counter = 0
    for scan, estep in zip(scans, enes):
        try:
            ds.set_scan(scan)
            escan, sig, lab, attrs = ds.get_curve(counter_signal)
        except Exception:
            _logger.error(f"cannot load scan {scan}!")
            continue
        if scntype == 'rixs_et':
            x = _mot2array(enestep, escan)
            y = escan
        else:
            x = escan
            y = _mot2array(enestep, escan)
        if _counter == 0:
            xcol = x
            ycol = y
            zcol = z
        else:
            xcol = np.append(xcol, x)
            ycol = np.append(ycol, y)
            zcol = np.append(zcol, z)
        _counter += 1
        _logger.info(f"Loaded scan {scan}: {estep} eV")

    outdict = {
        '_x': _xcol,
        '_y': _ycol,
        '_z': _zcol,
        'writer_name': _writer,
        'writer_version': _writer_version,
        'writer_timestamp': _writer_timestamp,
        'counter_signal': counter_signal,
        'counter_norm': counter_norm,
        'sample_name': sample_name,
        'ene_unit': 'eV',
        'rixs_header': header,
        'data_dir': data_dir,
        'out_dir': out_dir,
        }

    if save_rixs:
        fnout = "{0}_rixs.h5".format(fnstr)
        dicttoh5(outdict, os.path.join(out_dir, fnout))
        _logger.info("RIXS saved to {0}".format(fnout))

    return outdict

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

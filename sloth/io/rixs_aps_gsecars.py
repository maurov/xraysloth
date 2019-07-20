#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RIXS data reader for beamline 13-ID-E @ APS
===========================================

.. note: RIXS stands for Resonant Inelastic X-ray Scattering

.. note: 13-ID-E is GSECARS-CAT

"""
import os
import numpy as np
import glob

from silx.io.dictdump import dicttoh5

from sloth.utils.logging import getLogger
_logger = getLogger('io_gsecars_rixs')


def _parse_header(fname):
    """Get parsed header

    Return
    ------
    header : dict
        {
        'columns': list of strings,
        'Analyzer.Energy': float,
        }
    """
    with open(fname) as f:
        lines = f.read().splitlines()
    header_lines = [line[2:] for line in lines if line[0] == '#']
    header = {}
    for line in header_lines:
        if 'Analyzer.Energy' in line:
            ene_line = line.split(' ')
            break
        else:
            ene_line = ['Analyzer.Energy:', '0', '', '||', '', '13XRM:ANA:Energy.VAL']  #: expected line
    header['Analyzer.energy'] = float(ene_line[1])
    header['columns'] = header_lines[-1].split('\t')
    return header


def get_rixs_13ide(sample_name, scan_name, rixs_no='001', data_dir='.',
                  counter_signal='ROI1', counter_norm=None, save_rixs=False):
    """Build RIXS map without XY gridding, line-by-line interpolation

    Parameters
    ----------
    sample_name : str
    scan_name : str
    rixs_no : str, optional
        length 3 string, ['001']
    data_dir : str, optional
        path to the data ['.']
    counter_signal : str
        name of the data column to use as signal
    counter_norm : str
        name of the data column to use as normaliztion
    save_rixs : bool
        if True -> save rixs numpy array to disk

    Returns
    -------
    outdict : dict
        {
        'filename_root': str,
        'sample_name': str,
        'scan_name': str,
        'counter_signal': str,
        'counter_norm': str,
        'ene_in': 1D array,
        'ene_out': 1D array,
        'rixs': 2D array,
        }

    """
    fnstr = "{0}_{1}".format(scan_name, sample_name)
    grepstr = "{0}*.{1}".format(fnstr, rixs_no)
    fnames = glob.glob(os.path.join(data_dir, grepstr))
    enes = np.sort(np.array([_parse_header(fname)['Analyzer.energy'] for fname in fnames]))
    estep = round(np.average(enes[1:]-enes[:-1]), 2)

    fname0 = fnames[0]
    header = _parse_header(fname0)
    cols = header['columns']
    ix = cols.index('Energy') or 0
    iz = cols.index(counter_signal)
    i0 = cols.index(counter_norm)
    dat = np.loadtxt(fname0)
    x0 = dat[:, ix]
    xnew = np.arange(x0.min(), x0.max(), estep)
    if counter_norm is not None:
        z0 = dat[:, iz] / dat[:, i0]
    else:
        z0 = dat[:, iz]

    _scan = 0
    _signals = []
    for ifn, fname in enumerate(fnames):
        dat = np.loadtxt(fname)
        x = dat[:, ix]
        if counter_norm is not None:
            z = dat[:, iz] / dat[:, i0]
        else:
            z = dat[:, iz]
        znew = np.interp(xnew, x0, z)
        _signals.append(znew)
        _logger.info(f"Loaded scan {_scan+1}: {enes[ifn]} eV")
        _scan += 1

    rixs = np.array(_signals)

    outdict = {
        'ein': np.array(xnew),
        'eout': np.array(enes),
        'rmap': rixs,
        'e_grid': estep,
        'e_unit': 'eV',
        'filename_root': fnstr,
        'sample_name': sample_name,
        'scan_name': scan_name,
        'counter_signal': counter_signal,
        'counter_norm': counter_norm,
    }

    if save_rixs:
        fnout = "{0}_rixs.h5".format(fnstr)
        dicttoh5(outdict, os.path.join(data_dir, fnout))
        _logger.info(f"RIXS saved to {fnout}")

    return outdict


def get_xyz_13ide(sample_name, scan_name, rixs_no='001', data_dir='.',
                  counter_signal='ROI1', counter_norm=None):
    """function to get 3 arrays representing the RIXS plane

    .. note: better use get_rixs_13ide

    Parameters
    ----------
    sample_name : str
    scan_name : str
    rixs_no : str, optional
        length 3 string, ['001']
    data_dir : str, optional
        path to the data ['.']
    counter_signal : str
        name of the data column to use as signal
    counter_norm : str
        name of the data column to use as normaliztion

    Returns
    -------
    xcol, ycol, zcol: 1D arrays

    """
    grepstr = "{0}_{1}.{2}*.{2}".format(scan_name, sample_name, rixs_no)
    fnames = glob.glob(os.path.join(data_dir, grepstr))
    _scan = 0
    for fname in fnames:
        header = _parse_header(fname)
        emi = header['Analyzer.energy']
        cols = header['columns']
        ix = cols.index('Energy') or 0
        iy = cols.index(counter_signal)
        i0 = cols.index(counter_norm)
        dat = np.loadtxt(fname)
        x = dat[:, ix]
        y = np.ones_like(x) * emi
        if counter_norm is not None:
            z = dat[:, iy] / dat[:, i0]
        else:
            z = dat[:, iy]
        if _scan == 0:
            xcol = x
            ycol = y
            zcol = z
        else:
            xcol = np.append(xcol, x)
            ycol = np.append(ycol, y)
            zcol = np.append(zcol, z)
        _logger.info(f"Loaded scan {_scan+1}: {emi} eV")
        _scan += 1

    return xcol, ycol, zcol


if __name__ == '__main__':
    pass

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
                   out_dir=None, counter_signal='ROI1', counter_norm=None,
                   save_rixs=False):
    """Build RIXS map without XY gridding, line-by-line interpolation

    Parameters
    ----------
    sample_name : str
    scan_name : str
    rixs_no : str, optional
        length 3 string, ['001']
    data_dir : str, optional
        path to the data ['.']
    out_dir : str, optional
        path to save the data [None -> data_dir]
    counter_signal : str
        name of the data column to use as signal
    counter_norm : str
        name of the data column to use as normaliztion
    save_rixs : bool
        if True -> save outdict to disk (in 'out_dir')

    Returns
    -------
    outdict : dict
        {
        'filename_all' : list,
        'filename_root': str,
        'sample_name': str,
        'scan_name': str,
        'counters': str,
        'counter_signal': str,
        'counter_norm': str,
        'ene_in': 1D array,
        'ene_out': 1D array,
        'ene_grid': float,
        'ene_unit': str,
        'rixs_map': 2D array,
        }

    """
    if out_dir is None:
        out_dir = data_dir
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
        ynew = np.ones_like(xnew) * enes[ifn]
        if counter_norm is not None:
            z = dat[:, iz] / dat[:, i0]
        else:
            z = dat[:, iz]
        znew = np.interp(xnew, x0, z)

        if ifn == 0:
            _xcol = xnew
            _ycol = ynew
            _zcol = znew
        else:
            _xcol = np.append(xnew, _xcol)
            _ycol = np.append(ynew, _ycol)
            _zcol = np.append(znew, _zcol)
        _signals.append(znew)
        _logger.info(f"Loaded scan {_scan+1}: {enes[ifn]} eV")
        _scan += 1
    rixs = np.array(_signals)

    #: make energy transfer array
    ene_in = np.array(xnew)
    ene_out = np.array(enes)
    et_min = round(ene_in[0] - ene_out[-1], 2)
    et_max = round(ene_in[-1] - ene_out[0], 2)
    ene_et = np.arange(et_min, et_max+estep, estep)

    outdict = {
        'ene_in': ene_in,
        'ene_out': ene_out,
        'rixs_map': rixs,
        'ene_et' : ene_et,
        'ene_in_col' : _xcol,
        'ene_out_col' : _ycol,
        'rixs_map_col' : _zcol,
        'ene_grid': estep,
        'ene_unit': 'eV',
        'filename_root': fnstr,
        'filename_all': fnames,
        'sample_name': sample_name,
        'scan_name': scan_name,
        'counter_all': cols,
        'counter_signal': counter_signal,
        'counter_norm': counter_norm,
    }

    if save_rixs:
        fnout = "{0}_rixs.h5".format(fnstr)
        dicttoh5(outdict, os.path.join(out_dir, fnout))
        _logger.info(f"RIXS saved to {fnout}")

    return outdict


if __name__ == '__main__':
    pass

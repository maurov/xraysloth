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
from sloth.io.specfile_reader import _mot2array
import glob


def _parse_header_ene_spectro(fname):
    """Get Analyzer.Energy value from header"""
    with open(fname) as f:
        lines = f.read().splitlines()
    for line in lines:
        if 'Analyzer.Energy' in line:
            ene_line = line.split(' ')
            break
        else:
            ene_line = ['#', 'Analyzer.Energy:', '0', '', '||', '', '13XRM:ANA:Energy.VAL']  #: expected header line
    return float(ene_line[2])


def get_xyz_13ide(sample_name, scan_name, rixs_no='001', data_dir='.'):
    """function to get 3 arrays representing the RIXS plane

    .. note: this scheme is currently used at 13-ID-E


    Parameters
    ----------
    sample_name : str
    scan_name : str
    rixs_no : str, optional
        length 3 string, ['001']
    data_dir : str, optional
        path to the data ['.']


    Returns
    -------
    xcol, ycol, zcol: 1D arrays

    """
    grepstr = "{0}_{1}.{2}*.{2}".format(scan_name, sample_name, rixs_no)
    fnames = glob.glob(os.path.join(data_dir, grepstr))

    return fnames

if __name__ == '__main__':
    pass

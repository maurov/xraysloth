#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parser for N42 ascii files
--------------------------

File format description:

https://www.nist.gov/programs-projects/ansiieee-n4242-standard

"""
import numpy as np


def parse_n42(fname, header_length=36, footer_length=4, to_energy=True):
    """Parse a N42 file

    Parameters
    ----------
    - fname : str
        input file name
    - header_length : int
        line number at which ends the header [36]
    - footer_length : int
        line number at which the footer starts [4]
    - to_energy : bool
        convert to energy (eV) [True]
    """
    def _getfloat(value):
        return float(value.replace(',', '.').split(' ')[0])

    #: header dict with metadata
    hdict = {}

    with open(fname) as f:
        lines = f.read().splitlines()
    # header = [line for line in lines[:header_length]]
    # footer = [line for line in lines[-footer_length:]]
    ydata = np.array([int(line) for line in lines[header_length:-footer_length]])
    xdata = np.array(range(len(ydata)))

    #: energy conversion coefficients
    ene_calib = lines[17].split('\t')[-1].split(' ')
    ene_calib = [_getfloat(coeff) for coeff in ene_calib]
    hdict['ene_calib'] = ene_calib

    #: convert to energy
    if to_energy:
        xdata = xdata * ene_calib[1] * 1000

    return xdata, ydata, hdict

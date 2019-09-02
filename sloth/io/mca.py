#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parser for MCA ascii files
--------------------------

MCA: multi channel analyzer

"""
import numpy as np


def parse_mca(fname, header_length=38, to_energy=True):
    """Parse a MCA file"""

    with open(fname) as f:
        lines = f.read().splitlines()
    header = [line.split(' = ') for line in lines[:header_length]]
    ydata = np.array([int(line) for line in lines[header_length:]])
    xdata = np.array(range(len(ydata)))

    #: convert header list to dict
    hdict = {}
    for line in header:
        try:
            hdict[line[0]] = line[1]
        except Exception:
            pass

    def _getfloat(value):
        return float(value.replace(',', '.').split(' ')[0])

    #: write ICR/OCR and DT
    icr = _getfloat(hdict['Input Count Rate'])*1000
    ocr = _getfloat(hdict['Output Count Rate'])*1000
    rt = _getfloat(hdict['Realtime'])
    dt = (icr/ocr)*rt
    hdict['ICR'] = icr
    hdict['OCR'] = ocr
    hdict['DT'] = dt

    #: get FWHM
    fwhm = _getfloat(hdict['ROI0 FWHM'])
    hdict['FWHM'] = fwhm*1000

    #: peaking time
    pkt = _getfloat(hdict['Peaking Time'])
    hdict['PT'] = pkt

    #: convert to energy
    if to_energy:
        mca2ev = _getfloat(hdict['MCA Bin Width'])
        xdata = xdata * mca2ev

    return xdata, ydata, hdict

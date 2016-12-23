#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests/Examples for convolution1D
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt

# from __init__ import _libDir
# sys.path.append(_libDir)

_curDir = os.path.dirname(os.path.realpath(__file__))

from sloth.math.convolution1D import lin_gamma, atan_gamma, conv
from sloth.xray.xdata import _core_width

### TESTS/EXAMPLES

if __name__ == '__main__':

    fdat = os.path.join(_curDir, 'convolution1D_tests.dat')
    dat = np.loadtxt(fdat)
    fdat_ck = os.path.join(_curDir, 'convolution1D_tests_check.dat')
    dat_ck = np.loadtxt(fdat_ck)

    # e, f have the same index [n]
    e = dat[:,0]
    f = dat[:,1]
   
    plt.plot(e, f)
    plt.plot(dat_ck[:,0], dat_ck[:,1])

    ch_mnk = _core_width(element='Mn', edge='K')
    
    fwhm_lin = lin_gamma(e, fwhm=ch_mnk, linbroad=[5, -6, 60])
    fwhm_atan = atan_gamma(e, ch_mnk, gamma_max=5, e0=0, eslope=1.)
    
    c = conv(e, f, kernel='lorentzian', fwhm_e=fwhm_lin, efermi=-5)
    plt.plot(e, c)
    
    plt.show()

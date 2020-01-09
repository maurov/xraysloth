#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Some common lineshapes and distribution functions

.. note:: this simply imports functions from
    - :mod:`larch.math.lineshapes`
    - :mod:`lmfit.lineshapes`

"""
import math


#: SIGMA <-> FWHM
F2S = 2 * math.sqrt(2 * math.log(2))


def fwhm2sigma(fwhm):
    """get sigma from FWHM"""
    return fwhm / F2S


def sigma2fwhm(sigma):
    """get FWHM from sigma"""
    return sigma * F2S


def lorentzian(x, amplitude=1.0, center=0.0, sigma=1.0):
    """Return a 1-dimensional Lorentzian function.

    lorentzian(x, amplitude, center, sigma) = (amplitude/(1 +
    ((1.0*x-center)/sigma)**2)) / (pi*sigma)

    """
    return (amplitude / (1 + ((1.0 * x - center) / sigma) ** 2)) / (math.pi * sigma)

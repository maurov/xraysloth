#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""examples/tests for peakfit"""

# Fix Python 2.x
from __future__ import print_function

try:
    input = raw_input
except NameError:
    pass

import os, sys
import numpy as np

try:
    from PyMca5.PyMcaIO import specfilewrapper as specfile
except Exception:
    try:
        from PyMca import specfilewrapper as specfile
    except Exception:
        from PyMca import specfile

from sloth.fit.peakfit import fit_splitpvoigt, fit_results

_curDir = os.path.dirname(os.path.realpath(__file__))


def test_mock():
    # create mock data
    import numpy as np

    try:
        from PyMca5.PyMcaMath.fitting import SpecfitFuns
    except Exception:
        from PyMca import SpecfitFuns
    x = np.linspace(0, 50, 200)
    noise = np.random.normal(size=len(x), scale=10)
    y = 80.0 - x * 0.25 + noise
    y = y + 89 * SpecfitFuns.splitpvoigt([12.5, 30.75, 12.0, 5.0, 0.5], x)
    fit, pw = fit_splitpvoigt(x, y, plot=True, show_res=True)
    return x, y, fit, pw


def test_diffpat(fname=None):
    # tests on 'diff_pat.dat'
    if fname is None:
        fname = os.path.join(_curDir, "peakfit_tests_diffpat.dat")
    try:
        sf = specfile.Specfile(fname)
    except Exception:
        print("{0} not found".format(fname))
        return
    sd = sf.select("1")
    x = sd.datacol(1)
    y = sd.datacol(7)
    sf = 0  # close file
    fit, pw = fit_splitpvoigt(x, y, plot=True, show_res=True)
    return x, y, fit, pw


def test_real(scanno, fname=None, noreturn=False):
    # tests on real data
    if fname is None:
        fname = os.path.join(_curDir, "peakfit_tests_real.dat")
    try:
        sf = specfile.Specfile(fname)
    except Exception:
        print("{0} not found".format(fname))
        return
    sd = sf.select(str(scanno))
    x = sd.datacol(1) * 1000  # eV
    csig = "apd"
    cmon = "I02"
    csec = "Seconds"
    y = (
        sd.datacol(csig)
        / sd.datacol(cmon)
        * np.mean(sd.datacol(cmon))
        / sd.datacol(csec)
    )  # cps
    fit, pw = fit_splitpvoigt(x, y, dy=True, bkg="Constant", plot=True, show_res=True)
    if noreturn:
        input("Press Enter to return (kills plot window)...")
        return
    else:
        return x, y, fit, pw


if __name__ == "__main__":
    pass
    # uncomment at your convenience!
    # x, y, fit, pw = test_mock()
    # x, y, fit, pw = test_diffpat()
    # x, y, fit, pw = test_real(45)

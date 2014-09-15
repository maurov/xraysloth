#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" examples/tests for peakfit """

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Sept 2014"

import sys, os

# https://github.com/maurov/xrayspina
_curDir = os.path.dirname(os.path.realpath(__file__))
_parDir = os.path.realpath(os.path.join(_curDir, os.path.pardir))
_spinaDir = os.path.join(_parDir, 'spina')
sys.path.append(_spinaDir)

from peakfit import fit_splitpvoigt, fit_results

def test_mock():
    # create mock data
    import numpy as np
    from PyMca import SpecfitFuns
    x = np.linspace(0, 50, 200)
    noise = np.random.normal(size=len(x), scale=10)
    y = 80.0 - x*0.25 + noise
    y = y + 89*SpecfitFuns.splitpvoigt([12.5, 30.75, 12.0, 5.0, 0.5], x)
    fit, pw = fit_splitpvoigt(x, y, plot=True, show_res=True)
    return x, y, fit, pw

def test_diffpat(fname=None):
    # tests on 'diff_pat.dat'
    try:
        from PyMca import specfilewrapper as specfile
    except:
        from PyMca import specfile
    if fname is None:
        fname = os.path.join(_curdir, 'peakfit_test_diffpat.dat')
    try:
        sf = specfile.Specfile(fname)
    except:
        print '{0} not found'.format(fname)
        return
    sd = sf.select('1')
    x = sd.datacol(1)
    y = sd.datacol(7)
    sf = 0 # close file
    fit, pw = fit_splitpvoigt(x, y, plot=True, show_res=True)
    return x, y, fit, pw

def test_real(scanno, fname=None, noreturn=False):
    # tests on real data
    try:
        from PyMca import specfilewrapper as specfile
    except:
        from PyMca import specfile
    if fname is None:
        fname = 'align_jn_01'
    try:
        sf = specfile.Specfile(fname)
    except:
        print '{0} not found'.format(fname)
        return
    sd = sf.select(str(scanno))
    x = sd.datacol(1)*1000 #eV
    csig = 'apd'
    cmon = 'I02'
    csec = 'Seconds'
    y = sd.datacol(csig)/sd.datacol(cmon)*np.mean(sd.datacol(cmon))/sd.datacol(csec) #cps
    fit, pw = fit_splitpvoigt(x, y, dy=True, bkg='Constant', plot=True, show_res=True)
    if noreturn:
        raw_input("Press Enter to return (kills plot window)...")
        return
    else:
        return x, y, fit, pw

if __name__ == '__main__':
    pass
    # uncomment at your convenience!
    #x, y, fit, pw = test_mock()
    #x, y, fit, pw = test_diffpat()
    #x, y, fit, pw = test_real(45)

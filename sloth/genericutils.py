#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
generic utilities for daily work

TODO
====
- collect here daily work utilities

"""

import numpy as np

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.1"
__status__ = "in progress"
__date__ = "Aug 2014"

### Files ###
def cp_replace(grepfns, grepstr, rplstr, splitstr='_'):
    """given a filenames search string, copy the files with replaced string

    Parameters
    ----------
    grepfns : string
              search string passed to glob to generate files list to
              copy
    grepstr : string
              string to replace
    rplstr : string
             new string
    splitstr : string, '_'
               string used as separator
    """
    import glob
    import subprocess
    fns = glob.glob(grepfns)
    for fn in fns:
        _fn2 = [w.replace(grepstr, rplstr) for w in fn.split(splitstr)]
        fn2 = splitstr.join(_fn2)
        subprocess.call('cp {0} {1}'.format(fn, fn2), shell=True)
        print(fn2)

### Numpy ###
def imin(arr, check=False):
    """ index of minimum value """
    _im = np.argmin(arr)
    if check:
        print('Check: {0} = {1}'.format(np.min(arr), arr[_im]))
    return _im
        
def imax(arr, check=False):
    """ index of maximum value """
    _im = np.argmax(arr)
    if check:
        print('Check: {0} = {1}'.format(np.max(arr), arr[_im]))
    return _im
        
### IPython ###
def ipythonAutoreload():
    """ force ipython to autoreload imported modules """
    from IPython import get_ipython
    mgc = get_ipython().magic
    mgc(u'%load_ext autoreload')
    mgc(u'%autoreload 2')

### PyMca ###
def getPyMcaMain():
    """ show PyMcaMain from a shell (e.g. IPython) and return its obj """
    from matplotlib import rcParams
    rcParams['text.usetex'] = False
    HAS_PYMCA = False
    try:
        from PyMca5.PyMcaGui.pymca import PyMcaMain
        HAS_PYMCA = True
    except:
        from PyMca import PyMcaMain
        HAS_PYMCA = True

    if HAS_PYMCA:
        m = PyMcaMain.PyMcaMain()
        m.show()
        return m
    else:
        print("PyMca not found")
        return 0

### Matplotlib ###
def mplSetPubFont(size=8, usetex=True):
    """ very basic mpl set font for publication-quality figures """
    from matplotlib import rc
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size':size})
    rc('text', usetex=usetex)

if __name__ == '__main__':
    pass

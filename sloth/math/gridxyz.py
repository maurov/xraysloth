#!/usr/bin/env python
"""
Utilities to work with 2D grids and interpolation
=================================================
"""

import numpy as np

from sloth.utils.logging import getLogger
_logger = getLogger('gridxyz')

### GLOBAL VARIABLES ###
MODNAME = '_math'


def gridxyz(xcol, ycol, zcol, xystep=None, lib='scipy', method='cubic'):
    """Grid (X, Y, Z) 1D data on a 2D regular mesh

    Parameters
    ----------
    xcol, ycol, zcol : 1D arrays repesenting the map (z is the intensity)
    xystep : the step size of the XY grid
    lib : library used for griddata
          [scipy]
          matplotlib
    method : interpolation method

    Returns
    -------
    xgrid, ygrid : 1D arrays giving abscissa and ordinate of the map
    zz : 2D array with the gridded intensity map

    See also
    --------
    - MultipleScanToMeshPlugin in PyMca
    """
    if xystep is None:
        xystep = 0.1
        _logger.warning(f"'xystep' not given: using a default value of {xystep}")
    #create the XY meshgrid and interpolate the Z on the grid
    nxpoints = int((xcol.max()-xcol.min())/xystep)
    nypoints = int((ycol.max()-ycol.min())/xystep)
    xgrid = np.linspace(xcol.min(), xcol.max(), num=nxpoints)
    ygrid = np.linspace(ycol.min(), ycol.max(), num=nypoints)
    xx, yy = np.meshgrid(xgrid, ygrid)
    if ('matplotlib' in lib.lower()):
        try:
            from matplotlib.mlab import griddata
        except ImportError:
            _logger.error("Cannot load griddata from Matplotlib")
            return
        if not (method == 'nn' or method == 'nearest'):
            _logger.warning(f"Interpolation method {method} not supported by {lib}")
        _logger.info(f"Gridding data with {lib}...")
        zz = griddata(xcol, ycol, zcol, xx, yy)
        return xgrid, ygrid, zz
    elif ('scipy' in lib.lower()):
        try:
            from scipy.interpolate import griddata
        except ImportError:
            _logger.error("Cannot load griddata from Scipy")
            return
        _logger.info(f"Gridding data with {lib}...")
        zz = griddata((xcol, ycol), zcol, (xgrid[None,:], ygrid[:,None]), method=method, fill_value=0)
        return xgrid, ygrid, zz

### LARCH ###
def gridxyz_larch(xcol, ycol, zcol, xystep=None, method='cubic', lib='scipy', _larch=None):
    """Larch equivalent of gridxyz() """
    if _larch is None:
        raise Warning("Larch broken?")
    return gridxyz(xcol, ycol, zcol, xystep=xystep, method=method, lib=lib)
gridxyz_larch.__doc__ += gridxyz.__doc__


def registerLarchPlugin():
    return (MODNAME, {'gridxyz': gridxyz_larch})


if __name__ == '__main__':
    pass

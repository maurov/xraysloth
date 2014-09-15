#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" examples/tests for xcrystalbox

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Sept 2014"

import sys, os
from datetime import date

# https://github.com/maurov/xrayspina
_curDir = os.path.dirname(os.path.realpath(__file__))
_parDir = os.path.realpath(os.path.join(_curDir, os.path.pardir))
_spinaDir = os.path.join(_parDir, 'spina')
sys.path.append(_spinaDir)

from xcrystalbox import XCrystalBox

### TESTING ###
def test_Si444():
    """reflectivity of 0.4 mm thick Si(444) bent to 50 cm meridional,
    theta - theta_Bragg scan mode
    """
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_444-E_2000_20000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (4,4,4),
                 crys_type = 2,
                 geom = 0,
                 mos_spread = None,
                 thickness = 0.04,
                 asym = 0.0,
                 scan_mode = 3,
                 scan_pos = 8000,
                 scan_ang_unit = 3,
                 scan_min = -50.,
                 scan_max = 50.,
                 scan_npts = 400,
                 r_sag = 0,
                 r_mer = 50.,
                 elast_prompt = 0,
                 elast_info = 0,
                 poisson_ratio = 0.22)
    t = XCrystalBox(opts=odict)
    return t

def test_Si444_ene():
    """reflectivity of 0.4 mm thick Si(444) bent to 50 cm meridional,
    photon energy scan mode
    """
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_444-E_2000_20000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (4,4,4),
                 crys_type = 2,
                 geom = 0,
                 mos_spread = None,
                 thickness = 0.04,
                 asym = 0.0,
                 scan_mode = 4,
                 scan_pos = 8000,
                 scan_ang_unit = 3,
                 scan_min = -1.,
                 scan_max = 1.,
                 scan_npts = 400,
                 r_sag = 0,
                 r_mer = 50.,
                 elast_prompt = 0,
                 elast_info = 0,
                 poisson_ratio = 0.22)
    t = XCrystalBox(opts=odict)
    ene_pos = 10000.
    ene_dscan = 2
    si_d111 = 3.1355
    from bragg import bragg_th
    t.setopt('scan_pos', bragg_th(ene_pos, si_d111, n=4))
    t.setopt('scan_min', ene_pos-ene_dscan)
    t.setopt('scan_max', ene_pos+ene_dscan)
    return t

if __name__ == '__main__':
    pass
    # uncomment at your convenience!
    #t = test_Si444_ene()
    #t.run()
    #t.loadRefl()
    #t.fitRefl()
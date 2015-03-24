#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" examples/tests for xcrystalbox """

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"

import sys
from datetime import date
import numpy as np

from __init__ import _libDir
sys.path.append(_libDir)

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
    t.set_opt('scan_pos', bragg_th(ene_pos, si_d111, n=4))
    t.set_opt('scan_min', ene_pos-ene_dscan)
    t.set_opt('scan_max', ene_pos+ene_dscan)
    return t

def test_Si111_loop():
    """reflectivity of 400 microns thick Si(111) bent to 50 cm meridional and sagittal,
    theta - theta_Bragg (corrected) scan mode
    loop over energy 
    """
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_111-E_1000_10000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (1,1,1),
                 crys_type = 2,
                 geom = 0,
                 mos_spread = None,
                 thickness = 0.04,
                 asym = 0.0,
                 scan_mode = 2,
                 scan_pos = 1985,
                 scan_ang_unit = 3,
                 scan_min = -50.,
                 scan_max = 50.,
                 scan_npts = 400,
                 r_sag = 50.,
                 r_mer = 50.,
                 elast_prompt = 0,
                 elast_info = 0,
                 poisson_ratio = 0.22)
    t = XCrystalBox(opts=odict)

    #energies (eV) for Si(111) in 85 -- 35 deg range (every 10 eV #5 eV)
    npts = 74 #147 #293
    scn_hlims = np.linspace(700, 70, npts)
    enes = np.linspace(1985, 3445, npts)

    t.dres = {'ene' : [],
              'elen_s' : [],
              'elen_p' : [],
              'edep_s' : [],
              'edep_p' : []}
    
    for ene, hlim in zip(enes, scn_hlims):
        t.set_opt('scan_pos', ene)
        t.set_opt('scan_min', -1*hlim)
        t.set_opt('scan_max', hlim)
        t.run()
        #t.load_refl()
        #t.fit_refl()
        t.load_pars()
        t.dres['ene'].append(ene)
        t.dres['elen_s'].append(t.pars['ext_len_amp_s'])
        t.dres['elen_p'].append(t.pars['ext_len_amp_p'])
        t.dres['edep_s'].append(t.pars['ext_dep_amp_s'])
        t.dres['edep_p'].append(t.pars['ext_dep_amp_p'])
        
    return t

def test_Si440(ene=None, edelta=2):
    """reflectivity of 0.4 mm thick Si(333) bent to 100 cm meridional and sagittal,
    theta - theta_Bragg scan mode
    """
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_440-E_2000_20000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (4,4,0),
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
                 r_sag = 100.,
                 r_mer = 100.,
                 elast_prompt = 0,
                 elast_info = 0,
                 poisson_ratio = 0.22)
    t = XCrystalBox(opts=odict)
    if ene is not None:
        t.set_opt('scan_mode', 4)
        si_d440 = 0.96008572264122927
        from bragg import bragg_th
        t.set_opt('scan_pos', bragg_th(si_d440, ene))
        t.set_opt('scan_min', ene-edelta)
        t.set_opt('scan_max', ene+edelta)
 
    return t
    
if __name__ == '__main__':
    #pass
    # uncomment at your convenience!
    #t = test_Si444_ene()
    #t.run()
    #t.load_refl()
    #t.fit_refl()
    #t.pw.close() #close last window
    #t.load_pars()
    #t = test_Si111_loop()
    t = test_Si440(ene=6685)

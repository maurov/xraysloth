#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xcrystalbox: a toolbox to work with CRYSTAL_ from Python via system
call to diff_pat

.._CRYSTAL: https://github.com/srio/CRYSTAL

TODO
----

- [] elasticity inputs

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014"
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Apr 2014"

import sys, os
import subprocess
from optparse import OptionParser
from datetime import date
import numpy as np
from peakfit import fit_splitpvoigt, fit_results

# check XOP is correctly installed and define DIFFPAT_EXEC
HAS_XOP = False
DIFFPAT_EXEC = False
try:
    HAS_XOP = os.environ["XOP_HOME"]
    _platform = sys.platform.lower()
    if 'linux' in _platform:
        DIFFPAT_EXEC = os.path.join(HAS_XOP, 'bin.linux', 'diff_pat')
    elif 'win' in _platform:
        DIFFPAT_EXEC = os.path.join(HAS_XOP, 'bin.x86', 'diff_pat.exe')
    elif 'darwin' in _platform:
        DIFFPAT_EXEC = os.path.join(HAS_XOP, 'bin.darwin', 'diff_pat')
    else:
        try:
            DIFFPAT_EXEC = os.environ["DIFFPAT_EXEC"]
        except KeyError:
            print("Please set the environment variable DIFFPAT_EXEC")
            sys.exit(1)
except KeyError: 
   print("Please set the environment variable XOP_HOME")
   sys.exit(1)

# ../xop/data
_pardir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
DATA_DIR = os.path.join(_pardir, 'xop', 'data')

class XCrystalBox(object):
    """ XCrystalBox
    
    xcrystal.inp
    ------------
    bragg_file : Name of file with crystal data (from BRAGG)
    
    crys_type : What kind of crystal you want to use:
                [0] Perfect crystal
                [1] Mosaic crystal
                [2] Bent Multilamellar (ML)
                [3] Bent Penning-Polder (PP)
                [4] Bent Takagi-Taupin => NOT IMPLEMENTED YET
             
    geom : Reflection (Bragg) or Transmission (Laue) geometry. If the
           crystal is perfect allow to calculate the transmitted (not
           diffracted beams.

           [0] Diffracted beam in Reflection (Bragg) geometry 
           [1] Diffracted beam in Transmission (Laue) geometry
           [2] Transmitted beam in Bragg case
           [3] Transmitted beam in Laue case

    mos_spread : mosaicity, mosaic angle spread (FWHM) [deg]

    thickness : crystal thickness [cm]. In the Perfect crystal case,
                the thick crystal approximation is allowed. In such
                case, the user must input any negative value.

    asym : asymmetric cut angle [deg] between face and bragg planes
           (clock-wise, CW)

    scan_mode : scanning variable
                [1] Incident/Reflected angle [absolute] 
                [2] Incident/Reflected angle minus theta Bragg corrected
                [3] Incident/Reflected angle minus theta Bragg
                [4] Photon energy 
                [5] y variable [Zachariasen]

    scan_pos : at what position?
               in energy [eV] for scan_mode < 4 or 5
               in grazing angle [deg] for scan_mode == 4
       
    scan_ang_unit : units for the angular scanning variable
                    [0] radians
                    [1] microradians
                    [2] degrees
                    [3] arcsec

    scan_min / scan_max : scanning variable limits in the chosen units

    scan_npts : number of scanning points
    
    r_sag : sagittal bending radius [cm]
    
    r_mer : meridional radius [cm]

    elast_prompt : input 0 to call elasticity_prompt
    
    elast_info : Elasticity info. Obtain compliance tensor (CT) from:
                 [0] Poisson ratio (isotropic crystal)
                 [1] hkl (for Si/Ge/C)
                 [2] crystallographic directions (for Si/Ge/C)
                 [3] external file

    poisson_ratio : Poisson ratio

    crys_idx : CrystalIndex: 0,1,2=Si,3=Ge,4=Diamond
    
    """
    def __init__(self, opts=None):
        if opts is None:
            self.opts = dict(creator = 'XCrystalBox',
                             today = date.today(),
                             bragg_file = None,
                             crys_mat = None,
                             crys_refl = None,
                             crys_type = None,
                             geom = None,
                             mos_spread = None,
                             thickness = None,
                             asym = 0.0,
                             scan_mode = None,
                             scan_pos = None,
                             scan_ang_unit = None,
                             scan_min = None,
                             scan_max = None,
                             scan_npts = None,
                             r_sag = None,
                             r_mer = None,
                             elast_prompt = 0,
                             elast_info = 0,
                             poisson_ratio = None)
        else:
            self.opts = opts

        # check all options
        self.checkopts()

    def showhelp(self):
        print self.__doc__

    def checkopts(self):
        # bragg file
        if (self.opts['bragg_file'] is None):
            raise NameError("missing 'bragg_file'")
        elif not os.path.exists(self.opts['bragg_file']):
            bf_in_datadir = os.path.join(DATA_DIR, self.opts['bragg_file'])
            if not os.path.exists(bf_in_datadir):
                raise NameError("{} not found in {}".format(self.opts['bragg_file'], DATA_DIR))
            else:
                self.opts['bragg_file'] = bf_in_datadir
        # crystal type and geometry
        if self.opts['crys_type'] is None:
            raise NameError('crystal type not given')
        if self.opts['geom'] is None:
            raise NameError('geometry type not given')
        if (self.opts['crys_type'] > 0) and (self.opts['geom'] > 1):
            raise NameError('crystal type and geometry are not compatible')
        # mosaicity (only if mosaic crystal)
        if (self.opts['crys_type'] == 1):
            if (self.opts['mos_spread'] is None):
                raise NameError('mosaicity [deg, FWHM] not given')
            else:
                self.opts['mos_spread'] = np.deg2rad(self.opts['mos_spread'])/2.35
        else:
            self.opts['mos_spread'] = '!'
        # thickness
        if self.opts['thickness'] is None:
            raise NameError('crystal thickness [cm] not given!')
        # asymmetric cut
        # scan variable
        if self.opts['scan_mode'] is None:
            raise NameError('choose scanning variable')
        else:
            if self.opts['scan_pos'] is None:
                raise NameError('energy or angle position not given')
        # scan angular unit
        if self.opts['scan_mode'] < 4:
            if self.opts['scan_ang_unit'] is None:
                raise NameError('scan angular unit not given')
        else:
            self.opts['scan_ang_unit'] = '!'
        # scan ranges
        if (self.opts['scan_min'] is None) or (self.opts['scan_max'] is None):
            raise NameError('give min/max scan ranges')
        if (self.opts['scan_npts'] is None):
            raise NameError('give scan number of points')
        # bent crystal
        if (self.opts['crys_type'] > 1):
            if (self.opts['r_sag'] is None) or (self.opts['r_mer'] is None):
                raise NameError('give sagittal/meridional radii (0 for flat)')
            if (self.opts['elast_info'] == 0) and (self.opts['poisson_ratio'] is None):
                raise NameError('Poisson ratio not given')

    def setopt(self, opt, value):
        self.opts[opt] = value
        self.checkopts()

    def winpfile(self):
        """ write xcrystal.inp """
        outlst = ['{bragg_file}']
        outlst.append('{crys_type}')
        outlst.append('{geom}')
        if (self.opts['crys_type'] == 1):
            outlst.append('{mos_spread}')
        outlst.append('{thickness:.9f}')
        outlst.append('{asym:.9f}')
        outlst.append('{scan_mode}')
        outlst.append('{scan_pos:.9f}')
        if (self.opts['scan_mode'] < 4):
            outlst.append('{scan_ang_unit}')
        outlst.append('{scan_min:.9f}')
        outlst.append('{scan_max:.9f}')
        outlst.append('{scan_npts}')
        if (self.opts['crys_type'] > 1):
            outlst.append('{r_sag}')
            outlst.append('{r_mer}')
            outlst.append('{elast_prompt}')
            outlst.append('{elast_info}')
            outlst.append('{poisson_ratio}')
            
        outstr = '\n'.join(outlst)
        outstr = outstr.format(**self.opts)
        print outstr
        f = open('xcrystal.inp', 'w')
        f.write(outstr)
        f.close()
        
    def run(self):
        """ runs diff_pat """
        self.winpfile() # write xcrystal.inp
        cmdstr = '{} < xcrystal.inp'.format(DIFFPAT_EXEC)
        print cmdstr
        try:
            subprocess.call(cmdstr, shell=True) 
        except OSError:
            print "check 'diff_pat' executable exists!"

    def evaluate(self):
        """ evaluate diff_pat.dat """
        try:
            from PyMca import specfilewrapper as specfile
        except:
            from PyMca import specfile
        sf = specfile.Specfile('diff_pat.dat')
        sd = sf.select('1')
        self.x = sd.datacol(1)
        self.y = sd.datacol(7)
        sf = 0 # close file
        self.fit, self.pw = fit_splitpvoigt(self.x, self.y, plot=True)

### TESTING ###
def test_Si444():
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_444-E_2000_20000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (1,1,1),
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
    odict = dict(creator = 'XCrystalBox/test',
                 today = date.today(),
                 bragg_file = 'Si_444-E_2000_20000_50-A_3-T_1.bragg',
                 crys_mat = 'Si',
                 crys_refl = (1,1,1),
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
    #pass
    t = test_Si444_ene()
    t.run()
    t.evaluate()
    fit_results(t.fit)

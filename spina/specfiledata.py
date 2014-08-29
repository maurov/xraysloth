#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SpecfileData object to work with SPEC files from Certified Scientific
Software (http://www.certif.com/)

Requirements
============
- specfilewrapper from PyMca distribution (http://pymca.sourceforge.net/)
- gridutils plugin (https://github.com/maurov/larch_plugins)

Related
=======
- specfiledatawriter plugin (https://github.com/maurov/spectrox)

TODO
====
- _pymca_average() : use faster scipy.interpolate.interp1d
- implement a 2D normalization in get_map
- implement the case of dichroic measurements (two consecutive scans
  with flipped helicity)
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = "Matt Newville"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2013-2014"
__version__ = "0.9.6"
__status__ = "Beta"
__date__ = "Aug 2014"

import os, sys
import numpy as np

# Mauro's Larch Plugins (https://github.com/maurov/larch_plugins)
HAS_GRIDUTILS = False
try:
    from gridutils import _gridxyz
    HAS_GRIDUTILS = True
except:
    pass

# PyMca
HAS_SPECFILE = False
try:
    from PyMca import specfilewrapper as specfile
    HAS_SPECFILE = True
except ImportError:
    try:
        from PyMca import specfile
        HAS_SPECFILE = True
    except ImportError:
        try:
            from PyMca5.PyMcaIO import specfilewrapper as specfile
            HAS_SPECFILE = True
        except ImportError:
            pass
HAS_SIMPLEMATH = False
try:
    from PyMca import SimpleMath
    HAS_SIMPLEMATH = True
except ImportError:
    pass

### UTILITIES (the class is below!)
def _str2rng(rngstr, keeporder=True):
    """ simple utility to convert a generic string representing a
    compact list of scans to a sorted list of integers

    Example
    -------
    > _str2rng('100, 7:9, 130:140:5, 14, 16:18:1')
    > [7, 8, 9, 14, 16, 17, 18, 100, 130, 135, 140]

    NOTE: by default it keeps the original order, this can be turned
          into a sorted list by the keyword argument 'keeporder=False'
    """
    _rng = []
    for _r in rngstr.split(', '): #the space is important!
        if (len(_r.split(',')) > 1):
            raise NameError("Space after comma(s) is missing in '{0}'".format(_r))
        _rsplit2 = _r.split(':')
        if (len(_rsplit2) == 1):
            _rng.append(_r)
        elif (len(_rsplit2) == 2 or len(_rsplit2) == 3):
            if len(_rsplit2) == 2 :
                _rsplit2.append('1')
            if (_rsplit2[0] == _rsplit2[1]):
                raise NameError("Wrong range '{0}' in string '{1}'".format(_r, rngstr))
            if (int(_rsplit2[0]) > int(_rsplit2[1])):
                raise NameError("Wrong range '{0}' in string '{1}'".format(_r, rngstr))
            _rng.extend(range(int(_rsplit2[0]), int(_rsplit2[1])+1, int(_rsplit2[2])))
        else:
            raise NameError('Too many colon in {0}'.format(_r))

    #create the list and return it (removing the duplicates)
    _rngout = [int(x) for x in _rng]

    def uniquify(seq):
        # Order preserving uniquifier by Dave Kirby
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]

    if keeporder:
        return uniquify(_rngout)
    else:
        return list(set(_rngout))

def _mot2array(motor, acopy):
    """ simple utility to generate a copy of an array containing a
    constant value (e.g. motor position) """
    a = np.ones_like(acopy)
    return np.multiply(a, motor)

def _div_check(num, dnum):
    """simple division check to avoid ZeroDivisionError"""
    try:
        return num/dnum
    except ZeroDivisionError:
        print("ERROR: found a division by zero")

def _pymca_average(xdats, zdats):
    """ call to SimpleMath.average() method from PyMca/SimpleMath.py

    Parameters
    ----------
    - xdats, ydats : lists of arrays contaning the data to merge

    Returns
    -------
    - xmrg, zmrg : 1D arrays containing the merged data
    """
    if HAS_SIMPLEMATH:
        sm = SimpleMath.SimpleMath()
        print("Merging data...")
        return sm.average(xdats, zdats)
    else:
        raise NameError("SimpleMath is not available -- this operation cannot be performed!")

### MAIN CLASS
class SpecfileData(object):
    """SpecfileData object"""
    def __init__(self, fname=None, cntx=1, cnty=None, csig=None, cmon=None, csec=None, norm=None):
        """reads the given specfile"""
        if (fname == 'DUMMY!'):
            return
        if (HAS_SPECFILE is False):
            print("WARNING: 'specfile' is missing -> check requirements!")
            return
        if fname is None:
            raise NameError("Provide a SPEC data file to load with full path")
        elif not os.path.isfile(fname):
            raise OSError("File not found: '%s'" % fname)
        else:
            self.fname = fname
            if hasattr(self, 'sf'):
                pass
            else:
                self.sf = specfile.Specfile(fname) #sf = specfile file
                print("Loaded SPEC file: {0}".format(fname))
                # print("The total number of scans is: {0}".format(self.sf.scanno())
        #set common attributes
        self.cntx = cntx
        self.cnty = cnty
        self.csig = csig
        self.cmon = cmon
        self.csec = csec
        self.norm = norm

    def get_scan(self, scan=None, scnt=None, **kws):
        """ get a single scan from a SPEC file

        Parameters
        ----------
        scan : scan number to get [integer]
        cntx : counter for x axis, motor 1 scanned [string]
        cnty : counter for y axis, motor 2 steps [string] - used by get_map()
        csig : counter for signal [string]
        cmon : counter for monitor/normalization [string]
        csec : counter for time in seconds [string]
        scnt : scan type [string]
        norm : normalization [string]
               'max' -> z/max(z)
               'max-min' -> (z-min(z))/(max(z)-min(z))
               'area' -> (z-min(z))/trapz(z, x)
               'sum' -> (z-min(z)/sum(z)
 
        Returns
        -------
        scan_datx : 1D array with x data (scanned axis)
        scan_datz : 1D array with z data (intensity axis)
        scan_mots : dictionary with all motors positions for the given scan
                    NOTE: if cnty is given, it will return only scan_mots[cnty]
        scan_info : dictionary with information on the scan
        """
        if HAS_SPECFILE is False:
            raise NameError("Specfile not available!")
        
        #get keywords arguments
        cntx = kws.get('cntx', self.cntx)
        cnty = kws.get('cnty', self.cnty)
        csig = kws.get('csig', self.csig)
        cmon = kws.get('cmon', self.cmon)
        csec = kws.get('csec', self.csec)
        norm = kws.get('norm', self.norm)
        #input checks
        if scan is None:
            raise NameError('Give a scan number [integer]: between 1 and {0}'.format(self.sf.scanno()))
        if cntx is None:
            raise NameError('Give the counter for x, the abscissa [string]')
        if cnty is not None and not (cnty in self.sf.allmotors()):
            raise NameError("'{0}' is not in the list of motors".format(cnty))
        if csig is None:
            raise NameError('Give the counter for signal [string]')

        #select the given scan number
        self.sd = self.sf.select(str(scan)) #sd = specfile data

        #the case cntx is not given, the first counter is taken by default
        if cntx == 1:
            _cntx = self.sd.alllabels()[0]
        else:
            _cntx = cntx

        ## x-axis
        scan_datx = self.sd.datacol(_cntx)
        _xlabel = 'x'
        _xscale = 1.0
        if scnt is None:
            # try to guess the scan type if it is not given
            # this condition should work in case of an energy scan
            if ('ene' in _cntx.lower()):
                # this condition should detect if the energy scale is KeV
                if (scan_datx.max() - scan_datx.min()) < 3.0:
                    scan_datx = scan_datx*1000
                    _xscale = 1000.0
                    _xlabel = "energy, eV"
                else:
                    scan_datx = self.sd.datacol(cntx)
                    _xscale = 1.0
                    _xlabel = "energy, keV"
        else:
            raise NameError("Wrong scan type string")

        ## z-axis (start with the signal)
        # data signal
        datasig = self.sd.datacol(csig)
        # data monitor
        if cmon is None:
            datamon = np.ones_like(datasig)
            labmon = "1"
        elif (('int' in str(type(cmon))) or ('float' in str(type(cmon))) ):
               # the case we want to divide by a constant value
               datamon = _mot2array(cmon, datasig)
               labmon = str(cmon) 
        else:
            datamon = self.sd.datacol(cmon)
            labmon = str(cmon)
        # data cps
        if csec is not None:
            scan_datz = ( ( datasig / datamon ) * np.mean(datamon) ) / self.sd.datacol(csec)
            _zlabel = "((signal/{0})*mean({0}))/seconds".format(labmon)
        else:
            scan_datz = (datasig / datamon)
            _zlabel = "signal/{0}".format(labmon)

        ### z-axis normalization, if required
        if norm is not None:
            _zlabel = "{0} norm by {1}".format(_zlabel, norm)
            if norm == "max":
                scan_datz = _div_check(scan_datz, np.max(scan_datz))
            elif norm == "max-min":
                scan_datz = _div_check(scan_datz-np.min(scan_datz), np.max(scan_datz)-np.min(scan_datz))
            elif norm == "area":
                scan_datz = _div_check(scan_datz-np.min(scan_datz), np.trapz(scan_datz, x=scan_datx))
            elif norm == "sum":
                scan_datz = _div_check(scan_datz-np.min(scan_datz), np.sum(scan_datz))
            else:
                raise NameError("Provide a correct normalization type string")

        ### z-axis replace nan and inf, in case
        scan_datz = np.nan_to_num(scan_datz)

        ## the motors dictionary
        scan_mots = dict(zip(self.sf.allmotors(), self.sd.allmotorpos()))

        ## y-axis
        if cnty is not None:
            _ylabel = "motor {0} at {1}".format(cnty, scan_mots[cnty])
        else:
            _ylabel = _zlabel

        ## collect information on the scan
        scan_info = {'xlabel' : _xlabel,
                     'xscale' : _xscale,
                     'ylabel' : _ylabel,
                     'zlabel' : _zlabel}

        if cnty is not None:
            return scan_datx, scan_datz, scan_mots[cnty]*_xscale
        else:
            return scan_datx, scan_datz, scan_mots, scan_info

    def get_map(self, scans=None, **kws):
        """ get a map composed of many scans repeated at different
        position of a given motor

        Parameters
        ----------
        scans : scans to load in the map [string]; the format of the
                string is intended to be parsed by '_str2rng()'
        **kws : see get_scan() method

        Returns
        -------
        xcol, ycol, zcol : 1D arrays representing the map
        """
        #get keywords arguments
        cntx = kws.get('cntx', self.cntx)
        cnty = kws.get('cnty', self.cnty)
        csig = kws.get('csig', self.csig)
        cmon = kws.get('cmon', self.cmon)
        csec = kws.get('csec', self.csec)
        norm = kws.get('norm', self.norm)
        #check inputs - some already checked in get_scan()
        if scans is None:
            raise NameError("Provide a string representing the scans to load in the map - e.g. '100, 7:15, 50:90:3'")
        if cnty is None:
            raise NameError("Provide the name of an existing motor")

        _counter = 0
        for scan in _str2rng(str(scans)):
            x, z, moty = self.get_scan(scan=scan, cntx=cntx, cnty=cnty, csig=csig, cmon=cmon, csec=csec, scnt=None, norm=norm)
            y = _mot2array(moty, x)
            print("Loading scan {0} into the map...".format(scan))
            if _counter == 0:
                xcol = x
                ycol = y
                zcol = z
            else:
                xcol = np.append(xcol, x)
                ycol = np.append(ycol, y)
                zcol = np.append(zcol, z)
            _counter += 1

        return xcol, ycol, zcol

    def grid_map(self, xcol, ycol, zcol, xystep=None, lib='scipy', method='cubic'):
        if HAS_GRIDUTILS is True:
            return _gridxyz(xcol, ycol, zcol, xystep=xystep, lib=lib, method=method)
        else:
            return

    def get_mrg(self, scans=None, action='average', **kws):
        """ get a merged scan from a list of scans

        Parameters
        ----------
        scans : scans to load in the merge [string]
                the format of the string is intended to be parsed by '_str2rng()'
        action : action to perform on the loaded list of scans
                 'average' -> average the scans
                 'join' -> concatenate the scans
                 'single' -> scans_list[0] : equivalent to get_scan()
        **kws : see get_scan() method

        Returns
        -------
        xmrg, zmrg : 1D arrays
        """
        #get keywords arguments
        cntx = kws.get('cntx', self.cntx)
        cnty = kws.get('cnty', self.cnty)
        csig = kws.get('csig', self.csig)
        cmon = kws.get('cmon', self.cmon)
        csec = kws.get('csec', self.csec)
        norm = kws.get('norm', self.norm)
        #check inputs - some already checked in get_scan()
        if scans is None:
            raise NameError("Provide a string representing the scans to merge - e.g. '100, 7:15, 50:90:3'")

        _ct = 0
        xdats = []
        zdats = []
        #mdats = []
        #idats = []
        for scan in _str2rng(str(scans)):
            _x, _z, _m, _i = self.get_scan(scan=scan, cntx=cntx, cnty=None, csig=csig,
                                           cmon=cmon, csec=csec, scnt=None, norm=norm)
            xdats.append(_x)
            zdats.append(_z)
            #mdats.append(_m)
            #idats.append(_i)
            print("Loading scan {0}...".format(scan))
            _ct += 1

        # override 'action' keyword if it is only one scan
        if len(_str2rng(str(scans))) == 1:
            action = 'single'

        if action == 'average':
            return _pymca_average(xdats, zdats)
        elif action == 'join':
            return np.concatenate(xdats, axis=0), np.concatenate(zdats, axis=0)
        elif action == 'single':
            return xdats[0], zdats[0]

### LARCH ###
def _specfiledata_getdoc(method):
    """ to get the docstring of method inside a class """
    s = SpecfileData('DUMMY!')
    head = "\n Docstring from {0}:\n -------------------\n".format(method)
    return head + getattr(getattr(s, method), '__doc__')

def spec_getscan2group(fname, scan=None, cntx=None, csig=None, cmon=None, csec=None,
                       scnt=None, norm=None, _larch=None):
    """ *** simple mapping of SpecfileData.get_scan() to Larch group *** """
    if _larch is None:
        raise Warning("larch broken?")

    s = SpecfileData(fname)
    group = _larch.symtable.create_group()
    group.__name__ = 'SPEC data file %s' % fname
    x, y, motors, infos = s.get_scan(scan=scan, cntx=cntx, csig=csig, cmon=cmon, csec=csec, scnt=scnt, norm=norm)
    setattr(group, 'x', x)
    setattr(group, 'y', y)
    setattr(group, 'motors', motors)
    setattr(group, 'infos', infos)

    return group
spec_getscan2group.__doc__ += _specfiledata_getdoc('get_scan')

def spec_getmap2group(fname, scans=None, cntx=None, cnty=None, csig=None, cmon=None, csec=None,
                      xystep=None, norm=None, _larch=None):
    """ *** simple mapping of SpecfileData.get_map() + grid_map () to Larch group *** """
    if _larch is None:
        raise Warning("larch broken?")

    s = SpecfileData(fname)
    group = _larch.symtable.create_group()
    group.__name__ = 'SPEC data file %s' % fname
    xcol, ycol, zcol = s.get_map(scans=scans, cntx=cntx, cnty=cnty, csig=csig, cmon=cmon, csec=csec, norm=norm)
    x, y, zz = s.grid_map(xcol, ycol, zcol, xystep=xystep)
    setattr(group, 'x', x)
    setattr(group, 'y', y)
    setattr(group, 'zz', zz)

    return group
spec_getmap2group.__doc__ += _specfiledata_getdoc('get_map')

def spec_getmrg2group(fname, scans=None, cntx=None, csig=None, cmon=None, csec=None, norm=None, action='average', _larch=None):
    """ *** simple mapping of SpecfileData.get_mrg() to Larch group *** """
    if _larch is None:
        raise Warning("larch broken?")

    s = SpecfileData(fname)
    group = _larch.symtable.create_group()
    group.__name__ = 'SPEC data file {0}; scans {1}; action {2}'.format(fname, scans, action)
    x, y = s.get_mrg(scans=scans, cntx=cntx, csig=csig, cmon=cmon, csec=csec, norm=norm, action=action)
    setattr(group, 'x', x)
    setattr(group, 'y', y)

    return group
spec_getmrg2group.__doc__ += _specfiledata_getdoc('get_mrg')

def str2rng(rngstr, keeporder=True, _larch=None):
    """ larch equivalent of _str2rng() """
    if _larch is None:
        raise Warning("larch broken?")
    return _str2rng(rngstr, keeporder=keeporder)
str2rng.__doc__ = _str2rng.__doc__

def registerLarchPlugin():
    if HAS_PYMCA:
        return ('_io', {'read_specfile_scan': spec_getscan2group,
                        'read_specfile_map' : spec_getmap2group,
                        'read_specfile_mrg' : spec_getmrg2group,
                        'str2rng' : str2rng
                        })
    else:
        return ('_io', {})

### TESTS ###
def test01():
    """ test get_scan method """
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests', 'specfile_test.dat')
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    scan = 3
    t = SpecfileData(fname)
    for norm in [None, "area", "max", "max-min", "sum"]:
        x, y, motors, infos = t.get_scan(scan, cntx=counter, csig=signal, cmon=monitor, csec=seconds, norm=norm)
        print("Read scan {0} with normalization {1}".format(scan, norm))
        import matplotlib.pyplot as plt
        plt.ion()
        plt.figure(num=test01.__doc__)
        plt.plot(x, y)
        plt.xlabel(infos["xlabel"])
        plt.ylabel(infos["ylabel"])
        plt.show()
        raw_input("Press Enter to close the plot window and continue...")
        plt.close()

def test02(nlevels):
    """ test get_map method """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests', 'specfile_test.dat')
    rngstr = '5:70'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    norm = None #normalizing each scan does not make sense, the whole map has to be normalized!
    xystep = 0.05
    t = SpecfileData(fname)
    xcol, ycol, zcol = t.get_map(scans=rngstr, cntx=counter, cnty=motor, csig=signal, cmon=monitor, csec=seconds, norm=norm)
    etcol = xcol-ycol
    x, y, zz = t.grid_map(xcol, ycol, zcol, xystep=xystep)
    ex, et, ezz = t.grid_map(xcol, etcol, zcol, xystep=xystep)
    fig = plt.figure(num=test02.__doc__)
    ax = fig.add_subplot(121)
    ax.set_title('gridded data')
    cax = ax.contourf(x, y, zz, nlevels, cmap=cm.Paired_r)
    ax = fig.add_subplot(122)
    ax.set_title('energy transfer')
    cax = ax.contourf(ex, et, ezz, nlevels, cmap=cm.Paired_r)
    cbar = fig.colorbar(cax)
    plt.show()
    raw_input("Press Enter to close the plot and continue...")
    plt.close()

def test03():
    """ test get_mrg method """
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests', 'specfile_test.dat')
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    scans = '72, 74'
    t = SpecfileData(fname)
    for norm in [None, "area", "max-min", "sum"]:
        x, y = t.get_mrg(scans, cntx=counter, csig=signal, cmon=monitor, csec=seconds, norm=norm)
        print("Merged scans '{0}' with normalization {1}".format(scans, norm))
        import matplotlib.pyplot as plt
        plt.ion()
        plt.figure(num=test03.__doc__)
        plt.plot(x, y)
        plt.xlabel(counter)
        plt.ylabel("merged with norm {0}".format(norm))
        plt.show()
        raw_input("Press Enter to continue...")
        plt.close()

if __name__ == '__main__':
    """ to run some tests/examples on this class, uncomment the following """
    #test01()
    #test02(100)
    #test03
    pass



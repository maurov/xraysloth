#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple data export tool in SPEC_ format

.. _SPEC: http://www.certif.com/content/spec/

TODO
----
- add tests and checks for wrong input parameters

- if the given file exists, one should check if it is in spec format,
  otherwise there is an high risk of writing in a wrong file. in fact,
  specfile.Specfile does not check for the format at init (but it will
  go in segmentation fault at access!!!)

- #T/#M control line in scans not implemented

- #G and #Q control line in scans not implemented
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2011-2015"

import sys, os
import time

DEBUG = False

class SpecfileDataWriter(object):
    """Specfile data format is defined here:
    http://www.certif.com/spec_manual/user_1_4_1.html"""

    def __init__(self, fname, owrt=False, **kws):
        """init the file name and scan number only (no write at init)"""
        self.fn = os.path.abspath(fname)
        self.scanStart = 0
        self.scanOnly = False
        if os.path.isfile(self.fn) and os.access(self.fn, os.R_OK):
            if DEBUG: print('WARNING: {0} exists'.format(self.fn))
            HAS_SPECFILE = False
            HAS_PYMCA5 = False
            # PyMca5 branch
            try:
                from PyMca5.PyMcaIO import specfilewrapper as specfile
                HAS_SPECFILE = True
                HAS_PYMCA5 = True
            except ImportError:
                # PyMca 4.7 branch
                try:
                    from PyMca import specfilewrapper as specfile
                    HAS_SPECFILE = True
                except ImportError:
                    try:
                        from PyMca import specfile
                        HAS_SPECFILE = True
                    except ImportError:
                        if DEBUG: print("WARNING: no 'specfile' -> scanOnly mode is {0}".format(self.scanOnly))
                        pass
            if HAS_SPECFILE:
                try:
                    sf = specfile.Specfile(self.fn)
                    self.scanStart = sf.scanno()
                    self.scanOnly = True
                    if DEBUG: print('scanStart = {0}'.format(self.scanStart))
                except:
                    pass
        if owrt:
            self.scanOnly = False
            self.scan = 0
        else:
            self.scan = self.scanStart + 1

    def wHeader(self, **kws):
        print("DEPRECATED: use 'write_header' method")
        return self.write_header(**kws)
        
    def write_header(self, epoch=None, date=None, title=None, motnames=None, comms=None):
        """write the header to file by over-writing

        Parameters
        ----------
        title : str
                a title for the SPEC file
        motnames : list of str
                   a list of motor names
        comms : list of str
                list of comments to add in the header

        Returns
        -------
        None, write to file
        """
        if self.scanOnly:
            if DEBUG: print("'scanOnly' mode: header skipped")
            return

        _hl = [ '#F {0}'.format(self.fn) ]
        # epoch
        if epoch is not None:
            _hl.append('#E {0}'.format(epoch))
        else:
            _hl.append('#E {0}'.format(int(time.time())))
        # date
        if date is not None:
            _hl.append('#D {0}'.format(date))
        else:
            _hl.append('#D {0}'.format(time.ctime()))
        # title
        _hl.append('#C {0}'.format(str(title)))
        # motnames
        if motnames is not None:
            _mnl = ['#O0 ']
            for _mn in motnames:
                _mnl.append(str(_mn))
            _hl.append('{0}'.format('  '.join(_mnl)))
        # comms
        if comms is not None:
            for _com in comms:
                _hl.append('#C {0}'.format(str(_com)))

        _hl.append('\n')
        
        with open(self.fn, 'wb') as f:
            f.write('\n'.join(_hl))

    def wScan(self, cols, dats, **kws):
        print("DEPRECATED: use 'write_scan' method")
        return self.write_scan(cols, dats, **kws)

    def write_scan(self, cols, dats, title=None, motpos=None, comms=None):
        """write a scan to file by appending

        Parameters
        ----------
        cols : list of str
        dats : list of arrays
        title : str
                scan title (e.g. given command)
        motpos : list of floats
                 motors positions at beginning of the scan (following
                 the same order of the list of motors names given in
                 the header)
        comms : list of str
                list of comments relative to the scan

        Returns
        -------
        None, write to file
        """
        _sl = []
        _sl.append('#S {0} {1}'.format(int(self.scan), str(title)))
        _sl.append('#D {0}'.format(time.ctime()))

        if motpos is not None:
            _mpl = ['#P0 ']
            for _mp in motpos:
                _mpl.append(str(_mp))
            _sl.append('{0}'.format('  '.join(_mpl)))

        if comms is not None:
            for _com in comms:
                _sl.append('#C {0}'.format(str(_com)))
        _sl.append('#N {0}'.format(len(cols)))
        _cs = ['#L ']
        for _c in cols:
            _cs.append('{0}'.format(str(_c)))
        _sl.append('{0}'.format('  '.join(_cs)))

        for idx in range(len(dats[0])):
            _dl = []
            for _dat in dats:
                _dl.append('{0:.7f}'.format(_dat[idx]))
            _sl.append('{0}'.format(' '.join(_dl)))

        _sl.append('\n')
        
        with open(self.fn, 'ab') as f:
            f.write('\n'.join(_sl))

        self.scan += 1

if __name__ == '__main__':
    pass

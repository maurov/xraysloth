#!/usr/bin/env python

"""Simple data export tool in SPEC_ format
==========================================

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
import sys, os
import time

DEBUG = False
HAS_SPECFILE = False
try:
    from silx.io import specfilewrapper as specfile
    HAS_SPECFILE = True
except ImportError:
    pass

class SpecfileDataWriter:
    """Specfile data format is defined here:
    http://www.certif.com/spec_manual/user_1_4_1.html"""

    def __init__(self, fname, owrt=False, **kws):
        """init the file name and scan number only (no write at init)"""
        self.fn = os.path.abspath(fname)
        self.scanStart = 0
        self.scanOnly = False
        if os.path.isfile(self.fn) and os.access(self.fn, os.R_OK):
            if DEBUG: print(f'WARNING: {self.fn} exists')
            if HAS_SPECFILE:
                try:
                    sf = specfile.Specfile(self.fn)
                    self.scanStart = sf.scanno()
                    self.scanOnly = True
                    if DEBUG: print(f'INFO: scanStart = {self.scanStart}')
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
        
    def write_header(self, epoch=None, date=None, title=None,
                     motnames=None, comms=None):
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

        _hl = [ f'#F {self.fn}' ]
        # epoch
        if epoch is not None:
            _hl.append(f'#E {epoch}')
        else:
            _hl.append(f'#E {int(time.time())}')
        # date
        if date is not None:
            _hl.append(f'#D {date}')
        else:
            _hl.append(f'#D {time.ctime()}')
        # title
        _hl.append(f'#C {str(title)}')
        # motnames
        if motnames is not None:
            _mnl = ['#O0 ']
            for _mn in motnames:
                _mnl.append(str(_mn))
            _hl.append('{}'.format('  '.join(_mnl)))
        # comms
        if comms is not None:
            for _com in comms:
                _hl.append(f'#C {str(_com)}')

        _hl.append('\n')

        if sys.version < '3.0':
            accessMode = 'wb'
        else:
            accessMode = 'w'
        
        with open(self.fn, accessMode) as f:
            outstr = '\n'.join(_hl)
            f.write(outstr)

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
        _sl.append(f'#S {int(self.scan)} {str(title)}')
        _sl.append(f'#D {time.ctime()}')

        if motpos is not None:
            _mpl = ['#P0 ']
            for _mp in motpos:
                _mpl.append(str(_mp))
            _sl.append('{}'.format('  '.join(_mpl)))

        if comms is not None:
            for _com in comms:
                _sl.append(f'#C {str(_com)}')
        _sl.append(f'#N {len(cols)}')
        _cs = ['#L ']
        for _c in cols:
            _cs.append(f'{str(_c)}')
        _sl.append('{}'.format('  '.join(_cs)))

        for idx in range(len(dats[0])):
            _dl = []
            for _dat in dats:
                _dl.append(f'{_dat[idx]:.7f}')
            _sl.append('{}'.format(' '.join(_dl)))

        _sl.append('\n')

        if sys.version < '3.0':
            accessMode = 'ab'
        else:
            accessMode = 'a'
        
        with open(self.fn, accessMode) as f:
            f.write('\n'.join(_sl))

        self.scan += 1

if __name__ == '__main__':
    pass

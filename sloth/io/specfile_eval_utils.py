#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Specfile File Evaluation Utilities

Description
===========

Utility objects/functions to perform some data reduction/evaluation on
line scans (1D) contained in one or several SPEC data files collected
in the same experimental session (experiment).


Status
======

The current version is not generic nor stable. It should not be used
as it is, but only considered as an example.

Related
=======

gsutils* in sloth (https://github.com/maurov/xraysloth)

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import os, sys
import numpy as np

### Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib import cm, animation
from matplotlib import gridspec

### local imports
from specfiledata import SpecfileData, _check_scans

class SpecfileDataCollector(object):
    """wrapper"""

    def __init__(self, fndats, scans,\
                 counter=1, signal='det_dtc', monitor='I02', seconds='Seconds'):
        """collects data from a given scan list inside a single SPEC file

        Parameters
        ----------

        fndats  : string or list of strings -> file name(s)
        scans   : list of scans to load (parsed by str2rng)
        counter : counter name for x [string, 1]
        signal  : counter name for y [string, 'det_dtc']
        monitor : counter name for monitor [string, 'I02']
        seconds : counter name for time [string, 'Seconds']

        
        """
        if type(fndats) is str: fndats = [fndats] #make sure is a list
        if (len(fndats) == 1) and (len(fndats) != len(scans)):
            fndats *= len(scans)
        else:
            raise NameError("check fndats/scans input")

        nscans = _check_scans(scans)

        self.fndats = fndats
        self.nscans = nscans

        self.counter = counter
        self.signal = signal
        self.monitor = monitor
        self.seconds = seconds

        self.dats = {}
        self.dats['cntx'] = [] #cntx
        self.dats['csig'] = [] #csig
        self.dats['cmon'] = [] #cmon
        self.dats['csec'] = [] #csec

        self.sfd = SpecfileData(fname=self.fndats[0],
                                cntx=self.counter, cnty=None,
                                csig=None, cmon=None, csec=None,
                                norm=None)

    def load_dats(self):
        """load data """
        for fndat, scan in zip(self.fndats, self.nscans):
            if self.sfd.fname != fndat:
                self.sfd = SpecfileData(fname=fndat,
                                        cntx=self.counter, cnty=None, csig=None,
                                        cmon=None, csec=None, norm=None)
            else:
                _x, _y, _ym, _yi = self.sfd.get_scan(scan, csig=self.signal)
                _x, _m, _mm, _mi = self.sfd.get_scan(scan, csig=self.monitor)
                _x, _s, _sm, _si = self.sfd.get_scan(scan, csig=self.seconds)

            self.dats['cntx'].append(_x)
            self.dats['csig'].append(_y)
            self.dats['cmon'].append(_m)
            self.dats['csec'].append(_s)
        
if __name__ == '__main__':
    pass

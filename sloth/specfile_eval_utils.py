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
from specfiledata import SpecfileData

class SpecfileDataCollector(SpecfileData):
    """"""

    def __init__(self, fndat, scans,\
                 counter=1, signal='det_dtc', monitor='I02', seconds='Seconds'):
        """collects data from a given scan list inside a single SPEC file

        Parameters
        ----------

        fndat   : SPEC file name
        scans   : list of scans to load (parsed by str2rng)
        counter : counter name for x [string, 1]
        signal  : counter name for y [string, 'det_dtc']
        monitor : counter name for monitor [string, 'I02']
        seconds : counter name for time [string, 'Seconds']

        
        """

        # defaults arbitrary setted to ESRF/ID26!
        if signal is None: signal = 'det_dtc'
        if monitor is None: monitor = 'I02'
        if seconds is None: seconds = 'Seconds'
        
        super(SpecfileDataCollector, self).__init__(fname=fndat,
                                                    cntx=counter,
                                                    cnty=None,
                                                    csig=signal,
                                                    cmon=monitor,
                                                    csec=seconds,
                                                    norm=None)
        self.scans = scans
        
    def load_scans(self, scans=None):
        """load scans"""


        


if __name__ == '__main__':
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sloth: some utilies for x-ray spectroscopists

Naming
======

* classes MixedUpperCase
* varables lowerUpper _or_ lower
* functions underscore_separated _or_ lowerUpper

"""
from __future__ import absolute_import, print_function, division, unicode_literals
import os

# filter annoying numpy<1.8 warnings
import warnings

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

__author__ = "Mauro Rovezzi"
__version__ = "0.3.1.rc2"

_libDir = os.path.dirname(os.path.realpath(__file__))
_resourcesPath = os.path.join(_libDir, "resources")

__pkgs__ = [
    "sloth",
    "sloth.io",  # input-output
    "sloth.groups",  # data groups based on HDF5 model
    "sloth.collects",  # data containers !DEPRECATED! -> sloth.groups
    "sloth.utils",  # utilities (generic)
    "sloth.math",  # math&friends
    "sloth.test",  # main test suite
    "sloth.fit",  # fit utilities
    "sloth.gui",  # graphical user interface
    "sloth.inst",  # instrumentation
    "sloth.raytracing",  # ray tracing (shadow)
    "sloth.calculators",  # ab initio calculators
    #'sloth.examples',     # examples #TODO: fix this under windows!!!
    "sloth.resources",  # resoureces (= UI files, icons, etc.)
]


class NullClass(object):
    """Null object reliably doing nothing."""

    __version__ = __version__

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return "Null(  )"

    def __nonzero__(self):
        return 0

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self


if __name__ == "__main__":
    pass

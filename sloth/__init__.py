#!/usr/bin/env python
"""Sloth: utilies for x-ray spectroscopy

Naming
======

* classes MixedUpperCase
* varables lowerUpper _or_ lower
* functions underscore_separated _or_ lowerUpper

"""
import os

__author__ = "Mauro Rovezzi"
__version__ = "25.1.0"

_libDir = os.path.dirname(os.path.realpath(__file__))
_resourcesPath = os.path.join(_libDir, "resources")

__pkgs__ = [
    "sloth",
    "sloth.io",  #: input-output
    "sloth.groups",  #: data groups based on HDF5 model
    "sloth.collects",  #: data containers !DEPRECATED! -> sloth.groups
    "sloth.utils",  #: utilities (generic)
    "sloth.math",  #: math&friends
    "sloth.test",  #: main test suite
    "sloth.fit",  #: fit utilities
    "sloth.gui",  #: graphical user interfaces
    "sloth.inst",  #: instrumentation
    "sloth.raytracing",  #: ray tracing (shadow)
    "sloth.calculators",  #: ab initio calculators
    #'sloth.examples',     #: examples #TODO: fix this under windows!!!
    "sloth.resources",  #: resources (= UI files, icons, etc.)
]


class NullClass:
    """Null object reliably doing nothing."""

    __version__ = __version__

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return "Null(  )"

    def __bool__(self):
        return False

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self


if __name__ == "__main__":
    pass

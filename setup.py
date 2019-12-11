#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sloth

PROJECT = "sloth"

# ############################# #
# numpy.distutils Configuration #
# ############################# #


def configuration(parent_package="", top_path=None):
    """Recursive construction of package info to be used in setup().
    See http://docs.scipy.org/doc/numpy/reference/distutils.html#numpy.distutils.misc_util.Configuration
    """
    try:
        from numpy.distutils.misc_util import Configuration
    except ImportError:
        raise ImportError(
            "To install this package, you must install numpy first\n"
            "(See https://pypi.python.org/pypi/numpy)"
        )
    config = Configuration(None, parent_package, top_path)
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True,
    )
    config.add_subpackage(PROJECT)
    return config


def get_readme():
    """README.rst -> long description"""
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, "README.rst"), "r") as f:
        long_description = f.read()
    return long_description


def main():
    """The main entry point."""
    config = configuration()
    setup_kwargs = config.todict()
    setup_kwargs.update(
        name=PROJECT,
        version=sloth.__version__,
        packages=sloth.__pkgs__,
        description="some utilities for x-ray spectroscopy",
        long_description=get_readme(),
        license="BSD",
        author="Mauro Rovezzi",
        author_email="mauro.rovezzi@gmail.com",
        url="https://github.com/maurov/xraysloth",
        download_url="https://github.com/maurov/xraysloth",
        classifiers=[
            "Development Status :: 1 - Planning",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Topic :: Scientific/Engineering :: Physics",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
        ],
    )
    _setup = setup(**setup_kwargs)


if __name__ == "__main__":
    main()

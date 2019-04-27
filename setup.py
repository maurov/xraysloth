#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import shutil
from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sloth

PROJECT = "sloth"

###
isdir = os.path.isdir
pjoin = os.path.join
psplit = os.path.split
pexists = os.path.exists

# determine OS/platform
nbits = platform.architecture()[0].replace('bit', '')
uname = 'linux'
libfmt = 'lib%s.so'
bindir = 'bin'
pyexe = pjoin(bindir, 'python')

if os.name == 'nt':
    uname = 'win'
    libfmt = '%s.dll'
    bindir = 'Scripts'
    pyexe = 'python.exe'
elif sys.platform == 'darwin':
    uname = 'darwin'
    libfmt = 'lib%s.dylib'
uname = "%s%s" % (uname, nbits)

# ############################# #
# numpy.distutils Configuration #
# ############################# #


def configuration(parent_package='', top_path=None):
    """Recursive construction of package info to be used in setup().
    See http://docs.scipy.org/doc/numpy/reference/distutils.html#numpy.distutils.misc_util.Configuration
    """
    try:
        from numpy.distutils.misc_util import Configuration
    except ImportError:
        raise ImportError(
            "To install this package, you must install numpy first\n"
            "(See https://pypi.python.org/pypi/numpy)")
    config = Configuration(None, parent_package, top_path)
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True)
    config.add_subpackage(PROJECT)
    return config


def get_readme():
    """README.rst -> long description"""
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, 'README.rst'), 'r') as f:
        long_description = f.read()
    return long_description


def _install_scripts(_setup):
    """scripts to install besides the normal python modules"""
    scripts = glob('bin/*')
    if not uname.startswith('win'):
        scripts = [s for s in scripts if not s.endswith('.bat')]

    scriptdir = pjoin(sys.exec_prefix, bindir)
    install_prefix = _setup.get_command_obj('install').root
    if install_prefix is not None:
        scriptdir = pjoin(install_prefix, scriptdir)

    for src in scripts:
        _, fname = psplit(src)
        dest = pjoin(scriptdir, fname)
        shutil.copy(src, dest)
        os.chmod(dest, 493)  # mode=755


def main(install_scripts=True):
    """The main entry point."""
    config = configuration()
    setup_kwargs = config.todict()
    setup_kwargs.update(
        name = PROJECT,
        version = sloth.__version__,
        packages = sloth.__pkgs__,
        description = 'some utilities for x-ray spectroscopists',
        long_description = get_readme(),
        license = 'BSD',
        author = 'Mauro Rovezzi',
        author_email = 'mauro.rovezzi@gmail.com',
        url = 'https://github.com/maurov/sloth',
        download_url = 'https://github.com/maurov/sloth',
        classifiers = ['Development Status :: 1 - Planning',
                       'License :: OSI Approved :: BSD',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python :: 2',
                       'Programming Language :: Python :: 3',
                       'Topic :: Scientific/Engineering :: Physics',
                       'Intended Audience :: Education',
                       'Intended Audience :: Science/Research']
        )
    _setup = setup(**setup_kwargs)

    if install_scripts:
        _install_scripts(_setup)


if __name__ == '__main__':
    main()

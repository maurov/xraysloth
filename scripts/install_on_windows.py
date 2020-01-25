#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script for installing on Microsoft Windows

Wheels from [GOHLKE WINDOWS REPOSITORY](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

"""

try:
    from gohlkegrabber import GohlkeGrabber
except ImportError:
    print("gohlkegrabber not installed -> 'pip install gohlkegrabber")
    pass

import subprocess
import tempfile
import shutil

PACKAGES = ('numpy', 'cffi', 'pyopencl', 'pyopengl', 'h5py')


def install_packages(packages, remove_tmpdir=True):
    """main script"""

    _py = '3.7'
    _platform = 'win_amd64'

    _tmpdir = tempfile.mkdtemp(prefix='py37w')
    print(f"Temporary directory is: {_tmpdir}")

    gg = GohlkeGrabber()

    for pkg in packages:
        print(f"retreiving {pkg}...")
        try:
            pkwhl = gg.retrieve(_tmpdir, pkg, python=_py, platform=_platform)
        except KeyError:
            print(f"{pkg} not found")
            continue
        subprocess.call(f"pip install {pkwhl[0]}")

    if remove_tmpdir:
        shutil.rmtree(_tmpdir)
        print("temporary directory removed")


if __name__ == "__main__":
    pass


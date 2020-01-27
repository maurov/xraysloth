#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script for installing packages on Microsoft Windows using wheels
   from [GOHLKE WINDOWS REPOSITORY](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

- Steps to build this environment with Conda from the 'base':

    (base)$ conda create -n py37w python=3.7
    (base)$ conda activate py37w

"""

try:
    from gohlkegrabber import GohlkeGrabber
except ImportError:
    print("gohlkegrabber not installed -> 'pip install gohlkegrabber'")
    pass

import subprocess
import tempfile
import shutil

PACKAGES = ('numpy', 'cffi', 'pyopencl', 'pyopengl', 'h5py')


def install_packages(packages, pkgs_dir=None, remove_pkgs_dir=False):
    """main script"""

    _py = '3.7'
    _platform = 'win_amd64'

    if pkgs_dir is None:
        pkgs_dir = tempfile.mkdtemp(prefix='py37w')
        print(f"Temporary packages directory is: {pkgs_dir}")
        remove_pkgs_dir = True

    gg = GohlkeGrabber()

    for pkg in packages:
        print(f"retreiving {pkg}...")
        try:
            pkwhl = gg.retrieve(pkgs_dir, pkg, python=_py, platform=_platform)
        except KeyError:
            print(f"{pkg} not found")
            continue
        subprocess.call(f"pip install {pkwhl[0]}")

    if remove_pkgs_dir:
        shutil.rmtree(pkgs_dir)
        print("temporary directory removed")


if __name__ == "__main__":
    print("To install Windows packages from Gohlke, manually run 'install_packages()' function")
    # install_packages(PACKAGES)
    pass

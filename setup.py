#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sloth
    
def get_readme():
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, 'README.rst'), 'r') as f:
        long_description = f.read()
    return long_description

def main():
    """The main entry point."""
    kwargs = dict(
        name='sloth',
        version=sloth.__version__,
        packages=['sloth', 'sloth.raytracing'],
        description='some utilities for x-ray spectroscopists',
        long_description=get_readme(),
        license='BSD',
        author='Mauro Rovezzi',
        author_email='first_name DOT last_name AT gmail DOT com',
        url='https://github.com/maurov/sloth',
        classifiers=['Development Status :: 1 - Planning',
                     'License :: OSI Approved :: BSD',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 3',
                     'Topic :: Scientific/Engineering :: Physics',
                     'Intended Audience :: Education',
                     'Intended Audience :: Science/Research',
        ])

    setup(**kwargs)

if __name__ == '__main__':
    main()

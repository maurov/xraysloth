#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy.distutils.misc_util import Configuration


def configuration(parent_package='', top_path=None):
    config = Configuration('sloth', parent_package, top_path)
    config.add_subpackage('gui')
    config.add_subpackage('io')
    config.add_subpackage('math')
    config.add_subpackage('collects')
    config.add_subpackage('dft')
    config.add_subpackage('inst')
    config.add_subpackage('fit')
    config.add_subpackage('test')
    config.add_subpackage('raytracing')
    config.add_subpackage('utils')
    config.add_subpackage('resources')
    config.add_subpackage('examples', '../examples')

    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(configuration=configuration)

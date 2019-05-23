#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic 1D data groups: curves and scans
======================================

This module implements the following classes:

BaseCurve
---------

HDF5-like representation of a curve (1D dataset), that is:

- BaseCurve:
    - 'axis' (group):
        - attrs: axis attributes
            - default: 'name'
            - ...
        - 'x_name' (dataset): array
            - attrs: x attributes
                - label: 'x_label'
                - ...
    - 'signal' (group):
        - attrs: signal attributes
            - default: 'y_name'
            - ...
        - 'y_name' (dataset): array
            - attrs: y attributes
            - label: 'y_label'

BaseScan
--------


"""
from sloth.groups.baseh5 import EntryGroup


class BaseCurve(EntryGroup):
    """HDF5-like representation of a curve (1D dataset)"""

    def __init__(self, x_dict, y_dict, parent=None):
        pass
        # super(BaseCurve, self).__init__(name, attrs=attrs, parent=parent)

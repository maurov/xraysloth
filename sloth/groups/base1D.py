#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic 1D data groups: curves and scans
======================================

This module implements the following classes:

BaseCurve
---------

HDF5-like representation of a curve (1D dataset), that is, a dataset having one
axis array (the abscissa) and one signal array (the ordinate), plus at least one
attribute, the label.

 They go, respectively, in the :

- BaseCurve:
    - attrs: base attributes
        - label: curve label
    - 'axes' (group):
        - attrs: axes attributes
            - default: 'name'
            - ...
        - 'ax1_name' (dataset): array
            - attrs: x attributes
                - label: 'x_label'
                - ...
    - 'signals' (group):
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

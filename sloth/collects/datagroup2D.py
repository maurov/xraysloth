#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DataGroup2D: work with 2D data sets (planes/maps/images)
===========================================================
"""
from .datagroup import DataGroup

class DataGroup2D(DataGroup):
    """ 2D version of DataGroup """
    def __init__(self, kwsd=None, _larch=None):
        super(DataGroup2D, self).__init__(self, kwsd=kwsd, _larch=_larch)

if __name__ == '__main__':
    pass

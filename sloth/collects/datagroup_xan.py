#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DataGroupXanes: work with XANES data sets
============================================

- DataGroup
  - DataGroup1D
    - DataGroupXanes
"""
from .datagroup import MODNAME
from .datagroup1D import DataGroup1D

class DataGroupXanes(DataGroup1D):
    """DataGroup for XANES scans"""
    def __init__(self, kwsd=None, _larch=None):
        super(DataGroupXanes, self).__init__(kwsd=kwsd, _larch=_larch)

### LARCH ###    
def datagroup_xan(kwsd=None, _larch=None):
    """utility to perform wrapped operations on a list of XANES data
    groups"""
    return DataGroupXanes(kwsd=kwsd, _larch=_larch)

def registerLarchPlugin():
    return (MODNAME, {'datagroup_xan' : datagroup_xan})

if __name__ == '__main__':
    pass

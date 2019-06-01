#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FDMNES-related stuff
--------------------
"""


def get_efermi(fn):
    """get the Fermi level energy from a FDMNES out file"""
    try:
        f = open(fn)
    except:
        return 0
    line = f.readline()
    f.close()
    ef = float(line.split()[6])
    print('Calculated Fermi level: {0}'.format(ef))
    return ef

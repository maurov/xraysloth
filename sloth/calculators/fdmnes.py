#!/usr/bin/env python
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
    print(f'Calculated Fermi level: {ef}')
    return ef

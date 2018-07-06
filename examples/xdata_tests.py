#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests/Examples for xdata

"""
import sys
# from __init__ import _libDir
# sys.path.append(_libDir)
import numpy as np

from sloth.utils.xdata import (ELEMENTS, SHELLS, LINES_DICT,\
                               LINES_K, LINES_L, LINES_M, LINES, TRANSITIONS)

from sloth.utils.xdata import (ene_res, fluo_width, find_line, mapLine2Trans,\
                               fluo_spectrum)

### TESTS/EXAMPLES
def testEresLinesKLM(emin, emax):
    """ returns a list of the average energy resolution for K, L and M
    lines for the elements in the given energy range """
    k = ene_res(emin, emax, shells=['K'])
    l1 = ene_res(emin, emax, shells=['L1'])
    l2 = ene_res(emin, emax, shells=['L2'])
    l3 = ene_res(emin, emax, shells=['L3'])
    m1 = ene_res(emin, emax, shells=['M1'])
    m2 = ene_res(emin, emax, shells=['M2'])
    m3 = ene_res(emin, emax, shells=['M3'])
    m4 = ene_res(emin, emax, shells=['M4'])
    m5 = ene_res(emin, emax, shells=['M5'])
    #
    ss = [k, l1, l2, l3, m1, m2, m3, m4, m5]
    ss_n = ['K', 'L1', 'L2', 'L3', 'M1', 'M2', 'M3', 'M4', 'M5']
    #
    dees = []
    for s in ss:
        dees.append(np.mean(s['dee']))
    #
    return dees

def testFluoWidth(elem='Au', lines=['LB6', 'LB4', 'LB1', 'LB2', 'LB3', 'LB5']):
    """returns the line width for the lines of a given element
    this example: Au Lbeta lines
    """
    for line in lines:
        print("{0} {1} : {2:>.4f} eV".format(elem, line, fluo_width(elem, line)))

def testFluoSulphurK():
    """generate the Kalpha1,2 emission spectrum of Sulphur"""
    elem = 'S'
    x1,y1,i1 = fluo_spectrum(elem, 'KA1')
    x2,y2,i2 = fluo_spectrum(elem, 'KA2')
    x = np.arange(x2.min(), x1.max(), 0.05)
    y1i = np.interp(x, x1, y1)
    y2i = np.interp(x, x2, y2)
    y = y1i+y2i
    from silx.gui.plot import Plot1D
    p = Plot1D()
    p.addCurve(x, y, legend='sum', color='black')
    p.addCurve(x1,y1, legend='KA1', color='red')
    p.addCurve(x2,y2, legend='KA2', color='green')
    p.show()
    return p

if __name__ == '__main__':
    #pass
    #dees = testEresLinesKLM(2000, 5000)
    #find_line(1500., 5500., lines=LINES_DICT['L2'], outDict=False)
    p = testFluoSulphurK()

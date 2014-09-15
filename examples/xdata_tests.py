#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for xdata
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2013-2014"
__version__ = "0.0.2"
__status__ = "in progress"
__date__ = "Sept 2014"

# https://github.com/maurov/xrayspina
_curDir = os.path.dirname(os.path.realpath(__file__))
_parDir = os.path.realpath(os.path.join(_curDir, os.path.pardir))
_spinaDir = os.path.join(_parDir, 'spina')
sys.path.append(_spinaDir)

from xdata import ene_res

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

if __name__ == '__main__':
    pass
    #dees = testEresLinesKLM(2000, 5000)

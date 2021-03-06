#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for sloth.raytracing - shadow part"""

import os
import sys
import math
import unittest
from sloth.utils.bragg import bragg_ev

from sloth.raytracing.shadow_utils import plot_energy_histo, plot_footprint, plot_image

HAS_SHADOW = False
try:
    import Shadow

    Shadow.ShadowTools.plt.ion()
    HAS_SHADOW = True
except ImportError:
    print("WARNING: {0}\n => this test will probably fail!".format(sys.exc_info()[1]))
    pass

CURDIR = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(CURDIR, "testdata")

# human-like test (TODO: move to unittest)


def sbca_si555(
    nrays=500000,
    rmirr=50.0,
    theta0=75.0,
    cone_max=0.11,
    f_color=3,
    ph1=10229.0,
    ph2=10237,
    iwrite=0,
    f_angle=0,
    run=True,
):
    """Si(555) SBCA using flat crystal reflectivity

    .. *NOTE*: units given in cm

    Parameters
    ==========

    rmirr : bending radius of surface [50.]

    theta0 : Bragg angle in deg [75.]

    f_color : photon energy distribution type (1=single energy, 3=uniform energy
              distribution) [3]

    ph1, ph2 : energy_start, energy_end [10299.0, 10237]

    iwrite : write start/end/begin/star files (0=No, 1=Yes) [0]

    f_angle : write angle.XX (0=No, 1=Yes) [0]

    """
    if HAS_SHADOW is False:
        print("ERROR: Shadow not found")
        return (None, None, None)

    p = rmirr * math.sin(math.radians(theta0))

    si_d111 = 3.13562683
    ene0 = bragg_ev(theta0, si_d111 / 5)

    if (f_color == 1) and (ph1 is None):
        ph1 = ene0
        ph2 = ene0

    if (f_color == 3) and (ph1 is None):
        ph1 = ene0 - 0.1
        ph2 = ene0 + 0.1

    # initialize shadow3 source (src) and beam
    beam = Shadow.Beam()
    src = Shadow.Source()
    oe = Shadow.OE()

    # Define variables. See meaning of variables in:
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/source.nml
    src.CONE_MAX = cone_max
    src.FDISTR = 5
    src.FSOUR = 2  # elliptical
    src.FSOURCE_DEPTH = 0
    src.F_COLOR = f_color
    src.F_PHOT = 0  # eV
    src.NPOINT = nrays
    src.PH1 = ph1
    src.PH2 = ph2
    src.WXSOU = 0.08
    src.WZSOU = 0.01
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/oe.nml
    oe.DUMMY = 1.0
    oe.FHIT_C = 1
    oe.FILE_REFL = bytes(os.path.join(DATA, "Si555.dat"), "utf8")
    oe.FMIRR = 1
    oe.FSHAPE = 2
    oe.FWRITE = 1
    oe.F_ANGLE = f_angle
    oe.F_CRYSTAL = 1
    oe.F_EXT = 1
    oe.RLEN1 = 5.0
    oe.RLEN2 = 5.0
    oe.RMIRR = rmirr
    oe.RWIDX1 = 5.0
    oe.RWIDX2 = 5.0
    oe.T_IMAGE = p
    oe.T_INCIDENCE = 90.0 - theta0
    oe.T_REFLECTION = 90.0 - theta0
    oe.T_SOURCE = p

    if run:
        # Run SHADOW to create the source
        if iwrite:
            src.write("start.00")
        beam.genSource(src)
        if iwrite:
            src.write("end.00")
            beam.write("begin.dat")
        # Run optical element 1
        # print("INFO: running optical element: %d"%(1))
        if iwrite:
            oe.write("start.01")
        beam.traceOE(oe, 1)
        if iwrite:
            oe.write("end.01")
            beam.write("star.01")

    print("INFO: Si(555) SBCA, R = {0:.0f} cm, theta0 = {1:.3f}".format(rmirr, theta0))
    print("INFO: => p[q] = {0:.4f} cm , ene0 = {1:.3f}".format(p, ene0))

    return (beam, src, oe)


def run_test_sbca_si555():
    if HAS_SHADOW is False:
        print("ERROR: Shadow not found")
        return None
    print("MANUAL TEST FOR CHECKING IF SHADOW WORKS CORRECTLY")
    print(
        "it is recommended to run this in an empty directory as it generates temporary files"
    )
    beam, src, oe = sbca_si555(
        nrays=500000,
        rmirr=50.0,
        theta0=82.0,
        cone_max=0.11,
        ph1=9981,
        ph2=9984,
        iwrite=0,
    )
    plot_footprint()
    plot_image(beam)
    plot_energy_histo(beam)


# unittest ###


class TestShadow(unittest.TestCase):
    def test_shadow(self):
        self.assertTrue(HAS_SHADOW)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestShadow))
    return test_suite


if __name__ == "__main__":
    if 0:
        # unittest
        unittest.main(defaultTest="suite")
    if 1:
        # manual test
        run_test_sbca_si555()

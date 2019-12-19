#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests/Examples for dThetaXZ

TODO
====

"""
# Fix Python 2.x
try:
    input = raw_input
except NameError:
    pass

import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

from sloth.inst.dthetaxz import (
    dThetaXZ,
    mapCase2Num,
    mapNum2Case,
    getMeshMasked,
    getDthetaDats,
    writeScanDats,
)
from sloth.inst.dthetaxz_plot import plotEffScatt, plotScanThetaFile

#: TESTS


def test009():
    """effective scattering figure (updt: 2014-08-15)"""
    mxx1, mzz1 = getMeshMasked(
        mask="circular", r1p=500.0, cryst_x=50.0, cryst_z=50.0, csteps=500j
    )
    wrc = 1.25e-4
    cases = ["Jn", "Js", "SphJn", "TorJs"]
    casesLabs = ["1. Johann", "2. Johansson", "3. Spherical Jn", "4. Toroidal Js"]
    angles = [35, 55, 75]
    plotEffScatt(
        mxx1,
        mzz1,
        wrc=wrc,
        cases=cases,
        angles=angles,
        nlevels=30,
        plotMask=True,
        absWrc=False,
        casesLabels=casesLabs,
        xyFigSize=(8 * 150, 4.3 * 150),
        figName="test009",
    )


def test009b():
    """effective scattering figure (updt: 2014-08-21)"""
    mxx1, mzz1 = getMeshMasked(
        mask="circular", r1p=500.0, cryst_x=50.0, cryst_z=50.0, csteps=500j
    )
    wrc = 1.25e-4
    cases = ["Jn", "Js", "SphJn", "TorJs", "JsFocus"]
    casesLabs = [
        "1. Johann",
        "2. Johansson",
        "3. Spherical Jn",
        "4. Toroidal Js",
        "5. Gen. Js focus",
    ]
    angles = [35, 55, 75]
    plotEffScatt(
        mxx1,
        mzz1,
        wrc=wrc,
        cases=cases,
        casesLabels=casesLabs,
        angles=angles,
        nlevels=30,
        plotMask=True,
        absWrc=False,
        xyFigSize=(8.3 * 150, 3.7 * 150),
        figName="test009b",
        fontSize=9,
        colSpan=2,
        xyTicks=0.1,
    )


def test009c(retDats=False, showPlot=True):
    """effective scattering figure (updt: 2014-09-03)"""
    mxx1, mzz1 = getMeshMasked(
        mask="circular", r1p=500.0, cryst_x=50.0, cryst_z=50.0, csteps=500j
    )
    wrc = 1.25e-4
    cases = ["Jn", "Js", "SphJn", "TorJs", "JsFocus"]
    casesLabs = [
        "1. Johann",
        "2. Johansson",
        "3. Spherical Jn",
        "4. Toroidal Js",
        "5. Gen. Js focus",
    ]
    angles = [15, 45, 75]
    if showPlot:
        plotEffScatt(
            mxx1,
            mzz1,
            wrc=wrc,
            cases=cases,
            casesLabels=casesLabs,
            angles=angles,
            nlevels=30,
            plotMask=True,
            absWrc=False,
            xyFigSize=(8.3 * 150, 3.7 * 150),
            figName="test009c",
            fontSize=9,
            colSpan=2,
            xyTicks=0.1,
        )
    if retDats:
        return getDthetaDats(mxx1, mzz1, wrc=wrc, cases=cases, angles=angles)


def test009d():
    """effective scattering figure (updt: 2015-02-12) """
    wrc = 1.25e-4
    cases = ["SphJn", "Js", "TorJs"]
    casesLabs = ["1. Spherical", "2. Johansson", "3. Toroidal Js"]
    angles = [35, 55, 75]
    rd = 500.0  # bending radius
    msks = ["circular", "rectangular"]
    mxx1, mzz1 = getMeshMasked(
        mask=msks[0], r1p=rd, cryst_x=50.0, cryst_z=50.0, csteps=500j
    )
    mxx2, mzz2 = getMeshMasked(
        mask=msks[1], r1p=rd, cryst_x=50.0, cryst_z=12.5, csteps=500j
    )
    mzz3, mxx3 = getMeshMasked(
        mask=msks[1], r1p=rd, cryst_x=50.0, cryst_z=17.5, csteps=500j
    )
    mxx4, mzz4 = getMeshMasked(
        mask=msks[1], r1p=rd, cryst_x=50.0, cryst_z=25.0, csteps=500j
    )

    # all circular
    plotEffScatt(
        mxx1,
        mzz1,
        wrc=wrc,
        cases=cases,
        casesLabels=casesLabs,
        angles=angles,
        xlabel=r"x, sag. (R$_{1}^{\prime}$)",
        ylabel=r"z, mer. (R$_{1}^{\prime}$)",
        nlevels=30,
        xyFigHalfRange=0.1,
        plotMask=True,
        plotVert=True,
        absWrc=False,
        xyFigSize=(6.0 * 150, 4.0 * 150),
        xylab=(0.04, 0.96),
        figName="{0}mm.{1}".format(int(rd), msks[0]),
        fontSize=9,
        colSpan=2,
        xyTicks=0.1,
    )

    # js rect
    lmxx = [mxx1, mxx2, mxx1]
    lmzz = [mzz1, mzz2, mzz1]
    plotEffScatt(
        lmxx,
        lmzz,
        wrc=wrc,
        cases=cases,
        casesLabels=casesLabs,
        angles=angles,
        xlabel=r"x, sag. (R$_{1}^{\prime}$)",
        ylabel=r"z, mer. (R$_{1}^{\prime}$)",
        nlevels=30,
        xyFigHalfRange=0.1,
        plotMask=True,
        plotVert=True,
        absWrc=False,
        xyFigSize=(6.0 * 150, 4.0 * 150),
        xylab=(0.04, 0.96),
        figName="{0}mm.{1}".format(int(rd), msks[1]),
        fontSize=9,
        colSpan=2,
        xyTicks=0.1,
    )

    input("Press ENTER to close figures")


def test010():
    """multiple effective scattering figures (updt: 2014-06-29)"""
    for rd in [1000.0, 500.0]:
        for msk, cx, cz in zip(["circular", "rectangular"], [50.0, 40.0], [50.0, 12.5]):
            mxx1, mzz1 = getMeshMasked(
                mask=msk, r1p=rd, cryst_x=cx, cryst_z=cz, csteps=500j
            )
            plotEffScatt(
                mxx1,
                mzz1,
                wrc=1e-4,
                cases=["Johansson", "Spherical Jn", "Spherical Js", "Toroidal Js"],
                angles=[35, 55, 75],
                nlevels=30,
                plotMask=True,
                absWrc=False,
                figName="{0}mm.{1}".format(int(rd), msk),
                xyFigHalfRange=0.1,
                xyFigSize=(8 * 150, 4.3 * 150),
            )


def plotDats011(_d):
    """buggy"""
    fig = plt.figure(num="plotDats011", figsize=(5, 5), dpi=150)
    gs = gridspec.GridSpec(1, 2)
    for ird, rd in enumerate(_d["rds"]):
        gsplt = plt.subplot(gs[ird])
        for msk in _d["msks"]:
            if msk == "circular":
                _ls = "-"
                _mk = None
                # _mk = 'o'
                _ms = 2
                mC = 1.0
            else:
                _ls = "--"
                mC = 3.0
                _mk = None
                _ms = 2
            lab = "{0}mm.{1}".format(int(rd), msk)
            for cs, cl in zip(_d["cases"], _d["colors"]):
                gsplt.plot(
                    _d[lab][cs]["thetaB"],
                    np.array(_d[lab][cs]["sa"]) * mC,
                    lw=2,
                    color=cl,
                    ls=_ls,
                    marker=_mk,
                    ms=_ms,
                    label=r"{0} $\times$ {1} {2}".format(int(mC), msk[:4], cs),
                )
        gsplt.set_ylim(0.0, 0.05)
        gsplt.set_xlabel(r"Bragg angle $\theta_B$ (deg)")
        gsplt.set_ylabel(r"Effective solid angle (sr)")
        gsplt.set_title(r"Rect vs Circ at {0} mm bending".format(int(rd)))
        gsplt.legend(loc="best")
    plt.tight_layout()
    plt.show()
    return fig


def test011(retDats=True, plotDats=False):
    """angular study for analyser shapes: circular 50^2 vs rectangular 80x25"""
    _d = {}  # container
    _d["rds"] = [1000.0, 500.0]
    # _d['cases'] = ['Johansson', 'Spherical Jn', 'Toroidal Js', 'Spherical Js', 'Js 45 deg focusing', 'Berreman']
    # _d['cases'] = ['Johansson', 'Spherical Jn', 'Toroidal Js']
    _d["colors"] = ["blue", "green", "red", "orange"]
    _d["angles"] = np.linspace(15, 85, 29)
    _d["msks"] = ["circular", "rectangular"]
    _d["cxs"] = [50.0, 40.0]
    _d["czs"] = [50.0, 12.5]
    _d["csteps"] = 500j
    _d["wrc"] = 1.25e-4
    for rd in _d["rds"]:
        for msk, cx, cz in zip(_d["msks"], _d["cxs"], _d["czs"]):
            mxx, mzz = getMeshMasked(
                mask=msk, r1p=rd, cryst_x=cx, cryst_z=cz, csteps=_d["csteps"]
            )
            lab = "{0}mm.{1}".format(int(rd), msk)
            print("{0}:".format(lab))
            _d["label"] = lab
            _d[lab] = getDthetaDats(
                mxx, mzz, wrc=_d["wrc"], cases=_d["cases"], angles=_d["angles"]
            )
    #
    if plotDats:
        fig011 = plotDats011(_d)
    if retDats:
        return _d


def plotDats012(_d):
    """buggy"""
    fig = plt.figure(num="plotDats012", figsize=(5, 5), dpi=150)
    # gs = gridspec.GridSpec(1,2)
    gs = []
    gs.append(fig.add_subplot(211))
    gs.append(fig.add_subplot(212))
    cs = _d["cases"]
    _ls = 2  # line size
    _mk = None  # marker style
    _ms = 5  # marker size
    for ird, rd in enumerate(_d["rds"]):
        gsplt = plt.subplot(gs[ird])
        for cz, cl in zip(_d["czs"], _d["colors"]):
            lab = "{0}mm/{1}".format(int(rd), cz)
            gsplt.plot(
                _d[lab][cs]["thetaB"],
                _d[lab][cs]["eres"],
                lw=2,
                color=cl,
                ls=_ls,
                marker=_mk,
                ms=_ms,
                label=r"{0}mm".format(cz * 2),
            )
        # gsplt.set_ylim(0.,0.05)
        gsplt.set_xlabel(r"Bragg angle $\theta_B$ (deg)")
        gsplt.set_ylabel(r"Energy resolution $\frac{\Delta E}{E}$")
        gsplt.set_title(r"Js 80 mm height at {0} mm bending".format(int(rd)))
        gsplt.legend(loc="best")
    plt.tight_layout()
    plt.show()
    return fig


def test012(retDats=True):
    """ js energy resolution vs rectangular crystal size width """
    d = {}  # container
    d["fname"] = "dth_test012.spec"
    d["rds"] = [1000.0, 500.0]
    d["cases"] = ["Js"]
    d["angles"] = np.linspace(35, 85, 21)
    d["msks"] = "rectangular"
    d["cxs"] = 40.0
    d["czs"] = [2.5, 5.0, 7.5, 10.0, 12.5, 15.0]
    d["csteps"] = 500j
    d["wrc"] = 1.25e-4
    for rd in d["rds"]:
        # rectangular Js
        for cz in d["czs"]:
            mxx, mzz = getMeshMasked(
                mask=d["msks"], r1p=rd, cryst_x=d["cxs"], cryst_z=cz, csteps=d["csteps"]
            )
            lab = "{0}/{1}mm/{2}".format(d["cases"][0], int(rd), cz * 2)
            motpos = [
                mapCase2Num(d["cases"][0]),
                rd,
                d["msks"],
                d["cxs"],
                cz,
                d["wrc"],
                d["csteps"],
            ]
            print("{0}:".format(lab))
            d[lab] = getDthetaDats(
                mxx, mzz, wrc=d["wrc"], cases=d["cases"], angles=d["angles"]
            )
            writeScanDats(d[lab], d["fname"], scanLabel=lab, motpos=motpos)
        # Spherical plate, Wittry and General point focus 80x50 mm^2 for comparison
        for case in ["SphJn", "TorJs", "JsFocus"]:
            cz = 25.0
            mxx, mzz = getMeshMasked(
                mask=d["msks"], r1p=rd, cryst_x=d["cxs"], cryst_z=cz, csteps=d["csteps"]
            )
            lab = "{0}/{1}mm/{2}".format(case, int(rd), cz * 2)
            motpos = [
                mapCase2Num(case),
                rd,
                d["msks"],
                d["cxs"],
                cz,
                d["wrc"],
                d["csteps"],
            ]
            print("{0}:".format(lab))
            d[lab] = getDthetaDats(
                mxx, mzz, wrc=d["wrc"], cases=[case], angles=d["angles"]
            )
            writeScanDats(d[lab], d["fname"], scanLabel=lab, motpos=motpos)
    #
    if retDats:
        return d


def test013(retDats=True):
    """energy resolution"""
    d = {}  # container
    d["fname"] = "dth_test013.spec"
    d["rds"] = [1000.0, 500.0]
    d["cases"] = ["Js", "SphJn", "TorJs", "JsFocus"]
    d["angles"] = np.linspace(35, 85, 21)
    d["cxs"] = 50.0
    d["csteps"] = 500j
    d["wrc"] = 2e-4
    for rd in d["rds"]:
        for case in d["cases"]:
            if case == "Js":
                # for Js need to use an optimized mask in z
                d["msks"] = "rectangular"
                d["czs"] = 12.5
            else:
                d["msks"] = "circular"
                d["czs"] = 50.0
            mxx, mzz = getMeshMasked(
                mask=d["msks"],
                r1p=rd,
                cryst_x=d["cxs"],
                cryst_z=d["czs"],
                csteps=d["csteps"],
            )
            lab = "{0}/{1}mm/{2}{3}".format(
                case, int(rd), d["msks"][:4], int(d["czs"] * 2)
            )
            motpos = [
                mapCase2Num(case),
                rd,
                d["msks"],
                d["cxs"],
                d["czs"],
                d["wrc"],
                d["csteps"],
            ]
            print("{0}:".format(lab))
            d[lab] = getDthetaDats(
                mxx, mzz, wrc=d["wrc"], cases=[case], angles=d["angles"]
            )
            writeScanDats(d[lab], d["fname"], scanLabel=lab, motpos=motpos)
    #
    if retDats:
        return d


if __name__ == "__main__":
    # pass
    ### TESTS ###
    # uncomment at your convenience

    # utils
    # from genericutils import ipythonAutoreload, getPyMcaMain
    # ipythonAutoreload()
    # m = getPyMcaMain()

    # mxx1, mzz1 = test009(retDats=True)
    # test009()
    # d = test011(retDats=True, plotDats=False)
    # d = test012(retDats=True)
    # plotScanThetaFile('dth_test012.spec', str2rng('5, 7, 8, 13, 15, 16'), signal='eres', plotDeeShells=True, figName='fig1', showLegend=True)
    # plotScanThetaFile('dth_test012.spec', str2rng('5, 7, 8, 13, 15, 16'), signal='eres', plotDeeShells=True, figName='figEres', showLegend=True, xlims=(34,86), ylims=(9E-6, 1.1E-2), figSize=(3.5,6))
    # plotScanThetaFile('dth_test012.spec', str2rng('5, 7, 8, 13, 15, 16'), signal='sa', plotDeeShells=False, figName='figSA', showLegend=False, xlims=(34,86), ylims=None, figSize=(4.5,6), ylog=False, yscale=1)
    # plotScanThetaFile('dth_test013.spec', str2rng('1:8'), signal='eres', plotDeeShells=True, figName='figEres', showLegend=True, xlims=(34,86), ylims=(9E-6, 1.1E-2), figSize=(4.5,6), ylog=True, yscale=1)
    # plotScanThetaFile('dth_test013.spec', str2rng('1:8'), signal='eres', plotDeeShells=True, figName='figEres', showLegend=True, xlims=(34,86), ylims=(9E-6, 1.1E-2), figSize=(3,4), ylog=True, yscale=1)

    #
    # mxx1, mzz1 = test009c(retDats=True, showPlot=False)
    test009d()


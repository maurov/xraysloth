#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example of data reduction 1: peak-like 1D scans
===============================================

This is an example of data reduction performed by the author (M. Rovezzi). The
workflow presented here is applied to a set of peak-like 1D scans (XY) collected
at the beamline ID26 of ESRF in SPEC format (data file:
'peakfit_tests_real.dat'). The steps followed in the data reduction are:

- Step 0: collect the raw data (SPEC or any ASCII data format)
- Step 1: evaluate (load/treat) the data scan-by-scan
- Step 2: loop over the scans and a given set of parameters and write
  reduced data to file or return lists of data to further process
- Step 3: look/analyze the reduced data in PyMca or show a results
  table

"""
import os
import math
import time
import numpy as np
import matplotlib.pyplot as plt

from sloth.io.specfile_reader import SpecfileData
from sloth.fit.peakfit import fit_splitpvoigt, fit_results
from sloth.io.specfile_writer import SpecfileDataWriter
from sloth.utils.generic import imin, imax, colorstr

_curDir = os.path.dirname(os.path.realpath(__file__))

########################
# EVALUATION FUNCTIONS #
########################


def eval_scan(
    fndat,
    scan,
    infodict,
    counter=1,
    signal="det_dtc",
    monitor="I02",
    seconds="Seconds",
    norm="mon",
    showFit=False,
    **kws
):
    """data evaluation of a single peak-type scan contained in a SPEC
    file: load, fit with an asymmetric PseudoVoigt and return data

    Parameters
    ----------
    fndat : str, spec file name (relative or full path)
    scan : int, scan number of the SPEC file to load
    infodict : dictionary describing scan / experiment / sample / whatever
               *example of common keys*:
               'label'   : str, identifier
               'radius'  : float, bending radius in (mm)
               'stage'   : int, spectrometer position of the crystal analyzer
                    (between 1 and 5)
               'scntype' : str, type of scan ('elastic', 'focus')
    counter : str or 1, name of the counter to use as x [1]
    signal : str, name of the signal counter ['det_dtc']
    monitor : str, name of the monitor counter ['I02']
    seconds : str, name of the seconds counter ['Seconds']
    norm : str, signal normalization ['mon_sec']
           'mon'     : y = y_signal / y_monitor
           'cps'     : y = y_normon * np.mean(y_monitor) / y_seconds

    Returns
    -------
    ret_cols, ret_dats : lists with columns names and data
    infodict : info dictionary

    """
    infodict.update(
        {
            "date": "{0}_{1}_{2}_{3}_{4}_{5}".format(*time.localtime()),
            "fndat": fndat,
            "scan": scan,
            "norm": norm,
            "counter": counter,
            "signal": signal,
            "monitor": monitor,
            "seconds": seconds,
        }
    )

    # get label (if given)
    try:
        label = infodict["label"]
    except KeyError:
        label = "no_label_in_infodict"

    # get scantype (if given)
    try:
        scntype = infodict["scntype"]
    except KeyError:
        scntype = "unknown"

    # scale y to position on scattering plane
    y_elastic0 = 1.0
    y_elastic = 1.0

    # get separate data for signal, monitor and seconds
    t = SpecfileData(fndat)
    x, y_sec, motors, infos = t.get_scan(
        scan, cntx=counter, csig=seconds, cmon=None, csec=None, norm=None
    )
    x, y_mon, motors, infos = t.get_scan(
        scan, cntx=counter, csig=monitor, cmon=None, csec=None, norm=None
    )
    x, y_sig, motors, infos = t.get_scan(
        scan, cntx=counter, csig=signal, cmon=None, csec=None, norm=None
    )
    if norm == "mon":
        y = y_sig / y_mon
        infodict.update({"norm": "y_signal/y_monitor"})
    elif norm == "cps":
        y = y_sig / y_sec
        infodict.update({"norm": "(y_signal/y_monitor)*np.mean(y_monitor)/y_seconds"})
    else:
        y = y_sig
        infodict.update({"norm": "y_signal"})

    # fit x,y
    try:
        fit, pw = fit_splitpvoigt(
            x, y, dy=True, bkg="Constant", plot=showFit, show_res=showFit
        )
        fit.xrel = x - fit.resdict["cfwhm"]
        print("=> OK PEAK FIT [{0}] <=".format(label))
    except Exception:
        print("=> ERROR PEAK FIT [{0}] <=".format(label))
        fit.resdict = {
            "area": np.nan,
            "cfwhm": np.nan,
            "fwhm": np.nan,
            "height": np.nan,
            "position": np.nan,
        }
        fit.xrel = x
        fit.yfit = np.zeros_like(x)

    infodict.update(fit.resdict)
    infodict.update({"label": label})

    infodict.update(
        {
            "y_area": np.trapz(y),
            "y_max": np.max(y),
            "y_imax": imax(y),
            "y_min": np.min(y),
            "y_imin": imin(y),
        }
    )

    # apply yscale_el if an elastic peak
    y_elastic0 = 1.0
    y_elastic = 1.0
    y_el = y / (y_elastic / y_elastic0)
    infodict.update({"y_elastic": y_elastic / y_elastic0})

    ret_cols = ["x", "x_rel", "y_norm", "y_fit", "y_el", "signal", "monitor", "seconds"]
    ret_dats = [x, fit.xrel, y, fit.yfit, y_el, y_sig, y_mon, y_sec]

    return ret_cols, ret_dats, infodict


def eval_loop(
    scntype,
    fns,
    scans,
    labs,
    marks,
    rads,
    poss,
    flags,
    framert=125.0,
    axsep=120.0,
    theta0=75.0,
    fnout=None,
    owrt=True,
    retall=False,
    show_results=False,
    **kws
):
    """data evaluation step 2: loop over a set of lists

    Parameters
    ----------
    scntype : str, type of scan (e.g. 'elastic', 'focus')
    fns, scans, labs, marks, rads, poss, flags : lists with the same length
        fns   : SPEC file names
        scans : scan numbers
        labs  : labels
        marks : mark on the crystal
        rads  : bending radius
        poss  : positions on the spectrometer
        flags : 0 (not load)  or 1 (load)
    framert : float, rotation angle on the scattering plane (deg) [125.]
    axsep : float, analyzer-to-analyzer spacing (mm) [120.]
    theta0 : float, angle of the tests (deg) [75.]
    fnout : str, filename to write output [None]
    owrt : boolean, overwrite the output file [True]
    retall : boolean, return all list of lists and list of dicts [False]
    show_results : boolean, print '& fwhm & cfwhm & height & area' to screen [False]

    Returns
    -------
    if retall: lcols, ldats, linfs
    None, writes to fnout

    """
    lcols = []
    ldats = []
    linfs = []

    for fn, scan, lab, mark, rad, pos, flag in zip(
        fns, scans, labs, marks, rads, poss, flags
    ):
        if flag == 0:
            continue
        idict = {
            "label": lab,
            "mark": mark,
            "radius": rad,
            "stage": pos,
            "framert": framert,
            "axsep": axsep,
            "theta0": theta0,
            "scntype": scntype,
        }
        try:
            lcol, ldat, linf = eval_scan(fn, scan, idict, **kws)
        except Exception:
            print("ERROR with eval_scan(), nothing done!")
            continue
        lcols.append(lcol)
        ldats.append(ldat)
        linfs.append(linf)

    if fnout is not None:
        sfout = SpecfileDataWriter(fnout, owrt=owrt)
        try:
            motnames = [key for key in linfs[0].keys()]
        except Exception:
            print("WARNING: nothing to write")
            if retall:
                return lcols, ldats, linfs
            else:
                return
        sfout.write_header(title="eval_loop", motnames=motnames)
        for lcol, ldat, linf in zip(lcols, ldats, linfs):
            motpos = [val for val in linf.values()]
            title = "{0}_R{1:.0f}_P{2}_M{3}_{4}".format(
                linf["label"],
                linf["radius"],
                linf["stage"],
                linf["mark"],
                linf["scntype"],
            )
            sfout.write_scan(lcol, ldat, title=title, motpos=motpos)
        print("EVALUATION RESULTS WRITTEN TO SPECFILE")

    if show_results:
        eval_show_results(linfs, norm_to_first=True)

    if retall:
        return lcols, ldats, linfs


def eval_show_results(linfdict, norm_to_first=False):
    """evaluation step3 : show results

    Parameters
    ----------
    linfdict : list of dictionaries with results
    norm_to_first : boolean or tuple, to nomalize height and area

    """
    _tmpl_head = (
        "{0:^15} & {1:^5} &  {2:^5} & {3:^8} & {4:^7} & {5:^8} & {6:^8} & {7:^8}"
    )
    _tmpl_res = "{0:^15} & {1:^5.0f} & {2:^5.0f} & {3:^8.2f} & {4:^7.3f} & {5:^8.2f} & {6:^8.4f} & {7:^8.4f}"
    print("=> RESULTS <=")
    print(
        _tmpl_head.format(
            "label", "pos", "mark", "radius", "fwhm", "cfwhm", "height", "area"
        )
    )
    for idic, dic in enumerate(linfdict):
        if idic == 0:
            height0 = dic["height"]
            area0 = dic["area"]
        if norm_to_first:
            try:
                height0 = norm_to_first[0]
                area0 = norm_to_first[1]
            except Exception:
                pass
        else:
            height0 = 1.0
            area0 = 1.0
        print(
            _tmpl_res.format(
                dic["label"],
                dic["stage"],
                dic["mark"],
                dic["radius"],
                dic["fwhm"],
                dic["cfwhm"],
                dic["height"] / height0,
                dic["area"] / area0,
            )
        )


if __name__ == "__main__":
    plt.ion()
    plt.close("all")

    if 1:
        print(colorstr("=== xraysloth: example of data reduction 1 ==="))

        # take data from current directory
        _curDir = os.path.dirname(os.path.realpath(__file__))
        kwd = {
            "counter": 1,
            "signal": "det_dtc",
            "monitor": "I02",
            "seconds": "Seconds",
            "norm": "mon",
        }

        out_root = os.path.join(_curDir, "data_reduction_example1")
        out_date = "{0:04d}-{1:02d}-{2:02d}".format(*time.localtime())
        fnout_el = "{0}_{2}.spec".format(out_root, out_date, "out")
        resl_el = []
        resl_fc = []

        f0 = os.path.join(_curDir, "peakfit_tests_real.dat")

        fns = [f0, f0, f0, f0]
        escans = [26, 27, 45, 46]
        labs = ["T1", "T2", "T3", "T4"]
        marks = [1, 1, 1, 1]
        rads = [1000.0, 1000.0, 500.0, 500.0]
        poss = [1, 2, 3, 4]
        flags = [1, 1, 1, 1]

        lcols_el, ldats_el, linfs_el = eval_loop(
            "elastic",
            fns,
            escans,
            labs,
            marks,
            rads,
            poss,
            flags,
            fnout=fnout_el,
            owrt=True,
            retall=True,
            show_results=True,
            **kwd
        )
    if 1:
        # you can see the _out.spec file with PyMca
        print(colorstr("=== opening PyMca  ==="))
        from PyMca5.PyMcaGui import PyMcaMain

        m = PyMcaMain.PyMcaMain()
        m.show()
    pass

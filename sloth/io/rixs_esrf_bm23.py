#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RIXS data reader for beamline BM23 @ ESRF
=========================================

.. note: RIXS stands for Resonant Inelastic X-ray Scattering

"""
import os
import time
import numpy as np

from silx.io.dictdump import dicttoh5

from sloth.utils.bragg import ang2kev
from sloth.io.datasource_spech5 import DataSourceSpecH5

from sloth.utils.logging import getLogger

_LOGGER = getLogger("io_rixs_bm23")


def get_rixs_bm23(
    macro_in,
    d_spacing,
    sample_name="unknown_sample",
    data_dir=".",
    out_dir=None,
    counter_signal="alpha",
    counter_norm="I0",
    energy_to_ev=True,
    save_rixs=False,
):
    """Get RIXS data using a given macro file
    
    Parameters
    ----------
    macro_in : str
        file name (full path) of the macro used to collect the RIXS plane
        example of expected format:
            ```
            ...

            mv spth 86.74
            scan Au2S_rixs_65.dat

            ...

            ```
    d_spacing : float,
        spectrometer d-spacing
    sample_name : str, optional
        sample name ["unknown_sample"]
    out_dir : str, optional
        path to save the data [None -> data_dir]
    counter_signal : str
        name of the data column to use as signal
    counter_norm : str
        name of the data column to use as normaliztion
    interp_ene_in: bool
        perform interpolation ene_in to the energy step of ene_out [True]
    save_rixs : bool or str
        if True -> save outdict to disk as 'save_rixs' name in 'out_dir'

    Returns
    -------
    outdict : dict
        {
        '_x': array, energy in
        '_y': array, energy out
        '_z': array, signal
        'writer_name': str,
        'writer_version': str,
        'writer_timestamp': str,
        'filename_all' : list,
        'filename_root': str,
        'name_sample': str,
        'name_scan': str,
        'counter_all': str,
        'counter_signal': str,
        'counter_norm': str,
        'ene_grid': float,
        'ene_unit': str,
        }
    """
    _writer = "get_rixs_bm23"
    _writer_version = "1.5"  #: used for reading back in RixsData.load_from_h5()
    _writer_timestamp = "{0:04d}-{1:02d}-{2:02d}_{3:02d}{4:02d}".format(
        *time.localtime()
    )

    if out_dir is None:
        out_dir = data_dir

    if energy_to_ev:
        xscale = 1000.0
        ene_unit = "eV"
    else:
        xscale = 1.0
        ene_unit = "keV"

    if os.path.isfile(macro_in) and os.access(macro_in, os.R_OK):
        lines = open(macro_in, "r").read().splitlines()
    else:
        raise FileNotFoundError("check %s exists!", macro_in)

    enes_out = []
    fnames = []
    xcol, ycol, zcol = np.array([]), np.array([]), np.array([])

    for line in lines:
        ln_split = line.split(" ")
        if "spth" in ln_split:
            th = float(ln_split[2])
            eout = ang2kev(th, d=d_spacing) * xscale
            enes_out.append(eout)
        elif "scan" in ln_split:
            fn = ln_split[1]
            fnames.append(fn)
            d = DataSourceSpecH5(os.path.join(data_dir, fn))
            scan = d.get_scans()[0].split(".")[0]
            d.set_scan(scan)
            ein = d.get_array(0) * xscale
            eout = np.ones_like(ein) * enes_out[-1]
            sig = d.get_array(counter_signal)
            nor = d.get_array(counter_norm)
            sig_nor = sig / nor
            xcol = np.append(xcol, ein)
            ycol = np.append(ycol, eout)
            zcol = np.append(zcol, sig_nor)
            _LOGGER.info("Loaded scan %s: %.3f %s", fn, enes_out[-1], ene_unit)
        else:
            continue

    sig_lab = f"{counter_signal}/{counter_norm}"

    outdict = {
        "_x": xcol,
        "_y": ycol,
        "_z": zcol,
        "writer_name": _writer,
        "writer_version": _writer_version,
        "writer_timestamp": _writer_timestamp,
        "sample_name": sample_name,
        "filename_root": data_dir,
        "filename_all": fnames,
        "counter_signal": counter_signal,
        "counter_norm": counter_norm,
        "signal_label": sig_lab,
        "ene_unit": ene_unit,
    }

    if save_rixs:
        if os.path.isfile(save_rixs) and os.access(save_rixs, os.R_OK):
            _LOGGER.warning("File %s exists -> overwriting!", save_rixs)
            os.remove(save_rixs)
        try:
            dicttoh5(outdict, os.path.join(out_dir, save_rixs))
            _LOGGER.info("RIXS saved to %s", save_rixs)
        except Exception:
            _LOGGER.error("Cannot save RIXS to %s", save_rixs)

    return outdict


"""
Data Reduction workflow for multi-element fluorescence detector
===============================================================

Currently applied to BLISS data collected at ESRF/BM16 beamline
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@esrf.fr"
__version__ = "2024.1"
__license__ = "MIT"
__copyright__ = "2024, CNRS"

import os
import glob
import numpy as np
import logging
import palettable
from typing import NamedTuple

from IPython.display import display

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from larch.io.specfile_reader import DataSourceSpecH5, __version__, _str2rng
from larch.plot.plotly_xafsplots import PlotlyFigure

from larch.math.deglitch import remove_spikes_medfilt1d

from larch import Group
from larch.io import AthenaProject

from larch.xafs import pre_edge
from larch.xafs.rebin_xafs import rebin_xafs
from larch.io.mergegroups import merge_arrays_1d

_logger = logging.getLogger("WKFL_BLISS2LARCH_FLUO")
_logger.setLevel(logging.INFO)  # adjust logger level .INFO, .WARNING, .ERROR

_logger.debug(f"using DataSourceSpecH5 version {__version__}")


# colors
# CFLUO = palettable.colorbrewer.sequential.Blues_8_r.hex_colors[:4]
# CFLUO.extend(palettable.colorbrewer.sequential.BuGn_8_r.hex_colors[:4])
# CFLUO.extend(palettable.colorbrewer.sequential.OrRd_8_r.hex_colors[:4])
# CFLUO.extend(palettable.colorbrewer.sequential.YlOrBr_8_r.hex_colors[:4])

CFLUO = palettable.colorbrewer.diverging.RdBu_11.hex_colors[:4]
CFLUO.extend(palettable.colorbrewer.diverging.RdBu_11_r.hex_colors[:4])
CFLUO.extend(palettable.colorbrewer.diverging.PRGn_11.hex_colors[:4])
CFLUO.extend(palettable.colorbrewer.diverging.PRGn_11_r.hex_colors[:4])

# CFLUO = palettable.tableau.GreenOrange_12.hex_colors
# CFLUO.extend(palettable.tableau.PurpleGray_12.hex_colors)

CTABGO12 = palettable.tableau.GreenOrange_12.hex_colors
CTABPG12 = palettable.tableau.PurpleGray_12.hex_colors


class ExpCounters(NamedTuple):
    ene: str
    ix: list
    fluo_roi1: list
    fluo_corr: list
    fluo_time: list
    time: str
    mu: list


class ExpDataset(NamedTuple):
    sample_name: str
    name: str
    flag: int
    fname: str
    scans: list
    scans_flag: list  # flags for good/bad scans
    scans_mrg: list  # merged fluo per scan (list of Larch groups, same index as scans)
    scans_mu: list  # data_mu groups (e.g. reference)
    nscans: int
    data_fluo: dict  # data for cnts.fluo_x
    fluo_flag: dict  # flags for good/bad channels
    data_ix: dict  # data for cnts.ix


class EneScan(NamedTuple):
    flag: int
    fname: str
    scanno: str
    title: str
    time: str
    comment: str


def search_data(sample_name, datadir):
    """search for HDF5 files and enetraj scans, grouped by datasets

    - file search string is: f"{datadir}/RAW_DATA/{sample_name}/**/*.h5"
    - scan search string is: ".1" and "enetraj"

    """
    search_str = f"{datadir}/RAW_DATA/{sample_name}/**/*.h5"
    fnames = glob.glob(search_str)

    datasets = []
    outinfo = ["idx: [nscans] dataset name"]

    isamp = 0
    for fname in fnames:
        scans = []
        scans_flag = []
        scans_mrg = []
        scans_mu = []
        fnroot = fname.split(os.sep)[-1].split(".")[0]
        dat = DataSourceSpecH5(fname, verbose=False)
        dat._logger.setLevel("ERROR")
        nscans = 0
        for scanno, scantitle, scantstamp in dat.get_scans():
            if (".1" in scanno) and ("enetraj" in scantitle):
                try:
                    dat.set_scan(scanno)
                except Exception:
                    continue
                nscans += 1
                # scans.append(EneScan(flag=1, scanno=scanno, fname=fname, title=scantitle, time=scantstamp, comment=''))
                scanint = int(scanno.split(".")[0])
                scans.append(scanint)
                scans_flag.append(1)
                scans_mrg.append(None)
                scans_mu.append(None)
        dat.close()
        if nscans == 0:
            continue
        outinfo.append(f"{isamp}: [{nscans}] {fnroot}")
        datasets.append(
            ExpDataset(
                sample_name=sample_name,
                name=fnroot,
                flag=1,
                scans=scans,
                scans_flag=scans_flag,
                scans_mrg=scans_mrg,
                scans_mu=scans_mu,
                nscans=nscans,
                fname=fname,
                data_fluo={},
                fluo_flag={},
                data_ix={},
            )
        )
        isamp += 1

    _logger.info(f"found {len(datasets)} datasets [{len(fnames)} HDF5 files]")
    _logger.info("\n".join(outinfo))

    return datasets


def load_data(samp, cnts, use_fluo_corr=True, filter_spikes=False, wrong_scans=[], **kws):
    """load fluorescence data into ExpSample

    Parameters
    ----------

    samp : ExpDataset
        dataset NamedTuple

    cts : ExpCounters
        counters NamedTuple

    use_fluo_corr : bool [True]
        when True, use the dead-time corrected fluorescence channels otherwise
        the uncorrected `roi1` is used

    filter_spikes: bool [False]
        if True, remove spikes via median filter (with default parameters)

    Returns
    -------

    None : sets samp.data_* dictionaries


    """
    # assert isinstance(samp, ExpSample), "samp should be `ExpSample` type"
    # assert isinstance(cnts, ExpCounters), "counters should be `ExpCounters` type"

    if use_fluo_corr:
        cnts_fluo = cnts.fluo_corr
    else:
        cnts_fluo = cnts.fluo_roi1

    ds = DataSourceSpecH5(samp.fname)

    for iscan, scan in enumerate(samp.scans):
        _logger.debug(f"{samp.name}: scan {scan}")
        #eliminate problematic scans
        if scan in wrong_scans:
            samp.scans_flag[iscan] = 0
            continue

        ds.set_scan(scan)
        ene = ds.get_array(cnts.ene) * 1000  # in eV
        i0 = ds.get_array(cnts.ix[0])
        fluo0 = ds.get_array(cnts_fluo[0])
        stime = ds.get_array(cnts.time)

        _logger.debug(
            f"{cnts.ene} [{ene.shape}], {cnts.ix[0]} [{i0.shape}], {cnts_fluo[0]} [{fluo0.shape}]"
        )
        print(ene.shape, i0.shape)
        assert (
            ene.shape == i0.shape
        ), f"{samp.name}/{scan}: array shape mismatch ene/i0/i1/i2"

        # check points dicrepancies with fluorescence
        ptsene = ene.shape[0]
        ptsfluo = fluo0.shape[0]
        ptsdiff = ptsene - ptsfluo
        if ptsdiff:
            _logger.warning(
                f"{samp.name}/{scan}: ene/fluo pts mismatch -> skipping {ptsdiff} initial points"
            )
            ene = ene[ptsdiff:]
            i0 = i0[ptsdiff:]
            stime = stime[ptsdiff:]

        # load fluo data
        samp.data_fluo[scan] = []
        samp.fluo_flag[scan] = []
        for isig, (sig, etime) in enumerate(zip(cnts_fluo, cnts.fluo_time)):
            if filter_spikes:
                ysig = remove_spikes_medfilt1d(ds.get_array(sig))
                lab = f"{sig}_filt"
            else:
                ysig = ds.get_array(sig) / ds.get_array(etime) * stime
                lab = f"{sig}"
            ysig = (ysig / i0) * np.average(i0)  #: to keep number of counts
            lab += f"/{cnts.ix[0]}"

            # create Larch group (used after channels sum)
            # gname = f"{samp.name}_scan{scan}_fluo{isig}"
            # g = Group(
            #    id=gname,
            #    name=gname,
            #    datatype="xas",
            #    energy=ene,
            #    mu=ysig,
            #    i0=i0,
            #    flag=1,
            #    signal=sig,
            #    color=CFLUO[isig],
            #    sample=samp.sample_name,
            #    dataset=samp.name,
            #    fname=samp.fname,
            #    scan=scan,
            # )
            # pre_edge(g)
            # rebin_xafs(g)
            # samp.data_fluo[scan].append(g)

            # create curves (previous)
            info = {
                "flag": 1,
                "signal": sig,
                "color": CFLUO[isig],
                "scan": scan,
                "sample": samp.sample_name,
                "dataset": samp.name,
            }
            curve = [ene, ysig, lab, info]
            samp.data_fluo[scan].append(curve)
            samp.fluo_flag[scan].append(1)

        # load mu data
        #data_mu = []
        #for isig, sig in enumerate(cnts.mu):
        #    ysig = ds.get_array(sig)
        #    if not ysig.shape == ene.shape:
        #        ysig = ysig[ptsdiff:]
        #    assert (
        #        ene.shape == ysig.shape
        #    ), f"{samp.name}/{scan}: array shape mismatch ene/{sig}"
        #    # create Larch group (current)
        #    gname = f"{samp.name}_scan{scan}_{sig}"
        #    g = Group(
        #        id=gname,
        #        name=gname,
        #        filename=gname,
        #        groupname=gname,
        #        datatype="xas",
        #        energy=ene,
        #        mu=ysig,
        #        i0=i0,
        #        flag=1,
        #        signal=sig,
        #        color=CTABGO12[isig],
        #        sample=samp.sample_name,
        #        dataset=samp.name,
        #        scan=scan,
        #    )
        #    pre_edge(g)
        #    rebin_xafs(g)
        #    data_mu.append(g)
        #samp.scans_mu[iscan].append(data_mu)

        # load ix data
        # samp.data_ix[scan] = []
        # for isig, sig in enumerate(cnts.ix):
        #    ysig = ds.get_array(sig)
        #    if not ysig.shape == ene.shape:
        #        ysig = ysig[ptsdiff:]
        #    assert (
        #        ene.shape == ysig.shape
        #    ), f"{samp.name}/{scan}: array shape mismatch ene/{sig}"
        #    #create Larch group (current)
        #    g = Group(
        #        id=f"{samp.name}_scan{scan}_{sig}",
        #        datatype="xas",
        #        energy=ene,
        #        mu=ysig,
        #        flag=1,
        #        signal=sig,
        #        color=CTABPG12[isig],
        #        sample=samp.sample_name,
        #        dataset=samp.name,
        #        scan=scan,
        #    )
        #    samp.data_ix[scan].append(g)
        #    #create curves (previous)
        #    #info = {"flag": 1, "signal": sig, "color": CTABPG12[isig]}
        #    #curve = [ene, ysig, sig, info]
        #    #samp.data_ix[scan].append(curve)

    ds.close()


def plot_curves(samp, scan=None, yoffset=0, ynorm=False):
    """plot curves"""

    if scan is None:
        scans = samp.scans
        flags = samp.scans_flag
    else:
        assert scan in samp.scans, f"available scans: {samp.scans}"
        scans = [scan]
        flags = [1]

    data = samp.data_fluo  # TODO: extend to data_mu, data_ix

    for iscn, (scn, sflag) in enumerate(zip(scans, flags)):
        if sflag == 0:
            continue

        fig = make_subplots(rows=1, cols=1)
        curves = data[scn]

        yshift = 0
        for x, y, lab, info in curves:
            if info["flag"] == 0:
                continue

            detlab = info["signal"].split("_")[-1]

            if ynorm == "area":
                y = y / np.trapz(y)

            fig.add_trace(
                go.Scatter(
                    x=x, y=y, name=detlab, marker=None, line=dict(color=info["color"])
                ),
                row=1,
                col=1,
            )
            yshift += yoffset

        fig.update_layout(
            height=600,
            width=1000,
            title_text=f"dataset: {samp.name} | scan: {scn}",
            showlegend=True,
        )
        fig.show()


def set_bad_channels(samp, bad_channels, scan=None):
    """set bad fluo channels for a given scan or all scans"""

    if scan is None:
        allscans = []
        #do not consider the problematic scans, identified as wrong during loading
        for iscn,scn in enumerate(samp.scans):
            if samp.scans_flag[iscn]:
                 allscans.append(scn)
        #allscans = samp.scans
    else:
        assert scan in samp.scans, f"available scans: {samp.scans}"
        allscans = [scan]

    if isinstance(bad_channels, str):
        bad_channels = _str2rng(bad_channels)
    assert isinstance(bad_channels, list), "bad_channels should be a list"

    for scn in allscans:
        for ichannel, [x, y, lab, info] in enumerate(samp.data_fluo[scn]):
            if ichannel in bad_channels:
                info["flag"] = 0
                samp.fluo_flag[scn][ichannel] = 0

    # for scn in allscans:
    #    samp.bad_channels[scn] = bad_channels
    #    for ig, g in enumerate(samp.data_fluo[scn]):
    #        if ig in bad_channels:
    #            g.flag = 0


def set_bad_scans(samp, bad_scans):
    """set flag=0 to bad scans -> not included in merge"""

    if isinstance(bad_scans, str):
        bad_scans = _str2rng(bad_scans)
    assert isinstance(bad_scans, list), "bad scans should be a list"

    scans_flag0 = []
    for iscn, scn in enumerate(samp.scans):
        if scn in bad_scans:
            samp.scans_flag[iscn] = 0
            scans_flag0.append(scn)
    _logger.info(f"flagged {len(scans_flag0)} bad scans: {scans_flag0}")


def merge_data(samp):
    """merge data"""

    scans = samp.scans
    flags = samp.scans_flag
    data = samp.data_fluo

    outinfo = ["scan idx: group name"]

    for iscn, (scn, sflag) in enumerate(zip(scans, flags)):
        if sflag == 0:
            continue

        allcurves = data[scn]
        allflags = samp.fluo_flag[scn]
        curves_to_mrg = []
        for curve, flag in zip(allcurves, allflags):
            if flag == 0:
                continue
            curves_to_mrg.append(curve)

        nmrg = len(curves_to_mrg)
        ene, ymrg = merge_arrays_1d(curves_to_mrg, method="sum", data_fmt="curves")

        gname = f"{samp.name}_scan{scn}_sum{nmrg}"
        g = Group(
            id=gname,
            name=gname,
            groupname=gname,
            filename=gname,
            datatype="xas",
            energy=ene,
            mu=ymrg,
            flag=1,
            scan=scn,
        )
        pre_edge(g)
        rebin_xafs(g)
        pre_edge(g.rebinned)
        samp.scans_mrg[iscn] = g
        outinfo.append(f"{iscn}: {gname}")
    _logger.info("\n".join(outinfo))


def plot_groups(samp, show_rebinned=False):
    """plot merged Larch groups"""
    fig = make_subplots(rows=1, cols=1)
    for iscn, (grp, flag) in enumerate(zip(samp.scans_mrg, samp.scans_flag)):
        if flag == 0:
            continue

        if show_rebinned:
            x = grp.rebinned.energy
            y = grp.rebinned.mu
        else:
            x = grp.energy
            y = grp.mu

        fig.add_trace(
            go.Scatter(x=x, y=y, name=grp.id, marker=None),
            row=1,
            col=1,
        )

        fig.update_layout(
            height=600,
            width=1000,
            title_text=f"{samp.name}",
            showlegend=True,
        )
    fig.show()


def save_data(samp, datadir):
    """save all data to an Athena project file"""

    sx_logger = logging.getLogger("silx")
    sx_logger.setLevel(logging.ERROR)

    fnameout = os.path.join(datadir, "PROCESSED_DATA", f"{samp.name}.prj")

    apj = AthenaProject(fnameout)
    apj.info = {}

    apj.info["scans"] = samp.scans
    apj.info["cnts"] = []

    for iscn, (grp, flag) in enumerate(zip(samp.scans_mrg, samp.scans_flag)):
        if flag == 0:
            continue
        
        #apj.add_group(grp)
        g = grp.rebinned
        g.id=f"{grp.id}_rebin"
        print(g.id)
        apj.add_group(g)


    #for mu in samp.data_mu:

    apj.save()
    _logger.info(f"data saved in {fnameout}")

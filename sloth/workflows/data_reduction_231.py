"""
Data Evaluation utilities for BM16 users
========================================

This is intended to be used from the notebooks

(!) DEPRECATED (!) -> will be removed soon

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@esrf.fr"
__version__ = "2023.1"
__license__ = "MIT"
__copyright__ = "2024, CNRS"


import glob
import time
import datetime
import os
import logging
import copy
import numpy as np

from IPython.display import display

from larch.io.specfile_reader import DataSourceSpecH5
from larch.io.specfile_reader import _str2rng as str2rng
from larch.io.mergegroups import merge_arrays_1d
from larch.plot.plotly_xafsplots import PlotlyFigure

from larch.math.deglitch import remove_spikes_medfilt1d

from sloth.utils.strings import natural_keys

_logger = logging.getLogger("bm16_eval_utils")
_logger.setLevel(logging.INFO)

def show_data(datadir, samples):
    fns = {}
    for (samp_flag, samp_name, samp_scans) in samples:
        fn = glob.glob(os.path.join(datadir, samp_name, f"{samp_name}_*", "*.h5"), recursive=True)
        fn_ids = [_fn.split(os.sep)[-1].split("_")[-1].split(".")[0] for _fn in fn]
        fn_ids.sort(key=natural_keys)
        fn_keys = []
        for idx in fn_ids:
            samp_prefix = f"{samp_name}_{idx}"
            fnin = os.path.join(datadir, samp_name, samp_prefix, f"{samp_prefix}.h5")
            try:
                ds = DataSourceSpecH5(fnin)
                _scans = ds.get_scans()
                nscans = len(_scans)
                ds.close()
            except Exception:
                nscans="?"
            fn_id = f"{idx}/1:{nscans}"
            fn_keys.append(fn_id)
        fns[samp_name] = fn_keys
    display(fns)

def parse_samples(datadir, samples, counters):

    samps = []
    for (samp_flag, samp_name, samp_scans) in samples:
        for scanstr in samp_scans:
            try:
                file_idx, scns = scanstr.split("/")
            except Exception:
                continue
            samp_prefix = f"{samp_name}_{file_idx}"
            fn = os.path.join(datadir, samp_name, samp_prefix, f"{samp_prefix}.h5")
            scanno = str2rng(scns)
            samps.append([samp_flag, samp_name, fn, scanno])   
    return samps

class ExpDataV4:
    def __init__(self, datadir, samples, counters) -> None:
        assert os.path.exists(datadir), f"datadir does not exists"
        self._datadir = datadir
        self._samples = samples
        self._counters = counters
        self.data = []

    def get_curves(
        self,
        signal,
        monitor=None,
        samples=None,
        counters=None,
        datadir=None,
        plot=True,
        **kws,
    ):
        """get data"""

        if samples is None:
            samples = self._samples
        if counters is None:
            counters = self._counters
        if datadir is None:
            datadir = self._datadir

        if isinstance(signal, int):
            sig = counters["fluo"][signal - 1]
        else:
            sig = counters[signal]

        if monitor is not None:
            mon = counters[monitor]
        else:
            mon = None

        for samp in samples:
            if samp.flag == 0:
                continue

            # collect data per sample
            curves = []
            for scan in samp.scans:
                ds = DataSourceSpecH5(samp.fname)
                ds.set_scan(scan)
                (x, y, lab, info) = ds.get_curve(sig, mon=mon, **kws)
                ds.close()
                curves.append((x, y, lab, info))

        if plot:
            fig = self.plot_curves(curves)

        return curves

    def plot_curves(self, curves):
        fig = PlotlyFigure()
        for x, y, lab, info in curves:
            fig.add_plot(x[1:], y[1:], label=lab)
        fig.show()
        return fig



class ExpDataV3:
    def __init__(self, datadir, samples, counters) -> None:
        assert os.path.exists(datadir), f"datadir does not exists"
        self._datadir = datadir
        self._samples = samples
        self._counters = counters
        self.data = []

    def get_curves(
        self,
        signal,
        monitor=None,
        samples=None,
        counters=None,
        datadir=None,
        plot=True,
        **kws,
    ):
        """get data"""

        if samples is None:
            samples = self._samples
        if counters is None:
            counters = self._counters
        if datadir is None:
            datadir = self._datadir

        if isinstance(signal, int):
            sig = counters["fluo"][signal - 1]
        else:
            sig = counters[signal]

        if monitor is not None:
            mon = counters[monitor]
        else:
            mon = None

        for flag, samp, scanstr, scaninfo in samples:
            if flag == 0:
                continue
            file_idx, scans = str2rng(scanstr)
            samp_prefix = f"{samp}_{file_idx}"
            fname = os.path.join(datadir, samp, f"{samp_prefix}", f"{samp_prefix}.h5")

            # collect data per sample
            curves = []
            for scan in scans:
                ds = DataSourceSpecH5(fname)
                ds.set_scan(scan)
                (x, y, lab, info) = ds.get_curve(sig, mon=mon, **kws)
                ds.close()
                curves.append((x, y, lab, info))

        if plot:
            fig = self.plot_curves(curves)

        return curves

    def plot_curves(self, curves):
        fig = PlotlyFigure()
        for x, y, lab, info in curves:
            fig.add_plot(x[1:], y[1:], label=lab)
        fig.show()
        return fig


class ExpDataV1:
    def __init__(self, datadir, samples=None, counters=None) -> None:
        assert os.path.exists(datadir), f"datadir does not exists"
        self._datadir = datadir
        self._samples = samples
        self._counters = counters

    def plot_curves(self, curves):
        fig = PlotlyFigure()
        for x, y, lab, info in curves:
            fig.add_plot(x[1:], y[1:], label=lab)
        fig.show()
        return fig

    def get_curves(
        self,
        samp_name,
        scans_str,
        remove_spikes=False,
        iskip=1,
        verbose=False,
        **kwargs,
    ):
        """get scan data and returns a list of curves

        Arguments
        ---------

        h5path : str
            h5 file full path

        counters : dict


        Returns
        -------

        curves : list of lists
            Curves format is the following:
            [
                [x1, y1, label1, info1],
                ...
                [xN, yN, labelN, infoN]
            ]



        """
        counters = self._counters
        datadir = self._datadir

        curves = []

        assert isinstance(
            scans_str, str
        ), "scan_str should be a sting like '0004/1:10, 20, 30:40:3"
        fn_idx, scans = str2rng(scans_str)

        samp_prefix = f"{samp_name}_{fn_idx}"
        fnin = os.path.join(datadir, samp_name, samp_prefix, f"{samp_prefix}.h5")

        tstart = time.time()
        ds = DataSourceSpecH5(fnin, verbose=verbose)

        for scan in scans:
            try:
                ds.set_scan(scan)
            except Exception:
                _logger.info(f"cannot load {samp_prefix}/{scan}")
                continue
            ene = ds.get_array(counters["ene_cnt"])[iskip : -1 * iskip]
            i0 = ds.get_array(counters["i0_cnt"])[iskip : -1 * iskip]
            for fluo_cnt in counters["fluo_cnts"]:
                scan_label = f"{scan}: {fluo_cnt}"
                fluo = ds.get_array(fluo_cnt)[iskip : -1 * iskip]
                if remove_spikes:
                    fluo = remove_spikes_medfilt1d(fluo)
                if not (fluo.shape == i0.shape):
                    _logger.error(f"{scan_label}: shape mismatch")
                    continue
                fluo = (fluo / i0) * np.average(i0)  # convert to counts
                infos = dict(
                    norm="(fluo / i0) * np.average(i0)",
                    scan=scan,
                    remove_spikes=remove_spikes,
                )
                curve = [
                    copy.deepcopy(ene),
                    copy.deepcopy(fluo),
                    copy.deepcopy(fluo_cnt),
                    copy.deepcopy(infos),
                ]
                _logger.debug(scan_label)
                curves.append(curve)
        ds.close()
        tend = time.time()
        tdiff = tend - tstart
        _logger.info(
            f"=> loaded {len(curves)} curves in {datetime.timedelta(seconds=tdiff)}"
        )

        return curves

    def get_groups(
        self,
        samp_name,
        scans_str,
        remove_spikes=False,
        iskip=1,
        verbose=False,
        **kwargs,
    ):
        """get scan data as list of Larch groups"""
        counters = self._counters
        datadir = self._datadir

        groups = []

        assert isinstance(
            scans_str, str
        ), "scan_str should be a sting like '0004/1:10,20,30:40:3"
        fn_idx, scans = str2rng(scans_str)

        samp_prefix = f"{samp_name}_{fn_idx}"
        fnin = os.path.join(datadir, samp_name, samp_prefix, f"{samp_prefix}.h5")

        tstart = time.time()
        ds = DataSourceSpecH5(fnin, verbose=verbose)

        for scan in scans:
            try:
                g = ds.get_scan(scan)
            except Exception:
                _logger.info(f"cannot load {samp_prefix}/{scan}")
                continue
            groups.append(g)
        ds.close()
        tend = time.time()
        tdiff = tend - tstart
        _logger.info(
            f"=> loaded {len(groups)} Larch groups in {datetime.timedelta(seconds=tdiff)}"
        )

        return groups

    def get_merge(self, curves, method="sum"):
        """merge curves"""
        ncurves = len(curves)
        xmrg, ymrg = merge_arrays_1d(curves, method=method)
        label = f"{method}{ncurves}"
        return [xmrg, ymrg, label, dict()]

    def plot(self, curves, norm=False, show_merge=False):
        """plot curves

        Parameters
        ----------
        curves : list of lists
            Curves format is the following:
            [
                [x1, y1, label1, info1],
                ...
                [xN, yN, labelN, infoN]
            ]

        """

        fig = PlotlyFigure()

        for x, y, label, info in curves:
            if norm:
                y /= np.trapz(y)
            fig.add_plot(x, y, label=label)

        if show_merge:
            xmrg, ymrg, labmrg, imrg = self.get_merge(curves)
            if norm:
                ymrg /= np.trapz(ymrg)
            fig.add_plot(xmrg, ymrg, label=labmrg, color="black")

        if norm:
            _logger.debug("y normalized by area")

        fig.show()

        return fig


if __name__ == "__main__":
    pass

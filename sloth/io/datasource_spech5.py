#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility wrapper for h5py-like API to Spec files
===================================================

Requirements
------------

- silx (http://www.silx.org/doc/silx/latest/modules/io/spech5.html)

"""
import os
import numpy as np
import h5py
from silx.io.utils import open as silx_open
from silx.io.convert import write_to_h5, _is_commonh5_group
from sloth.utils.strings import str2rng


class DataSourceSpecH5(object):
    """Data source utility wrapper for a Spec file read as HDF5 object
    via silx.io.open"""

    def __init__(self, fname=None, logger=None, urls_fmt="silx"):
        """init with file name and default attributes
        
        Parameters
        ----------
        fname : str
            path string of a file that can be read by silx.io.open() [None]
        logger : logging.getLogger() instance
            [None -> sloth.utils.logging.getLogger()]
        urls_fmt : str
            how the data are organized in the HDF5 container
            'silx' : default
            'spec2nexus' : as converted by spec2nexus
        """
        if logger is None:
            from sloth.utils.logging import getLogger

            _logger_name = "sloth.io.DataSourceSpecH5"
            self._logger = getLogger(_logger_name, level="INFO")
        else:
            self._logger = logger

        self.fname = fname
        self._sf = None
        if self.fname is not None:
            self._init_source_file()
        self._scan_n = None
        self._scan_str = None
        self._sg = None  # ScanGroup
        if urls_fmt == "silx":
            self._set_urls_silx()
        elif urls_fmt == "spec2nexus":
            self._set_urls_spec2nexus()
        else:
            self._urls_fmt = None
            self._logger.error("'urls_fmt' not understood")
        self.set_group()
        # show data in a TreeView
        # self.view()

    def _init_source_file(self):
        """init source file object"""
        #: source file object (h5py-like)
        try:
            self._sf = silx_open(self.fname)
        except OSError:
            self._logger.error(f"cannot open {self.fname}")
            self._sf = None

    def open(self, mode="r"):
        """Open the source file object with h5py in given mode"""
        try:
            self._sf = h5py.File(self.fname, mode)
        except OSError:
            self._logger.error(f"cannot open {self.fname}")
            pass

    def close(self):
        """Close source file silx.io.spech5.SpecH5"""
        self._sf.close()
        self._sf = None

    def _set_urls_silx(self):
        """Set default SpecH5 urls"""
        self._mots_url = "instrument/positioners"
        self._cnts_url = "measurement"
        self._title_url = "title"
        self._urls_fmt = "silx"

    def _set_urls_spec2nexus(self):
        """Set default spec2nexus urls"""
        self._mots_url = "positioners"
        self._cnts_url = "data"
        self._title_url = "title"
        self._urls_fmt = "spec2nexus"

    def _get_sg(self):
        """Safe get self._sg"""
        if self._sg is None:
            raise AttributeError("group not selected yet")
        else:
            return self._sg

    def _initTreeView(self):
        """Init TreeView GUI"""
        from sloth.gui.hdf5.view import TreeView
        from sloth.gui.hdf5.model import TreeModel

        self._view = TreeView()
        self._model = TreeModel()
        self._view.setModel(self._model)
        # customization
        self._view.setWindowTitle("DataSourceSpecH5 - view")
        self._view.setMinimumWidth(1024)
        self._view.setMinimumHeight(400)
        self._view.setSortingEnabled(False)
        # Avoid the user to drop file in the widget
        self._model.setFileDropEnabled(False)
        # Allow the user to reorder files with drag-and-drop
        self._model.setFileMoveEnabled(True)
        self._model.insertH5pyObject(self._sf)

    def view(self):
        """Init the TreeView and show"""
        self._initTreeView()
        self._view.show()

    def set_group(self, group_url=None):
        """Select group url

        Parameters
        ----------
        group_url : str (optional)
            hdf5 url with respect to / where scans are stored [None -> /scans]

        Returns
        -------
        none: sets attribute self._group_url
        """
        self._group_url = group_url
        if self._group_url is not None:
            self._logger.info(f"selected group {self._group_url}")

    def set_scan(self, scan_n, scan_idx=1, group_url=None):
        """Select a given scan number

        Parameters
        ----------
        scan_n : int
            scan number
        scan_idx : int (optional)
            scan repetition index [1]
        group_url : str
            hdf5 url with respect to / where scans are stored [None -> /scans]

        Returns
        -------
        none: set attributes
            self._scan_n, self._scan_str, self._scan_url, self._sg
        """
        self._scan_n = scan_n
        if self._urls_fmt == "silx":
            self._scan_str = f"{scan_n}.{scan_idx}"
        elif self._urls_fmt == "spec2nexus":
            self._scan_str = f"S{scan_n}"
        else:
            self._logger.error("wrong 'urls_fmt'")
            return
        if group_url is not None:
            self.set_group(group_url)
        if self._group_url is not None:
            self._scan_url = f"{self._group_url}/{self._scan_str}"
        else:
            self._scan_url = f"{self._scan_str}"
        try:
            self._sg = self._sf[self._scan_url]
            self._scan_title = self.get_title()
            self._logger.info(f"selected scan {self._scan_url}: '{self._scan_title}'")
        except KeyError:
            self._sg = None
            self._scan_title = None
            self._logger.error(f"'{self._scan_url}' is not valid")

    def _list_from_url(self, url_str):
        """Utility method to get a list from a scan url

        .. warning:: the list is **not ordered**

        """
        try:
            return [i for i in self._get_sg()[url_str].keys()]
        except Exception:
            self._logger.error(f"'{url_str}' not found -> use 'set_scan' method first")

    # ================== #
    #: READ DATA METHODS
    # ================== #

    def get_scans(self):
        """Get list of scans"""
        return list(self._sf.keys())

    def get_motors(self):
        """Get list of motors names"""
        return self._list_from_url(self._mots_url)

    def get_counters(self):
        """Get list of motors names"""
        return self._list_from_url(self._cnts_url)

    def get_title(self, scan_n=None):
        """Get title str for a given scan

        Parameters
        ----------
        scan_n : int (optional)
            scan number [None -> self._scan_n]

        Returns
        -------
        title (str): scan title self._sg[self._title_url][()]
        """
        if scan_n is not None:
            self.set_scan(scan_n)
        return self._get_sg()[self._title_url][()]

    def get_scan_axis(self):
        """Get the name of the scanned axis from title"""
        _title = self.get_title()
        if isinstance(_title, np.ndarray):
            _title = np.char.decode(_title)[0]
        _title_splitted = _title.split(" ")
        _iax = 1
        _axisout = _title_splitted[_iax]
        if _axisout == "":
            _iax += 1
            _axisout = _title_splitted[_iax]
        if "scan" in _axisout:
            _iax += 1
            _axisout = _title_splitted[_iax]
        if _axisout == "":
            _iax += 1
            _axisout = _title_splitted[_iax]
        _mots, _cnts = self.get_motors(), self.get_counters()
        if not ((_axisout in _mots) and (_axisout in _cnts)):
            self._logger.warning(f"'{_axisout}' not present in counters and motors")
        return _axisout

    def get_array(self, cnt, scan_n=None, group_url=None):
        """Get array of a given counter

        Parameters
        ----------
        cnt : str or int
            counter name or index in the list of counters
        scan_n : int (optional)
            optional scan number [None -> self._scan_n]
        group_url : str (optional)
            group name [None -> self._group_url]

        Returns
        -------
        array
        """
        if group_url is not None:
            self.set_group(group_url)
        if scan_n is not None:
            self.set_scan(scan_n)
        cnts = self.get_counters()
        if type(cnt) is int:
            cnt = cnts[cnt]
            self._logger.info(f"selected counter '{cnt}'")
        if cnt in cnts:
            sel_cnt = f"{self._cnts_url}/{cnt}"
            return self._get_sg()[sel_cnt][()]
        else:
            self._logger.error(
                f"'{cnt}' not found among the available counters: {cnts}"
            )
            sel_cnt = f"{self._cnts_url}/{cnts[0]}"
            return np.zeros_like(self._get_sg()[sel_cnt][()])

    def get_value(self, mot, scan_n=None, group_url=None):
        """Get motor position

        Parameters
        ----------
        mot : str or int
            motor name or index in the list of motors
        scan_n : int (optional)
            optional scan number [None -> self._scan_n]
        group_url : str (optional)
            group name [None -> self._group_url]

        Returns
        -------
        value
        """
        if group_url is not None:
            self.set_group(group_url)
        if scan_n is not None:
            self.set_scan(scan_n)
        mots = self.get_motors()
        if type(mot) is int:
            mot = mots[mot]
            self._logger.info(f"selected motor '{mot}'")
        if mot in mots:
            sel_mot = f"{self._mots_url}/{mot}"
            return self._get_sg()[sel_mot][()]
        else:
            self._logger.error(f"'{mot}' not found in available motors: {mots}")
            return 0

    def get_axis_data(self, ax_name=None, to_energy=None):
        """Get data for the scan axis
        
        Description
        -----------
        This method returns the data (=label and array) for a given axis of the
        selected scan. It is primarily targeted to a "scanning" axis, but any
        counter can be used. It is possible to control common conversions, like
        Bragg angle to energy.
        
        Parameters
        ----------
        ax_name : str or None
            
        norm : dict
            Controls the normalization of the signal [None]
            {
                "monitor": "str",  #: name of counter used for normalization
                "cps": bool,  #: multiply back to np.average(monitor)
            }
        deglitch : dict
            Controls :func:`sloth.math.deglitch.remove_spikes_medfilt1d` [None]

        Returns
        -------
        label, data
        """
        if (ax_name is not None) and (ax_name not in self.get_counters()):
            self._logger.error("%s not a counter", ax_name)
            return None, None
        ax_label = ax_name or self.get_scan_axis()
        ax_data = self.get_array(ax_label)
        if to_energy is not None:
            from sloth.utils.bragg import ang2kev

            bragg_ax = to_energy["bragg_ax"]
            bragg_ax_type = to_energy["bragg_ax_type"]
            bragg_d = to_energy["bragg_d"]
            if bragg_ax_type == "counter":
                bragg_deg = self.get_array(bragg_ax).mean()
            elif bragg_ax_type == "motor":
                bragg_deg = self.get_value(bragg_ax)
            else:
                self._logger.error("wrong 'bragg_ax_type' (motor or counter?)")
            if "enc" in bragg_ax:
                bragg_deg = (np.abs(bragg_deg) / to_energy["bragg_enc_units"]) * 360
            ax_abs_deg = bragg_deg + np.rad2deg(ax_data) / 1000.0
            ax_abs_ev = ang2kev(ax_abs_deg, bragg_d) * 1000.0
            ax_data = ax_abs_ev
            ax_label += "_abs_ev"
            self._logger.debug("Converted axis %s", ax_label)
            xmin = ax_data.min()
            xmax = ax_data.max()
            self._logger.info("%s range: [%.3f, %.3f]", ax_label, xmin, xmax)
            return ax_label, ax_data

    def get_signal_data(self, sig_name, mon=None, deglitch=None, norm=None):
        """Get data for the signal counter

        Description
        -----------
        This method returns the data (=label and array) for a given signal of the
        selected scan. It is possible to control normalization and/or deglitching.
        
        Basic processing: raw data -> norm by monitor signal -> deglitch -> norm2

        Parameters
        ----------
        sig_name : str
        mon : dict
            Controls the normalization of the signal by a monitor signal [None]
            {
                "monitor": "str",  #: name of counter used for normalization
                "cps": bool,  #: multiply back to np.average(monitor)
            }
        deglitch : dict
            Controls :func:`sloth.math.deglitch.remove_spikes_medfilt1d` [None]
        norm : dict
            Controls the normalization by given method

        Returns
        -------
        label, data
        """
        if sig_name not in self.get_counters():
            self._logger.error("%s not a counter", sig_name)
            return None, None
        sig_data = self.get_array(sig_name)
        sig_label = sig_name
        if mon is not None:
            mon_name = mon["monitor"]
            mon_data = self.get_array(mon_name)
            sig_data /= mon_data
            sig_label += f"_mon({mon_name})"
            if norm["cps"]:
                sig_data *= np.average(mon_data)  #: put back in counts
                sig_label += "_cps"
        if deglitch is not None:
            from sloth.math.deglitch import remove_spikes_medfilt1d

            sig_data = remove_spikes_medfilt1d(sig_data, **deglitch)
            sig_label += "_dgl"
        if norm is not None:
            from sloth.math.normalization import norm1D

            norm_meth = norm["method"]
            sig_data = norm1D(sig_data, norm=norm_meth, logger=self._logger)
            sig_label += f"_norm({norm_meth})"
        self._logger.info("Loaded signal: %s", sig_label)
        return sig_label, sig_data

    def get_curve(self, *args, **kwargs):
        """Get XY data (=curve) for current scan"""
        pass

    def get_curves(self, *args, **kwargs):
        """Get list of XY data (=curves) for selected scans"""
        pass

    def get_merged(self, *args, **kwargs):
        """Get merged list of XY data with a given action"""
        pass

    # =================== #
    #: WRITE DATA METHODS
    # =================== #

    def write_scans_to_h5(
        self,
        scans,
        fname_out,
        scans_groups=None,
        h5path=None,
        overwrite=False,
        conf_dict=None,
    ):
        """Export a selected list of scans to HDF5 file

        .. note:: This is a simple wrapper to
            :func:`silx.io.convert.write_to_h5`

        Parameters
        ----------
        scans : str, list of ints or list of lists (str/ints)
            scan numbers to export (parsed by sloth.utils.strings.str2rng)
            if a list of lists, scans_groups is required
        fname_out : str
            output file name
        scans_groups : list of strings
            groups of scans
        h5path : str (optional)
            path inside HDF5 [None -> '/']
        overwrite : boolean (optional)
            force overwrite if the file exists [False]
        conf_dict : None or dict (optional)
            configuration dictionary saved as '{hdfpath}/.config'
        """
        self._fname_out = fname_out
        self._logger.info(f"output file: {self._fname_out}")
        if os.path.isfile(self._fname_out) and os.access(self._fname_out, os.R_OK):
            self._logger.info(f"output file exists (overwrite is {overwrite})")
            _fileExists = True
        else:
            _fileExists = False

        #: out hdf5 file
        if overwrite and _fileExists:
            os.remove(self._fname_out)
        h5out = h5py.File(self._fname_out, mode="a", track_order=True)

        #: h5path
        if h5path is None:
            h5path = "/"
        else:
            h5path += "/"

        #: write group configuration dictionary, if given
        if conf_dict is not None:
            from silx.io.dictdump import dicttoh5

            _h5path = f"{h5path}.config/"
            dicttoh5(
                conf_dict,
                h5out,
                h5path=_h5path,
                create_dataset_args=dict(track_order=True),
            )
            self._logger.info(f"written dictionary: {_h5path}")

        #: write scans
        def _loop_scans(scns, group=None):
            for scn in scns:
                self.set_scan(scn)
                _sg = self._sg
                if _sg is None:
                    continue
                if not _is_commonh5_group(_sg):
                    self._logger.error("scan '%s' is not commonh5 group", scn)
                if group is not None:
                    _h5path = f"{h5path}{group}/{self._scan_str}/"
                else:
                    _h5path = f"{h5path}{self._scan_str}/"
                write_to_h5(
                    _sg,
                    h5out,
                    h5path=_h5path,
                    create_dataset_args=dict(track_order=True),
                )
                self._logger.info(f"written scan: {_h5path}")

        if type(scans) is list:
            assert type(scans_groups) is list, "'scans_groups' should be a list"
            assert len(scans) == len(
                scans_groups
            ), "'scans_groups' not matching 'scans'"
            for scns, group in zip(scans, scans_groups):
                _loop_scans(str2rng(scns), group=group)
        else:
            _loop_scans(str2rng(scans))

        #: close output file
        h5out.close()


def main():
    """test"""
    from sloth.examples import _examplesDir

    test_specfile = os.path.join(_examplesDir, "specfiledata_tests.dat")
    test_ds = DataSourceSpecH5(test_specfile)
    test_ds.set_scan(1)
    print(test_ds.get_motors())
    return test_ds


if __name__ == "__main__":
    t = main()

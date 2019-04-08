#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility wrapper for h5py-like API to Spec files
===================================================

Requirements
------------

- silx (http://www.silx.org/doc/silx/latest/modules/io/spech5.html)

"""
import logging
import silx

########################
### DataSourceSpecH5 ###
########################
class DataSourceSpecH5(object):
    """Data source utility wrapper for a Spec file read as HDF5 object via silx.io.open"""

    def __init__(self, fname=None):
        """init with file name and default attributes"""
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self.fname = fname
        try:
            self._sf = silx.io.open(fname)
        except:
            self._logger.error(f"cannot open {self.fname}")
            self._sf = None
        self._scan_n = None
        self._scan_str = None
        self._sg = None #ScanGroup
        self._set_urls()
        self.set_group()

    def close(self):
        """close silx.io.spech5.SpecH5"""
        self._sf.close()
        self._sf = None

    def _set_urls(self):
        """set default SpecH5 urls
        """
        self._mots_url = 'instrument/positioners'
        self._cnts_url = 'measurement'
        self._title_url = 'title'

    def set_group(self, group_url=None):
        """select group url

        Args:
            group_url (str): hdf5 url with respect to / where scans are stored [None -> /scans]

        Returns:
            none: sets attribute self._group_url
        """
        self._group_url = group_url
        if group_url is not None: self._logger.info(f"selected group {self._group_url}")

    def set_scan(self, scan_n, scan_idx=1, group_url=None):
        """select a given scan number

        Args:
            scan_n (int): scan number
            scan_idx (int): scan repetition index [1]
            group_url (str): hdf5 url with respect to / where scans are stored [None -> /scans]

        Returns:
            none: set attributes self._scan_n, self._scan_str, self._scan_url, self._sg
        """
        self._scan_n = scan_n
        self._scan_str = f"{scan_n}.{scan_idx}"
        if group_url is not None: self.set_group(group_url)
        if self._group_url is not None:
            self._scan_url = f"{self._group_url}/{self._scan_str}"
        else:
            self._scan_url = f"{self._scan_str}"
        self._sg = self._sf[self._scan_url]
        self._scan_title = self.get_title()
        self._logger.info(f"selected scan {self._scan_url}: '{self._scan_title}'")

    def _list_from_url(self, url_str):
        """utility method to get a list from a scan url

        .. warning:: the list is **not ordered**

        """
        try:
            return [i for i in self._sg[url_str].keys()]
        except:
            self._logger.error(f"'{url_str}' not found. Hint: use set_scan method first")

    def get_motors(self):
        """get list of motors names"""
        return self._list_from_url(self._mots_url)

    def get_counters(self):
        """get list of motors names"""
        return self._list_from_url(self._cnts_url)

    def get_title(self, scan_n=None):
        """get title str for a given scan

        Args:
            scan_n (int): optional scan number [None -> self._scan_n]
        """
        if scan_n is not None: self.set_scan(scan_n)
        return self._sg[self._title_url][()]

    def get_scan_axis(self):
        """get the name of the scanned axis from title"""
        _title_splitted = self.get_title().split(' ')
        _axisout = _title_splitted[1]
        if _axisout == '':
            _axisout = _title_splitted[2]
        _mots, _cnts = self.get_motors(), self.get_counters()
        if not ((_axisout in _mots) and (_axisout in _cnts)):
            self._logger.warning(f"'{_axisout}' not present in counters and motors")
        return _axisout

    def get_array(self, cnt, scan_n=None, group_url=None):
        """get array of a given counter

        Args:
            cnt (str or int): counter name or index in the list of counters
            scan_n (int): optional scan number [None -> self._scan_n]
            group_url (str): optional group name [None -> self._group_url]

        Returns:
            array
        """
        if group_url is not None: self.set_group(group_url)
        if scan_n is not None: self.set_scan(scan_n)
        cnts = self.get_counters()
        if type(cnt) is int:
            cnt = cnts[cnt]
            self._logger.info(f"selected counter '{cnt}'")
        if cnt in cnts:
            sel_cnt = f'{self._cnts_url}/{cnt}'
            return self._sg[sel_cnt][()]
        else:
            self._logger.error(f"'{cnt}' not found among the available counters:\n {cnts}")
            sel_cnt = f'{self._cnts_url}/{cnts[0]}'
            return np.zeros_like(self._sg[sel_cnt][()])

    def get_value(self, mot, scan_n=None, group_url=None):
        """get motor position

        Args:
            mot (str or int): motor name or index in the list of motors
            scan_n (int): optional scan number [None -> self._scan_n]
            group_url (str): optional group name [None -> self._group_url]

        Returns:
            value
        """
        if group_url is not None: self.set_group(group_url)
        if scan_n is not None: self.set_scan(scan_n)
        mots = self.get_motors()
        if type(mot) is int:
            mot = mots[mot]
            self._logger.info(f"selected motor '{mot}'")
        if mot in mots:
            sel_mot = f'{self._mots_url}/{mot}'
            return self._sg[sel_mot][()]
        else:
            self._logger.error(f"'{mot}' not found among the available motors:\n {mots}")
            return 0

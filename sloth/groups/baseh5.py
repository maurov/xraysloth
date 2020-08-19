#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic data groups that mimics HDF5 tree-like structure
======================================================

.. note:: The implementation stricty follows the one in :mod:`silx.io.spech5`
    expanding it by disentanglig from the Spec file.

Notes
-----

- :mod:`silx.io.commonh5` is the base layer here. This module provides
  :class:`silx.io.commonh5.Node` (object) that is a layer on top of :mod:`h5py`.
  The base classes for *groups* and *datasets* are, respectively,
  :class:`silx.io.commonh5.Group` (Node) and :class:`silx.io.commonh5.Dataset`
  (Node).

- The base structure is::

    /NXroot (Group)
        NXentry (Group)
            (Dataset)
            NXentry
                (Dataset)
        ...
            ...
                ...
                    ....

-
"""
import os
import tempfile
import datetime

from silx.io import commonh5
from silx.io.utils import H5Type

from sloth import __version__ as sloth_version
from sloth.utils.strings import get_timestamp

#: module logger
from sloth.utils.logging import getLogger

_logger = getLogger("sloth.groups.h5base", level="INFO")

##########
# GROUPS #
##########


class BaseGroup(commonh5.Group):
    """Base group used to build the tree structure"""

    def __init__(self, name, parent=None, attrs=None, logger=None):
        """Constructor"""
        super(BaseGroup, self).__init__(name, parent=parent, attrs=attrs)
        self._logger = logger or _logger

    def add_group(self, name, attrs=None, cls=None):
        """Add Group"""
        if cls is None:
            cls = EntryGroup
        self.add_node(cls(name, attrs=attrs, parent=self))

    def add_dataset(self, name, data, attrs=None, cls=None):
        """Add Group"""
        if cls is None:
            cls = BaseDataset
        self.add_node(cls(name, data, attrs=attrs, parent=self))

    def _get_children(self):
        """List of children"""
        return list(self._get_items().values())

    def __str__(self, level=0):
        """Tree representation"""
        if level == 0:
            ret = f"/('{self.basename}' )\n"
        else:
            ret = f"{'|'*level}+---{self.basename}\n"
        for child in self._get_children():
            ret += child.__str__(level + 1)
        return ret

    def write_to_h5(self, filename, overwrite=False):
        """Write the whole tree to file"""
        self._fname_out = filename
        import os

        if os.path.isfile(self._fname_out) and os.access(self._fname_out, os.R_OK):
            _fileExists = True
        else:
            _fileExists = False
        if _fileExists and (not overwrite):
            self._logger.info(f"Output file exists and 'overwrite' is {overwrite}")
            return
        if overwrite:
            mode = "w"
        else:
            mode = "a"
        from silx.io.convert import write_to_h5

        write_to_h5(
            self,
            self._fname_out,
            mode=mode,
            overwrite_data=overwrite,
            create_dataset_args=dict(track_order=True),
        )
        self._logger.info(f"{self.basename} written to {filename}")
        self._logger.warning("FIXME: the order of groups is currently not kept")


class RootGroup(BaseGroup):
    """Root group (= '/')

    Description
    -----------

    This is inspired from `commonh5.File` providing an equivalent object to
    `h5py.File`. It creates and open a temporary File object (file or memory)
    were the data are loaded in.

    """

    def __init__(self, mode=None, logger=None, in_memory=False):
        """Constructor with default NXroot class"""
        self._logger = logger or _logger
        if in_memory:
            import io

            self._logger.warning("IN MEMORY FILE, NOT TESTED YET!")
            ft = io.BytesIO()
        else:
            ft = os.path.join(tempfile.gettempdir(), f"sloth_{get_timestamp()}.h5")
            self._logger.info("Working temporary file is: %s", ft)
        attrs = {
            "NX_class": "NXroot",
            "file_time": datetime.datetime.now().isoformat(),
            "file_name": ft,
            "creator": "sloth %s" % sloth_version,
        }
        self._file_name = ft
        if mode is None:
            mode = "w"
        assert mode in ["r", "w"]
        self._mode = mode
        super(RootGroup, self).__init__(
            self._file_name, parent=None, attrs=attrs, logger=self._logger
        )

    @property
    def filename(self):
        return self._file_name

    @property
    def mode(self):
        return self._mode

    @property
    def h5_class(self):
        """Returns the :class:`h5py.File` class"""
        return H5Type.FILE

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the object, and free up associated resources.
        """
        # TODO
        pass


class EntryGroup(BaseGroup):
    """Generic group entry in the tree structure

    .. note:: This is equivalent to :class:`silx.io.spech5.ScanGroup`

    """

    def __init__(self, name, parent=None, attrs=None, logger=None):
        """Constructor: simply adding default NXentry class"""
        _attrs = {"NX_class": "NXentry"}
        if attrs is not None:
            attrs.update(_attrs)
        else:
            attrs = _attrs
        super(EntryGroup, self).__init__(
            name, parent=parent, attrs=attrs, logger=logger
        )


############
# DATASETS #
############


class BaseDataset(commonh5.Dataset):
    """Base dataset used to insert data in a group"""

    def __init(self, name, data, parent=None, attrs=None):
        """Constructor simply adding default NXdata class"""
        _attrs = {"NX_class": "NXdata"}
        if attrs is not None:
            attrs.update(_attrs)
        else:
            attrs = _attrs
        super(BaseDataset, self).__init__(name, data, parent=parent, attrs=attrs)

    def __str__(self, level=0):
        """Dataset representation"""
        ret = f"{'|'*level}----{self.basename}\n"
        return ret


def test_example(write=True, view=True):
    """Test example for :mod:`sloth.groups.h5base`"""
    t = RootGroup(logger=_logger)
    t._logger.info("Data model example: 't' is the root instance")
    t.add_group("Z9entry1", cls=EntryGroup)
    t.add_group("A0entry2")
    t["Z9entry1"].add_group("ZZsubentry1")
    t["Z9entry1"].add_group("ZAsubentry2")
    t["A0entry2"].add_group("AAsubentry1")
    t["A0entry2"].add_group("AZsubentry2")
    t["A0entry2/AZsubentry2"].add_group("Bsubsubentry1")
    t["A0entry2/AZsubentry2"].add_group("Dsubsubentry2")
    t["A0entry2/AZsubentry2"].add_group("Asubsubentry3")

    #: +dataset
    import numpy as np

    x = np.arange(10)
    t["Z9entry1"].add_dataset("x", x)
    t["Z9entry1/ZZsubentry1"].add_dataset("x", x)

    t._logger.info("print(t):\n%s", t)

    if write:
        #: +write to file
        ft = tempfile.mktemp(prefix="test_", suffix=".h5")
        t.write_to_h5(ft)

    if view:
        from silx import sx

        sx.enable_gui()
        # from silx.app.view.Viewer import Viewer
        # v = Viewer()
        # v.appendFile(ft)
        # v.setMinimumSize(1280, 800)
        # v.show()
        from sloth.gui.hdf5.view import TreeViewWidget

        v = TreeViewWidget()
        # v.model().appendFile(t._fname_out)
        v.model().insertH5pyObject(t)
        v.show()
        input("Press ENTER to close the view window...")

    return t


if __name__ == "__main__":
    t = test_example(write=True, view=True)

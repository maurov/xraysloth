#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic data groups that mimics HDF5 tree-like structure
=========================================================

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
import datetime
from silx.io import commonh5
from sloth import __version__ as sloth_version

#: module logger
from sloth.utils.logging import getLogger
_logger = getLogger('sloth.groups.h5base', level='DEBUG')

##########
# GROUPS #
##########


class BaseGroup(commonh5.Group):
    """Base group used to build the tree structure"""

    def __init__(self, name, parent=None, attrs=None):
        """Constructor"""
        super(BaseGroup, self).__init__(name,
                                        parent=parent, attrs=attrs)

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
        ret = f"{'|'*level}+---{self.basename}\n"
        for child in self._get_children():
            ret += child.__str__(level+1)
        return ret


class RootGroup(BaseGroup):
    """Root group (= '/')"""

    def __init__(self, name='/NXroot'):
        """Constructor with default NXroot class"""

        attrs = {"NX_class": "NXroot",
                 "created": datetime.datetime.now().isoformat(),
                 "creator": "sloth %s" % sloth_version
                 }
        super(RootGroup, self).__init__(name, parent=None,
                                        attrs=attrs)


class EntryGroup(BaseGroup):
    """Generic group entry in the tree structure

    .. note:: This is equivalent to :class:`silx.io.spech5.ScanGroup`

    """

    def __init__(self, name, parent=None, attrs=None):
        """Constructor simply adding default NXentry class"""

        _attrs = {"NX_class": "NXentry"}
        if attrs is not None:
            attrs.update(_attrs)
        else:
            attrs = _attrs

        super(EntryGroup, self).__init__(name, parent=parent, attrs=attrs)


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

        super(BaseDataset, self).__init__(name, data,
                                          parent=parent, attrs=attrs)

    def __str__(self, level=0):
        """Dataset representation"""
        ret = f"{'|'*level}----{self.basename}\n"
        return ret


def test_example():
    """Test example for :mod:`sloth.groups.h5base`"""
    _logger.info("Data model example: 't' is the root instance")
    t = RootGroup('test')
    t.add_group('entry1', cls=EntryGroup)
    t.add_group('entry2')
    t['entry1'].add_group('subentry1')
    t['entry2'].add_group('subentry2')
    t['entry2/subentry2'].add_group('subsubentry2')

    #: +dataset
    import numpy as np
    x = np.arange(10)
    t['entry1'].add_dataset('x', x)
    t['entry1/subentry1'].add_dataset('x', x)

    _logger.info('print(t):\n%s', t)
    return t


if __name__ == '__main__':
    t = test_example()

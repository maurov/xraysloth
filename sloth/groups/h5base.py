#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic data groups that mimics HDF5 tree-like structure
=========================================================

.. note:: The implementation stricty follows the one in :mod:`silx.io.spech5`
    expanding it by disentanglig from the Spec file.

Notes
-----

- :mod:`silx.io.commonh5` is the base layer here. This module provides
  :class:`Node`(object) that is a layer on top of :mod:`h5py`. The base classes
  for *groups* and *datasets* are, respectively, :class:`Group`(Node) and
 :class:`Dataset`(Node).

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
_logger = getLogger('sloth.groups.h5base')

##########
# GROUPS #
##########


class BaseGroup(commonh5.Group):
    """Base group used to build the tree structure"""

    def __init__(self, name, parent=None, attrs=None):
        """Constructor"""
        super(BaseGroup, self).__init__(name,
                                        parent=parent, attrs=attrs)

    def add_entry(self, name):
        """Add EntryGroup"""
        self.add_node(EntryGroup(name, parent=self))

    def get_children(self):
        """List of children"""
        return list(self._get_items().values())

    def __str__(self, level=0):
        """Tree representation"""
        ret = "+" + "---"*level + self.basename + "\n"
        for child in self.get_children():
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
        """Constructor with default NXentry class"""

        _attrs = {"NX_class": "NXentry"}
        if attrs is not None:
            attrs.update(_attrs)

        super(EntryGroup, self).__init__(name, parent=parent, attrs=attrs)


############
# DATASETS #
############


class BaseDataset(commonh5.Dataset):
    """Base dataset used to insert data in a group"""

    def __init(self, name, data, parent=None, attrs=None):
        """Constructor"""
        super(BaseDataset, self).__init__(name, data,
                                          parent=parent, attrs=attrs)


def test_example():
    """Test example for :mod:`sloth.groups.h5base`"""
    _logger.info("Data model example: 't' is the root instance")
    t = RootGroup('test')
    t.add_node(EntryGroup('entry1', parent=t))
    t.add_entry('entry2')
    t['entry1'].add_entry('subentry1')
    t['entry2'].add_entry('subentry2')
    t['entry2/subentry2'].add_entry('subsubentry2')
    return t


if __name__ == '__main__':
    t = test_example()

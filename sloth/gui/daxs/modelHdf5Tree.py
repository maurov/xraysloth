#!/usr/bin/env python
# coding: utf-8
"""Model based on :mod:`silx.gui.hdf5.Hdf5TreeModel`
"""

from silx.gui import qt
from silx.gui.hdf5 import Hdf5TreeModel

from .items import TreeItem, RootItem


class TreeModel(Hdf5TreeModel):

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent=parent)

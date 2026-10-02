#!/usr/bin/env python
"""
Model based on :mod:`silx.gui.hdf5.Hdf5TreeModel`
"""

from silx.gui.hdf5 import Hdf5TreeModel


class TreeModel(Hdf5TreeModel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

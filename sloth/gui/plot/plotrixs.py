#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot RIXS data
=================

.. note:: SILX equivalent of :mod:`sloth.collects.datagroup_rixs.RixsDataPlotter`

"""
from sloth.gui.plot.plot2D import Plot2D


class RixsPlot2D(Plot2D):
    """RIXS equivalent of Plot2D"""

    def __init__(self, parent=None, backend=None):
        super(RixsPlot2D, self).__init__(parent=parent, backend=backend)
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('Blues')


if __name__ == '__main__':
    pass

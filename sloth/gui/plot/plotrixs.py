#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot RIXS data
=================

.. note:: SILX equivalent of :mod:`sloth.collects.datagroup_rixs.RixsDataPlotter`

"""
from sloth.gui.plot.plot2D import Plot2D
from sloth.utils.logging import getLogger

class RixsPlot2D(Plot2D):
    """RIXS equivalent of Plot2D"""

    def __init__(self, parent=None, backend=None, logger=None):
        """Constructor"""

        if logger is not None:
            self._logger = logger
       else:
            self._logger = getLogger("RixsPlot2D")

        super(RixsPlot2D, self).__init__(parent=parent, backend=backend, logger=self._logger)
        self.setKeepDataAspectRatio(True)
        self.getDefaultColormap().setName('Blues')

        #List of RixsData objects
        self.data = []

    def addRixsData(self, rdobj, nlevels=50):
        """Add a RixsData object -> basic operations"""
        self.data.append(rdobj)
        self.clear()
        self.addImage(rdobj.zz, x=rdobj.x, y=rdobj.y, title=rdobj.label,
                      xlabel='Ene_in', ylabel='Ene_out')
        self.addContours(nlevels)


if __name__ == '__main__':
    pass

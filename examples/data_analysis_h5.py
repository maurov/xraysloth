#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example of data analysis based on a HDF5-like data model
========================================================

.. note:: WORK-IN-PROGRESS / NOT COMPLETE!

This example aims building a data analysis workflow based on a HDF5
representation. The goal is to keep everything in a HDF5-like container class.

Notes on the workflow
---------------------

.. note:: the *scan* here is not only an experimental thing where one or more
    axes are moved while one or more signals arevcollected, the scan can also
    be something generated by simulation or data analysis

- / HDF5-like data analysis project (NXroot)

    - Group of scans of the same type (e.g. XANES, XES, RIXS, peaks, aligns)

        - 1 (Loaded ScanN)
            - 1 (raw data)

                - axes
                - signals
                - scalars

            - 2 (when no change, just link, no copy)
                - axes
                - signals
                - scalars

            - ...

            - N (step N in the analysis without changing shape)
                - axes
                - signals
                - scalars

        - ...

        - N (Rebinned Scan N (rebinning is like generating another scan))

            - 1 (rebinned data)

                - axes
                - counters
                - scalars

        - M (Merge set of scans something at a given step)


- The scan is the base thing. It is composed of:

    - *axes*: single or multiple variables changed over time, like a set of
        motors following a trajectory
            *type*: 1D arrays, all the same shape

    - *signals*: signals read by detectors during movent of the axes or
        generated by analysis, that is, for each point in the axes, corresponds
        a point in the signals. Differently that axes, signals may refer to
        multi-dimensional data like images or MCA datasets
            *type*: 1D, 2D or ND arrays for each element in axes

    - *scalars*: key-value type data (0D) not changing over the scan shape.

- Actions performed on the single scan:

    - *converting*: scale conversion, affects only axes, no change in shape.

    - *rebinning*: affects axes and counters.

    - *merging*: affects axes and counters.


"""
from silx.gui import qt
from sloth.groups.baseh5 import RootGroup
from sloth.gui.plot.plotarea import PlotArea
from sloth.io.datasource_spech5 import DataSourceSpecH5

from sloth.utils.logging import getLogger

_logger = getLogger("sloth.examples.data_analysis_h5", level="INFO")


class MyDataAnalysisApp(qt.QMainWindow):
    """GUI application containing the whole data analysis workflow"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent=parent)
        if parent is not None:
            #: behave as a widget
            self.setWindowFlags(qt.Qt.Widget)
        else:
            self.setWindowTitle("My Great Data Analysis Box")

        #: logger
        self._logger = _logger

    def _init_gui(self):
        """build GUI"""
        centralWidget = qt.QWidget(self)
        #: instance of plot area
        self._plot = PlotArea()
        self._logger.info(f"'{self.__class__.__name__}._plot': plot area")
        #: assign grid layout
        gridLayout = qt.QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        #: addWidget(widget, row, column, rowSpan, columnSpan[, alignment=0]))
        gridLayout.addWidget(self._plot, 0, 0, 2, 2)
        #: set grid layout in the central widget
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setMinimumSize(1024, 800)

    def _init_data_model(self):
        """init data model"""
        self._dm = RootGroup(logger=self._logger)
        self._logger.info(f"'{self.__class__.__name__}._dm': data model")

    def _init_data_source(self, fname=None):
        """init data source"""
        self._ds = DataSourceSpecH5(fname=fname, logger=self._logger)
        self._logger.info(
            f"'{self.__class__.__name__}._ds': data source (file={fname})"
        )


########
# MAIN #
########


def main(fname=None):
    """main with the possibility to load a filename"""
    from sloth.utils.jupyter import run_from_ipython

    _ipy = run_from_ipython()
    from silx import sx

    sx.enable_gui()
    t = MyDataAnalysisApp()
    # t.show()
    t._init_gui()
    t._init_data_model()
    t._init_data_source(fname=fname)
    #: now start playing yourself!
    _logger.info(f"'{t.__class__.__name__}': called 't' here, ENJOY!")
    if not _ipy:
        input("Please, run this in IPython. Press ENTER to QUIT")
    return t


if __name__ == "__main__":
    t = main()

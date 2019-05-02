.. -*- coding: utf-8 -*-

Change Log
==========

v.0.3.0 (dev)
-------------

*master branch (not released/tagged yet)*

.. warning:: This version is extremely **UNSTABLE** and going under **CONTINUOUS REFACTORING**. Use it at your own risk.

New features
''''''''''''

* :mod:`sloth.gui.daxs`

  - Qt-based GUI application featuring a TreeModel/View from **Marius Retegan**
    and the SILX group at ESRF. The GUI has an internal Jupyter kernel that give
    access to core components directly from a Qtconsole.

  .. note::

        DAXS stands for **Data Analysis in X-ray Spectroscopy**. It has its own
        name because this GUI-project may be consider as a submodule of Sloth.

* :mod:`sloth.io.datasource_spech5`

  - unified way of reading Spec, HDF5 and NeXus files via :mod:`silx.io.open`

* :mod:`sloth.utils`

  - strong refactoring!

* :mod:`sloth.inst.spectro14`

  - simple geometry calculations of the FAME-UHD (BM16 at ESRF) X-ray
    emission spectrometer (2 rows of 7 spherically bent crystal
    analyzers arranged in a _mixed_ Rowland circle)

* :mod:`sloth.gui.sloth_main`

  - initial GUI layout (mainly an IPython embedded shell).

* :mod:`sloth.raytracing.shadow_utils`

  - utilities for running SHADOW3 simulations (specific cases).

* :mod:`sloth.utils.xdata`

  - :func:`xray_edge` + cleaning output of :func:`xray_line`

Bug fixes
'''''''''

* :class:`sloth.inst.rowland.RcVert` -> bug in `chi` calculation.

* :mod:`sloth.__init__`

  - re-enable larch imports in :var:`_slothKit` (currently disabled
    because loading seems too slow!!!)

Broken backward compatibility
'''''''''''''''''''''''''''''

* The whole library is not backward compatible at this stage!

* :mod:`sloth.collect`

  - `DataGroup` objects and derivative have methods with `_`
    (e.g. `self.getkwsd` -> `self.get_kwsd`)


v.0.2.1 (2018-07-04)
--------------------

* :mod:`sloth.inst`

   * TEXS pantograph final version.

* :mod:`sloth.raytracing`

  * Added `shadow3` test with a real SBCA to carefully check its installation.

v0.2.0 (2017-06-29)
-------------------

First *stable* release:

* published to Zenodo `DOI:10.5281/zenodo.821221 <https://doi.org/10.5281/zenodo.821221>`_

v0.1.0 (2016-11-16)
-------------------

First *testing* release.

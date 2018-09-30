.. -*- coding: utf-8 -*-

Change Log
==========

v.0.3.0 (dev)
-------------

*master branch (not released/tagged yet)*

New features
''''''''''''

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

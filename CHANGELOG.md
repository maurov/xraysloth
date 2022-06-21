# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.4.0 - unrelased]

### Changed
  - Moved to Larch:
    - Reading RIXS data from ESRF-BM16 -> :mod:`larch.io.rixs_esrf_fame`
    - Spec/HDF5 files reading -> :mod:`larch.io.specfile_reader`

## [0.3.1 - unreleased]

## Added
  - `sloth.gui.jupyx`
    - Jupyter UI -> :mod:`sloth.utils.jupyter` **deprecated**.
  - `sloth.gui.daxs`
    - Qt-based GUI application featuring a TreeModel/View from **Marius
      Retegan** and the SILX group at ESRF. The GUI has an internal Jupyter
      kernel that give access to core components directly from a Qtconsole. DAXS
      stands for **Data Analysis in X-ray Spectroscopy**. It has its own name
      because this GUI-project may be consider as a submodule of Sloth.
  - `sloth.io.datasource_spech5`
    - unified way of reading Spec, HDF5 and NeXus files via :mod:`silx.io.open`
  - `sloth.utils`
    - strong refactoring!
  - `sloth.inst.spectro14`
    - simple geometry calculations of the FAME-UHD (BM16 at ESRF) X-ray emission
      spectrometer (2 rows of 7 spherically bent crystal analyzers arranged in a
      _mixed_ Rowland circle)
  - `sloth.gui.sloth_main`
    - initial GUI layout (mainly an IPython embedded shell).
  - `sloth.raytracing.shadow_utils`
    - utilities for running SHADOW3 simulations (specific cases).
  - `sloth.utils.xdata`
    - :func:`xray_edge` + cleaning output of :func:`xray_line`

### Fixed
  - `sloth.inst.rowland.RcVert` -> bug in `chi` calculation.
  - `sloth.__init__`
    - re-enable larch imports in `_slothKit` (currently disabled
      because loading seems too slow!!!)

### Changed
  - The whole library is not backward compatible at this stage!
  - Removed :mod:`sloth.utils.genericutils`
  - `sloth.collect`
  - `DataGroup` objects and derivative have methods with `_`
      (e.g. `self.getkwsd` -> `self.get_kwsd`)

## [0.2.1 - 2018-07-04 ]

### Added
  - `sloth.inst`: TEXS pantograph final version.
  - `sloth.raytracing`: Added `shadow3` test with a real SBCA to carefully check its installation.

## [0.2.0 - 2017-06-29]

  - First *stable* release: published to Zenodo `DOI:10.5281/zenodo.821221 <https://doi.org/10.5281/zenodo.821221>`_

### [0.1.0 - 2016-11-16]

  - First *testing* release.
.. Sloth documentation master file, created by
   sphinx-quickstart on Fri Dec 23 15:42:32 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

Sloth is a collection of utilities (library) oriented to X-ray optics and data
reduction/analysis for XAS (XANES/EXAFS), XES and RIXS techniques.

Current version is |release|.

.. warning::

  In the current status, the library is **not stable enough to be used in
  production environments**. It performs as a partial random snapshot of daily
  research in X-ray instrumentation and still-to-implement ideas (mainly due to
  lack of time). Feel free to use/hack it and do not hesitate to drop me a line
  if you find them useful. Furthermore, I appreciate if you could report bugs,
  enhancements or comments directly in `Github Issues
  <https://github.com/maurov/xraysloth/issues>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   installation.rst
   changelog.rst
   data_model/index.rst
   modules/index.rst
   workflows/index.rst

:doc:`installation`
  Step-by-step guide to installation.

:doc:`workflows/index`
  Personal notes on workflows.

:doc:`data_model/index`
  How the data are structured (from file to memory and back).

:doc:`changelog`
  List of changes.

:doc:`modules/index`
  Documentation automatically built from the docstrings of the packages
  included in *sloth*.

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

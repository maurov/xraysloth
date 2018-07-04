Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

.. _Numpy : http://www.numpy.org
.. _Matplotlib : http://matplotlib.org
.. _PyMca : https://github.com/vasole/pymca
.. _SILX : https://github.com/silx-kit/silx
.. _Larch : https://github.com/xraypy/xraylarch
.. _XrayLib : https://github.com/tschoonj/xraylib/wiki
.. _XOP : http://ftp.esrf.eu/pub/scisoft/xop2.3/
.. _SHADOW3 : https://forge.epn-campus.eu/projects/shadow3
.. _CRYSTAL : https://github.com/srio/CRYSTAL
.. _OASYS1: https://github.com/lucarebuffi/OASYS1
.. _Orange3 : https://github.com/biolab/orange3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _Orange-XOPPY: https://github.com/srio/Orange-XOPPY
.. _XRT : http://pythonhosted.org/xrt

This repository contains (simple) utilities for x-ray spectroscopists,
oriented to x-ray optics and data reduction/analysis for XAS/XES/RIXS
techniques.

**NOTE** These scripts perform as a partial random snapshot of daily
research in x-ray instrumentation and still-to-implement ideas (mainly
due to lack of time). Feel free to use/hack them and do not hesitate
to drop me a line if you find them useful.

Installation
------------

Currently, only installation from source is available.

The utilities can be installed the standard way ::

  python setup.py install --user

For developers, the best is to fork this repository and install with
symbolic links ::

  pip install -e . 

Requirements
............

The following Python modules are required to fully run the scripts:

* Numpy_
* Matplotlib_
* PyMca_
* SILX_
* Larch_
* XrayLib_
* XOP_
* SHADOW3_
* XRT_

**NOTE** Numpy, Matplotlib and PyMca/SILX are used widely and are
mandatory. The other modules are recommended, not mandatory. They are
used only partially in some scripts and may result not required
depending on your specific application.

Notes on installing requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the required Python libraries (and more!) can be easily installed
via `conda <https://conda.io/docs/>`_ on any platform. My personal
workflow is described `setup_conda_envs.sh
<https://github.com/maurov/software-notes/blob/master/setup_conda_envs.sh>`_.

A dedicated Conda environment called `sloth-env` can be automagically
installed by::

  conda env create -f environment.yml

Or run directly in Binder

.. image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/maurov/xraysloth/master

Usage
-----

Full documentation will reside in the ``doc`` directory at a certain
point. Meanwhile, the best is to read directly the ``__doc__`` strings
in the source code. The Python files sometimes have a test/example
included in the ``__main__`` block or referring to the ``examples``
directory where each script has its own examples/tests. Unit tests are
in progress and will reside in ``sloth.test``.

The functionality of the scripts can be easily converted to Larch_
plugins in order to have access via the Domain Specific Language (DSL)
of Larch. If you need it, just drop me a line! Some functions are
already exposed to Larch.  To load the plugins into Larch is described
`here <http://xraypy.github.io/xraylarch/devel/index.html#plugins>`_.

To report bugs, enhancements or comments, please use the `Issues
<https://github.com/maurov/xraysloth/issues>`_

Citation
--------

Please cite this work using the following DOI at Zenodo:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.821221.svg
   :target: https://doi.org/10.5281/zenodo.821221


License
-------

This is an open source software released under the terms of `BSD-3
license <https://opensource.org/licenses/BSD-3-Clause>`_

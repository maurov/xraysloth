Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.167068.svg
   :target: https://doi.org/10.5281/zenodo.167068

.. _Numpy : http://www.numpy.org
.. _Matplotlib : http://matplotlib.org
.. _PyMca : https://github.com/vasole/pymca
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

The utilities can be installed the standard way ::

  python setup.py install --user

**NOTE** These scripts perform as a partial random snapshot of daily
research in x-ray instrumentation and still-to-implement ideas (mainly
due to lack of time). Feel free to use/hack them and do not hesitate
to drop me a line if you find them useful.

Documentation will reside in the ``doc`` directory at a certain
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

Requirements
------------

The following Python modules are required to fully run the scripts:

* Numpy_
* Matplotlib_
* PyMca_
* Larch_
* XOP_
* SHADOW3_
* XRT_
* XrayLib_

**NOTE** Numpy, Matplotlib and PyMca are used widely and are
mandatory. The other modules are recommended, not mandatory. They are
used only partially in some scripts and may result not required
depending on your specific application.

Notes on installing requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the required Python libraries can be easily installed via
``pip``. My personal workflow consists in an XUbuntu virtual machine,
Python 3.5, Qt5 installed system-wide and all required modules
installed in a virtual environment. This is described `here
<https://github.com/maurov/software-notes>`. For OASYS and friends
`here <https://github.com/srio/oasys-installation-scripts>`.

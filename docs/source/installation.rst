Installation
------------

Currently, the recommended installation method is from source on a Linux-like environment.

.. note:: For Microsoft Windows users, it is recommended to run the following setup in a `Windows Subsystem for Linux (WSL) <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_. Debian or Ubuntu are preferred Linux distributions. Furthermore, an optimized experience is obtained with `MobaXterm <https://mobaxterm.mobatek.net/>`_.

Minimal setup
.............

The following instructions will guide you to set-up a dedicated Python
environment called `sloth` and install a minimal version of the library.

- First of all, install `Conda <https://conda.io>`_ on your system. If you are on Linux, this can be done just by::

      wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
      bash miniconda.sh -b -p $HOME/local/conda

- Open a shell with the Conda `base` environment activated. I refer to it as `(base)$` in the following::

      $ source $HOME/local/conda/bin/activate

- Update to the latest version of `conda`, `python` and `pip`:

      (base)$ conda update -y conda python pip

- Install git (if not yet present in your environment)::

      (base)$ conda install -y git

- Clone Sloth repository::

      (base)$ git clone https://github.com/maurov/xraysloth.git
      
.. note:: if you are behind a proxy, you may need to configure git for it::

      (base)$ git config --global http.proxy HOST:PORT

- Make sure the packages listed in `binder/apt.txt` are available in your system, otherwise install them::

      $ grep -v '^#' apt.txt | xargs sudo apt-get install -y

- Create `sloth` Conda environment::

      (base)$ cd xraysloth/binder
      (base)$ conda env create -f environment.yml

.. note:: This will install a relatively large number of libraries. If you want to keep a minimal environment and install only those librariers you want, you can manually create the `sloth` environment::

      (base)$ conda create -n sloth python==3.7

- Activate the environment::

      (base)$ conda activate sloth

- Run the `postBuild` script to complete install the Jupyter extensions::

      (sloth)$ bash postBuild

- Enjoy!

Daily working environment
.........................

For a daily working environment, you should use a `Python IDE
<https://wiki.python.org/moin/IntegratedDevelopmentEnvironments>`_.

Recommended IDEs are:

- `Microsoft Visual Studio Code <https://code.visualstudio.com/>`_::

      (sloth)$ wget https://go.microsoft.com/fwlink/?LinkID=760868
      (sloth)$ dpkg -i <downloaded_file.deb>

.. note:: Under Windows install it the application the standard way and use the integrated WSL extension.

- `Spyder <https://www.spyder-ide.org/>`_::

      (sloth)$ conda install -y spyder

- `Jupyter lab <https://jupyterlab.readthedocs.io/en/stable/#>`_::

      (sloth)$ jupyter lab

Notes requirements
..................

Currently, the mandatory requirements are:

* Numpy_
* Matplotlib_
* SciPy_
* SILX_

Nevertheless, other libraries are required to fully run all the scripts:

* PyMca_
* Larch_
* XrayLib_
* SHADOW3_
* OASYS_
* XOP_
* XRT_


Usage
-----

Full documentation will reside in the ``docs`` directory at a certain
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


.. _Numpy : http://www.numpy.org
.. _Matplotlib : http://matplotlib.org
.. _SciPy : https://scipy.org/
.. _SILX : https://github.com/silx-kit/silx
.. _PyMca : https://github.com/vasole/pymca
.. _Larch : https://github.com/xraypy/xraylarch
.. _XrayLib : https://github.com/tschoonj/xraylib/wiki
.. _SHADOW3 : https://forge.epn-campus.eu/projects/shadow3
.. _XOP : http://ftp.esrf.eu/pub/scisoft/xop2.3/
.. _CRYSTAL : https://github.com/srio/CRYSTAL
.. _OASYS: https://github.com/oasys-kit/OASYS1
.. _Orange3 : https://github.com/biolab/orange3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _Orange-XOPPY: https://github.com/srio/Orange-XOPPY
.. _XRT : https://github.com/kklmn/xrt

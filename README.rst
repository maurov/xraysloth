Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

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

There is no build/install script (``setup.py``) because at the moment
these utilities are rather independent from each other. To use these
utilities in your scripts, simply clone the GIT repository to
``somewhere`` and then append it to your PYTHONPATH ::

  import sys
  sys.path.append('path_to_somewhere')

**NOTE** These scripts perform as a partial random snapshot of daily
research in x-ray instrumentation and still-to-implement ideas (mainly
due to lack of time). Feel free to use/hack them and do not hesitate
to drop me a line if you find them useful.

Documentation will reside in the ``docs`` directory at a certain
point. Meanwhile, the best is to read directly the ``__doc__`` strings
in the source code. The Python files sometimes have a test/example
included in the ``__main__`` block or referring to the ``examples``
directory where each script has its own examples/tests (TODO unit
tests).

The functionality of the scripts can be easily converted to Larch_
plugins in order to have access via the Domain Specific Language (DSL)
of Larch. If you need it, just drop me a line! Some functions are
already exposed to Larch.  To load the plugins into Larch is described
`here <http://xraypy.github.io/xraylarch/devel/index.html#plugins>`_.

To report bugs, enhancements or comments, please use the
`Issues <https://github.com/maurov/xraysloth/issues>`_

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

PyMca5 user install
-------------------

Procedure to install PyMca_ as user
::
   # USER-LOCAL INSTALL: recommended (in .local/lib/pythonX.Y/site-packages/)
   cd /path/to/your/local/
   sudo aptitude install python-qt4 python-qt4-dev
   # fisx
   git clone https://github.com/vasole/fisx.git
   cd fisx
   python setup.py install --user
   #pymca
   git clone https://github.com/vasole/pymca.git
   cd pymca
   SPECFILE_USE_GNU_SOURCE=1 python setup.py install --user
   # USER INSTALL: alternative (within a virtual environment)
   # (in_your_virt_env) SPECFILE_USE_GNU_SOURCE=1 python setup.py build
   # (in_your_virt_env) python setup.py install
   # SYSTEM-WIDE INSTALL: not recommended
   #sudo SPECFILE_USE_GNU_SOURCE=1 python setup.py install
   # make CLEAN:
   #(sudo) rm -rf /usr/local/lib/python2.7/dist-packages/PyMca*
   #(sudo) rm -rf ~/local/pymca/build/
   #
   # documentation
   python setup.py build_doc

Larch user install
------------------

Procedure to install Larch_ as user
::
   cd /path/to/your/local
   git clone http://github.com/xraypy/xraylarch.git
   cd xraylarch
   pip install --user -U wxmplot wxutils termcolor
   python setup.py build
   python setup.py install --user

How to install XOP and SHADOW3
------------------------------

The following procedure has been successfully tested on Linux machines
(Ubuntu 12.04 and Debian 6.0). Having superuser rights is not required
::
   export MYLOCAL=/path/to/your/local
   cd $MYLOCAL
   wget http://ftp.esrf.eu/pub/scisoft/xop2.3/xop2.3_Linux_20140616.tar.gz
   tar xzvf xop2.3_Linux_20140616.tar.gz
   export XOP_HOME=$MYLOCAL/xop2.3
   cd $MYLOCAL
   mkdir xop_extensions
   cd xop_extensions
   wget http://ftp.esrf.eu/pub/scisoft/xop2.3/shadowvui1.12_Linux_20140708.tar.gz
   tar xzvf shadowvui1.12_Linux_20140708.tar.gz
   cd $MYLOCAL/xop2.3/extensions
   ln -s $MYLOCAL/xop_extensions/shadowvui shadowvui
   # IF YOU WANT TO UPDATE SHADOW3 TO THE LAST VERSION
   # cd shadow3
   # git pull
   # OR if this does not work:
   #    cd ..; rm -rf shadow3; 
   #    git clone git://git.epn-campus.eu/repositories/shadow3
   #    cd shadow3
   # make
   # make python
   export SHADOW3_HOME=$MYLOCAL/xop_extensions/shadowvui/shadow3
   export SHADOW3_BUILD=$SHADOW3_HOME/build/lib.linux-x86_64-2.7
   export LD_LIBRARY_PATH=$SHADOW3_HOME:$LD_LIBRARY_PATH
   export PYTHONPATH=$SHADOW3_BUILD:$PYTHONPATH
   
   # TIPS:
   # run shadow with 'xop shadowvui'
   # put all previous environment variables in .bashrc
   # sudo ln -s $MYLOCAL/xop2.3/xop /usr/local/bin/xop

How to install OASYS1 and friends
---------------------------------

OASYS1_ is the Python-based graphical user interface (GUI) for XOP_ and
SHADOW3_. It is currently under active development and will replace the previous
IDL-based GUI. This software is a fork of Orange3_, a component-based data
mining software. Orange-Shadow_ and Orange-XOPPY_ are developed within this
framework. The drawback is the dependence on Python3.4 and a big list of
required packages with the very last versions... here a tentative *clean*
installation procedure of OASYS1 and friends is given. The procedure has been
tested on a Linux Debian 8 machine. Root (superuser) access is required for
having a working Python 3.4 plus Qt environment. Apart this, everything is
installed in a virtual environment.

::
   
   # Python3, Qt and tools as system-wide packages
   sudo apt-get install git python-virtualenv python-pip
   sudo apt-get install python3-sphinx python3-jinja2
   sudo apt-get install python3-numpy python3-scipy
   sudo apt-get install python3-pyqt4 python-qt4-dev python3-sip-dev libqt4-dev
   sudo apt-get install ipython3 ipython3-qtconsole

   # work in an local directory and virtual Python3 environment
   export MYLOCAL=/path/to/your/local
   cd $MYLOCAL
   python3.4 -m venv py34env --clear --without-pip --system-site-packages
   source py34env/bin/activate
   cd py34env; wget https://bootstrap.pypa.io/get-pip.py
   python get-pip.py

   # OASYS1
   git clone https://github.com/lucarebuffi/OASYS1
   cd OASYS1
   pip install -r requirements.txt
   python setup.py develop
   #to test: cd; python -m Orange.canvas

   
License
-------

`BSD 3-Clause License <http://opensource.org/licenses/BSD-3-Clause>`_
::
   <OWNER> = Mauro Rovezzi
   <ORGANIZATION> = European Synchrotron Radiation Facility, Grenoble
   <YEAR> = 2011-2015

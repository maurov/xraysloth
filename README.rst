Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

.. _XRT : http://pythonhosted.org/xrt
.. _CRYSTAL : https://github.com/srio/CRYSTAL
.. _XOP : http://ftp.esrf.eu/pub/scisoft/xop2.3/
.. _SHADOW3 : https://forge.epn-campus.eu/projects/shadow3
.. _PyMca : https://github.com/vasole/pymca
.. _Larch : https://github.com/xraypy/xraylarch
.. _XrayLib : https://github.com/tschoonj/xraylib/wiki
.. _Numpy : http://www.numpy.org/

This repository contains (simple) utilities for x-ray spectroscopists,
mainly oriented to instrumentation.

There is no build/install script (``setup.py``). To use these
utilities in your scripts, simply clone the GIT repository to
``somewhere`` and then append it to your PYTHONPATH ::

  import sys
  sys.path.append('path_to_somewhere')

**NOTE** These scripts are not part of a full-fledged package but
rather perform as a partial random snapshot of daily research in x-ray
instrumentation and still-to-implement ideas (mainly due to lack of
time). Feel free to use/hack and drop me a line if you find them
useful.

Documentation will reside in the ``docs`` directory, but the best is
to read directly the ``__doc__`` strings in the source code. The
Python files sometimes have a test/example included in the
``__main__`` block or referring to the ``examples`` directory where
each script has its own examples/tests (TODO unit tests).

The functionality of the scripts can be easily converted to Larch
plugins in order to have access via the Domain Specific Language (DSL)
of Larch. If you need it, just drop me a line! Some functions are
already exposed to Larch.  To load the plugins into Larch: `here
<http://xraypy.github.io/xraylarch/devel/index.html#plugins>`_.

To report bugs, enhancements or comments, please use the
`Issues <https://github.com/maurov/xraysloth/issues>`_

Requirements
------------

The following Python modules are required to fully run the scripts:

* Numpy_
* PyMca_
* Larch_
* XOP_
* SHADOW3_
* XRT_
* XrayLib_

Apart from Numpy and PyMca that are used widely, other modules are
used partially and are mainly recommended, not mandatory.

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


License
-------

Copyright (c) 2014, Mauro Rovezzi

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.
3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

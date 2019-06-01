Sloth: slowly evolving utilities for X-ray spectroscopists
==========================================================

Sloth is a Python library oriented to X-ray instrumentation/optics and data
reduction/analysis for X-ray Absorption Spectroscopy (XAS, XANES/EXAFS), X-ray
emission spectroscopy (XES) and Resonant Inelastic X-ray Scattering (RIXS)
techniques.

Sloth is lazy by nature and the main motto is *do not reinvent the Python
wheel!*, this nerdy statement wants simply to point out that in the Python
open-source ecosystem there are tons of libraries that implements more or less
similar things for the simple reason of reducing dependencies... well, here is
the contrary! Apart few very basic libraries that are required, many other are
used randomly in various parts and you will discover them by usage, so I
strongly encourage to read the code and the work-in-progress documentation.

.. warning:: In the current status, the library is not stable enough to be used
in production environments. This is simply due to the fact that there is one
developer for a single user, that is, myself!. For this reason, the library
performs as a partial random snapshot of daily work/research in X-ray
instrumentation and still-to-implement ideas (mainly due to lack of time). Feel
free to use/hack it and do not hesitate to drop me a line if you find them
useful. This will force me to stabilize the project. Furthermore, I appreciate
if you could report bugs, enhancements or comments directly in `Github Issues
<https://github.com/maurov/xraysloth/issues>`_

Finally, before going deep into the code, I recommend visiting the `Sloth
appreciation society <http://www.slothville.com/>`_ and I acknowledge them for
inspiring the logo.

Resources
---------

- **Documentation**: https://xraysloth.readthedocs.io |rtd|
- Documentation (*backup*): http://mauro.rovezzi.it/xraysloth |travis|
- Citation: |zenodo|
- License: |license|
- BinderHub (*experimental*): |binder|

.. |license| image:: https://img.shields.io/github/license/maurov/xraysloth.svg
    :target: https://github.com/maurov/xraysloth/blob/master/LICENSE.txt
    :alt: License

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.821221.svg
    :target: https://doi.org/10.5281/zenodo.821221
    :alt: Citation DOI

.. |travis| image:: https://travis-ci.org/maurov/xraysloth.svg?branch=master
    :target: https://travis-ci.org/maurov/xraysloth
    :alt: Travis-CI status

.. |rtd| image:: https://readthedocs.org/projects/xraysloth/badge/?version=latest
    :target: https://xraysloth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |binder| image:: https://img.shields.io/badge/launch-sloth-579ACA.svg
    :target: https://mybinder.org/v2/gh/maurov/xraysloth/master?filepath=notebooks%2Findex.ipynb
    :alt: Launch Sloth on Binder

Sloth: slowly evolving utilities for x-ray spectroscopists
==========================================================

Sloth is a collection of Python scripts that may result useful in the field of
x-ray instrumentation/optics and data reduction/analysis for x-ray Absorption
Spectroscopy (XAS, XANES/EXAFS), x-ray emission spectroscopy (XES) and Resonant
Inelastic x-ray Scattering (RIXS) techniques.

Sloth is lazy by nature and tries reusing as much as possible the existing
open-source libraries of the Python ecosystem. Nevertheless, apart few very
basic libraries that are mandatory, many other are used randomly in various
parts and you will discover them by usage, so I strongly encourage to read the
code and the work-in-progress documentation.

**WARNING** Sloth is designed as a library, but it should not be used in
production environments, because its API is changing rapidily and backward
compatibility is not guarenteed. The main reason is the fact that there is only
one developer for a single user, myself!. Thus, the library performs as a
partial random snapshot of daily work/research and still-to-implement ideas
(mainly due to lack of time). Feel free to use/hack it and do not hesitate to
drop me a line if you find any script useful. Furthermore, I appreciate if bugs,
enhancements or comments  could be reported directly in `Github Issues
<https://github.com/maurov/xraysloth/issues>`_

This project works in close collaboration with `Larch
<https://github.com/xraypy/xraylarch>`_ and the goal is to transfer stable
portions of the code there. This means that **it is recommended to use Larch in
production environments**.

Finally, I recommend visiting the `Sloth appreciation society
<http://www.slothville.com/>`_ and I acknowledge them for inspiring the logo.

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

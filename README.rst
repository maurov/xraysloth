Sloth: slowly evolving utilities for x-ray spectroscopy
=======================================================

Sloth is a collection of Python scripts, examples of workflows and documentation
that may result useful in the field of **x-ray instrumentation, optics and
spectroscopy**. The project aims providing a full Python environment for the
generic user of an x-ray spectroscopy beamline. It should help with the tasks of
data reduction/analysis and simulation for x-ray Absorption Spectroscopy (XAS,
XANES/EXAFS), x-ray emission spectroscopy (XES) and Resonant Inelastic x-ray
Scattering (RIXS) techniques.

Sloth is lazy by nature and tries reusing as much as possible the existing
open-source libraries of the Python ecosystem. It results in a large number of
dependecies. Nevertheless, apart few very basic libraries that are mandatory,
many other are used randomly in specific modules and you may discover them only
by usage, so I strongly encourage to read the code and the work-in-progress
documentation.

Sloth is designed as a **Python environment running on a Linux-like
(virtual)machine** (see Installation in the documentation for a full
description). On top of this, there is a basic library and some rudimentary
not-yet-finished GUIs. The structure of the code or the API is changing rapidily
and *backward compatibility is not guarenteed*. Thus, the library performs as a
partial random snapshot of daily work/research and still-to-implement ideas
(mainly due to lack of time). Feel free to use/hack it and do not hesitate to
drop me a line if you find any script useful. Furthermore, I appreciate if bugs,
enhancements or comments  could be reported directly in `Github Issues
<https://github.com/maurov/xraysloth/issues>`_

This project works in close collaboration with `Larch
<https://github.com/xraypy/xraylarch>`_ and the goal is to transfer stable
portions of the code there. It means that **it is recommended to use Larch in
production environments**.

Finally, I recommend visiting the `Sloth appreciation society
<http://www.slothville.com/>`_ and I acknowledge them for inspiring the logo.

Resources
---------

- **Documentation**: https://xraysloth.readthedocs.io |rtd|
- Documentation (*backup*): http://mauro.rovezzi.net/xraysloth |travis|
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

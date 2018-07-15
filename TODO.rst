.. -*- coding: utf-8 -*-

To Do
=====

A list of tasks that should be implemented and come up to my mind
while coding. Everything is collected in a single file instead of
dispersing *TODO* tags in the code. Another approach is to create
issues and self-assign them, but it is definitively overkill.

New features
------------

Here well defined tasks ready for implementation, grouped by
modules. No particular priority order is given.

* :mod:`sloth.utils.xdata`

  - make a single API for both `xraylib` and `larch` backends.


* :mod:`sloth.gui.sloth_main`

  - load data workflow.
  - 2D plots
  - Rowland circle
  - ...

* :mod:`sloth.fit.peakfit`

  - implement everything with the choice of backend: `silx` or `lmfit`
  - :func:`fit_silx` move to a :class:`FitManager`
  - :func:`fit_splitpvoigt` move to :class:`Specfit` or :class:`FitManager`
  
* :mod:`sloth.utils.genericutils`

  - restructure/refresh/collect sparse pieces of code elsewhere

* :mod:`sloth.utils.pymca`

  * class:`myPyMcaMain`

    - add method to change configuration on the fly without clicking

* :mod:`sloth.math.deglitch`

  - document/improve :func:`remove_spikes`, get rid of Pandas

* :mod:`sloth.raytracing.shadow_jscyl`

  - move from `wippy`
    
Refactoring
-----------

* :mod:`sloth.raytracing`

  * revise the whole thing... currently a mess!

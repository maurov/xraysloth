.. -*- coding: utf-8 -*-

To Do
=====

A list of tasks that should be implemented and come up to my mind
while coding. Everything is collected in a single file instead of
dispersing *TODO* tags in the code. Another approach is to create
issues and self-assign them, but it is definitively overkill.

Bug fixes
---------

New features
------------

Here well defined tasks ready for implementation, grouped by
modules. No particular priority order is given.

* :mod:`sloth`

  - [ ] clean imports

* :mod:`sloth.utils.genericutils`

  - [ ] clean imports

* :mod:`sloth.utils.xdata`

  - [ ] make a single API for both `xraylib` and `larch` backends.


* :mod:`sloth.gui.sloth_main`

  - [ ] load data workflow.
  - [ ] 2D plots
  - [ ] Rowland circle
  - ...

* :mod:`sloth.fit.peakfit`

  - [ ] implement everything with the choice of backend: `silx` or `lmfit`
  - [ ] :func:`fit_silx` move to a :class:`FitManager`
  - [ ] :func:`fit_splitpvoigt` move to :class:`Specfit` or :class:`FitManager`
  
* :mod:`sloth.utils.genericutils`

  - [ ] restructure/refresh/collect sparse pieces of code elsewhere

* :mod:`sloth.utils.pymca`

  * class:`myPyMcaMain`

    - add method to change configuration on the fly without clicking

* :mod:`sloth.math.deglitch`

  - [ ] document/improve :func:`remove_spikes`, get rid of Pandas

* :mod:`sloth.raytracing.shadow_jscyl`

  - [ ] migrate from `wippy`

* :mod:`sloth.collects.datagroup`
    
  - [ ] *REFACTOR THE WHOLE THING!!!*
  - [ ] move self.getkwsd() to the respective data objects
  - [ ] move 1D parts to datagroup1D
  - [ ] use map() instead of for loops...
  - [ ] use update() for kwsd: see `https://github.com/xraypy/xraylarch/issues/66#issuecomment-30948135`_
  - [ ] control multiple plot windows ('win' keyword argument) when plotting
  - [ ] plotting with SILX instead of PyMca

* :mod:`sloth.collects.datagroup1D`
    
  - [ ] mksum
  - [ ] plotxy: self.pw.setGeometry(700, 50, 900, 900), use config!

* :mod:`sloth.math.normalization`

  - [ ] :func:`norm1D` add XANES normalization with Larch

* :mod:`sloth.rixs.rixdata`

  - [ ] move self.getkwsd() to ConfigParser
  
* :mod:`sloth.rixs.rixdata_plotter`
    
  - [ ] make possible more than one data set in the same figure
        controlled by the 'replace' variable
  - [ ] RixsDataPlotter should inherit directly from RixsData class !
  - [ ] remove the model/controller from the plot method (view):
        e.g. move in a separate method the line cuts
  - [ ] interactive cuts with mouse selection

  
Refactoring
-----------

* :mod:`sloth.raytracing`

  - [ ] revise the whole thing... currently a mess!

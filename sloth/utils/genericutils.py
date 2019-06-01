#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic utilities for daily work
===================================

TODO
====
- collect all bits and pieces here

"""
from .logging import getLogger
_logger = getLogger('sloth.utils.genericutils')
_logger.error("!!! DEPRECATED !!! -> sloth.utils.<submodule>")


#: TO REMOVE AT NEXT RELEASE!!!
from .qt import (qt_get_version, qt_create_window, qt_close_all_windows)
from .jupyter import (ipythonAutoreload, is_in_notebook, run_from_ipython)
from .matplotlib import mplSetPubFont
from sloth.calculators.fdmnes import get_efermi


if __name__ == '__main__':
    #qt5_get_version()
    pass

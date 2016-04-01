#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_preprocessors: utility to run SHADOW3_ preprocessors via
ShadowOui_ layer

.. note:: requires python3.x

.. _SHADOW3: https://github.com/srio/shadow3
.. _ShadowOui: https://github.com/lucarebuffi/ShadowOui

TODO
----

- update to ShadowOui_

- re-structure the whole thing by inheriting from ShadowLibExtensions
  or Orange-Shadow

"""
__author__ = "Mauro Rovezzi"
__credits__ = ""
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import sys

HAS_SHADOW = False
HAS_SWOUI = False

try:
    from orangecontrib.shadow.widgets.preprocessor.xsh_bragg import OWxsh_bragg
    HAS_SWOUI = True
except:
    #raise ImportError('ShadowOui not found!')
    #sys.exit(1)
    pass

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    t = OWxsh_bragg()
    t.show()
    sys.exit(app.exec_())


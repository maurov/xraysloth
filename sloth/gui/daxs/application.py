# coding: utf-8
# /*##########################################################################
# MIT License
#
# Copyright (c) 2018 DAXS developers.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
from __future__ import absolute_import, division

__authors__ = ['Marius Retegan', 'Mauro Rovezzi']
__license__ = 'MIT'

import logging
import sys
import argparse

from silx.gui import qt

from .window import MainWindow


# The logger object has a setLevel method, but the level of the handler
# must also be changed to actually display messages lower that the default
# level which is logging.WARNING.
# See https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python.
# We use the module function to set the log data.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show():
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument(
        '-k', '--with-ipykernel',
        dest='with_ipykernel',
        action='store_true',
        default=False,
        help='start an IPython kernel within the application')

    options = parser.parse_args()

    logger.info('Starting application')
    app = qt.QApplication([])
    window = MainWindow(app, with_ipykernel=options.with_ipykernel)
    window.show()
    logger.info('Finished initialization')

    if options.with_ipykernel:
        # Very important, IPython-specific step: this gets GUI event loop
        # integration going, and it replaces calling app.exec_()
        logger.info('Starting the IPython kernel')
        window._ipykernel.kernel.start()

    sys.exit(app.exec_())

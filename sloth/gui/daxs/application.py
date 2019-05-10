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

import sys
import argparse
import logging
import signal

from sloth.utils.logging import getLogger
_logger = getLogger('sloth.gui.daxs')
"""Module logger"""


def createParser():
    """Application parser"""
    parser = argparse.ArgumentParser(description="Sloth-DAXS GUI - arguments parser")
    parser.add_argument(
        '-d', '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')
    parser.add_argument(
        '-k', '--with-ipykernel',
        dest='with_ipykernel',
        action='store_true',
        default=False,
        help='start an IPython kernel within the application')
    parser.add_argument(
        '-m0', '--model-v0',
        dest='model_v0',
        action='store_true',
        default=False,
        help='import MainWindow based on original TreeView model')
    parser.add_argument(
        '-f', '--fresh',
        dest="fresh_start",
        action="store_true",
        default=False,
        help='Ignore saved user preferences')
    parser.add_argument(
        '-gl', '--use-opengl',
        dest="use_opengl_plot",
        action="store_true",
        default=False,
        help='Use OpenGL for plots (instead of matplotlib)')

    return parser


def mainQtApp(options):
    """Part of the main application depending on Qt"""
    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    try:
        # it should be loaded before h5py
        import hdf5plugin  # noqa
    except ImportError:
        _logger.debug("Backtrace", exc_info=True)
    import h5py

    import silx
    import silx.utils.files
    from silx.gui import qt

    # Make sure matplotlib is configured
    # Needed for Debian 8: compatibility between Qt4/Qt5 and old matplotlib
    from silx.gui.plot import matplotlib

    _logger.info('Starting application')
    app = qt.QApplication([])
    qt.QLocale.setDefault(qt.QLocale.c())

    def sigintHandler(*args):
        """Handler for the SIGINT signal."""
        qt.QApplication.quit()

    signal.signal(signal.SIGINT, sigintHandler)
    sys.excepthook = qt.exceptionHandler

    timer = qt.QTimer()
    timer.start(500)
    # Application have to wake up Python interpreter, else SIGINT is not
    # catched
    timer.timeout.connect(lambda: None)

    from .config import Config
    config = Config()
    settings = config.read()
    if options.fresh_start:
        settings.clear()

    if options.model_v0:
        from .window import MainWindow
    else:
        from .windowHdf5Tree import MainWindowHdf5Tree as MainWindow

    window = MainWindow(app, with_ipykernel=options.with_ipykernel)
    window.setAttribute(qt.Qt.WA_DeleteOnClose, True)

    if options.use_opengl_plot:
        # To be done after the settings (after the Viewer creation)
        silx.config.DEFAULT_PLOT_BACKEND = "opengl"

    window.show()
    _logger.info('Finished initialization')

    if options.with_ipykernel:
        # Very important, IPython-specific step: this gets GUI event loop
        # integration going, and it replaces calling app.exec_()
        _logger.info('Starting the IPython kernel')
        window._ipykernel.kernel.start()

    result = app.exec_()
    # remove ending warnings relative to QTimer
    app.deleteLater()
    return result


def main(argv):
    """Main function to launch sloth-daxs as an Application

    Parameters
    ----------
    argv : list
        command line arguments
    """
    parser = createParser()
    options = parser.parse_args(argv[1:])
    mainQtApp(options)


if __name__ == '__main__':
    main(sys.argv)

#!/usr/bin/env python
# coding: utf-8
"""
Sloth customization of NeXpy
============================

This module is a customization of `NeXpy <https://github.com/nexpy/nexpy>`_
application. Part of the code here is take or directly inspired by reading
NeXpy code.

#+LICENSE: https://github.com/nexpy/nexpy/blob/master/COPYING
"""
import sys
import argparse

from sloth.utils.logging import getLogger
_logger = getLogger('sloth.gui.nexpy')

__NEXPY_ERROR = "NeXpy (https://github.com/nexpy/nexpy) is REQUIRED\
    -> pip install nexpy"

try:
    import nexpy
    from nexpy.gui.consoleapp import NXConsoleApp
except ImportError as e:
    _logger.error(__NEXPY_ERROR)
    _logger.error(e)
    from sloth import NullClass
    nexpy = NullClass


class myNXConsoleApp(NXConsoleApp):
    """Customized version of the NeXpy console application"""

    def __init__(self):
        super(myNXConsoleApp, self).__init__()


def createParser():
    """Application parser"""
    parser = argparse.ArgumentParser(description="Sloth-NeXpy GUI - parser")

    parser.add_argument(
        '-o', '--open',
        dest='filename',
        nargs='?',
        help='NeXus file to open on launch (optional)')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s v'+nexpy.__version__)

    return parser


def mainMyNexpyApp(options):
    """Main NeXpy application"""
    app = myNXConsoleApp()
    app.initialize(filename=options.filename)
    app.start()
    sys.exit(0)


def main(argv):
    """Main function to launch sloth-nexpy as an Application

    Parameters
    ----------
    argv : list
        command line arguments
    """
    parser = createParser()
    options = parser.parse_args(argv[1:])
    mainMyNexpyApp(options)


if __name__ == '__main__':
    main(sys.argv)

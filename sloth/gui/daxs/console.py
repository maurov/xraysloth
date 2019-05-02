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
"""This module provides integration of an IPython kernel.

.. Note:: Initial idea taken from ipykernel example `internal_ipkernel.py`.
"""

from __future__ import absolute_import, division

__authors__ = ['Mauro Rovezzi']
__license__ = 'MIT'

import sys
from ipykernel import connect_qtconsole
from ipykernel.kernelapp import IPKernelApp


class InternalIPyKernel(object):

    def init_kernel(self, backend='qt', log_level='INFO'):
        _optslist = ['python',
                     '--gui={0}'.format(backend),
                     '--log-level={0}'.format(log_level)]

        self.kernel = IPKernelApp.instance()
        self.kernel.initialize(_optslist)

        # To create and track active qt consoles
        self.consoles = []

        # This application will also act on the shell user namespace
        self.namespace = self.kernel.shell.user_ns
        self.add_to_namespace('kernel', self.kernel)

    def print_namespace(self, evt=None):
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.items():
            if not k.startswith('_'):
                print('%s -> %r' % (k, v))
        sys.stdout.flush()

    def add_to_namespace(self, namestr, nameobj):
        """Extend kernel namespace."""
        self.namespace[namestr] = nameobj

    def new_qt_console(self):
        """Start a new qtconsole connected to our kernel."""
        self.consoles.append(connect_qtconsole(self.kernel.abs_connection_file, profile=self.kernel.profile))

    def cleanup_consoles(self):
        for c in self.consoles:
            c.kill()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JupyX: Jupyter UI for X-ray data analysis
-----------------------------------------
"""

#################
# IPython utils #
#################


def ipythonAutoreload():
    """Force ipython to autoreload imported modules"""
    from IPython import get_ipython
    mgc = get_ipython().magic
    mgc(u'%load_ext autoreload')
    mgc(u'%autoreload 2')


def run_from_ipython():
    """Check if inside ipython -> see :func:`is_in_notebook`"""
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


def is_in_notebook():
    """check if code is run from IPython notebook

    .. note:: code from StackOverflow `https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook/24937408#24937408`_
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

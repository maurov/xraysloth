"""
The :mod:`sloth.utils` module collects small (useful) utilities for daily work
"""
from .pymca import getPyMcaMain, myPyMcaMain
from .xdata import (xray_line, get_element, find_edge, find_line, ene_res, fluo_width, fluo_amplitude, xray_edge, fluo_spectrum, fluo_lines)
from .strings import str2rng
from .files import cp_replace, get_fnames

__all__ = ['getPyMcaMain',
            'myPyMcaMain',
            'xray_line',
            'xray_edge',
            'get_element',
            'find_edge',
            'find_line',
            'fluo_width',
            'fluo_amplitude',
            'fluo_spectrum',
            'fluo_lines',
            'str2rng',
            'cp_replace',
            'get_fnames']

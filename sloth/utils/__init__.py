"""
The :mod:`sloth.utils` module collects simple utilities for daily work
"""
from .bragg import findhkl
from .bragg import d_cubic
from .bragg import d_hexagonal
from .bragg import d_triclinic
from .bragg import kev2ang
from .bragg import ang2kev

from .pymca import getPyMcaMain
from .pymca import myPyMcaMain

from .xdata import xray_line
from .xdata import xray_edge
from .xdata import get_element
from .xdata import find_edge
from .xdata import find_line
from .xdata import ene_res
from .xdata import fluo_width
from .xdata import fluo_amplitude
from .xdata import fluo_spectrum
from .xdata import fluo_lines

from .strings import str2rng

from .files import cp_replace
from .files import get_fnames

from .arrays import imin
from .arrays import imax
from .arrays import sum_arrays_1d

__all__ = ['findhkl',
           'd_cubic',
           'd_hexagonal',
           'd_triclinic',
           'kev2ang',
           'ang2kev',
           'getPyMcaMain',
           'myPyMcaMain',
           'xray_line',
           'xray_edge',
           'get_element',
           'find_edge',
           'find_line',
           'ene_res',
           'fluo_width',
           'fluo_amplitude',
           'fluo_spectrum',
           'fluo_lines',
           'str2rng',
           'cp_replace',
           'get_fnames',
           'imin',
           'imax',
           'sum_arrays_1d']

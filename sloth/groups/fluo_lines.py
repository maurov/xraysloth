#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data groups for x-ray fluorescence lines
===========================================
"""

from .h5base import (EntryGroup, BaseDataset)

from sloth.utils.xdata import (get_element, get_line, mapLine2Trans,
                                xray_line, xray_edge,
                               fluo_width, fluo_amplitude)

#: module logger
from sloth.utils.logging import getLogger
_logger = getLogger('sloth.groups.fluo_lines')


class FluoLine(EntryGroup):
    """Single fluorescence line"""

    #: dictionary of stored attributes
    attrs = {'element': None,  #: absorbing element name
             'element_Z': None,  #: atomic number
             'line': None,  #: emission line name
             'transition': None,  #: emission line IUPAC notation
             'edge': None,  #: energy edge of the given line
             'energy': None,  #: emission line energy (eV)
             'width': None,  #: line width => sum atomic levels XAS+XES
             'excitation': None,  #: excitation energy in eV
             'amplitude': None,
             }

    def __init__(self, element, line, excitation=None):
        """Constructor with element and line names"""
        self.__dict__.update(self.attrs)
        element = get_element(element)
        self.element = element[0]
        self.element_Z = element[1]
        line = get_line(line)
        self.line = line
        self.transition = self.get_transition()
        self.edge = self.get_edge()
        self.energy = self.get_energy()
        self.width = self.get_width()
        if excitation is not None:
            self.excitation = excitation

    def get_transition(self):
        """Line transition IUPAC"""
        _trans = mapLine2Trans(self.line)
        return f"{_trans[2]}-{_trans[3]}"

    def get_edge(self):
        """Edge for the given line level"""
        _level = self.transition.split('-')[0]
        return xray_edge(self.element, initial_level=_level)

    def get_energy(self):
        """Line energy in eV"""
        return xray_line(self.element, self.line)

    def get_width(self):
        """Line width XAS+XES"""
        return fluo_width(self.element, self.line)

    def get_amplitude(self):
        """Line cross section"""
        return fluo_amplitude(self.element, self.line, self.excitation)


def test():
    """quick and dirty manual test"""
    f = FluoLine('Pd', 'LA1', excitation=5000.)
    return f


if __name__ == '__main__':
    f = test()

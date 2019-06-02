#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data groups for x-ray fluorescence lines
========================================
"""

from sloth.groups.baseh5 import EntryGroup

from sloth.utils.xdata import (get_element, get_line, mapLine2Trans,
                               xray_line, xray_edge,
                               fluo_width, fluo_amplitude, fluo_spectrum)

#: module logger
from sloth.utils.logging import getLogger
_logger = getLogger('sloth.groups.fluo_lines')


class FluoLine(EntryGroup):
    """Single fluorescence line"""

    #: dictionary of stored attributes
    attrs = {'element': None,  #: absorbing element name
             'element_Z': None,  #: atomic number
             'line': None,  #: emission line name
             'label': None,  #: group label = {element}_{line}
             'transition': None,  #: emission line IUPAC notation
             'edge': None,  #: energy edge of the given line
             'energy': None,  #: emission line energy (eV)
             'width': None,  #: line width => sum atomic levels XAS+XES
             'excitation': None,  #: excitation energy in eV
             'amplitude': None,  #: cross section of the line
             }

    def __init__(self, element, line, excitation=None, parent=None):
        """Constructor with element and line names"""
        element = get_element(element)
        line = get_line(line)
        self._update_attrs(dict(element=element[0],
                                element_Z=element[1],
                                line=line,
                                label=f"{element[0]}_{line}",
                                excitation=excitation
                               )
                          )
        self._update_attrs(dict(transition=self.get_transition()))
        self._update_attrs(dict(edge=self.get_edge()))
        self._update_attrs(dict(energy=self.get_energy()))
        self._update_attrs(dict(width=self.get_width()))
        self._update_attrs(dict(amplitude=self.get_amplitude()))

        super(FluoLine, self).__init__(self.label, attrs=self.attrs,
                                       parent=parent)

        self._init_spectrum()
        self._plotWin = None

    def _getPlotWin(self):
        """Get plot window object"""
        plotWin = self._plotWin
        if plotWin is None:
            from silx import sx
            from sloth.gui.plot.plot1D import Plot1D
            sx.enable_gui()
            plotWin = Plot1D()
            self._plotWin = plotWin
        return plotWin

    def _update_attrs(self, attrs=None):
        """Update attributes"""
        if attrs is not None:
            self.attrs.update(attrs)
        self.__dict__.update(self.attrs)

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

    def _init_spectrum(self, xwidth=3., xstep=0.05):
        """Generate the fluorescence spectrum

        Parameters
        ----------
        xwidth : int or float (optional)
            FWHM multiplication factor to establish xmin, xmax range
            (= center -+ xwidth*fwhm) [3]
        xstep : float (optional)
            energy step in eV [0.05]
        """
        x, y, _i = fluo_spectrum(self.element, self.line, xwidth=xwidth,
                                 xstep=xstep, excitation=self.excitation,
                                 showInfos=False)
        _gid = 'spectrum'
        self.add_group(_gid)
        self[_gid].add_dataset('x', x)
        self[_gid].add_dataset('y', y)
        self[_gid].attrs.update(dict(xlabel='Energy (eV)',
                                     ylabel='Intensity'))

    @property
    def spectrum(self):
        return self['spectrum']

    @property
    def x(self):
        return self['spectrum/x'].value

    @property
    def y(self):
        return self['spectrum/y'].value

    def plot(self, plotWin=None):
        """Plot the spectrum"""
        if plotWin is None:
            plotWin = self._getPlotWin()
        plotWin.addCurve(self.x, self.y, legend=self.label, replace=True)
        plotWin.setWindowTitle('FluoLine')
        plotWin.setGraphTitle(f"Center:{self.energy} eV, Width:{self.width} eV")
        plotWin.setGraphXLabel(self.spectrum.attrs['xlabel'])
        plotWin.setGraphYLabel(self.spectrum.attrs['ylabel'])
        plotWin.show()


def test():
    """quick and dirty manual test"""
    f = FluoLine('Pd', 'LA1', excitation=5000.)
    return f


if __name__ == '__main__':
    f = test()

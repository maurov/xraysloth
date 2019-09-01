#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Matplotlib plotter for XAFS data
=======================================

This utility is a pure matplotlib visualizer/plotter (no interaction!, no
widgets) for XAFS (x-ray absorption fine structure) data. It is intended to be
used in Jupyter notebooks with Larch.

"""
from .plotter import Plotter


class XAFSPlotter(Plotter):

    def __init__(self, name='XAFSplotter', data=None, **kws):

        super(XAFSPlotter, self).__init__(name=name, **kws)
        self._data = data

    def _updateLabels(self, labels=None):
        """update default plot labels"""
        #: default plot labels
        if labels is None:
            labels = dict(k=r'$k \rm\,(\AA^{-1})$',
                          r=r'$R \rm\,(\AA)$',
                          energy=r'$E\rm\,(eV)$',
                          mu=r'$\mu(E)$',
                          norm=r'normalized $\mu(E)$',
                          flat=r'flattened $\mu(E)$',
                          deconv=r'deconvolved $\mu(E)$',
                          dmude=r'$d\mu(E)/dE$',
                          dnormde=r'$d\mu_{\rm norm}(E)/dE$',
                          chie=r'$\chi(E)$',
                          chikw=r'$k^{{{0:g}}}\chi(k) \rm\,(\AA^{{-{0:g}}})$',
                          chir=r'$\chi(R) \rm\,(\AA^{{-{0:g}}})$',
                          chirmag=r'$|\chi(R)| \rm\,(\AA^{{-{0:g}}})$',
                          chirre=r'${{\rm Re}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                          chirim=r'${{\rm Im}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                          chirpha=r'${{\rm Phase}}[\chi(R)] \rm\,(\AA^{{-{0:g}}})$',
                          e0color='#B2B282',
                          chirlab=None)
        self._labels.update(labels)


if __name__ == '__main__':
    pass

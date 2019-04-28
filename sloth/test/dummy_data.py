#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate dummy data for tests/examples
"""
import numpy as np


def dummy_gauss_image(x=None, y=None,
                      xhalfrng=1.5, yhalfrng=None, xcen=0.5, ycen=0.9,
                      xnpts=1024, ynpts=None, xsigma=0.55, ysigma=0.25,
                      noise=0.3):
    """Create a dummy 2D Gaussian image with noise

    Parameters
    ----------
    x, y : 1D arrays (optional)
        arrays where to generate the image [None -> generated]
    xhalfrng : float (optional)
        half range of the X axis [1.5]
    yhalfrng : float or None (optional)
        half range of the Y axis [None -> xhalfrng]
    xcen : float (optional)
        X center [0.5]
    ycen : float (optional)
        Y center [0.9]
    xnpts : int (optional)
        number of points X [1024]
    ynpts : int or None (optional)
        number of points Y [None -> xnpts]
    xsigma : float (optional)
        sigma X [0.55]
    ysigma : float (optional)
        sigma Y [0.25]
    noise : float (optional)
        random noise level between 0 and 1 [0.3]

    Returns
    -------
    x, y : 1D arrays
    signal : 2D array
    """
    if yhalfrng is None:
        yhalfrng = xhalfrng
    if ycen is None:
        ycen = xcen
    if ynpts is None:
        ynpts = xnpts
    if x is None:
        x = np.linspace(xcen-xhalfrng, xcen+xhalfrng, xnpts)
    if y is None:
        y = np.linspace(ycen-yhalfrng, ycen+yhalfrng, ynpts)
    xx, yy = np.meshgrid(x, y)
    signal = np.exp(-((xx-xcen)**2 / (2*xsigma**2) +
                      ((yy-ycen)**2 / (2*ysigma**2))))
    # add noise
    signal += noise * np.random.random(size=signal.shape)
    return x, y, signal


def dummy_gauss_curve(xhalfrng=15, xcen=5, xnpts=512, xsigma=0.65, noise=0.3):
    """Create a dummy 1D Gaussian curve with noise

    Parameters
    ----------
    xhalfrng : float (optional)
        half range of the X axis [1.5]
    xcen : float (optional)
        X center [0.5]
    xnpts : int (optional)
        number of points X [1024]
    xsigma : float (optional)
        sigma X [0.55]
    noise : float (optional)
        random noise level between 0 and 1 [0.3]

    Returns
    -------
    x, signal : 1D arrays
    """
    x = np.linspace(xcen-xhalfrng, xcen+xhalfrng, xnpts)
    signal = np.exp(-((x-xcen)**2 / (2*xsigma**2)))
    # add noise
    signal += noise * np.random.random(size=signal.shape)
    return x, signal


def main():
    """Show two plot windows with dummy data"""
    from silx import sx
    sx.enable_gui()
    from sloth.gui.plot.plot1D import Plot1D
    from sloth.gui.plot.plot2D import Plot2D
    p1 = Plot1D()
    p2 = Plot2D()
    x, y = dummy_gauss_curve()
    p1.addCurve(x, y, legend="test dummy Gaussian with noise")
    p1.show()
    x, y, signal = dummy_gauss_image()
    p2.addImage(signal, x=x, y=y, legend="test dummy image")
    p2.show()
    input("Press enter to close windows")


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple peak fitting utility with Lmfit
======================================

Current fitting backend: Lmfit_

.. _Lmfit: https://lmfit.github.io/lmfit-py/

"""
#: BASE
import numpy as np
from matplotlib.pyplot import cm

#: LMFIT IMPORTS
from lmfit.models import ConstantModel, VoigtModel

#: SLOTH
from sloth.utils.matplotlib import get_colors
from sloth.utils.logging import getLogger

_logger = getLogger("sloth.fit.peakfit_lmfit", level="INFO")


def fit_peak(
    x,
    y,
    num=1,
    positions=[None],
    amplitudes=[None],
    widths=[None],
    expressions=None,
    bkgModel=None,
    peakModel=None,
):
    """peak fit with lmfit

    Description
    -----------
    This peak fitting model is built to fit one to three peaks (with prefixes:
    'p1_', 'p2_', 'p3_'). The main control parameter is the initial guess of the
    peaks positions.

    Notes
    -----
    For the Gaussian function, amplitude means weighting factor
    multiplying a unit-normalized Gaussian, so that the maximum height
    at the centroid is Amplitude/(sqrt(2pi)*sigma), and that the
    full-width at half maximum is ~2.355 sigma. In the fit, amplitude,
    center, and sigma can be varied, while height and fwhm are
    reported values, derived from these quantities.

    To guess the Gaussian amplitude (A) from the peak maximum (H) and
    a guess width (W), one could use the simple relation::

        A ~ 5.90 * H * W

    Parameters
    ----------
    num : int
        number of peaks to fit: currently between 1 and 3 [1]
    positions : list of floats
        initial peaks positions
    amplitudes : list of floats
        initial peaks amplitudes
    widths : list of floats
        initial peaks widths
    expressions : None or dict
        parameters expressions
    bkgModel : None or lmfit.Model (optional)
        if None: ConstantModel
    peakModel : None or lmfit.Model (optional)
        if None: VoigtModel

    Returns
    -------
    lmfit.fit object

    """
    if num > 3:
        _logger.error("current model is limited to 3 peaks only!")
        return None

    if (len(positions) < num) or (len(amplitudes) < num) or (len(widths) < num):
        _logger.error("'positions'/'amplitudes'/'widths' < 'num'!")
        return None

    if bkgModel is None:
        bkgModel = ConstantModel
    if peakModel is None:
        peakModel = VoigtModel

    bkg = bkgModel(prefix="bkg_")
    pars = bkg.guess(y, x=x)
    pars["bkg_c"].set(y.min())
    mod = bkg

    for ipk in range(num):
        pkPos = positions[ipk]
        pkAmp = amplitudes[ipk]
        pkW = widths[ipk]
        pfx = f"p{ipk+1}_"
        xmax = x[np.argmax(y)]
        ymax = y.max()
        if pkPos is None:
            _logger.info(f"{pfx} center guess at x={xmax}")
            pkPos = xmax
            positions[ipk] = pkPos
        if pkAmp is None:
            _logger.info(f"{pfx} amplitude guess at y={ymax}")
            pkAmp = ymax
            amplitudes[ipk] = pkAmp
        if pkW is None:
            pkW = 1
            _logger.info(f"{pfx} width guess {pkW}")
            widths[ipk] = pkW
        pk = peakModel(prefix=pfx)
        pars.update(pk.make_params())
        pars[f"{pfx}center"].set(pkPos)
        pars[f"{pfx}amplitude"].set(pkAmp)
        pars[f"{pfx}sigma"].set(pkW)
        #: force side peaks to stay same side of the main peak
        if not (ipk == 0):
            if pkPos < positions[0]:
                pars[f"{pfx}center"].set(pkPos, max=positions[0])
            else:
                pars[f"{pfx}center"].set(pkPos, min=positions[0])
        mod += pk
    #: set mathematical constraints if given
    if expressions is not None:
        assert type(expressions) is dict, "Expressions should be a dictionary"
        for key, value in expressions.items():
            try:
                if isinstance(value, str):
                    pars[key].set(expr=value)
                else:
                    pars[key].set(value)
            except KeyError:
                _logger.warning(f"[fit_peak] cannot set expression 'key':'value'")
    _logger.info("Running fit...")
    fitobj = mod.fit(y, pars, x=x)
    return fitobj


def get_curves_fit(x, fitobj, components="p", with_initial_guess=False):
    """get a list of curves from the fit object

    Parameters
    ----------
    x : array
    fitobj : lmfit.model.fit object
    components : False or str (optional)
        if give, include components starting with 'components' string
        default is 'p' (=peaks only)

    Returns
    -------
    curves = [[x, y_best, {'legend': 'best fit', 'color': 'red'}]
              [x, y_initial, {'legend': 'initial guess', 'color': 'gray'}]
              [x, y_componentN], {'legend': 'component prefix N', 'color': 'pink'}]
             ]
    """
    curves = []
    curve_dict = {
        "legend": "best fit",
        "label": "best fit",
        "color": "red",
        "linewidth": 1,
        "linestyle": "-",
    }
    curve = [x, fitobj.best_fit, curve_dict]
    curves.append(curve)
    if with_initial_guess:
        guess_dict = {
            "legend": "initial guess",
            "label": "initial guess",
            "color": "gray",
            "linewidth": 0.5,
            "linestyle": "-",
        }
        curve = [x, fitobj.init_fit, guess_dict]
        curves.append(curve)
    if components:
        comps = fitobj.eval_components()
        _logger.debug(f"Available fit components are: {comps.keys()}")
        colors = get_colors(len(comps.keys()), colormap=cm.viridis)
        for icomp, kcomp in enumerate(comps.keys()):
            if kcomp.startswith(components):
                comp_dict = {
                    "legend": f"{kcomp}",
                    "label": f"{kcomp}",
                    "color": colors[icomp],
                    "linewidth": 1,
                    "linestyle": "-",
                }
                curve = [x, comps[kcomp], comp_dict]
                curves.append(curve)
    return curves


def main_test():
    """Test and show example usage"""
    import matplotlib.pyplot as plt
    from lmfit.lineshapes import gaussian
    from lmfit.models import GaussianModel

    def _get_gauss(x, amp, cen, sigma, noise):
        signal = gaussian(x, amplitude=amp, center=cen, sigma=sigma)
        signal += noise * np.random.random(size=signal.shape)
        return signal

    x = np.linspace(-100, 100, 200)
    y1 = _get_gauss(x, 100, 0, 5, 0.2)
    y2 = _get_gauss(x, 60, -18, 10, 0.1)
    y3 = _get_gauss(x, 90, 10, 10, 0.2)
    y = 0.0015 * x + y1 + y2 + y3
    figname = "test_peakfit_lmfit"

    ymax = y.max()
    xmax = x[np.argmax(y)]
    fitobj = fit_peak(
        x,
        y,
        num=3,
        positions=[xmax, xmax - 20, xmax + 17],
        amplitudes=[ymax, ymax / 2.0, ymax / 3.0],
        widths=[1, 1, 1],
        peakModel=GaussianModel,
    )

    fit_curves = get_curves_fit(x, fitobj, with_initial_guess=True)
    #: plot
    plt.ion()
    plt.close(figname)
    fig, ax = plt.subplots(num=figname)
    ax.plot(x, y, label="data", color="black")

    for fc in fit_curves:
        ax.plot(fc[0], fc[1], label=fc[2]["legend"], color=fc[2]["color"])

    ax.legend(loc="best")
    plt.show()

    return fig, ax


if __name__ == "__main__":
    fig, ax = main_test()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple peak fitting utility with PyMCA/SILX
===========================================

Current fitting backends: PyMca_ or SILX_

.. _PyMca: https://github.com/vasole/pymca
.. _SILX: https://github.com/silx-kit/silx

"""
import os
import numpy as np

HAS_SILX = False
try:
    from silx.math.fit import fittheories, bgtheories
    from silx.math.fit.fitmanager import FitManager
    HAS_SILX = True
except ImportError:
    pass

HAS_PYMCA = False
HAS_PYMCA5 = False
try:
    from PyMca5.PyMcaMath.fitting import Specfit, SpecfitFunctions
    HAS_PYMCA5 = True
except ImportError:
    try:
        from PyMca import Specfit, SpecfitFunctions
        HAS_PYMCA = True
    except ImportError:
        from sloth import NullClass
        Specfit = NullClass
        SpecfitFunctions = NullClass
        pass

from sloth.utils.jupyter import run_from_ipython
IN_IPYTHON = run_from_ipython()

##############
# SILX BASED #
##############


def fit_silx(x, y, theory=None, bkg=None):
    """fit a peak with using silx library

    Parameters
    ==========

    x, y: data 1D arrays

    theory : string [None]
             available theories:
             +---------------------+
             | Gaussians           |
             | Lorentz             |
             | Area Gaussians      |
             | Area Lorentz        |
             | Pseudo-Voigt Line   |
             | Area Pseudo-Voigt   |
             | Split Gaussian      |
             | Split Lorentz       |
             | Split Pseudo-Voigt  |
             | Step Down           |
             | Step Up             |
             | Slit                |
             | Atan                |
             | Hypermet            |
             | Degree 2 Polynomial |
             | Degree 3 Polynomial |
             | Degree 4 Polynomial |
             | Degree 5 Polynomial |
             +---------------------+

    bkg : string [None]
          available bkg theories:
          +---------------------+
          | No Background       |
          | Constant            |
          | Linear              |
          | Strip               |
          | Snip                |
          | Degree 2 Polynomial |
          | Degree 3 Polynomial |
          | Degree 4 Polynomial |
          | Degree 5 Polynomial |
          +---------------------+

    Returns
    =======

    yfit : fit array like x

    """
    fit = FitManager()
    fit.loadtheories(fittheories)
    fit.loadbgtheories(bgtheories)
    fit.setdata(x=x, y=y)
    yfit = y
    _kwerror = False
    if (theory is None):
        print('fit theory not given! choose one of the following:')
        print('\n'.join(map(str, fit.theories.keys())))
        _kwerror = True
    if (bkg is None):
        print('fit background not given! choose one of the following:')
        print('\n'.join(map(str, fit.bgtheories.keys())))
        _kwerror = True
    if _kwerror:
        return yfit
    fit.settheory(theory)
    fit.setbackground(bkg)
    try:
        fit.estimate()
        fit.runfit()
        yfit = fit.gendata()
    except Exception:
        print('ERROR: fit_silx FAILED!!!')

    #print('FWHM: {0}'.format(fwhm(x,yfit,method='bin')))
    return yfit


###############
# PYMCA BASED #
###############


def fit_splitpvoigt(x, y, dy=False,\
                    theory='Split Pseudo-Voigt', bkg='Constant',\
                    conf=None, npeaks=1,\
                    show_infos=True, show_res=True, plot=True, **kws):
    """simple wrapper to PyMca.Specfit

    the goal is to fit (automagically) a set of 1D data (x,y) with an
    asymmetric PseudoVoigt (splitpvoigt) function plus a constant
    background

    Parameters
    ----------
    x, y : data arrays

    dy : boolean or float, False
         error bar on y. If dy==True: dy=np.sqrt(y) or give an
         explicit array

    theory : str, ['Split Pseudo-Voigt',
                   'Gaussians',
                   'Lorentz',
                   'Area Gaussians',
                   'Area Lorentz',
                   'Pseudo-Voigt Line',
                   'Area Pseudo-Voigt',
                   'Split Gaussian',
                   'Split Lorentz',
                   'Step Down',
                   'Step Up',
                   'Slit',
                   'Atan',
                   'Hypermet',
                   'Periodic Gaussians']

    bkg : str, ['Constant', 'No Background', 'Linear', 'Internal']

    conf : dictionary, None
           to tune Specfit configuration, default:
           'FwhmPoints' : int(len(y)/5.
           'Sensitivity' : 5.
           'EtaFlag' : 1 (force eta between 0 and 1)
           'WeightFlag' : 0 (do not weight by noise)
           'AutoScaling' : 1 (auto scale y)
           'AutoFwhm' : 1 (auto guess fwhm)

    npeaks : int, 1
             limit the number of split-PseudoVoigt peaks to guess

    show_infos: boolean, True
                print information on the peakfit setup

    show_res : boolean, True
               print fit results to standard output

    plot : boolean, True
           plot data, fit and residual with PyMca (ScanWindow)

    Returns
    -------
    PyMca.Specfit.Specfit, PyMca.ScanWindow.ScanWindow (None if plot=False)
    """
    # default fit configuration
    fwhmpts_guess = int(len(y)/10.) #guess 1/10 of points resides in fwhm
    iflat = int(len(y)/5.) #guess 1/5 of points are flat or out of peak
    sens_guess = np.mean(y[:iflat])+np.mean(y[-iflat:])
    dconf = {'FwhmPoints' : fwhmpts_guess, #fwhm points
             'Sensitivity' : max(5., sens_guess), #sensitivity
             'Yscaling' : 1.0, #Y factor
             'ForcePeakPresence' : 1, #1 force peak presence
             'HeightAreaFlag' : 1, #1 force positive Height/Area
             'PositionFlag' : 1, #1 force position in interval
             'PosFwhmFlag' : 1, #1 force positive FWHM
             'SameFwhmFlag' : 0, #1 force same FWHM
             'EtaFlag' : 1, #1 to force Eta between 0 and 1
             'NoConstrainsFlag' : 0, #1 ignore Restrains
             'WeightFlag' : 0,
             'AutoScaling' : 0,
             'AutoFwhm' : 0}

    # force update config of bkg and theory
    dconf.update({'fitbkg' : bkg,
                  'fittheory' : theory})

    if conf is not None: dconf.update(conf)

    if show_infos: print('{0:=^64}'.format('FIT INFOS'))

    # init Specfit object
    fit = Specfit.Specfit()

    # set the data
    if dy is True:
        dy = np.sqrt(y)
        fit.setdata(x=x, y=y, sigmay=dy)
    elif dy is False:
        fit.setdata(x=x, y=y)
    else:
        fit.setdata(x=x, y=y, sigmay=dy)

    # initialize fitting functions
    if not len(fit.theorylist):
        funsFile = "SpecfitFunctions.py"
        if not os.path.exists(funsFile):
            funsFile = os.path.join(os.path.dirname(Specfit.__file__), funsFile)
            fit.importfun(funsFile)

    # limit number of estimated peaks
    def _estimate_splitpvoigt2(xx, yy, zzz, xscaling=1.0, yscaling=None, npeaks=npeaks):
        """wrap to SpecfitFunctions.estimate_splitpvoigt to limit to npeaks"""
        currpars, currcons = sff.estimate_splitpvoigt(xx, yy, zzz, xscaling, yscaling)
        #print(currpars)
        #print(currcons)
        newpars = currpars[:5*npeaks]
        newcons = currcons[:][:5*npeaks]
        return newpars, newcons

    # force Split Pseudo-Voigt estimate to a single peak
    sff = SpecfitFunctions.SpecfitFunctions()
    conf_fun = sff.configure(**dconf)
    fit.addtheory('Split Pseudo-Voigt', sff.splitpvoigt, ['Height','Position','LowFWHM', 'HighFWHM', 'Eta'], _estimate_splitpvoigt2)
    theory = 'Split Pseudo-Voigt'

    if show_infos:
        print('backgroung: {0}'.format(bkg))
        print('theory: {0} {1}'.format(npeaks, theory))

    # update configuration
    fit_conf = fit.configure(**dconf)

    # set theory and bkg
    fit.settheory(theory)
    fit.setbackground(bkg)

    # automatic estimate and fit
    fit_est = fit.estimate()
    fit.startfit()

    # RESULTS
    yfit = fit.gendata(x=x, parameters=fit.paramlist)
    residual = y-yfit

    # outputs
    pk_area = np.trapz(yfit, x=x)
    fit.resdict = fit_results(fit, output='dict', pk_info=True)
    fit.resdict.update({'area' : pk_area})
    fit.yfit = yfit
    fit.residual = residual

    # print results
    if show_res is True:
        fit_results(fit, output='print', pk_info=True)

    # plot
    if plot is True:
        if HAS_PYMCA5:
            from PyMca5.PyMcaGui import ScanWindow
        elif HAS_PYMCA:
            from PyMca import ScanWindow
        else:
            return fit, 0
        if (not IN_IPYTHON):
            from PyMca import PyMcaQt as qt
            qtApp = qt.QApplication([])
        pw = ScanWindow.ScanWindow()
        pw.setGeometry(50,50,800,800)
        pw.addCurve(x, y, legend='data', replace=True)
        pw.addCurve(x, yfit, legend='yfit', replace=False)
        pw.addCurve(x, residual, legend='residual', replace=False)
        pw.show()
        if (not IN_IPYTHON):
            qtApp.exec_()
    if plot is True:
        return fit, pw
    else:
        return fit, None

def fit_results(fitobj, output='print', pk_info=True):
    """ simple report of fit results

    Arguments
    ---------
    fitobj : Specfit object
    output : 'string'
             'list'
             'print'
             'dict'
    """
    # templates
    tmpl_head = '{0:=^64}'
    tmpl_parhead = '{0:<4} {1:=^12} {2:=^15} {3:=^13} ({4:=^14})'
    tmpl_parlist = '{0:<4} {1:<12} {2:< 15.5f} {3:< 13.5f} ({4:^ 14.5f})'
    tmpl_pkhead = '{0:<4} {1:=^12} {2:=^14} {3:=^12} ({4:=^14})'
    tmpl_pkinfo = '{0:<4} {1:< 12.5f} {2:< 15.5f} {3:< 13.5f} {4:^ 14.5f}'

    # HEADER
    out = [tmpl_head.format(' FIT RESULTS ')]

    # STATISTICS
    out.append(tmpl_head.format(' STATISTICS '))
    out.append('chi_squared = {0}'.format(fitobj.chisq))

    # FITTED PARAMETERS
    out.append(tmpl_head.format(' FITTED PARAMETERS '))
    out.append(tmpl_parhead.format('#idx', ' name ', ' fitresult ', ' sigma ', ' estimation '))
    for idx, d in enumerate(fitobj.paramlist):
        out.append(tmpl_parlist.format(idx, d['name'], d['fitresult'], d['sigma'], d['estimation']))
    # PEAK INFO
    if pk_info:
        out.append(tmpl_head.format(' PEAK INFO '))
        bkg = fitobj.bkgfun.__str__().lower()
        if 'none' in bkg:
            ioff = 0
            #const = 0
        elif 'constant' in bkg:
            ioff = 1
            #const = fitobj.paramlist[0]['fitresult']
        elif 'linear' in bkg:
            ioff = 2
            #const = fitobj.paramlist[0]['fitresult']
        elif 'internal' in bkg:
            ioff = 3
            #const = fitobj.paramlist[2]['fitresult']
        else:
            pass

        pk_height = fitobj.paramlist[ioff]['fitresult'] - np.min(fitobj.ydata)
        pk_pos = fitobj.paramlist[ioff+1]['fitresult']
        pk_fwhm = (fitobj.paramlist[ioff+2]['fitresult']/2.) + (fitobj.paramlist[ioff+3]['fitresult']/2.)
        pk_cfwhm = pk_pos + ( pk_fwhm/2. - (fitobj.paramlist[ioff+2]['fitresult']/2.) )
        # collect peak infos in a dictionary
        resdict = {'height' : pk_height,
                   'position' : pk_pos,
                   'fwhm' : pk_fwhm,
                   'cfwhm' : pk_cfwhm}

        out.append(tmpl_pkhead.format('#', ' hght-min ', ' position ', ' FHWM ', ' cen_FWHM '))
        out.append(tmpl_pkinfo.format('1', pk_height, pk_pos, pk_fwhm, pk_cfwhm))

    # OUTPUT
    if ('print' in output.lower()):
        print('\n'.join(out))
    elif ('list' in output.lower()):
        return out
    elif ('dict' in output.lower()):
        return resdict
    else:
        return '\n'.join(out)

if __name__ == '__main__':
    pass
    # TESTS are in examples/peakfit_tests.py

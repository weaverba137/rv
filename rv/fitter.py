# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for fitting the model, etc.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np


def initial_period(N=100, logTmin=2, logTmax=5):
    """Return a vector of initial frequencies.

    Parameters
    ----------
    N : int, optional
        Number of frequencies, default 100.
    logTmin : float, optional
        Minumum log period, default 2 (100 days).
    logTmax : float, optional
        Maximum log period, default 5 (100,000 days).

    Returns
    -------
    ndarray
        Array containing orbital angular frequencies.
    """
    Ts = np.logspace(logTmin, logTmax, N)
    return 2.0*np.pi/Ts


def fitter(data, options):
    """Runs scipy.minimize on a set of initial guesses.
    """
    from scipy.optimize import minimize
    from .model import obj, dobj, d2obj
    fitter_options = {'disp': False}
    if options.method == 'TNC':
        fitter_options['maxiter'] = 10000
    w0 = initial_period()
    fits = list()
    fitter_args = (data['vhelio'], data['mjd'], data['vrelerr'], options.Q)
    fitter_bounds = ((None, None), (None, None), (None, None),
                     (2.0*np.pi*1.0e-6, 2.0*np.pi))
    for k in range(len(w0)):
        p0 = np.array([data['vhelio_avg'], data['vscatter'], 0, w0[k]])
        fit = minimize(obj, p0, args=fitter_args, method=options.method,
                       jac=dobj,  # hess=d2obj,
                       bounds=fitter_bounds, options=fitter_options)
        fits.append(fit)
    return fits

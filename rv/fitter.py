# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for fitting the model, etc.
"""
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
#
#
#
def initial_period(N=100,logTmin=2,logTmax=5):
    """Return a vector of initial frequencies.
    """
    Ts = np.logspace(logTmin,logTmax,N)
    return 2.0*np.pi/Ts
#
#
#
def fitter(data,options):
    """Runs scipy.minimize on a set of initial guesses.
    """
    from scipy.optimize import minimize
    from .model import obj, dobj, d2obj
    w0 = initial_period()
    fits = list()
    for k in range(len(w0)):
        p0 = np.array([data['vhelio_avg'],data['vscatter'],0,w0[k]])
        fit =  minimize(obj,p0,
                        args=(data['vhelio'],data['mjd'],data['vrelerr'],options.Q),
                        method='TNC',
                        jac=dobj,
                        # hess=d2obj,
                        bounds=((None,None),(None,None),(None,None),(2.0*np.pi*1.0e-6,2.0*np.pi)),
                        options={'disp':False,'maxiter':10000})
        fits.append(fit)
    return fits

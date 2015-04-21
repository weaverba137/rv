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
def fitter(data,Q):
    """Runs scipy.minimize on a set of initial guesses.
    """
    from scipy.optimize import minimize
    from .model import obj, dobj, d2obj
    N = 100
    Ts = np.logspace(2,5,N)
    w0 = 2.0*np.pi/Ts
    fits = list()
    for k in range(N):
        p0 = np.array([data['vhelio_avg'],data['vscatter'],0,w0[k]])
        fit =  minimize(obj,p0,
                        args=(data['vhelio'],data['mjd'],data['vrelerr'],Q),
                        method='TNC',
                        jac=dobj,
                        # hess=d2obj,
                        bounds=((None,None),(None,None),(None,None),(2.0*np.pi*1.0e-6,2.0*np.pi)),
                        options={'disp':False,'maxiter':10000})
        fits.append(fit)
    return fits

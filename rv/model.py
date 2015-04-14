# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for computing the model, objective function, etc.
"""
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
#
#
#
def model(p,t):
    """The model.
    """
    return p[0] + p[1]*np.sin(p[3]*t) + p[2]*np.cos(p[3]*t)
#
#
#
def dmdp(p,t):
    """The gradient of the model with respect to the parameters.
    """
    return np.vstack((
        np.ones(t.shape,dtype=t.dtype),
        np.sin(p[3]*t),
        np.cos(p[3]*t),
        t*p[1]*np.cos(p[3]*t)-t*p[2]*np.sin(p[3]*t)
        ))
#
#
#
def d2mdpdp(p,t):
    """The second derivative of the model with respect to the parameters.
    """
    H = np.zeros((p.size,p.size,t.size),dtype=p.dtype)
    H[3,3,:] = -t*t*p[1]*np.sin(p[3]*t) - t*t*p[2]*np.cos(p[3]*t)
    H[1,3,:] = H[3,1,:] = t*np.cos(p[3]*t)
    H[2,3,:] = H[3,2,:] = -t*np.sin(p[3]*t)
    return H
#
#
#
def chin(p,x,t,s):
    """The value of 'chi'.
    """
    return (x - model(p,t))/s
#
#
#
def f2(p,x,t,s,Q=0):
    chi = chin(p,x,t,s)
    if Q == 0:
        return chi**2
    else:
        return Q*chi**2/(chi**2 + Q)
#
#
#
def df2dp(p,x,t,s,Q=0):
    chi = chin(p,x,t,s)
    d = dmdp(p,t)
    if Q == 0:
        f = -2*chi/s
    else:
        f = -2*chi/s * (Q**2 / (chi**2 + Q)**2)
    return f*d
#
#
#
def d2f2dpdp(p,x,t,s,Q=0):
    H = np.zeros((p.size,p.size,t.size),dtype=p.dtype)
    chi = chin(p,x,t,s)
    d = dmdp(p,t)
    dd = d2mdpdp(p,t)
    for i in range(p.size):
        for j in range(p.size):
            H[i,j,:] = d[i,:]*d[j,:]
    if Q == 0:
        f = -2*chi/s
        f2 = 2/s**2
    else:
        f = -2*chi/s * (Q**2 / (chi**2 + Q)**2)
        f2 = 2*(Q**2/s**2)*((Q**2 - 3*chi**2)/(chi**2 + Q)**3)
    return f2*H + f*dd
#
#
#
def obj(p,x,t,s,Q=0):
    return f2(p,x,t,s,Q).sum()
#
#
#
def dobj(p,x,t,s,Q=0):
    return df2dp(p,x,t,s,Q).sum(1)
#
#
#
def d2obj(p,x,t,s,Q=0):
    return d2f2dpdp(p,x,t,s,Q).sum(2)

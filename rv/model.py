# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for computing the model, objective function, etc.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np


def model(p, t):
    """The model.

    The model has the functional form:

    .. math::

        m(t; p) = p_0 + p_1 \sin p_3 t + p_2 \cos p_3 t

    Parameters
    ----------
    p : array-like
        List of parameters.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.

    Returns
    -------
    :class:`float` or :class:`~numpy.ndarray`
        The model evaluated for the inputs.
    """
    return p[0] + p[1]*np.sin(p[3]*t) + p[2]*np.cos(p[3]*t)


def dmdp(p, t):
    """The gradient of the :func:`model` with respect to the parameters.

    Given the :func:`model`, the gradient computed here is:
    :math:`\partial m(t; p)/\partial p_i`.

    Parameters
    ----------
    p : array-like
        List of parameters.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.

    Returns
    -------
    :class:`~numpy.ndarray`
        The gradient evaluated for the inputs.
    """
    return np.vstack((
                     np.ones(t.shape, dtype=t.dtype),
                     np.sin(p[3]*t),
                     np.cos(p[3]*t),
                     t*p[1]*np.cos(p[3]*t)-t*p[2]*np.sin(p[3]*t)
                     ))


def d2mdpdp(p, t):
    """The second derivative of the :func:`model` with respect to
    the parameters.

    Given the :func:`model`, the gradient computed here is:
    :math:`\partial^2 m(t; p)/\partial p_i \partial p_j`.

    Parameters
    ----------
    p : array-like
        List of parameters.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.

    Returns
    -------
    :class:`~numpy.ndarray`
        The second derivative evaluated for the inputs.
    """
    H = np.zeros((p.size, p.size, t.size), dtype=p.dtype)
    H[3, 3, :] = -t*t*p[1]*np.sin(p[3]*t) - t*t*p[2]*np.cos(p[3]*t)
    H[1, 3, :] = H[3, 1, :] = t*np.cos(p[3]*t)
    H[2, 3, :] = H[3, 2, :] = -t*np.sin(p[3]*t)
    return H


def chin(p, x, t, s):
    """The value of :math:`\chi`.  In some sense the residual at `x`.

    Formally this is, :math:`\chi = (x - m(t; p))/\sigma`,
    where :math:`x` are the (radial velocity) data values, and :math:`\sigma`
    are the errors on those values.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.

    Returns
    -------
    :class:`~numpy.ndarray`
        The residual.
    """
    return (x - model(p, t))/s


def f2(p, x, t, s, Q=0):
    """Function of :math:`\chi` that will be summed to produce the final
    objective function.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        A vector that when summed produces something like :math:`\chi^2`.
    """
    chi = chin(p, x, t, s)
    if Q == 0:
        return chi**2
    else:
        return Q*chi**2/(chi**2 + Q)


def df2dp(p, x, t, s, Q=0):
    """Gradient of :func:`f2` with respect to the parameters.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        A vector that when summed produces something like
        :math:`\partial \chi^2/\partial p_i`.
    """
    chi = chin(p, x, t, s)
    d = dmdp(p, t)
    if Q == 0:
        f = -2*chi/s
    else:
        f = -2*chi/s * (Q**2 / (chi**2 + Q)**2)
    return f*d


def d2f2dpdp(p, x, t, s, Q=0):
    """Second derivative of :func:`f2` with respect to the parameters.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        A vector that when summed produces something like
        :math:`\partial^2 \chi^2/\partial p_i \partial p_j`.
    """
    H = np.zeros((p.size, p.size, t.size), dtype=p.dtype)
    chi = chin(p, x, t, s)
    d = dmdp(p, t)
    dd = d2mdpdp(p, t)
    for i in range(p.size):
        for j in range(p.size):
            H[i, j, :] = d[i, :] * d[j, :]
    if Q == 0:
        f = -2*chi/s
        f2 = 2/s**2
    else:
        f = -2*chi/s * (Q**2 / (chi**2 + Q)**2)
        f2 = 2*(Q**2/s**2)*((Q**2 - 3*chi**2)/(chi**2 + Q)**3)
    return f2*H + f*dd


def obj(p, x, t, s, Q=0):
    """The objective function, that is the function to be minimized.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        The objective function.
    """
    return f2(p, x, t, s, Q).sum()


def dobj(p, x, t, s, Q=0):
    """Gradient of the objective function with respect to the parameters.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        The first derivative of the objective function.
    """
    return df2dp(p, x, t, s, Q).sum(1)


def d2obj(p, x, t, s, Q=0):
    """Second derivative of the objective function with respect to the
    parameters.

    Parameters
    ----------
    p : array-like
        List of parameters.
    x : :class:`float` or :class:`~numpy.ndarray`
        Independent (radial velocity) variable.
    t : :class:`float` or :class:`~numpy.ndarray`
        Time variable.
    s : :class:`float` or :class:`~numpy.ndarray`
        Error on `x`.
    Q : :class:`float`, optional
        A regularization parameter, to suppress outliers.

    Returns
    -------
    :class:`~numpy.ndarray`
        The second derivative of the objective function.
    """
    return d2f2dpdp(p, x, t, s, Q).sum(2)

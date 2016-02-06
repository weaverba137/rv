# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for loading plotting the data.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['figure.figsize'] = (10.0, 10.0)
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
#
# Configure plots
#
legendfont = FontProperties(size='medium')
titlefont = FontProperties(size='x-large')


def diagnostic_plots(stars, options):
    """Produce diagnostic plots.

    Parameters
    ----------
    stars : :class:`dict`
        A dictionary containing data.
    options : :class:`~argparse.Namespace`
        Command-line options.
    """
    from numpy import array, hypot, arctan2, pi
    from os.path import join
    max_mjd = array([stars[s].mjd[-1] for s in stars])
    min_mjd = array([stars[s].mjd[0] for s in stars])
    delta_mjd = max_mjd - min_mjd
    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(111)
    n, bins, patches = ax.hist(delta_mjd, 20)
    foo = ax.set_xlabel('Time Baseline [days]')
    foo = ax.set_ylabel('N')
    fig.savefig(join(options.plotDir, 'time.png'))
    fig.clf()
    plt.close(fig)
    # print(min_mjd.min(), max_mjd.max())
    nvisit = list()
    kappa1 = list()
    P1 = list()
    kappa2 = list()
    P2 = list()
    for s in stars:
        nvisit.append(stars[s].nvisits)
        if 'fit1' in stars[s]:
            kappa1.append(hypot(stars[s].fit1[1], stars[s].fit1[2]))
            # phi1.append(arctan2(stars[s].fit1[2], stars[s].fit1[1]))
            P1.append(2.0*pi/stars[s].fit1[3])
        if 'fit2' in stars[s]:
            kappa2.append(hypot(stars[s].fit2[1], stars[s].fit2[2]))
            # phi2.append(arctan2(stars[s].fit2[2], stars[s].fit2[1]))
            P2.append(2.0*pi/stars[s].fit2[3])
    nvisit = array(nvisit)
    ax = inthist(nvisit, True)
    foo = ax.set_xlabel('Number of Visits')
    foo = ax.set_ylabel('N')
    fig = ax.get_figure()
    fig.savefig(join(options.plotDir, 'nvisit.png'))
    fig.clf()
    plt.close(fig)
    if len(kappa1) > 0:
        kappa1 = array(kappa1)
        P1 = array(P1)
        fig = plt.figure(dpi=100)
        ax = fig.add_subplot(111)
        p1 = ax.loglog(P1, kappa1, 'k.')
        foo = ax.set_xlabel('Orbital Period [days]', fontproperties=titlefont)
        foo = ax.set_ylabel('Velocity Amplitude [km/s]',
                            fontproperties=titlefont)
        fig.savefig(join(options.plotDir, 'kappa-P.png'))
        fig.clf()
        plt.close(fig)
    return


def rv_plot(data, fits, options):
    """Plot RV curve.

    Parameters
    ----------
    data : :class:`dict`
        The data on an individual star.
    fits : :class:`list`
        The fitted curves produced by :func:`~rv.fitter.fitter`.
    options : :class:`~argparse.Namespace`
        Command-line options.

    Returns
    -------
    :func:`tuple`
        The best and second-best fitted values.
    """
    from os.path import join
    from numpy import array, argsort, linspace
    from .model import model
    good_fits = [f for f in fits if f.success]
    chi = array([f.fun for f in fits if f.success])
    k = argsort(chi)
    # print(good_fits(k[0]))
    days = linspace(data.mjd[0], data.mjd[-1], 100)
    fig = plt.figure(dpi=100)
    plt.subplots_adjust(hspace=0.001)
    ax = fig.add_subplot(211)
    p0 = ax.errorbar(data.mjd, data.vhelio, yerr=data.vrelerr,
                     fmt='ks')
    p1 = ax.plot([data.mjd[0], data.mjd[-1]],
                 [data.vhelio_avg, data.vhelio_avg], 'b-')
    p2 = ax.plot([data.mjd[0], data.mjd[-1]],
                 [data.vhelio_avg+data.vscatter,
                  data.vhelio_avg+data.vscatter], 'b--')
    p3 = ax.plot([data.mjd[0], data.mjd[-1]],
                 [data.vhelio_avg-data.vscatter,
                  data.vhelio_avg-data.vscatter], 'b--')
    p4 = ax.plot(days, model(good_fits[k[0]].x, days), 'r-')
    p5 = ax.plot(days, model(good_fits[k[1]].x, days), 'r--')
    # foo = [l.set_label(WDs[f]['labels'][k]) for k, l in enumerate(p)]
    # foo = ax.set_xlabel('MJD - {0:d}'.format(data.mjd_zero),
    #                     fontproperties=titlefont)
    foo = ax.set_ylabel('Heliocentric Velocity [km/s]',
                        fontproperties=titlefont)
    foo = ax.set_title(data.apstar_id, fontproperties=titlefont)
    foo = ax.grid(True)
    # leg = ax.legend(loc=1, prop=legendfont, numpoints=1)
    foo = ax.set_xticklabels([])
    ax = fig.add_subplot(212)
    p0 = ax.plot(data.mjd, data.snr, 'ks')
    foo = ax.set_xlabel('MJD - {0:d}'.format(data.mjd_zero),
                        fontproperties=titlefont)
    foo = ax.set_ylabel('S/N', fontproperties=titlefont)
    foo = ax.grid(True)
    fig.savefig(join(options.plotDir, data.apstar_id+'.png'))
    fig.clf()
    plt.close(fig)
    return (good_fits[k[0]].x, good_fits[k[1]].x)


def inthist(foo, show=False):
    """Create a histogram of integer values.

    Parameters
    ----------
    foo : :class:`~numpy.ndarray`
        An array containing integers.
    show : :class:`bool`, optional
        If ``True``, create a histogram and return the
        :class:`matplotlib.axes.Axes` instance.

    Returns
    -------
    :func:`tuple` or :class:`matplotlib.axes.Axes`
        If `show` is ``False``, just return the number in each bin and the
        bins, respectively.
    """
    import numpy as np
    xmin = min(foo)
    xmax = max(foo)
    x = np.arange(xmin, xmax+1)
    n = np.zeros(x.shape, dtype=x.dtype)
    for k in range(len(n)):
        n[k] = np.sum(foo == x[k])
    if show:
        fig = plt.figure(dpi=100)
        ax = fig.add_subplot(111)
        b = ax.bar(x, n, align='center', width=0.5, color='w')
        ax.set_xlim(xmin-1, xmax+1)
        # ax.set_ylim(0, np.ceil(max(n)/10.0)*10.0)
        ax.set_ylim(0, 10**np.ceil(np.log10(max(n))))
        return ax
    else:
        return (n, x)

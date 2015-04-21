# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for loading data, setting options, etc.
"""
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['figure.figsize'] = (10.0, 10.0)
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
#
# Configure plots
#
legendfont= FontProperties(size='medium');
titlefont = FontProperties(size='x-large')
#
#
#
def diagnostic_plots(stars,options):
    """Produce diagnostic plots.
    """
    from numpy import array
    max_mjd = array([stars[s]['mjd'][-1] for s in stars])
    min_mjd = array([stars[s]['mjd'][0]  for s in stars])
    delta_mjd = max_mjd - min_mjd
    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(111)
    n, bins, patches = ax.hist(delta_mjd,20)
    foo = ax.set_xlabel('Time Baseline [days]')
    foo = ax.set_ylabel('N')
    fig.savefig(join(options.plotDir,'time.png'))
    fig.clf()
    plt.close(fig)
    # print(min_mjd.min(),max_mjd.max())
    nvisit = list()
    for s in stars:
        nvisit.append(len(stars[s]['mjd']))
    nvisit = np.array(nvisit)
    ax = inthist(nvisit,True)
    foo = ax.set_xlabel('Number of Visits')
    foo = ax.set_ylabel('N')
    fig = ax.get_figure()
    fig.savefig(join(options.plotDir,'nvisit.png'))
    fig.clf()
    plt.close(fig)
    return
#
#
#
def rv_plot(data,fits,options):
    """Plot RV curve.
    """
    from numpy import array, argsort, linspace
    from .model import model
    apstar_id = 'apogee.apo25m.s.stars.{0:d}.{1}'.format(data['locid'],data['tmassid'])
    good_fits = [f for f in fits if f.success]
    chi = array([f.fun for f in fits if f.success])
    k = argsort(chi)
    # print(good_fits(k[0]))
    days = linspace(data['mjd'][0],data['mjd'][-1],100)
    fig = plt.figure(dpi=100)
    plt.subplots_adjust(hspace=0.001)
    ax = fig.add_subplot(211)
    p0 = ax.errorbar(data['mjd'],data['vhelio'],yerr=data['vrelerr'],fmt='ks')
    p1 = ax.plot([data['mjd'][0],data['mjd'][-1]],[data['vhelio_avg'],data['vhelio_avg']],'b-')
    p2 = ax.plot([data['mjd'][0],data['mjd'][-1]],
                 [data['vhelio_avg']+data['vscatter'],data['vhelio_avg']+data['vscatter']],'b--')
    p3 = ax.plot([data['mjd'][0],data['mjd'][-1]],
                 [data['vhelio_avg']-data['vscatter'],data['vhelio_avg']-data['vscatter']],'b--')
    p4 = ax.plot(days,model(good_fits[k[0]].x,days),'r-')
    p5 = ax.plot(days,model(good_fits[k[1]].x,days),'r--')
    # foo = [l.set_label(WDs[f]['labels'][k]) for k,l in enumerate(p)]
    # foo = ax.set_xlabel('MJD - {0:d}'.format(options.mjd_zero), fontproperties=titlefont)
    foo = ax.set_ylabel('Heliocentric Velocity [km/s]', fontproperties=titlefont)
    foo = ax.set_title(apstar_id, fontproperties=titlefont)
    foo = ax.grid(True)
    # leg = ax.legend(loc=1,prop=legendfont,numpoints=1)
    foo = ax.set_xticklabels([])
    ax = fig.add_subplot(212)
    p0 = ax.plot(data['mjd'],data['snr'],'ks')
    foo = ax.set_xlabel('MJD - {0:d}'.format(options.mjd_zero), fontproperties=titlefont)
    foo = ax.set_ylabel('S/N', fontproperties=titlefont)
    foo = ax.grid(True)
    fig.savefig(join(options.plotDir,apstar_id+'.png'))
    fig.clf()
    plt.close(fig)
    return
#
#
#
def inthist(foo, show=False):
    """Create a histogram of integer values.

    Parameters
    ----------
    foo : numpy.ndarray
        An array containing integers.
    show : bool, optional
        If ``True``, create a histogram and return the matplotlib.axes.Axes
        instance.

    Returns
    -------
    inthist : mixed
    """
    import numpy as np
    xmin = min(foo)
    xmax = max(foo)
    x = np.arange( xmin, xmax+1 )
    n = np.zeros( x.shape, dtype=x.dtype )
    for k in range(len(n)):
        n[k] = np.sum( foo == x[k] )
    if show:
        fig = plt.figure(dpi=100)
        ax = fig.add_subplot(111)
        b = ax.bar(x,n,align='center',width=0.5,color='w')
        ax.set_xlim(xmin-1, xmax+1)
        # ax.set_ylim(0, np.ceil(max(n)/10.0)*10.0)
        ax.set_ylim(0, 10**np.ceil(np.log10(max(n))))
        return ax
    else:
        return (n,x)

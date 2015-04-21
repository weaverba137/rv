# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for loading data, setting options, etc.
"""
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
#
#
#
def rv_options(description="RV",set_args=None):
    """Set the options typically used by rv.
    """
    from os import getenv
    from os.path import join
    from argparse import ArgumentParser
    parser = ArgumentParser(description=description,prog='rv')
    parser.add_argument('-c', '--clobber', action='store_true', dest='clobber',
        help='Overwrite any cache file(s).')
    parser.add_argument('-d', '--diagnostics', action='store_true', dest='diag',
        help='Produce diagnostic plots.')
    parser.add_argument('-D', '--data-dir', action='store', dest='plotDir',
        default=join(getenv('HOME'),'Desktop','apogee-rv'), metavar='DIR',
        help='Read data from DIR.')
    parser.add_argument('-I', '--no-index', action='store_false', dest='index',
        help='Do not regenerate index file.')
    parser.add_argument('-p', '--plot', action='store_true', dest='plot',
        help='Produce plots.')
    parser.add_argument('-Q', '--q-value', action='store', type=float, dest='Q',
        default=0, metavar='Q', help='Set Q value.')
    parser.add_argument('-z', '--zero', action='store', type=int, dest='mjd_zero',
        metavar='MJD', default=55800,
        help='Set zero day to this MJD.')
    if set_args is None:
        options = parser.parse_args()
    else:
        set_args = parser.parse_args(set_args)
    return options
#
#
#
def rv_data(options):
    """Load RV data.
    """
    from os import getenv
    from os.path import exists, join
    import cPickle as pickle
    from collections import OrderedDict
    import astropy.io.fits as pyfits
    import numpy as np
    #
    #
    #
    f = join(options.plotDir,'apogee_vrel.pickle')
    if exists(f) and not options.clobber:
        with open(f) as p:
            stars = pickle.load(p)
    else:
        fit = join(options.plotDir,'apogee_vrel_weaver.fit')
        hdulist = pyfits.open(fit)
        data = hdulist[1].data
        hdulist.close()
        # data.dtype
        #
        # Sort the data
        #
        stars = OrderedDict()
        for row in data:
            if row['apstar_id'] not in stars:
                foo = row['apstar_id'].split('.')
                locid = int(foo[4])
                c = int(foo[2] == 'c')
                sas_url="http://mirror.sdss3.org/irSpectrumDetail?locid={0:d}&commiss={1:d}&apogeeid={2}".format(locid,c,foo[5])
                cas_url="http://skyserver.sdss.org/dr12/en/tools/explore/Summary.aspx?apid="+row['apstar_id']
                stars[row['apstar_id']] = {'mjd':[],'vhelio':[],'vrelerr':[],
                                           'teff':row['teff'],'logg':row['logg'],'mh':row['param_m_h'],
                                           'snr':[],
                                           'vhelio_avg':row['vhelio_avg'],'vscatter':row['vscatter'],
                                           'commiss':c,'locid':int(foo[4]),'tmassid':foo[5],
                                           'sas':sas_url,'cas':cas_url}
            stars[row['apstar_id']]['mjd'].append(row['jd'] - 2400000.5 - options.mjd_zero)
            stars[row['apstar_id']]['vhelio'].append(row['vhelio'])
            stars[row['apstar_id']]['vrelerr'].append(row['vrelerr'])
            stars[row['apstar_id']]['snr'].append(row['snr'])
        for s in stars:
            for c in ('mjd','vhelio','vrelerr','snr'):
                stars[s][c] = np.array(stars[s][c])
        #
        # Save the data
        #
        with open(f,'w') as p:
            pickle.dump(stars,p)
    return stars

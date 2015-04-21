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
    parser = ArgumentParser(description=description,prog='rvMain')
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
    from numpy import array
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
                stars[s][c] = array(stars[s][c])
        #
        # Save the data
        #
        with open(f,'w') as p:
            pickle.dump(stars,p)
    return stars
#
#
#
def create_index(stars,ncol=6):
    """Create index.html file.

    Parameters
    ----------
    stars : dict
        Dictionary containing data grouped by star.
    ncol : int, optional
        Number of columns in the output.

    Returns
    -------
    create_index : str
        The index.html file as a string.
    """
    index_text = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta name="robots" content="noindex" />
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>APOGEE Radial Velocities</title>
        <style type="text/css">
img {{display: block; width: 200px; height: 200px;}}
td {{text-align: center;}}
        </style>
    </head>
    <body>
        <h1>APOGEE Radial Velocities</h1>
        <h2 id="intro">Introduction</h2>
        <p>Data were obtained with this query:</p>
        <pre>
SELECT aspcap.apstar_id, aspcap.teff, aspcap.logg, aspcap.param_m_h,
  star.vhelio_avg, star.vscatter, star.verr, star.verr_med,
  visit.visit_id, visit.ra, visit.dec, visit.glon, visit.glat,
  visit.snr, visit.jd, visit.vhelio, visit.vrelerr
INTO MyDB.apogee_vrel
FROM apogeeVisit     AS visit
JOIN apogeeStarVisit AS starvisit ON visit.visit_id   = starvisit.visit_id
JOIN aspcapStar      AS aspcap    ON aspcap.apstar_id = starvisit.apstar_id
JOIN apogeeStar      AS star      ON star.apstar_id   = starvisit.apstar_id
WHERE (aspcap.aspcapflag   &amp; dbo.fApogeeAspcapFlag('STAR_BAD')) = 0
  AND (star.apogee_target1 &amp; dbo.fApogeeTarget1('APOGEE_LONG')) &gt; 0
  AND aspcap.teff &gt; 0
  AND star.nvisits &gt; 5
ORDER BY aspcap.apstar_id, visit.jd;
        </pre>
        <h2 id="diag">Diagnostics</h2>
        <table>
            <tr>
                <td><a href="time.png"><img src="time.png" alt="Time Baseline" /></a></td>
                <td><a href="nvisit.png"><img src="nvisit.png" alt="Number of Visits" /></a></td>
            </tr>
            <tr>
                <td>Histogram of RV time baselines.</td>
                <td>Histogram of number of visits.</td>
            </tr>
        </table>
{0}
    </body>
</html>
"""
    th = '<tr><th></th>' + ''.join(['<th>{0:d}</th>'.format(k+1) for k in range(ncol)]) + '</tr>'
    locations = dict()
    for s in stars:
        col = '<td><a href="apogee.apo25m.s.stars.{locid:d}.{tmassid}.png"><img src="apogee.apo25m.s.stars.{locid:d}.{tmassid}.png" alt="apogee.apo25m.s.stars.{locid:d}.{tmassid}" /></a><br /><var>T</var><sub>eff</sub> = {teff:.2f}<br />log&nbsp;<var>g</var> = {logg:.2f}<br />[M/H] = {mh:.2f}<br /><a href="{sas}">SAS</a>&nbsp;&nbsp;<a href="{cas}">CAS</a></td>'.format(**stars[s])
        if stars[s]['locid'] in locations:
            locations[stars[s]['locid']].append(col)
        else:
            locations[stars[s]['locid']] = [col]
    tables = ''
    for l in sorted(locations.keys()):
        while len(locations[l]) % ncol != 0:
            locations[l].append('<td></td>')
        rows = list()
        for k in range(len(locations[l])//ncol):
            rows.append('<tr><td><strong>{0:d}</strong></td>'.format(k+1)+''.join(locations[l][ncol*k:ncol*k+ncol])+'</tr>')
        tables += '<h2 id="loc{0:d}">{0:d}</h2>\n<table>\n<thead>\n{1}\n</thead>\n<tbody>\n'.format(l,th)
        tables += "\n".join(rows)
        tables += '</tbody>\n</table>\n'
    return index_text.format(tables)

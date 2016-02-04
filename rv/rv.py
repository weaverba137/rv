# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Radial velocity webapp using Flask.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from flask import Flask, render_template, jsonify, request, json
from werkzeug.contrib.cache import SimpleCache
from .model import model, obj, dobj, d2obj
from .fitter import fitter
from .util import rv_options, rv_data


app = Flask(__name__)
cache = None
options = None
stars = None
locids = None
tmass_ids = None


def load_app_data():
    """Load the global data needed by the application.
    """
    global cache, options, stars, locids, tmass_ids
    cache = SimpleCache()
    options = rv_options(description='RV', set_args=[])
    stars = rv_data(options)
    locids = sorted(list(set([int(s.split('.')[4]) for s in stars])))
    tmass_ids = dict()
    for s in stars:
        foo = s.split('.')
        l = int(foo[4])
        if l in tmass_ids:
            tmass_ids[l].append(foo[5])
        else:
            tmass_ids[l] = [foo[5]]
    return


@app.route("/")
def index():
    """Return the set of location IDs.
    """
    return render_template('index.html', title='RV', locids=locids)


@app.route("/doc")
def doc():
    """Documentation page.
    """
    return render_template('doc.html', title='RV - Documentation')


@app.route("/<int:locid>")
def list_stars(locid):
    """Return the set of stars that match a given location ID.
    """
    return render_template('stars.html', title=str(locid), locids=locids,
                           locid=locid, stars=sorted(tmass_ids[locid]))


@app.route("/<int:locid>/<tmass_id>")
def star(locid, tmass_id):
    """Return data on an individual star.
    """
    apstar_id = 'apogee.apo25m.s.stars.{0:d}.{1}'.format(locid, tmass_id)
    data = stars[apstar_id]
    return render_template('star.html',
                           title="{0:d}.{1}".format(locid, tmass_id),
                           locids=locids, teff=data['teff'],
                           logg=data['logg'], mh=data['mh'],
                           sas=data['sas'], cas=data['cas'],
                           apstar_id=apstar_id, locid=locid,
                           stars=sorted(tmass_ids[locid]), tmass_id=tmass_id,
                           mjd_zero=options.mjd_zero)


@app.route("/<int:locid>/<tmass_id>/<int:Q>")
def data(locid, tmass_id, Q):
    """Return fitted model parameters.
    """
    apstar_id = 'apogee.apo25m.s.stars.{0:d}.{1}'.format(locid, tmass_id)
    response = cache.get(apstar_id+'.'+str(Q))
    if response is None:
        data = stars[apstar_id]
        options.Q = Q
        fits = fitter(data, options)
        good_fits = [f for f in fits if f.success]
        chi = np.array([f.fun for f in fits if f.success])
        k = np.argsort(chi)
        days = np.linspace(data['mjd'][0], data['mjd'][-1], 100)
        fit1 = model(good_fits[k[0]].x, days).tolist()
        fit2 = model(good_fits[k[1]].x, days).tolist()
        day_data = days.tolist()
        json_data = {"Q": Q,
                     'apstar_id': apstar_id,
                     'mjd_zero': options.mjd_zero,
                     'fit1': [[day_data[d], fit1[d]]
                              for d in range(len(day_data))],
                     'fit2': [[day_data[d], fit2[d]]
                              for d in range(len(day_data))],
                     'fit1_param': good_fits[k[0]].x.tolist(),
                     'fit2_param': good_fits[k[1]].x.tolist()
                     }
        for k in data:
            if k in ('mjd', 'vhelio', 'vrelerr', 'snr'):
                json_data[k] = data[k].tolist()
            else:
                try:
                    f = np.issubdtype(data[k], float)
                except:
                    f = False
                if f:
                    json_data[k] = float(data[k])
                else:
                    json_data[k] = data[k]
        response = jsonify(**json_data)
        cache.set(apstar_id+'.'+str(Q), response, timeout=10*60)
    return response


if __name__ == '__main__':
    load_app_data()
    app.run(port=56789)  # , debug=True)

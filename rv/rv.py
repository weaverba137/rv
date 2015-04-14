#!/opt/local/bin/python2.7
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
from os import getenv
from os.path import join
import numpy as np
from scipy.optimize import minimize
import cPickle as pickle
from flask import Flask, render_template, jsonify, request, json
from werkzeug.contrib.cache import SimpleCache
#
#
#
app = Flask(__name__)
cache = SimpleCache()
#
#
#
plotDir = join(getenv('HOME'),'Desktop','apogee-rv')
mjd_zero = 55800
#
# Files
#
f = join(plotDir,'apogee_vrel.pickle')
with open(f) as p:
    stars = pickle.load(p)
locids = sorted(list(set([int(s.split('.')[4]) for s in stars])))
tmass_ids = dict()
for s in stars:
    foo = s.split('.')
    l = int(foo[4])
    if l in tmass_ids:
        tmass_ids[l].append(foo[5])
    else:
        tmass_ids[l] = [foo[5]]
#
#
#
def model(p,t):
    return p[0] + p[1]*np.sin(p[3]*t) + p[2]*np.cos(p[3]*t)
#
#
#
def dmdp(p,t):
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
    H = np.zeros((p.size,p.size,t.size),dtype=p.dtype)
    H[3,3,:] = -t*t*p[1]*np.sin(p[3]*t) - t*t*p[2]*np.cos(p[3]*t)
    H[1,3,:] = H[3,1,:] = t*np.cos(p[3]*t)
    H[2,3,:] = H[3,2,:] = -t*np.sin(p[3]*t)
    return H
#
#
#
def chin(p,x,t,s):
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
#
#
#
@app.route("/")
def index():
    """Return the set of location IDs.
    """
    return render_template('index.html', title='RV', locids=locids)
#
#
#
@app.route("/doc")
def doc():
    """Documentation page.
    """
    return render_template('doc.html', title='RV - Documentation')
#
#
#
@app.route("/<int:locid>")
def list_stars(locid):
    """Return the set of stars that match a given location ID.
    """
    return render_template('stars.html', title=str(locid), locids=locids,
        locid=locid, stars=sorted(tmass_ids[locid]))
#
#
#
@app.route("/<int:locid>/<tmass_id>")
def star(locid,tmass_id):
    apstar_id = 'apogee.apo25m.s.stars.{0:d}.{1}'.format(locid,tmass_id)
    data = stars[apstar_id]
    return render_template('star.html', title="{0:d}.{1}".format(locid,tmass_id),
        locids=locids, teff=data['teff'], logg=data['logg'], mh=data['mh'],
        sas=data['sas'], cas=data['cas'], apstar_id=apstar_id,
        locid=locid, stars=sorted(tmass_ids[locid]), tmass_id=tmass_id,
        mjd_zero=mjd_zero)
#
#
#
@app.route("/<int:locid>/<tmass_id>/<int:Q>")
def data(locid,tmass_id,Q):
    apstar_id = 'apogee.apo25m.s.stars.{0:d}.{1}'.format(locid,tmass_id)
    data = stars[apstar_id]
    response = cache.get(apstar_id+'.'+str(Q))
    if response is None:
        N = 200
        Ts = np.logspace(2,5,N)
        w0 = 2.0*np.pi/Ts
        fits = list()
        for k in range(N):
            p0 = np.array([data['vhelio_avg'],data['vscatter'],0,w0[k]])
            fit =  minimize(obj,p0,args=(data['vhelio'],data['mjd'],data['vrelerr'],Q),method='Newton-CG',jac=dobj,hess=d2obj,options={'disp':False})
            fits.append(fit)
        good_fits = [f for f in fits if f.success]
        chi = np.array([f.fun for f in fits if f.success])
        k = np.argsort(chi)
        days = np.linspace(data['mjd'][0],data['mjd'][-1],100)
        fit1 = model(good_fits[k[0]].x,days).tolist()
        fit2 = model(good_fits[k[1]].x,days).tolist()
        day_data = days.tolist()
        json_data = {"Q":Q,
            'apstar_id':apstar_id,
            'mjd_zero':mjd_zero,
            'fit1':[ [day_data[d], fit1[d]] for d in range(len(day_data))],
            'fit2':[ [day_data[d], fit2[d]] for d in range(len(day_data))]
            }
        for k in data:
            if k in ('mjd','vhelio','vrelerr','snr'):
                json_data[k] = data[k].tolist()
            else:
                try:
                    f = np.issubdtype(data[k],float)
                except:
                    f = False
                if f:
                    json_data[k] = float(data[k])
                else:
                    json_data[k] = data[k]
        response = jsonify(**json_data)
        cache.set(apstar_id+'.'+str(Q),response,timeout=10*60)
    return response
#
#
#
if __name__ == "__main__":
    app.run(port=56789,debug=True)

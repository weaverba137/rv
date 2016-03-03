# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Functions for loading data, setting options, etc.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from numpy import issubdtype, append, array
from astropy.extern.six import string_types


class BitMask(object):
    """Base class for specific bitmask objects.
    """
    bits = (('UNUSED_00', "Unused"))

    def flagname(self, value):
        """Convert a flag value into readable names.

        Parameters
        ----------
        value : :class:`int`
            Mask value.

        Returns
        -------
        :func:`tuple`
            The names of the flags.
        """
        names = [self.bits[bit][0] for bit in range(len(self.bits))
                 if (value & (1 << bit)) != 0]
        return tuple(names)

    def flagval(self, name):
        """Convert a name or set of names into a bitmask value.

        Parameters
        ----------
        name : :class:`str` or iterable.
            Name(s) of flags to convert.

        Returns
        -------
        :class:`int`
            The value of the mask
        """
        if isinstance(name, string_types):
            name = [name]
        names = set(name)
        value = 0
        for bit in range(len(self.bits)):
            if self.bits[bit][0] in names:
                value += (1 << bit)
        return value


class APOGEE_STARFLAG(BitMask):
    """APOGEE star-level mask bits.
    """

    bits = (('BAD_PIXELS', "Spectrum has many bad pixels (>40%): BAD"),
            ('COMMISSIONING', ("Commissioning data (MJD<55761), " +
                               "non-standard configuration, poor " +
                               "LSF: WARN")),
            ('BRIGHT_NEIGHBOR', "Star has neighbor more than 10 " +
                                "times brighter: WARN"),
            ('VERY_BRIGHT_NEIGHBOR', "Star has neighbor more than " +
                                     "100 times brighter: BAD"),
            ('LOW_SNR', "Spectrum has low S/N (S/N<5): BAD"),
            ('UNUSED_05', "Unused"),
            ('UNUSED_06', "Unused"),
            ('UNUSED_07', "Unused"),
            ('UNUSED_08', "Unused"),
            ('PERSIST_HIGH', "Spectrum has significant number " +
                             "(>20%) of pixels in high persistence " +
                             "region: WARN"),
            ('PERSIST_MED', "Spectrum has significant number " +
                            "(>20%) of pixels in medium persistence " +
                            "region: WARN"),
            ('PERSIST_LOW', "Spectrum has significant number " +
                            "(>20%) of pixels in low persistence " +
                            "region: WARN"),
            ('PERSIST_JUMP_POS', "Spectrum show obvious positive " +
                                 "jump in blue chip: WARN"),
            ('PERSIST_JUMP_NEG', "Spectrum show obvious negative " +
                                 "jump in blue chip: WARN"),
            ('UNUSED_14', "Unused"),
            ('UNUSED_15', "Unused"),
            ('SUSPECT_RV_COMBINATION', "WARNING: RVs from synthetic " +
                                       "template differ significantly from " +
                                       "those from combined template"),
            ('SUSPECT_BROAD_LINES', "WARNING: cross-correlation peak with " +
                                    "template significantly broader than " +
                                    "autocorrelation of template"),)


def rv_options(description="RV", set_args=None):
    """Set the options typically used by rv.

    Parameters
    ----------
    description : :class:`str`, optional
        The overall description of the command-line program.
    set_args : :class:`list`, optional
        A list that will be passed to
        :meth:`argparse.ArgumentParser.parse_args`.

    Returns
    -------
    :class:`~argparse.Namespace`
        Parsed command-line options.
    """
    from os import getenv
    from os.path import join
    from argparse import ArgumentParser
    parser = ArgumentParser(description=description, prog='rvMain')
    parser.add_argument('-c', '--clobber', action='store_true', dest='clobber',
                        help='Overwrite any cache file(s).')
    parser.add_argument('-D', '--data-dir', action='store', dest='plotDir',
                        default=join(getenv('HOME'), 'Desktop', 'apogee-rv'),
                        metavar='DIR', help='Read data from DIR.')
    parser.add_argument('-I', '--no-index', action='store_false', dest='index',
                        help='Do not regenerate index file.')
    parser.add_argument('-m', '--method', action='store', dest='method',
                        default='L-BFGS-B', metavar='METHOD',
                        help=('Set the optimization method for ' +
                              'scipy.optimize.minimize (default "L-BFGS-B").'))
    parser.add_argument('-p', '--plot', action='store_true', dest='plot',
                        help='Produce plots.')
    parser.add_argument('-Q', '--q-value', action='store', type=float,
                        dest='Q', default=0, metavar='Q', help='Set Q value.')
    parser.add_argument('-z', '--zero', action='store', type=int,
                        dest='mjd_zero', metavar='MJD', default=55800,
                        help='Set zero day to this MJD.')
    if set_args is None:
        options = parser.parse_args()
    else:
        options = parser.parse_args(set_args)
    return options


class Star(object):
    """Simple object to hold data and metadata about a star.

    Parameters
    ----------
    row : :class:`~astropy.io.fits.fitsrec.FITS_record`
        Row from a FITS binary table.
    mjd_zero : :class:`int`
        The offset to the MJD, to make the range of days reasonable.

    Attributes
    ----------
    apstar_id : :class:`str`
        The "fully qualified" ID of the object.
    cas_base_url : :class:`str`
        Used to construct links to data on CAS.
    commiss : :class:`int`
        The commissioning flag.
    fit1 : :class:`~scipy.optimize.OptimizeResult`
        Placeholder for the best fit information.
    fit2 : :class:`~scipy.optimize.OptimizeResult`
        Placeholder for the second-best fit information.
    jd2mjd : :class:`float`
        The offset from Julian Day to Modified Julian Day.
    locid : :class:`int`
        The location ID.
    logg : :class:`float`
        The surface gravity.
    mh : :class:`float`
        The metallicity.
    min_visits : :class:`int`
        The number of data points should be greater than this for a viable fit.
    mjd_zero : :class:`int`
        Stores the corresponding input parameter.
    sas_base_url : :class:`str`
        Used to construct links to data on SAS.
    teff : :class:`float`
        The effective temperature.
    tmassid : :class:`str`
        The ID used for targeting the object.
    vhelio_avg : :class:`float`
        The average heliocentric velocity.
    vscatter : :class:`float`
        The error on `vhelio_avg`.
    """
    sas_base_url = 'http://mirror.sdss3.org/irSpectrumDetail'
    cas_base_url = ("http://skyserver.sdss.org/dr12/en/tools/" +
                    "explore/Summary.aspx?apid=")
    jd2mjd = 2400000.5
    min_visits = 5  # number of data points required for viable fit.

    def __init__(self, row, mjd_zero):
        self.mjd_zero = mjd_zero
        #
        # Try to initialize data as close to the column order as possible.
        #
        self.apstar_id = str(row['apstar_id'])
        foo = self.apstar_id.split('.')
        self.commiss = int(foo[2] == 'c')
        self.locid = int(foo[4])
        self.tmassid = foo[5]
        self.teff = float(row['teff'])
        self.logg = float(row['logg'])
        self.mh = float(row['param_m_h'])
        self.vhelio_avg = float(row['vhelio_avg'])
        self.vscatter = float(row['vscatter'])
        # self.verr = float(row['verr'])
        # self.verr_med = float(row['verr'])
        self.synthvhelio_avg = float(row['synthvhelio_avg'])
        self.synthvscatter = float(row['synthvscatter'])
        # self.synthverr = float(row['synthverr'])
        # self.synthverr_med = float(row['synthverr'])
        self.ORstarflag = int(row['ORstarflag'])
        self.ANDstarflag = int(row['ANDstarflag'])
        self._visit_list = array((row['visit_id'],))
        # self.ra = float(row['ra'])
        # self.dec = float(row['dec'])
        # self.glon = float(row['glon'])
        # self.glat = float(row['glat'])
        self._snr_list = array((row['snr'],))
        self._mjd_list = array((row['jd'] - self.jd2mjd - self.mjd_zero,))
        self._visitstarflag_list = array((row['visitstarflag'],))
        self._vhelio_list = array((row['vhelio'],))
        self._vrelerr_list = array((row['vrelerr'],))
        self._synthvhelio_list = array((row['synthvhelio'],))
        self._synthvrelerr_list = array((row['synthvrelerr'],))
        #
        # Placeholders
        #
        self._visits = None
        self._snr = None
        self._mjd = None
        self._visitstarflag = None
        self._vhelio = None
        self._vrelerr = None
        self._synthvhelio = None
        self._synthvrelerr = None
        self._clean = None
        self._valid_flags = None
        self._nvisits = None
        self._json_data = None
        self.fit1 = None
        self.fit2 = None
        return

    @property
    def sas(self):
        """URL for this object on SAS.
        """
        return ("{0.sas_base_url}?locid={0.locid:d}&commiss={0.commiss:d}&" +
                "apogeeid={0.tmassid}").format(self)

    @property
    def cas(self):
        """URL for this object on SkyServer.
        """
        return self.cas_base_url + self.apstar_id

    @property
    def visits(self):
        """Visit IDs corresponding to each observation, excluding bad data.
        """
        if self._visits is None:
            self._visits = self._visit_list[self.clean]
        return self._visits

    @property
    def snr(self):
        """Signal-to-noise ratio.
        """
        if self._snr is None:
            self._snr = self._snr_list[self.clean]
        return self._snr

    @property
    def mjd(self):
        """Date of observation.
        """
        if self._mjd is None:
            self._mjd = self._mjd_list[self.clean]
        return self._mjd

    @property
    def visitstarflag(self):
        """Flags set for each visit.
        """
        if self._visitstarflag is None:
            self._visitstarflag = self._visitstarflag_list[self.clean]
        return self._visitstarflag

    @property
    def vhelio(self):
        """Heliocentric radial velocity.
        """
        if self._vhelio is None:
            self._vhelio = self._vhelio_list[self.clean]
        return self._vhelio

    @property
    def vrelerr(self):
        """Radial velocity error.
        """
        if self._vrelerr is None:
            self._vrelerr = self._vrelerr_list[self.clean]
        return self._vrelerr

    @property
    def synthvhelio(self):
        """Heliocentric radial velocity, based on synthetic spectra.
        """
        if self._synthvhelio is None:
            self._synthvhelio = self._synthvhelio_list[self.clean]
        return self._synthvhelio

    @property
    def synthvrelerr(self):
        """Radial velocity error, based on synthetic spectra..
        """
        if self._synthvrelerr is None:
            self._synthvrelerr = self._synthvrelerr_list[self.clean]
        return self._synthvrelerr

    @property
    def clean(self):
        """A boolean array indicating where the velocity has reasonable values.
        """
        if self._clean is None:
            self._clean = self._vhelio_list < 3e5
        return self._clean

    @property
    def valid_flags(self):
        """Make sure that the flags are self-consistent.
        """
        if self._valid_flags is None:
            #
            # numpy.bitwise_and.identity = 1, so numpy.bitwise_and.reduce
            # doesn't work as expected.
            # Looks like this is fixed in bleeding-edge versions of numpy,
            # but for now...
            #
            n = self.visitstarflag.size
            o = self.visitstarflag[0]
            a = self.visitstarflag[0]
            for i in range(1, n):
                o |= self.visitstarflag[i]
                a &= self.visitstarflag[i]
            self._valid_flags = ((self.ORstarflag == o) and
                                 (self.ANDstarflag == a))
        return self._valid_flags

    @property
    def nvisits(self):
        """Number of data points, excluding bad data.
        """
        if self._nvisits is None:
            self._nvisits = len(self.mjd)
        return self._nvisits

    @property
    def fittable(self):
        """``True`` if there are enough data points for a viable fit.
        """
        return self.nvisits > self.min_visits

    @property
    def json(self):
        """Encode the Star data as a dictionary that can be converted to
        JSON format.
        """
        if self._json_data is None:
            self._json_data = dict()
            self._json_data['mjd_zero'] = self.mjd_zero
            self._json_data['apstar_id'] = self.apstar_id
            self._json_data['commiss'] = self.commiss
            self._json_data['locid'] = self.locid
            self._json_data['tmassid'] = self.tmassid
            self._json_data['teff'] = self.teff
            self._json_data['logg'] = self.logg
            self._json_data['mh'] = self.mh
            self._json_data['vhelio_avg'] = self.vhelio_avg
            self._json_data['vscatter'] = self.vscatter
            self._json_data['synthvhelio_avg'] = self.synthvhelio_avg
            self._json_data['synthvscatter'] = self.synthvscatter
            self._json_data['visits'] = self.visits.tolist()
            self._json_data['snr'] = self.snr.tolist()
            self._json_data['mjd'] = self.mjd.tolist()
            self._json_data['visitstarflag'] = self.visitstarflag.tolist()
            self._json_data['vhelio'] = self.vhelio.tolist()
            self._json_data['vrelerr'] = self.vrelerr.tolist()
            self._json_data['synthvhelio'] = self.synthvhelio.tolist()
            self._json_data['synthvrelerr'] = self.synthvrelerr.tolist()
            if self.fit1 is None:
                self._json_data['fit1_param'] = None
            else:
                self._json_data['fit1_param'] = self.fit1.x.tolist()
            if self.fit2 is None:
                self._json_data['fit2_param'] = None
            else:
                self._json_data['fit2_param'] = self.fit2.x.tolist()
        return self._json_data

    def append(self, row):
        """Add data to object already initialized.

        Parameters
        ----------
        row : :class:`~astropy.io.fits.fitsrec.FITS_record`
            Row from a FITS binary table.

        Returns
        -------
        :class:`Star`
            Returns the instance, in case you need to chain.
        """
        self._visit_list = append(self._visit_list, row['visit_id'])
        self._snr_list = append(self._snr_list, row['snr'])
        self._mjd_list = append(self._mjd_list,
                                row['jd'] - self.jd2mjd - self.mjd_zero)
        self._visitstarflag_list = append(self._visitstarflag_list,
                                          row['visitstarflag'])
        self._vhelio_list = append(self._vhelio_list, row['vhelio'])
        self._vrelerr_list = append(self._vrelerr_list, row['vrelerr'])
        self._synthvhelio_list = append(self._synthvhelio_list,
                                        row['synthvhelio'])
        self._synthvrelerr_list = append(self._synthvrelerr_list,
                                         row['synthvrelerr'])
        return self


def rv_data(options):
    """Load RV data.

    Parameters
    ----------
    options : :class:`~argparse.Namespace`
        Command-line options.

    Returns
    -------
    :class:`~collections.OrderedDict`
        The data loaded from disk.
    """
    from os import getenv
    from os.path import exists, join
    import cPickle as pickle
    from collections import OrderedDict
    import astropy.io.fits as pyfits
    #
    #
    #
    f = join(options.plotDir, 'apogee_vrel.pickle')
    if exists(f) and not options.clobber:
        with open(f) as p:
            stars = pickle.load(p)
    else:
        fit = join(options.plotDir, 'apogee_vrel_v2_weaver.fit')
        hdulist = pyfits.open(fit)
        data = hdulist[1].data
        hdulist.close()
        # data.dtype
        #
        # Sort the data
        #
        stars = OrderedDict()
        for row in data:
            if row['apstar_id'] in stars:
                stars[row['apstar_id']].append(row)
            else:
                stars[row['apstar_id']] = Star(row, options.mjd_zero)
        #
        # Save the data
        #
        with open(f, 'w') as p:
            pickle.dump(stars, p)
    return stars


def create_index(stars, ncol=6):
    """Create index.html file.

    Parameters
    ----------
    stars : :class:`dict`
        Dictionary containing data grouped by star.
    ncol : :class:`int`, optional
        Number of columns in the output.

    Returns
    -------
    :class:`str`
        The index.html file as a string.
    """
    from collections import OrderedDict
    from jinja2 import Environment, PackageLoader
    tables = OrderedDict()
    for s in stars:
        stuple = (stars[s].tmassid,
                  stars[s].teff,
                  stars[s].logg,
                  stars[s].mh,
                  stars[s].sas,
                  stars[s].cas,
                  stars[s].ANDstarflag,
                  stars[s].ORstarflag,)
        if stars[s].locid in tables:
            tables[stars[s].locid].append(stuple)
        else:
            tables[stars[s].locid] = [stuple]
    #
    # Pad tables out to multiples of ncol
    #
    for t in tables:
        while len(tables[t]) % ncol != 0:
            tables[t].append(tuple())
    env = Environment(loader=PackageLoader('rv', 'templates'))
    template = env.get_template('plots.html')
    return template.render(title='APOGEE Radial Velocities', ncol=ncol,
                           tables=tables)

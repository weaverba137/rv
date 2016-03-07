# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import os
import numpy as np
from ..util import APOGEE_STARFLAG, Star, rv_options, rv_data, create_index


class TestUtil(object):
    """Test rv.util.
    """

    def setup(self):
        self.dataDir = os.path.join(os.path.dirname(__file__), 't')
        self.pickleFile = 'apogee_vrel_testdata.pickle'
        self.dataFile = 'apogee_vrel_testdata.fits'
        self.indexFile = 'testdata_index.html'
        self.starflag = APOGEE_STARFLAG()

    def teardown(self):
        if os.path.exists(os.path.join(self.dataDir, self.pickleFile)):
            os.remove(os.path.join(self.dataDir, self.pickleFile))

    def test_rv_options(self):
        """Verify the command-line options.
        """
        options = rv_options()
        assert not options.plot
        assert options.mjd_zero == 55800
        options = rv_options(set_args=['--method', 'foobar',
                                       '--zero', '50000'])
        assert options.method == 'foobar'
        assert options.mjd_zero == 50000

    def test_flagname(self):
        """Test the interpretation of APOGEE_STARFLAG values.
        """
        assert self.starflag.flagname(1) == (self.starflag.bits[0][0],)
        assert self.starflag.flagname(2) == (self.starflag.bits[1][0],)
        assert self.starflag.flagname(3) == (self.starflag.bits[0][0],
                                             self.starflag.bits[1][0])

    def test_flagval(self):
        """Test the conversion of names into APOGEE_STARFLAG values.
        """
        assert self.starflag.flagval(self.starflag.bits[0][0]) == 1
        assert self.starflag.flagval(self.starflag.bits[1][0]) == 2
        assert self.starflag.flagval((self.starflag.bits[0][0],
                                      self.starflag.bits[1][0])) == 3

    def test_rv_data(self):
        """Test aspects of loading data.
        """
        options = rv_options(set_args=['--clobber', '--data-dir',
                                       self.dataDir])
        assert options.plotDir == self.dataDir
        stars = rv_data(options, self.pickleFile, self.dataFile)
        assert os.path.exists(os.path.join(self.dataDir, self.pickleFile))
        options = rv_options(set_args=['--data-dir', self.dataDir])
        stars2 = rv_data(options, self.pickleFile, self.dataFile)
        for s in stars:
            assert stars[s].apstar_id == stars2[s].apstar_id
            assert (stars[s].clean == stars2[s].clean).all()
            assert stars[s].valid_flags
            assert stars[s].fittable
            assert stars[s].cas == Star.cas_base_url + stars[s].apstar_id
            # assert stars[s].sas == 'bar'

    def test_create_index(self):
        """Test creation of plot index file.
        """
        options = rv_options(set_args=['--data-dir', self.dataDir])
        stars = rv_data(options, self.pickleFile, self.dataFile)
        i = create_index(stars)
        with open(os.path.join(self.dataDir, self.indexFile)) as f:
            index_data = f.read()
        assert i == index_data

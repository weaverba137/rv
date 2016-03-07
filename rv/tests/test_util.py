# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import os
import numpy as np
from ..util import APOGEE_STARFLAG, rv_options


class TestUtil(object):
    """Test rv.util.
    """

    def setup(self):
        self.dataDir = os.path.join(os.path.dirname(__file__), 't')
        self.starflag = APOGEE_STARFLAG()

    def teardown(self):
        pass

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

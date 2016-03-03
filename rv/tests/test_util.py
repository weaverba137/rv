# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
from ..util import APOGEE_STARFLAG, flagname, flagval, rv_options


class TestUtil(object):
    """Test rv.util.
    """

    def setup(self):
        pass

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
        assert flagname(1) == (APOGEE_STARFLAG[0][0],)
        assert flagname(2) == (APOGEE_STARFLAG[1][0],)
        assert flagname(3) == (APOGEE_STARFLAG[0][0], APOGEE_STARFLAG[1][0])

    def test_flagval(self):
        """Test the conversion of names into APOGEE_STARFLAG values.
        """
        assert flagval(APOGEE_STARFLAG[0][0]) == 1
        assert flagval(APOGEE_STARFLAG[1][0]) == 2
        assert flagval((APOGEE_STARFLAG[0][0], APOGEE_STARFLAG[1][0])) == 3

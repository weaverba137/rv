# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
from ..util import rv_options

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
        options = rv_options(set_args=['--method', 'foobar', '--zero', '50000'])
        assert options.method == 'foobar'
        assert options.mjd_zero == 50000

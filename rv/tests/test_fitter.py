# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
from ..fitter import initial_period


class TestFitter(object):
    """Test rv.fitter.
    """

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_initial_period(self):
        """Verify the construction of period vectors.
        """
        foo = initial_period(N=2)
        assert np.allclose(foo, np.array([6.28318531e-02, 6.28318531e-05]))

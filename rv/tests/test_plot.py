# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
import matplotlib.pyplot as plt
from ..plot import inthist

class TestPlot(object):
    """Test rv.plot.
    """

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_inthist(self):
        """Test the inthist function.
        """
        data = np.array([1, 1, 1, 1, 2, 2, 3])
        n, x = inthist(data)
        assert (n == np.array([4,2,1])).all()
        assert (x == np.array([1,2,3])).all()
        ax = inthist(data,True)
        assert ax.get_xlim() == (0.0, 4.0)
        assert ax.get_ylim() == (0.0, 10.0)
        fig = ax.get_figure()
        fig.clf()
        plt.close(fig)

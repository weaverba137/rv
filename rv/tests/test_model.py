# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
from ..model import chin, d2mdpdp, dmdp, model


class TestModel(object):
    """Test rv.model.
    """

    def setup(self):
        self.pi = float(np.pi)
        self.pi2 = self.pi/2.0
        self.pi32 = self.pi2*3.0
        self.pipi = 2.0*self.pi
        self.x = np.array([1.01, 0.99, -0.99, -0.99, 1.01])
        self.p = np.array([0.0, 1.0, 1.0, 1.0])
        self.t = np.array([0, self.pi2, self.pi, self.pi32, self.pipi])
        self.s = np.array([0.01, 0.01, 0.01, 0.01, 0.01])

    def teardown(self):
        pass

    def test_model(self):
        """Verify the behaviour of the model.
        """
        answer = np.array([1.0, 1.0, -1., -1.,  1.])
        assert np.allclose(model(self.p, self.t), answer)

    def test_dmdp(self):
        """Verify the behaviour of the derivative of the model.
        """
        answer = np.array([[1.0, 1.0, 1.0, 1.0, 1.0],
                           [0.0, 1.0, 0.0, -1.0, 0.0],
                           [1.0, 0.0, -1.0, 0.0, 1.0],
                           [0.0, -self.pi2, -self.pi, self.pi32, self.pipi]
                           ])
        assert np.allclose(dmdp(self.p, self.t), answer)

    def test_d2mdpdp(self):
        """Verify the behaviour of the second derivative of the model.
        """
        pi_sq = self.pi**2
        pi2_sq = self.pi2**2
        pi32_sq = self.pi32**2
        pipi_sq = self.pipi**2
        answer = np.array([[[0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0]],
                           [[0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, -self.pi, 0.0, self.pipi]],
                           [[0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, -self.pi2, 0.0, self.pi32, 0.0]],
                           [[0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, -self.pi, 0.0, self.pipi],
                            [0.0, -self.pi2, 0.0, self.pi32, 0.0],
                            [0.0, -pi2_sq, pi_sq, pi32_sq, -pipi_sq]
                           ]])
        assert np.allclose(d2mdpdp(self.p, self.t), answer)

    def test_chi(self):
        """Test the chi function.
        """
        answer = np.array([1., -1., 1., 1., 1.])
        assert np.allclose(chin(self.p, self.x, self.t, self.s), answer)

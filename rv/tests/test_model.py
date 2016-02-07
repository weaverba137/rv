# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
import numpy as np
from ..model import (model, dmdp, d2mdpdp, chin, f2, df2dp, d2f2dpdp,
                     obj, dobj, d2obj)


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
                            [0.0, -pi2_sq, pi_sq, pi32_sq, -pipi_sq]]])
        assert np.allclose(d2mdpdp(self.p, self.t), answer)

    def test_chi(self):
        """Test the chi function.
        """
        answer = np.array([1., -1., 1., 1., 1.])
        assert np.allclose(chin(self.p, self.x, self.t, self.s), answer)

    def test_f2(self):
        """Test the f2 function.
        """
        chi_answer = np.array([1., -1., 1., 1., 1.])
        answer = chi_answer**2
        Q_answer = answer**2/(answer**2 + 1.0)
        assert np.allclose(f2(self.p, self.x, self.t, self.s), answer)
        assert np.allclose(f2(self.p, self.x, self.t, self.s, 1.0), Q_answer)

    def test_df2dp(self):
        """Test the derivative of the f2 function.
        """
        chi_answer = np.array([1., -1., 1., 1., 1.])
        d_answer = np.array([[1.0, 1.0, 1.0, 1.0, 1.0],
                             [0.0, 1.0, 0.0, -1.0, 0.0],
                             [1.0, 0.0, -1.0, 0.0, 1.0],
                             [0.0, -self.pi2, -self.pi, self.pi32, self.pipi]])
        answer = (-2.0*chi_answer/self.s)*d_answer
        Q_answer = answer * (1.0/(chi_answer**2 + 1.0)**2)
        assert np.allclose(df2dp(self.p, self.x, self.t, self.s), answer)
        assert np.allclose(df2dp(self.p, self.x, self.t, self.s, 1.0),
                           Q_answer)

    def test_d2f2dpdp(self):
        """Test the second derivative of the f2 function.
        """
        H = np.zeros((self.p.size, self.p.size, self.t.size),
                     dtype=self.p.dtype)
        chi = chin(self.p, self.x, self.t, self.s)
        d = dmdp(self.p, self.t)
        dd = d2mdpdp(self.p, self.t)
        for i in range(self.p.size):
            for j in range(self.p.size):
                H[i, j, :] = d[i, :] * d[j, :]
        f = -2*chi/self.s
        f2 = 2/self.s**2
        answer = f2*H + f*dd
        assert np.allclose(d2f2dpdp(self.p, self.x, self.t, self.s), answer)
        f = -2*chi/self.s * (1.0 / (chi**2 + 1.0)**2)
        f2 = 2*(1.0/self.s**2)*((1.0 - 3*chi**2)/(chi**2 + 1.0)**3)
        Q_answer = f2*H + f*dd
        assert np.allclose(d2f2dpdp(self.p, self.x, self.t, self.s, 1.0),
                           Q_answer)

    def test_obj(self):
        """Test the objective function.
        """
        answer = f2(self.p, self.x, self.t, self.s).sum()
        assert np.allclose(obj(self.p, self.x, self.t, self.s), answer)

    def test_dobj(self):
        """Test the derivative of the objective function.
        """
        answer = df2dp(self.p, self.x, self.t, self.s).sum(1)
        assert np.allclose(dobj(self.p, self.x, self.t, self.s), answer)

    def test_d2obj(self):
        """Test the second derivative of the objective function.
        """
        answer = d2f2dpdp(self.p, self.x, self.t, self.s).sum(2)
        assert np.allclose(d2obj(self.p, self.x, self.t, self.s), answer)

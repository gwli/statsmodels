"""
Test functions for models.robust.scale
"""

import numpy as np
from numpy.random import standard_normal
from numpy.testing import *
from scipy import stats

# Example from Section 5.5, Venables & Ripley (2002)

import statsmodels.robust.scale as scale
import statsmodels.robust.norms as rnorms

DECIMAL = 4
#TODO: Can replicate these tests using stackloss data and R if this
# data is a problem
class TestChem(object):
    def __init__(self):
        self.chem = np.array([2.20, 2.20, 2.4, 2.4, 2.5, 2.7, 2.8, 2.9, 3.03,
            3.03, 3.10, 3.37, 3.4, 3.4, 3.4, 3.5, 3.6, 3.7, 3.7, 3.7, 3.7,
            3.77, 5.28, 28.95])

    def test_mean(self):
        assert_almost_equal(np.mean(self.chem), 4.2804, DECIMAL)

    def test_median(self):
        assert_almost_equal(np.median(self.chem), 3.385, DECIMAL)

    def test_mad(self):
        assert_almost_equal(scale.mad(self.chem), 0.52632, DECIMAL)

    def test_huber_scale(self):
        assert_almost_equal(scale.huber(self.chem)[0], 3.20549, DECIMAL)

    def test_huber_location(self):
        assert_almost_equal(scale.huber(self.chem)[1], 0.67365, DECIMAL)

    def test_huber_huberT(self):
        n = scale.norms.HuberT()
        n.t = 1.5
        h = scale.Huber(norm=n)
        assert_almost_equal(scale.huber(self.chem)[0], h(self.chem)[0], DECIMAL)
        assert_almost_equal(scale.huber(self.chem)[1], h(self.chem)[1], DECIMAL)

    def test_huber_Hampel(self):
        hh = scale.Huber(norm=scale.norms.Hampel())
        assert_almost_equal(hh(self.chem)[0], 3.17434, DECIMAL)
        assert_almost_equal(hh(self.chem)[1], 0.66782, DECIMAL)

class TestMad(object):
    def __init__(self):
        np.random.seed(54321)
        self.X = standard_normal((40,10))

    def test_mad(self):
        m = scale.mad(self.X)
        assert_equal(m.shape, (10,))

    def test_mad_center(self):
        n = scale.mad(self.X, center=0)
        assert_equal(n.shape, (10,))

class TestMadAxes(object):
    def __init__(self):
        np.random.seed(54321)
        self.X = standard_normal((40,10,30))

    def test_axis0(self):
        m = scale.mad(self.X, axis=0)
        assert_equal(m.shape, (10,30))

    def test_axis1(self):
        m = scale.mad(self.X, axis=1)
        assert_equal(m.shape, (40,30))

    def test_axis2(self):
        m = scale.mad(self.X, axis=2)
        assert_equal(m.shape, (40,10))

    def test_axisneg1(self):
        m = scale.mad(self.X, axis=-1)
        assert_equal(m.shape, (40,10))

class TestHuber(object):
    def __init__(self):
        np.random.seed(54321)
        self.X = standard_normal((40,10))

    def basic_functionality(self):
        h = scale.Huber(maxiter=100)
        m, s = h(self.X)
        assert_equal(m.shape, (10,))

class TestHuberAxes(object):
    def __init__(self):
        np.random.seed(54321)
        self.X = standard_normal((40,10,30))
        self.h = scale.Huber(maxiter=1000, tol=1.0e-05)

    def test_default(self):
        m, s = self.h(self.X, axis=0)
        assert_equal(m.shape, (10,30))

    def test_axis1(self):
        m, s = self.h(self.X, axis=1)
        assert_equal(m.shape, (40,30))

    def test_axis2(self):
        m, s = self.h(self.X, axis=2)
        assert_equal(m.shape, (40,10))

    def test_axisneg1(self):
        m, s = self.h(self.X, axis=-1)
        assert_equal(m.shape, (40,10))


def test_scale_iter():
    # regression test, and approximately correct
    np.random.seed(54321)
    v = np.array([1, 0.5, 0.4])
    x = standard_normal((40,3)) * np.sqrt(v)
    x[:2] = [2, 2, 2]

    x = x[:,0]  # 1d only ?
    v = v[0]

    c = 4.685
    # c**2/6=3.6582041666667 shifts origin to zero BUG #1341
    meef_scale=lambda x:rnorms.TukeyBiweight().rho(x) + (c**2/6)
    scale_bias = 0.43684963023076195
    s = scale._scale_iter(x, meef_scale=meef_scale, scale_bias=scale_bias)
    assert_allclose(s, v, rtol=1e-1)
    assert_allclose(s, 1.0683298, rtol=1e-6)  # regression test number


def test_scale_trimmed_approx():
    scale_trimmed = scale.scale_trimmed # shorthand
    nobs = 500
    np.random.seed(965578)
    x = 2*np.random.randn(nobs)
    x[:10] = 60

    alpha = 0.2
    res = scale_trimmed(x, alpha)
    s = scale_trimmed(np.column_stack((x, 2*x)), alpha).scale
    assert_allclose(s, [2, 4], rtol=1e-1)
    s = scale_trimmed(np.column_stack((x, 2*x)).T, alpha, axis=1).scale
    assert_allclose(s, [2, 4], rtol=1e-1)
    s = scale_trimmed(np.column_stack((x, x)).T, alpha, axis=None).scale
    assert_allclose(s, [2], rtol=1e-1)
    s2 = scale_trimmed(np.column_stack((x, x)).ravel(), alpha).scale
    assert_allclose(s2, [2], rtol=1e-1)
    assert_allclose(s2, s, rtol=1e-1)
    s = scale_trimmed(x, alpha, distr=stats.t, distargs=(100,)).scale
    assert_allclose(s, [2], rtol=1e-1)


if __name__=="__main__":
    run_module_suite()

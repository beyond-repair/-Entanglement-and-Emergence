import numpy as np

from entanglement_emergence.spin_chain import (
    compare_regimes,
    metric_proxy_from_entropy,
)


def test_metric_proxy_finite_and_flat_for_affine():
    s = np.array([1.0, 2.0, 3.0, 4.0])
    dg = metric_proxy_from_entropy(s, epsilon=1.0)
    assert dg.shape == s.shape
    assert np.all(np.isfinite(dg))
    assert np.allclose(dg, 0.0, atol=1e-12)


def test_metric_proxy_nonzero_for_curved():
    s = np.array([0.0, 1.0, 0.0, 1.0, 0.0])
    dg = metric_proxy_from_entropy(s, epsilon=2.0)
    assert np.any(np.abs(dg) > 0.0)
    assert np.all(np.isfinite(dg))


def test_compare_regimes_high_entropy_smoother_metric():
    results = compare_regimes(n=8, seed=0)
    assert results["high"].mean_entropy > results["low"].mean_entropy
    # Inhomogeneous J → more disordered δg proxy (paper §3.3 narrative)
    assert results["high"].metric_rms < results["low"].metric_rms
    assert np.all(np.isfinite(results["high"].metric_proxy))
    assert np.all(np.isfinite(results["low"].metric_proxy))

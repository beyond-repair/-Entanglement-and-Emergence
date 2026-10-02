import numpy as np
import pytest

from entanglement_emergence.spin_chain import (
    bipartite_entropy,
    build_hamiltonian,
    entropy_profile,
    ground_state,
)


def test_product_state_zero_entropy():
    # |0000> has S=0 across every cut
    n = 4
    psi = np.zeros(2**n, dtype=np.complex128)
    psi[0] = 1.0
    for cut in range(1, n):
        assert bipartite_entropy(psi, n, cut) == pytest.approx(0.0, abs=1e-12)


def test_bell_pair_max_entropy():
    # Two-qubit Bell state: S = 1 bit
    psi = np.array([1, 0, 0, 1], dtype=np.complex128) / np.sqrt(2)
    s = bipartite_entropy(psi, 2, 1)
    assert 0.0 <= s <= 1.0 + 1e-12
    assert s == pytest.approx(1.0, abs=1e-10)


def test_entropy_bounds_ground_state():
    n = 5
    h = build_hamiltonian(n, np.ones(n - 1))
    _, psi = ground_state(h)
    profile = entropy_profile(psi, n)
    assert profile.shape == (n - 1,)
    for cut, s in enumerate(profile, start=1):
        max_s = float(min(cut, n - cut))  # log2(dim_A) with qubits
        assert 0.0 - 1e-12 <= s <= max_s + 1e-9

import numpy as np
import pytest

from entanglement_emergence.spin_chain import build_hamiltonian, ground_state


def test_hamiltonian_shape_and_hermitian():
    n = 4
    h = build_hamiltonian(n, [1.0, 1.0, 1.0])
    assert h.shape == (16, 16)
    assert np.allclose(h, h.conj().T)


def test_hamiltonian_rejects_bad_couplings():
    with pytest.raises(ValueError):
        build_hamiltonian(3, [1.0])


def test_ground_state_energy_real_and_normalized():
    h = build_hamiltonian(3, [0.5, 0.5])
    e0, psi = ground_state(h)
    assert np.isfinite(e0)
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-10

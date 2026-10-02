"""
1D spin-chain numerical toy (paper §3.3).

Hamiltonian (nearest-neighbor XX + ZZ, optional local Z fields):
    H = -Σ_i J_i (σ^x_i σ^x_{i+1} + σ^z_i σ^z_{i+1}) - Σ_i h_i σ^z_i

Emergent-metric proxy (1D form of g ~ η + ε ∇∇S):
    δg_i ∝ discrete second difference of bipartite von Neumann entropy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

# Pauli matrices
_SX = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
_I2 = np.eye(2, dtype=np.complex128)


def _embed(op: np.ndarray, site: int, n: int) -> np.ndarray:
    """Embed a single-site operator at `site` in an n-qubit Hilbert space."""
    mats = [_I2] * n
    mats[site] = op
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out


def _embed_two(op_a: np.ndarray, op_b: np.ndarray, i: int, j: int, n: int) -> np.ndarray:
    """Embed op_a ⊗ op_b on sites i, j (i < j)."""
    mats = [_I2] * n
    mats[i] = op_a
    mats[j] = op_b
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out


def build_hamiltonian(
    n: int,
    couplings: Sequence[float],
    fields: Sequence[float] | None = None,
) -> np.ndarray:
    """
    Build H = -Σ J_i (X_i X_{i+1} + Z_i Z_{i+1}) - Σ h_i Z_i for an open 1D chain.

    Parameters
    ----------
    n : int
        Number of qubits (sites). Must be >= 2.
    couplings : sequence of length n-1
        Nearest-neighbor J_i values.
    fields : optional sequence of length n
        Local Z-field strengths h_i (default: all zero).
    """
    if n < 2:
        raise ValueError("n must be >= 2")
    couplings = np.asarray(couplings, dtype=float)
    if couplings.shape != (n - 1,):
        raise ValueError(f"couplings must have length n-1={n - 1}, got {couplings.shape}")

    dim = 2**n
    h_mat = np.zeros((dim, dim), dtype=np.complex128)
    for i, j_coup in enumerate(couplings):
        xx = _embed_two(_SX, _SX, i, i + 1, n)
        zz = _embed_two(_SZ, _SZ, i, i + 1, n)
        h_mat -= j_coup * (xx + zz)

    if fields is not None:
        fields_arr = np.asarray(fields, dtype=float)
        if fields_arr.shape != (n,):
            raise ValueError(f"fields must have length n={n}, got {fields_arr.shape}")
        for i, hi in enumerate(fields_arr):
            if hi != 0.0:
                h_mat -= hi * _embed(_SZ, i, n)
    return h_mat


def ground_state(hamiltonian: np.ndarray) -> tuple[float, np.ndarray]:
    """Exact diagonalization: return (E0, |ψ0>) for Hermitian H."""
    evals, evecs = np.linalg.eigh(hamiltonian)
    return float(evals[0].real), evecs[:, 0].astype(np.complex128)


def bipartite_entropy(psi: np.ndarray, n: int, cut: int) -> float:
    """
    Von Neumann entanglement entropy S = -Tr(ρ_A log2 ρ_A) across a cut
    after `cut` sites (1 <= cut <= n-1). Uses base-2 so max is cut bits.
    """
    if not (1 <= cut <= n - 1):
        raise ValueError(f"cut must be in [1, n-1], got {cut}")
    psi = np.asarray(psi, dtype=np.complex128).reshape(-1)
    if psi.shape[0] != 2**n:
        raise ValueError(f"psi length {psi.shape[0]} != 2**n={2**n}")

    dim_a = 2**cut
    dim_b = 2 ** (n - cut)
    mat = psi.reshape(dim_a, dim_b)
    singular = np.linalg.svd(mat, compute_uv=False)
    probs = singular.real**2
    probs = probs[probs > 1e-15]
    return float(-np.sum(probs * np.log2(probs)))


def entropy_profile(psi: np.ndarray, n: int) -> np.ndarray:
    """Bipartite entropy for every bond cut 1..n-1."""
    return np.array([bipartite_entropy(psi, n, c) for c in range(1, n)], dtype=float)


def metric_proxy_from_entropy(entropy: Sequence[float], epsilon: float = 1.0) -> np.ndarray:
    """
    Discrete 1D metric perturbation δg_i = ε * Δ² S_i.

    Pads endpoints with nearest-neighbor values so length matches `entropy`.
    Finite and zero when S is affine (smooth-flat proxy).
    """
    s = np.asarray(entropy, dtype=float)
    if s.ndim != 1 or s.size < 1:
        raise ValueError("entropy must be a non-empty 1D array")
    if s.size == 1:
        return np.array([0.0])
    if s.size == 2:
        return np.zeros(2)

    interior = s[2:] - 2.0 * s[1:-1] + s[:-2]
    dg = np.empty_like(s)
    dg[0] = interior[0]
    dg[1:-1] = interior
    dg[-1] = interior[-1]
    return epsilon * dg


@dataclass(frozen=True)
class RegimeResult:
    name: str
    n: int
    couplings: np.ndarray
    fields: np.ndarray
    energy: float
    entropies: np.ndarray
    mean_entropy: float
    metric_proxy: np.ndarray
    metric_rms: float
    metric_max_abs: float


def _run_regime(
    name: str,
    n: int,
    couplings: Iterable[float],
    fields: Iterable[float] | None,
    epsilon: float,
) -> RegimeResult:
    j = np.asarray(list(couplings), dtype=float)
    h_fields = np.zeros(n) if fields is None else np.asarray(list(fields), dtype=float)
    ham = build_hamiltonian(n, j, fields=h_fields)
    e0, psi = ground_state(ham)
    s = entropy_profile(psi, n)
    dg = metric_proxy_from_entropy(s, epsilon=epsilon)
    return RegimeResult(
        name=name,
        n=n,
        couplings=j,
        fields=h_fields,
        energy=e0,
        entropies=s,
        mean_entropy=float(np.mean(s)),
        metric_proxy=dg,
        metric_rms=float(np.sqrt(np.mean(dg**2))),
        metric_max_abs=float(np.max(np.abs(dg))),
    )


def compare_regimes(
    n: int = 8,
    epsilon: float = 1.0,
    seed: int = 0,
) -> dict[str, RegimeResult]:
    """
    High-entanglement (uniform J) vs low/disordered-entanglement (inhomogeneous J).

    Uniform couplings yield a smoother entropy profile; inhomogeneous J yields
    lower mean bipartite entropy and a more disordered δg proxy — the §3.3 sketch.
    """
    if n < 2 or n > 12:
        raise ValueError("n must be in [2, 12] for exact diagonalization sketch")

    rng = np.random.default_rng(seed)
    high_j = np.ones(n - 1)
    # Inhomogeneous couplings: some near-zero bonds suppress entanglement and
    # roughen the entropy profile (disordered metric proxy).
    low_j = rng.uniform(0.05, 2.0, size=n - 1)

    return {
        "high": _run_regime("high_entanglement", n, high_j, None, epsilon),
        "low": _run_regime("low_entanglement", n, low_j, None, epsilon),
    }


def results_to_rows(results: dict[str, RegimeResult]) -> list[dict[str, float | str | int]]:
    """Flatten regime results into CSV-friendly row dicts."""
    rows: list[dict[str, float | str | int]] = []
    for key, r in results.items():
        rows.append(
            {
                "regime": key,
                "n": r.n,
                "mean_J": float(np.mean(r.couplings)),
                "std_J": float(np.std(r.couplings)),
                "E0": r.energy,
                "mean_S": r.mean_entropy,
                "metric_rms": r.metric_rms,
                "metric_max_abs": r.metric_max_abs,
            }
        )
    return rows

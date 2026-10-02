"""Claim-0 1D spin-chain toy for emergent-metric / entanglement essay."""

from .spin_chain import (
    build_hamiltonian,
    ground_state,
    bipartite_entropy,
    entropy_profile,
    metric_proxy_from_entropy,
    compare_regimes,
)

__version__ = "0.1.0"
__all__ = [
    "build_hamiltonian",
    "ground_state",
    "bipartite_entropy",
    "entropy_profile",
    "metric_proxy_from_entropy",
    "compare_regimes",
    "__version__",
]

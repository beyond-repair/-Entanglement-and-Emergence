"""CLI demo: high vs low entanglement regimes + optional figure."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from .spin_chain import compare_regimes, results_to_rows


def _maybe_plot(results: dict, out_path: Path) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    high = results["high"]
    low = results["low"]
    cuts = np.arange(1, high.n)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    axes[0].plot(cuts, high.entropies, "o-", label="high entanglement (uniform J)")
    axes[0].plot(cuts, low.entropies, "s--", label="low/disordered (inhomogeneous J)")
    axes[0].set_xlabel("cut after site")
    axes[0].set_ylabel(r"$S$ (bits)")
    axes[0].set_title("Bipartite entanglement entropy")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(cuts, high.metric_proxy, "o-", label="high")
    axes[1].plot(cuts, low.metric_proxy, "s--", label="low")
    axes[1].set_xlabel("cut after site")
    axes[1].set_ylabel(r"$\delta g$ proxy ($\varepsilon\,\Delta^2 S$)")
    axes[1].set_title("1D metric perturbation proxy")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle("Claim-0 toy: entanglement vs emergent-metric proxy (1D spin chain)")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return True


def run_demo(
    n: int = 8,
    epsilon: float = 1.0,
    seed: int = 0,
    csv_path: Path | None = None,
    figure_path: Path | None = None,
) -> int:
    results = compare_regimes(n=n, epsilon=epsilon, seed=seed)
    rows = results_to_rows(results)

    print("Entanglement-and-Emergence — Claim-0 1D spin-chain toy")
    print(f"N={n} qubits | exact diagonalization | ε={epsilon} | seed={seed}")
    print()
    header = f"{'regime':<8} {'mean_J':>8} {'E0':>12} {'mean_S':>8} {'δg_rms':>10} {'|δg|_max':>10}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['regime']:<8} {row['mean_J']:8.4f} {row['E0']:12.6f} "
            f"{row['mean_S']:8.4f} {row['metric_rms']:10.6f} {row['metric_max_abs']:10.6f}"
        )
    print()
    high_s = results["high"].mean_entropy
    low_s = results["low"].mean_entropy
    print(
        f"Sanity: high-entanglement mean S ({high_s:.4f}) "
        f"{'>' if high_s > low_s else '<='} low-entanglement mean S ({low_s:.4f})."
    )
    print(
        "Note: δg is a discrete 1D proxy from entropy curvature — not a measured spacetime metric."
    )

    if csv_path is not None:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote CSV: {csv_path}")

    if figure_path is not None:
        if _maybe_plot(results, figure_path):
            print(f"Wrote figure: {figure_path}")
        else:
            print("matplotlib unavailable; skipped figure generation.")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Claim-0 demo: 1D spin chain entanglement → metric proxy"
    )
    parser.add_argument("-n", type=int, default=8, help="number of qubits (2..12)")
    parser.add_argument("--epsilon", type=float, default=1.0, help="metric proxy scale ε")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for disordered J")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/regime_comparison.csv"),
        help="output CSV path (use '' to skip)",
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=Path("figures/metric_entanglement.png"),
        help="optional PNG path",
    )
    parser.add_argument("--no-csv", action="store_true", help="skip CSV write")
    parser.add_argument("--no-figure", action="store_true", help="skip figure write")
    args = parser.parse_args(argv)

    csv_path = None if args.no_csv or str(args.csv) == "" else args.csv
    figure_path = None if args.no_figure else args.figure
    return run_demo(
        n=args.n,
        epsilon=args.epsilon,
        seed=args.seed,
        csv_path=csv_path,
        figure_path=figure_path,
    )


if __name__ == "__main__":
    sys.exit(main())

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_py_exit_zero(tmp_path):
    csv = tmp_path / "out.csv"
    fig = tmp_path / "fig.png"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "main.py"),
            "-n",
            "4",
            "--csv",
            str(csv),
            "--figure",
            str(fig),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "Claim-0" in proc.stdout
    assert csv.is_file()


def test_module_entrypoint_exit_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "entanglement_emergence", "-n", "4", "--no-csv", "--no-figure"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout

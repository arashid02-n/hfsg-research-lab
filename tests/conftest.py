"""Shared pytest fixtures for the Research Lab test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

LAB_ROOT = Path(__file__).resolve().parents[1]
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))


@pytest.fixture(scope="module")
def gate2a_stores():
    """The two REAL Gate 2A recorded runs (integration proof + identical re-run)."""
    a_dir = LAB_ROOT / "runs" / "min_integration_proof"
    b_dir = LAB_ROOT / "runs" / "repro_B"
    assert (a_dir / "simulation_summary.parquet").is_file(), (
        "Gate 2A proof store missing; run proof/run_proofs.py first"
    )
    assert (b_dir / "simulation_summary.parquet").is_file()
    return a_dir, b_dir
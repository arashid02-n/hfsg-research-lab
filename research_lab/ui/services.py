"""Lab services singleton provider (adapter, run store, comparator).

Module-level singletons keep instantiation cheap (config load happens once).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from ..adapter import ResearchLabAdapter
from ..reproducibility import ReproducibilityComparator
from ..result_store import RunStore

LAB_ROOT = Path(__file__).resolve().parents[2]
RESULTS_ROOT = LAB_ROOT / "results"
EXPORTS_DIR = RESULTS_ROOT / "exports"
VALIDATION_EVIDENCE_DIR = RESULTS_ROOT / "validation_evidence"


@lru_cache(maxsize=1)
def get_adapter() -> ResearchLabAdapter:
    return ResearchLabAdapter()


@lru_cache(maxsize=1)
def get_store() -> RunStore:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    return RunStore(RESULTS_ROOT)


@lru_cache(maxsize=1)
def get_comparator() -> ReproducibilityComparator:
    return ReproducibilityComparator(get_adapter(), get_store())


def ensure_export_dirs() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
"""Lab services singleton provider (adapter, run store, comparator).

Module-level singletons keep instantiation cheap (config load happens once).
"""

from __future__ import annotations

from functools import lru_cache, wraps
from pathlib import Path
from typing import Callable, Optional

import streamlit as st

from ..adapter import ResearchLabAdapter
from ..core import CoreNotFoundError, resolve_core_dir
from ..identity import verified_identity
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


def core_identity() -> dict:
    return verified_identity()


def core_blocked_message() -> Optional[str]:
    """Return a friendly message when live runs must be blocked, else None.

    A live run is blocked when (a) no Core could be resolved, or (b) the
    resolved Core fails the identity check (version / baseline / frozen commit
    / modified tracked files). The message is user-facing, never a traceback.
    """
    if resolve_core_dir() is None:
        return (
            "HFSG Core not found. Place the approved Core in `hfsg_core/`, "
            "set HFSG_CORE_DIR, or select it on the About / System Information "
            "page."
        )
    identity = verified_identity()
    if not identity.get("core_integrity_ok"):
        return (
            "LIVE RUN BLOCKED — incompatible HFSG Core detected. "
            "See the About / System Information page for details."
        )
    return None


def require_core(render_fn: Callable) -> Callable:
    """Decorate a page renderer so a missing/incompatible Core is surfaced
    as a friendly message and blocks the page's live-run capability."""

    @wraps(render_fn)
    def wrapper(*args, **kwargs):
        try:
            blocked = core_blocked_message()
            if blocked is not None:
                st.error(f"**{blocked}**")
                return
            return render_fn(*args, **kwargs)
        except CoreNotFoundError:
            st.error(
                "**HFSG Core not found.** Configure the Core location on the "
                "About / System Information page, then retry."
            )
            return

    return wrapper
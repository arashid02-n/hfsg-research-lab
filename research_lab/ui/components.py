"""Shared UI building blocks.

All main pages render the identity banner and the mandatory disclaimer:
    "SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL PATIENT DATA —
     NOT CLINICALLY VALIDATED"
plus RESEARCH / EDUCATION USE and the Live-Demo vs Validated-Release split.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from ..identity import verified_identity
from .services import get_store
from .state import ensure_state

DISCLAIMER = (
    "SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL PATIENT DATA — "
    "NOT CLINICALLY VALIDATED"
)


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def disclaimer() -> None:
    st.warning(f"**{DISCLAIMER}** — RESEARCH / EDUCATION USE ONLY.")


def rapport() -> None:
    """Identity banner with live verification against the frozen repo."""
    identity = verified_identity()
    ok = bool(identity["core_integrity_ok"])
    suffix = "  — verified." if ok else "  — **UNVERIFIED — STOP**"
    st.info(f"**HFSG Core lineage:** {identity['statement']}{suffix}")
    if not ok:
        with st.expander("Lineage verification details"):
            st.json(identity)


def status_badge(status: str) -> str:
    status = (status or "UNKNOWN").upper()
    palette = {
        "VALIDATED": ("VALIDATED", ":green"),
        "VALIDATION": ("VALIDATION", ":orange"),
        "RUNNING": ("RUNNING", ":blue"),
        "UNKNOWN": ("UNKNOWN", ":gray"),
    }
    label, color = palette.get(status, (status, ":gray"))
    return f"{color}[**{label}**]"


def match_badge(matched: bool) -> str:
    return ":green[**MATCH**]" if matched else ":red[**FAIL**]"


def fmt_int(value: Optional[Any]) -> str:
    if value is None:
        return "—"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def fmt_float(value: Optional[Any], places: int = 4) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{places}f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_bytes(value: Optional[int]) -> str:
    if not value:
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def select_run(prefix: str = "", key: str = "selected_run") -> Optional[Dict[str, Any]]:
    ensure_state()
    store = get_store()
    runs = store.list_runs()
    if not runs:
        st.info("No recorded runs yet. Run a simulation first.")
        return None

    def display(r: Dict[str, Any]) -> str:
        patients = fmt_int(r.get("patients")) or "?"
        return f"{r['label']}  [{r['scenario_id']}, {patients} patients, {r['validation_status']}]"

    options = [display(r) for r in runs]
    index = 0
    current = st.session_state.get(key)
    if current:
        for i, r in enumerate(runs):
            if r["label"] == current:
                index = i
                break
    chosen = st.selectbox(
        "Recorded run", options, index=index, key=f"{prefix}run_select"
    )
    label = chosen.split("  [")[0]
    st.session_state[key] = label
    return next(r for r in runs if r["label"] == label)


def runs_table(runs: List[Dict[str, Any]]) -> None:
    rows = []
    for r in runs:
        rows.append(
            {
                "label": r["label"],
                "scenario_id": r["scenario_id"],
                "patients": r["patients"],
                "events": r["events"],
                "status": r["validation_status"],
                "master_seed": r["master_seed"],
                "config_hash": (r["config_hash"] or "—")[:16] + "…",
            }
        )
    if not rows:
        st.info("No recorded runs.")
        return
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
"""Scenario Comparison page.

Compares recorded runs side by side (totals, census paths, run-level
summaries). The Core's own `scenario_comparison.csv` is shown per run.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..services import get_store
from ..state import ensure_state
from ..components import (
    disclaimer,
    fmt_float,
    fmt_int,
    page_header,
    rapport,
)

CENSUS_COLS = ["ed_census", "specialty_census", "general_census", "icu_census"]


def render() -> None:
    ensure_state()
    page_header(
        "Scenario Comparison",
        "Side-by-side comparison of recorded scenario batches.",
    )
    rapport()
    store = get_store()
    runs = store.list_runs()
    if not runs:
        st.info("No recorded runs yet.")
        disclaimer()
        return

    labels = st.multiselect(
        "Runs to compare",
        options=[r["label"] for r in runs],
        default=[r["label"] for r in runs][:2],
    )
    if not labels:
        st.info("Select at least one run.")
        disclaimer()
        return

    rows = []
    for r in runs:
        if r["label"] not in labels:
            continue
        summary = store.summary(r["label"])
        if summary is None or summary.empty:
            continue
        totals = summary[["total_patients", "total_events"]].sum()
        row = summary.iloc[0]
        rows.append(
            {
                "run": r["label"],
                "scenario": r["scenario_id"],
                "status": r["validation_status"],
                "patients": int(totals["total_patients"]),
                "events": int(totals["total_events"]),
                "mean_active_census": round(float(row["mean_active_census"]), 1),
                "max_active_census": int(row["max_active_census"]),
                "max_abs_mbe": float(row["max_abs_mbe"]),
                "seed": r["master_seed"],
            }
        )
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.warning("Selected runs have no readable summary.")
        disclaimer()
        return

    st.subheader("Census comparison (per chosen unit)")
    unit = st.selectbox("Unit", CENSUS_COLS, format_func=lambda c: c.replace("_census", ""))
    frames = {}
    for label in labels:
        agg = store.aggregate(label)
        if agg.empty:
            continue
        frames[f"{label} [{agg['scenario_id'].iloc[0]}]"] = agg.set_index("hour")[unit]
    if frames:
        combined = pd.concat(frames, axis=1).ffill()
        st.line_chart(combined, width="stretch")

    st.subheader("Core scenario_comparison.csv (per run)")
    reports = []
    for label in labels:
        path = store.out_dir(label) / "scenario_comparison.csv"
        if path.is_file():
            df = pd.read_csv(path)
            reports.append((label, df))
    for label, df in reports:
        with st.expander(label):
            st.dataframe(df, width="stretch", hide_index=True)

    disclaimer()
"""Results Dashboard page — live data from the recorded Result Store.

All figures are read from the frozen Core's generated Parquet outputs for the
selected run; nothing here is estimated or mocked."
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..services import get_adapter, get_store
from ..state import ensure_state
from ..components import (
    disclaimer,
    fmt_float,
    fmt_int,
    page_header,
    rapport,
    select_run,
    status_badge,
)

CENSUS_COLS = ["ed_census", "specialty_census", "general_census", "icu_census"]
CAPACITY_FIELDS = {"ed_census": "ed", "specialty_census": "specialty", "general_census": "general", "icu_census": "icu"}


def render() -> None:
    ensure_state()
    page_header(
        "Results Dashboard",
        "Aggregate-flow results of one validated simulated run.",
    )
    rapport()
    store = get_store()
    run = select_run()
    if run is None:
        disclaimer()
        return

    summary = store.summary(run["label"])
    if summary is not None and not summary.empty:
        row = summary.iloc[0]
        agg = store.aggregate(run["label"])
        events = store.events(run["label"])
        _headline(row, run["validation_status"])
        _census_chart(agg)
        _flows_chart(agg)
        _occupancy_table(agg)
        _events_chart(events)
        _runs_table(summary)
    else:
        st.error("Simulation summary unavailable for this run.")

    disclaimer()


def _headline(row: pd.Series, status: str) -> None:
    values = {
        "total_patients": row["total_patients"],
        "total_events": row["total_events"],
        "total_arrivals": row["total_arrivals"],
        "total_transfers": row["total_transfers"],
        "total_discharges": row["total_discharges"],
        "total_deaths": row["total_deaths"],
        "mean_active_census": row["mean_active_census"],
        "max_active_census": row["max_active_census"],
        "max_abs_mbe": row["max_abs_mbe"],
        "reconciliation_issues": row["reconciliation_issues"],
    }
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Patients", fmt_int(values["total_patients"]))
    c2.metric("Events", fmt_int(values["total_events"]))
    c3.metric("Mean active census", fmt_float(values["mean_active_census"], 1))
    c4.metric("Max active census", fmt_int(values["max_active_census"]))
    c5.metric("Status", status_badge(status))
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Arrivals", fmt_int(values["total_arrivals"]))
    c2.metric("Transfers", fmt_int(values["total_transfers"]))
    c3.metric("Discharges", fmt_int(values["total_discharges"]))
    c4.metric("Deaths", fmt_int(values["total_deaths"]))
    c5.metric(
        "Max |MBE|",
        f"{values['max_abs_mbe']}" if values.get("max_abs_mbe") is not None else "—",
    )
    with st.expander("Reconciliation / MBE details"):
        st.markdown(
            f"**reconciliation_issues:** {values['reconciliation_issues']} — "
            "the frozen-Core validation suite verifies no mass-balance issue "
            "for a VALIDATED run."
        )


def _census_chart(agg: pd.DataFrame) -> None:
    st.subheader("Census by unit over time")
    if agg.empty:
        st.info("No aggregate rows.")
        return
    chart = agg.set_index("hour")[list(CENSUS_COLS)]
    st.line_chart(chart, width="stretch")


def _flows_chart(agg: pd.DataFrame) -> None:
    st.subheader("ED arrivals: drawn vs accepted vs unmet")
    if agg.empty:
        return
    cols = ["arrivals_drawn", "arrivals_accepted", "unmet_arrivals"]
    chart = agg.set_index("hour")[cols] if all(c in agg.columns for c in cols) else None
    if chart is None:
        st.caption("flow columns not present for this run.")
        return
    st.area_chart(chart, width="stretch")


def _occupancy_table(agg: pd.DataFrame) -> None:
    st.subheader("Peak occupancy vs configured capacity")
    adapter = get_adapter()
    capacities = adapter.frozen_defaults()["capacities"]
    rows = []
    for stock_field, unit in CAPACITY_FIELDS.items():
        cap = capacities.get(unit)
        peak = float(agg[stock_field].max()) if not agg.empty else 0.0
        occupancy = (peak / cap * 100.0) if cap else float("nan")
        rows.append(
            {
                "unit": unit,
                "capacity": cap,
                "peak_census": int(peak),
                "occupancy_at_peak": f"{occupancy:.1f}%",
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _events_chart(events: pd.DataFrame) -> None:
    st.subheader("Events by type")
    if events.empty:
        st.info("No patient events recorded.")
        return
    counts = (
        events["event_type"]
        .value_counts()
        .rename_axis("event_type")
        .rename("count")
        .reset_index()
    )
    st.dataframe(counts, width="stretch", hide_index=True)
    st.bar_chart(counts, x="event_type", y="count", width="stretch")


def _runs_table(summary: pd.DataFrame) -> None:
    st.subheader("Per-run summary (this scenario batch)")
    columns = [
        "run_index",
        "total_patients",
        "total_events",
        "total_arrivals",
        "total_transfers",
        "total_discharges",
        "total_deaths",
        "max_abs_mbe",
        "master_seed",
        "child_seed",
        "configuration_hash",
    ]
    present = [c for c in columns if c in summary.columns]
    st.dataframe(summary[present], width="stretch", hide_index=True)
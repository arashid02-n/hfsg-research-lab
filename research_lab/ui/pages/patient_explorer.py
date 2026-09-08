"""Synthetic Patient Explorer page.

Filters the REAL synthetic patient records of a selected validated run and
drills into a single patient's event timeline. All data comes from the frozen
Core's generated Parquet; nothing is fabricated in the UI.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..services import get_store
from ..state import ensure_state
from ..components import (
    disclaimer,
    fmt_int,
    page_header,
    rapport,
    select_run,
)


def render() -> None:
    ensure_state()
    page_header(
        "Synthetic Patient Explorer",
        "Drill into synthetic patient-level records of a validated run.",
    )
    rapport()
    store = get_store()
    run = select_run(key="selected_patient_run")
    if run is None:
        disclaimer()
        return

    patients = store.patients(run["label"])
    st.info(
        f"Loaded {fmt_int(len(patients))} patient records. Filtering and "
        "display are capped to 2,000 rows at a time; the full dataset is "
        "never loaded into the UI at once."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        pid_filter = st.text_input("Patient ID contains", value="")
    with c2:
        entry_type = st.selectbox("Entry type", ["ALL"] + sorted(patients["entry_type"].unique().tolist()) if not patients.empty else ["ALL"])
    with c3:
        options = sorted(patients["initial_unit"].unique().tolist()) if not patients.empty else []
        unit = st.selectbox("Initial unit", ["ALL"] + options)
    with c4:
        age_options = sorted(patients["age_group"].unique().tolist()) if not patients.empty else []
        age = st.selectbox("Age group", ["ALL"] + age_options)
    with c5:
        sev_options = sorted(patients["severity_level"].unique().tolist()) if not patients.empty else []
        sev = st.selectbox("Severity", ["ALL"] + sev_options)

    view = patients
    if pid_filter:
        view = view[view["patient_id"].astype(str).str.contains(pid_filter, case=False)]
    if entry_type != "ALL":
        view = view[view["entry_type"] == entry_type]
    if unit != "ALL":
        view = view[view["initial_unit"] == unit]
    if age != "ALL":
        view = view[view["age_group"] == age]
    if sev != "ALL":
        view = view[view["severity_level"] == sev]

    st.markdown(f"**{fmt_int(len(view))} records match** the current filters.")
    st.dataframe(view.head(2000), width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("Patient event timeline")
    if patients.empty:
        st.info("No patient records to explore.")
        disclaimer()
        return
    if pid_filter:
        matching_ids = patients[patients["patient_id"].astype(str).str.contains(pid_filter, case=False)]["patient_id"].unique().tolist()
    else:
        matching_ids = patients["patient_id"].unique().tolist()[:200]
    selected_patient = st.selectbox("Patient", matching_ids[:200])
    events = store.events(run["label"])
    patient_events = events[events["patient_id"] == selected_patient].sort_values("event_hour")
    st.markdown(f"**Patient {selected_patient}:** {fmt_int(len(patient_events))} events.")
    st.dataframe(
        patient_events[["event_hour", "event_type", "from_unit", "to_unit", "quota_flow", "event_id"]],
        width="stretch",
        hide_index=True,
    )
    disclaimer()
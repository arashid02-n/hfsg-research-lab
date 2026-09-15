"""Home page."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from ...core import core_released_manifest
from ..state import ensure_state, set_page
from ..components import disclaimer, page_header, rapport, status_badge
from ..services import get_store


def _released_manifest() -> Path | None:
    return core_released_manifest()


def render() -> None:
    ensure_state()
    page_header(
        "HFSG Research Lab",
        "Synthetic hospital-flow scenario generation — research / education "
        "instrument (non-clinical).",
    )
    rapport()
    disclaimer()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Live Demo")
        st.markdown(
            "Runs the **frozen HFSG Core** on demand from this Lab: scenario "
            "selection, CUSTOM multipliers, master seed, horizon, target "
            "patient volume, certification and reproducibility comparison. "
            "Each Live Demo Result Store is validated with the Core's own "
            "validation suite before it may be labelled VALIDATED."
        )
        if st.button("Open Academic Quick Demo", key="home_demo"):
            set_page("Academic Quick Demo")
            st.rerun()
        if st.button("Open Scenario Builder", key="home_builder"):
            set_page("Scenario Builder")
            st.rerun()

    with col_right:
        st.subheader("Validated Phase 1 Release (read-only)")
        manifest_path = _released_manifest()
        if manifest_path is not None:
            with manifest_path.open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)
            st.info(
                "The Phase 1 Released Dataset exists at the frozen Core's "
                "`data/output/step9` and is only READ here — never written."
            )
            fields = [
                ("Dataset", manifest.get("dataset_id")),
                ("Scenarios", manifest.get("pack")),
                ("Patients", manifest.get("total_patients")),
                ("Events", manifest.get("total_events")),
                ("Status", status_badge(manifest.get("validation_status"))),
            ]
            for label, value in fields:
                st.markdown(f"**{label}:** {value}")
        else:
            st.info(
                "The Phase 1 release manifest is not included in this "
                "Academic Demo package: the Master Dataset (Core "
                "`data/output/step9`) is excluded by design at the "
                "distribution boundary. The frozen Core still validates this "
                "Lab's own runs independently."
            )

    st.subheader("Recorded Lab runs")
    store = get_store()
    runs = store.list_runs()
    if runs:
        df = pd.DataFrame(
            [
                {
                    "label": r["label"],
                    "scenario": r["scenario_id"],
                    "status": r["validation_status"],
                    "patients": r["patients"],
                    "events": r["events"],
                    "seed": r["master_seed"],
                    "created": r["created_at"],
                }
                for r in runs
            ]
        )
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No recorded runs yet — run an Academic Quick Demo to begin.")

    st.markdown("---")
    st.caption(
        "This Lab layers on the frozen HFSG Core (v0.6.0) via a thin adapter "
        "with NO model logic. No Core repository, configuration or validation "
        "behaviour is modified."
    )
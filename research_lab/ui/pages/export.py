"""Export / Run Summary page.

Produces a portable zip of a recorded run's Result Store (deterministic file
ordering) and shows the exact job inputs for provenance.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from ..services import EXPORTS_DIR, get_store
from ..state import ensure_state
from ..components import (
    disclaimer,
    fmt_bytes,
    fmt_int,
    page_header,
    rapport,
    select_run,
)


def render() -> None:
    ensure_state()
    page_header(
        "Export / Run Summary",
        "Inspect the exact recorded job inputs and export the Result Store.",
    )
    rapport()
    store = get_store()
    run = select_run(key="selected_export_run")
    if run is None:
        disclaimer()
        return

    summary = store.summary(run["label"])
    if summary is not None and not summary.empty:
        st.subheader("Run summary")
        cols = [
            "run_index",
            "total_patients",
            "total_events",
            "total_arrivals",
            "total_transfers",
            "total_discharges",
            "total_deaths",
            "max_abs_mbe",
            "configuration_hash",
        ]
        present = [c for c in cols if c in summary.columns]
        st.dataframe(summary[present], width="stretch", hide_index=True)

    st.subheader("Exact job inputs (job_spec.json)")
    spec = store.job_spec(run["label"])
    if spec:
        display = dict(spec)
        display.pop("frozen_config_source", None)
        st.json(display)
    else:
        st.warning("No job_spec.json in this Result Store.")

    st.subheader("Dataset manifest (dataset_manifest.json)")
    manifest = store.dataset_manifest(run["label"])
    if manifest:
        st.json(manifest)
    else:
        st.warning("No dataset_manifest.json in this Result Store.")

    st.subheader("Export")
    out_dir = store.out_dir(run["label"])
    size = sum(p.stat().st_size for p in out_dir.rglob("*") if p.is_file())
    st.markdown(
        f"Result Store: `{out_dir}` — total {fmt_bytes(size)} across "
        f"{len([p for p in out_dir.rglob('*') if p.is_file()])} files."
    )

    if st.button("Build export zip", key="exp_build"):
        with st.spinner("Bundling the Result Store into a zip..."):
            target = store.export_zip(run["label"], EXPORTS_DIR)
        st.success(f"Export ready: `{target}`")
        if target.stat().st_size <= 100 * 1024 * 1024:
            st.download_button(
                "Download export zip",
                data=target.read_bytes(),
                file_name=target.name,
                mime="application/zip",
                key="exp_download",
            )
        else:
            st.caption(
                "Export is large (>100 MB); retrieve it from the path above "
                "rather than downloading through the browser."
            )

    with st.expander("Frozen-Core validation report (raw JSON)"):
        report = store.validation_report(run["label"])
        if report:
            st.json(report)
    disclaimer()
"""Validation / Reproducibility Center page.

Shows the frozen-Core validation report for the selected recorded run, then
supports the prove-it reproducibility action:

    "Re-run with Same Seed" -> the SAME scenario, configuration, horizon,
    master seed, target patients and run cap are executed again into a fresh
    Result Store, and both executions are compared on:
      * configuration hash
      * child seed
      * patient count
      * event count
      * validation result
      * output fingerprints (volatile fields normalised, MODEL.md sec. 28)
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from ..services import VALIDATION_EVIDENCE_DIR, get_comparator, get_store
from ..state import ensure_state
from ..components import (
    disclaimer,
    fmt_float,
    fmt_int,
    match_badge,
    page_header,
    rapport,
    select_run,
    status_badge,
)

FIELD_LABELS = {
    "configuration_hash": "Configuration Hash",
    "child_seed": "Child Seed",
    "patient_count": "Patient Count",
    "event_count": "Event Count",
    "max_abs_mbe": "Max |MBE|",
}


def render() -> None:
    ensure_state()
    page_header(
        "Validation / Reproducibility Center",
        "Frozen-Core validation results, plus proof-by-repetition with the "
        "same seed.",
    )
    rapport()
    store = get_store()
    run = select_run(key="selected_validation_run")
    if run is None:
        disclaimer()
        return

    _validation_report_section(run["label"])
    _rerun_section(run["label"])
    disclaimer()


def _validation_report_section(label: str) -> None:
    st.subheader("Frozen-Core validation report")
    report = get_store().validation_report(label)
    if not report:
        st.warning("No validation_report.json in this Result Store.")
        return
    st.markdown(f"**validation_status:** {status_badge(report.get('validation_status'))}")

    checks = report.get("checks", {})
    checks_df = []
    checks_df.append({"check": "overall", "status": report.get("validation_status"), "detail": ""})
    for check_name, payload in checks.items():
        checks_df.append(
            {
                "check": check_name,
                "status": _check_status(payload),
                "detail": _check_detail(payload),
            }
        )
    st.dataframe(pd.DataFrame(checks_df), width="stretch", hide_index=True)

    critical = report.get("critical_failures") or []
    if critical:
        st.error(f"Critical failures: {critical}")
    num_checks = report.get("num_checks")
    if num_checks:
        st.caption(
            f"{num_checks} checks executed; "
            f"amples={report.get('num_samples')}, success={report.get('num_successes')}."
        )


def _rerun_section(label: str) -> None:
    st.markdown("---")
    st.subheader("Re-run with Same Seed (proof-by-repetition)")
    comparator = get_comparator()
    shown = st.session_state.get("repro_comparison")

    if st.button("Re-run with Same Seed", key="val_rerun", type="primary"):
        try:
            with st.spinner(
                "Re-running the EXACT same job (same seed, same configuration) "
                "through the frozen Core, then comparing both executions."
            ):
                shown = comparator.rerun_same_seed(label)
            st.session_state["repro_comparison"] = shown
            _persist_evidence(shown)
            st.rerun()
        except Exception as exc:
            st.error(f"Reproducibility re-run failed: {exc}")
            st.code(repr(exc))
            return

    if shown:
        _render_comparison(shown)


def _render_comparison(shown: dict) -> None:
    status = shown["status"]
    st.markdown(
        f"**Scenario:** {shown['scenario_id']} — original "
        f"{status_badge(status['A'])} vs re-run {status_badge(status['B'])} "
        f"— validation result **{match_badge(status['MATCH'])}**."
    )
    st.caption(
        f"Original store: `{shown['original_label']}` — "
        f"re-run store: `{shown['rerun_label']}`."
    )

    summary_rows = []
    for i, run_row in enumerate(shown["runs"]):
        for field, label in FIELD_LABELS.items():
            summary_rows.append(
                {
                    "run_index": run_row["run_index"],
                    "field": label,
                    "A": _value(run_row[field]["A"]),
                    "B": _value(run_row[field]["B"]),
                    "MATCH": match_badge(run_row[field]["MATCH"]),
                }
            )
    for i, run_row in enumerate(shown["runs"]):
        for field, label in FIELD_LABELS.items():
            summary_rows.append(
                {
                    "run_index": run_row["run_index"],
                    "field": label,
                    "A": _value(run_row[field]["A"]),
                    "B": _value(run_row[field]["B"]),
                    "MATCH": match_badge(run_row[field]["MATCH"]),
                }
            )

    st.markdown("**Required reproducibility comparison fields**")
    st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

    st.markdown("**Output fingerprints**")
    fp = shown["fingerprints"]
    fp_rows = []
    for f in fp["files"]:
        fp_rows.append(
            {
                "file": f["file"],
                "sha256 A": f["sha256_A"],
                "sha256 B": f["sha256_B"],
                "MATCH": match_badge(f["MATCH"]),
            }
        )
    st.dataframe(pd.DataFrame(fp_rows), width="stretch", hide_index=True)
    if fp["method"]:
        for note in fp["method"]:
            st.caption(note)

    all_match = bool(shown["overall_match"])
    st.markdown("---")
    if all_match:
        st.success(
            "**REPRODUCIBILITY MATCH** — the re-run reproduced the original "
            "run: same configuration hash, same child seeds, same patient & "
            "event counts, same validation result, and matching output "
            "fingerprints."
        )
    else:
        st.error(
            "**REPRODUCIBILITY FAIL** — the re-run diverged from the original "
            "run. Inspect the fields above; do not treat this run as "
            "reproducible."
        )


def _check_status(payload) -> str:
    if not isinstance(payload, dict):
        return ""
    if "passed" in payload:
        return "PASS" if payload["passed"] is True else "FAIL"
    if "total_violations" in payload:
        return "PASS" if payload["total_violations"] == 0 else "FAIL"
    if "failures" in payload:
        return "PASS" if not payload["failures"] else "FAIL"
    if "met" in payload:
        return "PASS" if payload["met"] else "FAIL"
    return ""


def _check_detail(payload) -> str:
    if not isinstance(payload, dict):
        return str(payload)[:200]
    if "summary" in payload:
        return str(payload["summary"])[:200]
    if "details" in payload:
        return str(payload["details"])[:200]
    text = ", ".join(
        f"{k}={v}" for k, v in payload.items() if k not in ("passed", "summary", "details")
    )
    return text[:200]


def _value(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        try:
            return fmt_int(v) if float(v).is_integer() else str(v)
        except (TypeError, ValueError):
            return str(v)
    return str(v)


def _persist_evidence(shown: dict) -> None:
    VALIDATION_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = VALIDATION_EVIDENCE_DIR / f"{shown['rerun_label']}_comparison.json"
    path.write_text(json.dumps(shown, indent=2, default=str), encoding="utf-8")
    st.caption(f"Comparison evidence persisted: `{path}`")
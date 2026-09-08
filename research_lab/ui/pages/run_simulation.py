"""Run Simulation page.

One job = one scenario batch through the frozen Core: LIVE GENERATION ->
VALIDATION -> Result Store. Progress is surfaced from the frozen Core's own
records (each run's child seed + patient/event counts), not estimated.
"""

from __future__ import annotations

import streamlit as st

from ..services import get_adapter, get_store
from ..state import (
    SCENARIO_IDS,
    current_custom_profile,
    ensure_state,
)
from ..components import (
    disclaimer,
    fmt_int,
    page_header,
    rapport,
    status_badge,
)

# Documented Gate 2A measured throughput (S1, seed 20260805) used ONLY as an
# informational estimate in the UI — actual runs always use live Core results.
MEASURED_MEAN_PER_RUN = 1199


def render() -> None:
    ensure_state()
    page_header(
        "Run Simulation",
        "Execute a live scenario batch through the frozen HFSG Core and record "
        "it in the Result Store with full validation.",
    )
    rapport()
    adapter = get_adapter()
    store = get_store()

    if st.session_state.get("busy"):
        _run_stage(adapter, store)
        return

    st.session_state["selected_scenario_id"] = st.selectbox(
        "Scenario",
        SCENARIO_IDS,
        format_func=lambda sid: sid,
        index=SCENARIO_IDS.index(st.session_state["selected_scenario_id"]),
        key="rs_scenario",
    )
    scenario = st.session_state["selected_scenario_id"]

    c2, c3, c4 = st.columns(3)
    with c2:
        st.session_state["master_seed"] = int(
            st.number_input(
                "Master seed",
                value=int(st.session_state.get("master_seed", 20260805)),
                min_value=1,
                step=1,
            )
        )
    with c3:
        st.session_state["simulation_hours"] = float(
            st.number_input(
                "Simulation horizon (hours)",
                value=float(st.session_state.get("simulation_hours", 720.0)),
                min_value=1.0,
                step=24.0,
            )
        )
    with c4:
        st.session_state["run_cap"] = int(
            st.number_input(
                "Run cap (planned runs per scenario)",
                value=int(st.session_state.get("run_cap", 60)),
                min_value=1,
                step=1,
            )
        )
    c5, c6 = st.columns(2)
    with c5:
        st.session_state["demo_target"] = int(
            st.number_input(
                "Target patients",
                value=int(st.session_state.get("demo_target", 10_000)),
                min_value=100,
                step=100,
            )
        )
    with c6:
        st.text_input(
            "Run label (optional)",
            value="",
            placeholder="auto label is used",
            disabled=True,
        )

    if scenario == "CUSTOM":
        profile = current_custom_profile()
        try:
            adapter.validate_custom(profile)
        except Exception as exc:
            st.error(f"CUSTOM profile rejected by frozen Core: {exc}")
            return
        st.caption(
            f"CUSTOM profile: arrivals={profile['arrivals_multiplier']}, "
            f"icu={profile['icu_capacity_multiplier']}, "
            f"discharge={profile['discharge_multiplier']}"
        )
    elif scenario == "S7":
        st.caption("S7 activates the approved arrivals wave (48 h).")

    expected_runs = max(1, round(st.session_state["demo_target"] / MEASURED_MEAN_PER_RUN))
    st.info(
        f"Estimated work: ~{expected_runs} runs (documented Gate 2A measured "
        f"mean ~{MEASURED_MEAN_PER_RUN} patients/run; 10k ≈ 36 s, 25k ≈ 80 s "
        "on this machine). Actual duration depends on live Core execution."
    )

    if st.button("Run Simulation (live, validated)", key="rs_run", type="primary"):
        st.session_state["busy"] = True
        st.rerun()

    _show_last_outcome()


def _run_stage(adapter, store) -> None:
    """Busy stage: perform the real Core run, then present results."""
    scenario = st.session_state["selected_scenario_id"]
    master_seed = int(st.session_state["master_seed"])
    horizon = float(st.session_state["simulation_hours"])
    run_cap = int(st.session_state["run_cap"])
    target = int(st.session_state["demo_target"])
    profile = current_custom_profile() if scenario == "CUSTOM" else None

    label = store.new_label(scenario, prefix="lab")
    try:
        with st.spinner(
            f"Running {scenario} (seed {master_seed}, target {target:,}) "
            "through the frozen Core — generation then validation."
        ):
            outcome = adapter.run_job(
                scenario,
                store.out_dir(label),
                target_patients=target,
                planned_runs_per_scenario=run_cap,
                master_seed=master_seed,
                simulation_hours=horizon,
                custom_profile=profile,
                run_label=label,
            )
        st.session_state["selected_run"] = label
        st.session_state["last_outcome"] = {
            "label": label,
            "scenario": scenario,
            "status": outcome.validation_status,
            "patients": outcome.cumulative_patients,
            "events": outcome.cumulative_events,
            "runs": len(outcome.runs),
            "elapsed": outcome.generation_elapsed_seconds,
            "mbe": outcome.max_abs_mbe,
        }
        st.session_state["busy"] = False
        st.rerun()
    except Exception as exc:
        st.session_state["busy"] = False
        st.error(f"Run failed: {exc}")
        st.code(repr(exc))


def _show_last_outcome() -> None:
    outcome = st.session_state.get("last_outcome")
    if not outcome:
        return
    st.markdown("---")
    cols = st.columns(5)
    cols[0].metric("Run", outcome["label"])
    cols[1].metric("Scenario", outcome["scenario"])
    cols[2].metric("Patients", fmt_int(outcome["patients"]))
    cols[3].metric("Events", fmt_int(outcome["events"]))
    cols[4].metric("Status", status_badge(outcome["status"]))
    st.success("Run recorded in the Result Store. Open the Results Dashboard.")

    from ..state import set_page

    c1, c2 = st.columns(2)
    if c1.button("Open Results Dashboard", key="rs_dash", width="stretch"):
        set_page("Results Dashboard")
        st.rerun()
    if c2.button(
        "Open Validation / Reproducibility Center", key="rs_val", width="stretch"
    ):
        set_page("Validation / Reproducibility Center")
        st.rerun()
"""Academic Quick Demo page.

Two live demo sizes, both fully backed by the frozen Core:
  - Academic Quick Demo: target 10,000 patients (measured ≈ 36 s, S1)
  - Extended Demo:       target 25,000 patients (measured ≈ 80 s, S1)

Only the approved EXPOsed controls appear (scenario, seed, horizon). The run
is executed live, validated, and recorded — it is a LIVE DEMO, never labelled
RELEASED.
"""

from __future__ import annotations

import streamlit as st

from ..services import get_adapter, get_store
from ..state import (
    EXTENDED_DEMO_TARGET,
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

SEMANTIC = {
    "Quick Demo (recommended)": ("quick", 10_000, "Academic Quick Demo · target 10,000 · ≈ 36 s for S1"),
    "Extended / Slower Demo": ("extended", EXTENDED_DEMO_TARGET, "Extended Demo · target 25,000 · ≈ 80 s for S1"),
}


def render() -> None:
    ensure_state()
    page_header(
        "Academic Quick Demo",
        "Run a live, validated synthetic scenario through the frozen HFSG "
        "Core in about a minute.",
    )
    rapport()

    if st.session_state.get("busy"):
        _demo_stage()
        return

    adapter = get_adapter()
    store = get_store()

    mode = st.radio(
        "Demo target",
        list(SEMANTIC),
        help="Both are live frozen-Core runs; 25k is labelled Extended / Slower.",
    )
    _, target, caption = SEMANTIC[mode]
    st.session_state["qd_mode"] = mode
    st.session_state["demo_target"] = target
    st.caption(caption)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state["demo_scenario"] = st.selectbox(
            "Scenario",
            SCENARIO_IDS,
            index=SCENARIO_IDS.index(st.session_state["selected_scenario_id"]),
            key="qd_scenario",
        )
    with c2:
        st.session_state["demo_seed"] = int(
            st.number_input(
                "Master seed",
                value=int(st.session_state.get("master_seed", 20260805)),
                min_value=1,
                step=1,
            )
        )
    with c3:
        st.session_state["demo_horizon"] = float(
            st.number_input(
                "Simulation horizon (hours)",
                value=float(st.session_state.get("simulation_hours", 720.0)),
                min_value=1.0,
                step=24.0,
            )
        )

    scenario = st.session_state["demo_scenario"]
    if scenario == "CUSTOM":
        profile = current_custom_profile()
        try:
            adapter.validate_custom(profile)
        except Exception as exc:
            st.error(f"CUSTOM profile rejected: {exc}")
            return
        st.caption(
            f"CUSTOM profile: arrivals={profile['arrivals_multiplier']}, "
            f"icu={profile['icu_capacity_multiplier']}, "
            f"discharge={profile['discharge_multiplier']}"
        )

    if st.button("Run Quick Demo (live, validated)", key="qd_run", type="primary"):
        st.session_state["busy"] = True
        st.rerun()

    summary = st.session_state.get("last_outcome")
    if summary:
        _result(summary)

    disclaimer()


def _demo_stage() -> None:
    adapter = get_adapter()
    store = get_store()
    scenario = st.session_state["demo_scenario"]
    seed = int(st.session_state["demo_seed"])
    horizon = float(st.session_state["demo_horizon"])
    target = int(st.session_state["demo_target"])
    profile = current_custom_profile() if scenario == "CUSTOM" else None

    label = store.new_label(scenario, prefix="demo")
    try:
        with st.spinner(
            f"Running {scenario} demo (seed {seed}, target {target:,}) through "
            "the frozen Core — generation then validation."
        ):
            outcome = adapter.run_job(
                scenario,
                store.out_dir(label),
                target_patients=target,
                planned_runs_per_scenario=60,
                master_seed=seed,
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
        st.error(f"Quick Demo failed: {exc}")
        st.code(repr(exc))


def _result(outcome: dict) -> None:
    st.markdown("---")
    st.markdown(
        f"**Demo complete** — {status_badge(outcome['status'])} — "
        f"`{outcome['label']}`"
    )
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Scenario", outcome["scenario"])
    c2.metric("Patients", fmt_int(outcome["patients"]))
    c3.metric("Events", fmt_int(outcome["events"]))
    c4.metric("Runs", outcome["runs"])
    c5.metric(
        "Generation time",
        f"{outcome['elapsed']:.1f} s" if outcome.get("elapsed") is not None else "—",
    )
    _buttons()


def _buttons() -> None:
    from ..state import set_page

    c1, c2, c3 = st.columns(3)
    if c1.button("Open Results Dashboard", key="qd_dash", width="stretch"):
        set_page("Results Dashboard")
        st.rerun()
    if c2.button(
        "Validation & Reproducibility", key="qd_val", width="stretch"
    ):
        set_page("Validation / Reproducibility Center")
        st.rerun()
    if c3.button("Patient Explorer", key="qd_pex", width="stretch"):
        set_page("Synthetic Patient Explorer")
        st.rerun()
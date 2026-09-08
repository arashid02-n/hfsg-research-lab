"""Scenario Builder page.

Exposes ONLY the approved EXPOsed controls:
  - scenario S1..S8 / CUSTOM selection;
  - CUSTOM multipliers: arrivals (0.5-2.0), ICU capacity (0.5-1.5),
    discharge (0.5-2.0);
Master seed / horizon / target size are set on the Run / Demo pages.
All other parameters are INTERNAL/FROZEN and shown read-only.
"""

from __future__ import annotations

import copy
import json

import pandas as pd
import streamlit as st

from ..services import get_adapter
from ..state import (
    APPROVED_CUSTOM_LIMITS,
    SCENARIO_DESCRIPTIONS,
    SCENARIO_IDS,
    SCENARIO_LABELS,
    current_custom_profile,
    ensure_state,
    set_page,
)
from ..components import disclaimer, page_header, rapport


def _stringify_value(value) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def render() -> None:
    ensure_state()
    page_header(
        "Scenario Builder",
        "Choose a Standard-8 scenario or approve a CUSTOM profile within the "
        "Core's validated limits.",
    )
    rapport()
    adapter = get_adapter()

    selected = st.selectbox(
        "Scenario",
        SCENARIO_IDS,
        format_func=lambda sid: SCENARIO_LABELS[sid],
        key="sb_scenario",
        index=SCENARIO_IDS.index(st.session_state["selected_scenario_id"]),
    )
    st.markdown(SCENARIO_DESCRIPTIONS[selected])
    st.session_state["selected_scenario_id"] = selected

    if selected != "CUSTOM":
        definition = adapter.scenario_definition(selected)
        st.markdown("**Frozen preset multipliers (fixed):**")
        df = pd.DataFrame(
            [
                {
                    "parameter": "arrivals_multiplier",
                    "value": _stringify_value(definition.get("arrivals_multiplier", 1.0)),
                },
                {
                    "parameter": "icu_capacity_multiplier",
                    "value": _stringify_value(
                        definition.get("icu_capacity_multiplier", 1.0)
                    ),
                },
                {
                    "parameter": "discharge_multiplier",
                    "value": _stringify_value(
                        definition.get("discharge_multiplier", 1.0)
                    ),
                },
                {
                    "parameter": "arrivals_wave",
                    "value": "enabled" if definition.get("arrivals_wave") else "—",
                },
            ]
        )
        st.dataframe(df, width="stretch", hide_index=True)
        if selected == "S7":
            wave = definition.get("arrivals_wave", {})
            st.caption(
                "S7 activates the approved arrivals wave: "
                f"factor={wave.get('factor')}, start={wave.get('start_hour')}h, "
                f"duration={wave.get('duration_hours')}h."
            )
    else:
        st.markdown("**Approve CUSTOM multipliers** (frozen-Core limit enforcement).")
        limits = APPROVED_CUSTOM_LIMITS
        arrivals = st.slider(
            "Arrivals multiplier",
            min_value=limits["arrivals_multiplier"]["min"],
            max_value=limits["arrivals_multiplier"]["max"],
            value=float(
                st.session_state.get(
                    "custom_arrivals", limits["arrivals_multiplier"]["default"]
                )
            ),
            step=0.05,
        )
        icu = st.slider(
            "ICU capacity multiplier",
            min_value=limits["icu_capacity_multiplier"]["min"],
            max_value=limits["icu_capacity_multiplier"]["max"],
            value=float(
                st.session_state.get(
                    "custom_icu", limits["icu_capacity_multiplier"]["default"]
                )
            ),
            step=0.05,
        )
        discharge = st.slider(
            "Discharge multiplier",
            min_value=limits["discharge_multiplier"]["min"],
            max_value=limits["discharge_multiplier"]["max"],
            value=float(
                st.session_state.get(
                    "custom_discharge", limits["discharge_multiplier"]["default"]
                )
            ),
            step=0.05,
        )
        st.session_state["custom_arrivals"] = arrivals
        st.session_state["custom_icu"] = icu
        st.session_state["custom_discharge"] = discharge
        st.caption(
            "CUSTOM arrivals_wave is **NOT AVAILABLE IN CURRENT CORE** "
            "(approved limits disable it)."
        )
        profile = current_custom_profile()
        if st.button("Validate CUSTOM profile with frozen Core", key="sb_validate"):
            try:
                adapter.validate_custom(profile)
            except Exception as exc:  # ScenarioError from frozen Core
                st.error(f"CUSTOM profile rejected by frozen Core: {exc}")
            else:
                st.session_state["custom_approved"] = True
                st.success("CUSTOM profile approved by frozen Core limits.")
        if st.session_state.get("custom_approved"):
            st.json(profile)

    # Effective configuration hash preview (what the run page will record).
    st.markdown("---")
    st.subheader("Effective configuration hash preview")
    horizon = float(st.session_state.get("simulation_hours", 720.0))
    try:
        profile = current_custom_profile() if selected == "CUSTOM" else None
        eff_hash = adapter.effective_configuration_hash(
            selected, simulation_hours=horizon, custom_profile=profile
        )
        st.code(eff_hash)
        st.caption(
            f"This is the frozen-Core canonical hash for {selected} at "
            f"horizon={horizon:.0f}h. Re-running the same inputs must always "
            "reproduce this hash."
        )
    except Exception as exc:
        st.error(f"Could not build effective configuration: {exc}")

    # Read-only internal / frozen table.
    st.markdown("---")
    st.subheader("INTERNAL / FROZEN parameters (read-only)")
    with st.expander("Show frozen Core parameters (not configurable here)"):
        base = copy.deepcopy(adapter.frozen_config.data)
        frozen_defaults = adapter.frozen_defaults()
        rows = [
            ("simulation_hours", base.get("simulation_hours")),
            ("time_step_hours", base.get("time_step_hours")),
            ("initial_conditions", base.get("initial_conditions")),
            ("capacities", base.get("capacities")),
            ("arrivals", base.get("arrivals")),
            ("ed_processing", base.get("ed_processing")),
            ("destination_shares", base.get("destination_shares")),
            ("transfer_rates", base.get("transfer_rates")),
            ("discharge_rates", base.get("discharge_rates")),
            ("mortality_rates", base.get("mortality_rates")),
            ("default master_seed", frozen_defaults["master_seed"]),
            ("time_unit", base.get("time_unit")),
        ]
        frozen_for_arrow = [
            {"parameter": name, "frozen value": _stringify_value(value)}
            for name, value in rows
        ]
        st.dataframe(
            pd.DataFrame(frozen_for_arrow, columns=["parameter", "frozen value"]),
            width="stretch",
            hide_index=True,
        )

    col1, col2 = st.columns(2)
    if col1.button("Open Run Simulation", key="sb_run", width="stretch"):
        set_page("Run Simulation")
        st.rerun()
    if col2.button("Open Quick Demo", key="sb_demo", width="stretch"):
        set_page("Academic Quick Demo")
        st.rerun()
    disclaimer()
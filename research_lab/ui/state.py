"""Lab UI session state: defaults + approved EXPOsed controls.

These are the ONLY controls the UI exposes, per the approved Gate 1 scope:
scenario, master seed, simulation horizon, target patients (demo size), run
cap, and the CUSTOM multipliers (limits enforced by the frozen Core).
Everything else is INTERNAL/FROZEN.
"""

from __future__ import annotations

import streamlit as st

APPROVED_CUSTOM_LIMITS = {
    "arrivals_multiplier": {"min": 0.5, "max": 2.0, "default": 1.25},
    "icu_capacity_multiplier": {"min": 0.5, "max": 1.5, "default": 1.00},
    "discharge_multiplier": {"min": 0.5, "max": 2.0, "default": 1.10},
}

DEFAULT_MASTER_SEED = 20260805
DEFAULT_HORIZON_HOURS = 720.0
DEFAULT_DEMO_TARGET = 10_000
EXTENDED_DEMO_TARGET = 25_000
DEFAULT_RUN_CAP = 60

SCENARIO_IDS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "CUSTOM"]

SCENARIO_LABELS = {
    "S1": "S1 — Normal Operation",
    "S2": "S2 — Busy Week",
    "S3": "S3 — Crisis Mode",
    "S4": "S4 — ICU Capacity Loss",
    "S5": "S5 — Bed Block",
    "S6": "S6 — Compound Stress",
    "S7": "S7 — Emergency Wave",
    "S8": "S8 — Recovery Strategy",
    "CUSTOM": "CUSTOM — Customer Scenario",
}

SCENARIO_DESCRIPTIONS = {
    "S1": "Standard-8 Reference: normal baseline operation with approved "
    "reference arrival and capacity multipliers.",
    "S2": "Elevated arrival pressure over a sustained busy week.",
    "S3": "Crisis: high arrival surge combined with restricted capacity.",
    "S4": "ICU capacity loss: reduced intensive-care availability.",
    "S5": "Bed block: reduced downstream ward / specialty capacity.",
    "S6": "Compound stress: several stressors active at once.",
    "S7": "Emergency wave: short, sharp spike in arrivals.",
    "S8": "Recovery strategy: planned capacity and arrival recovery profile.",
    "CUSTOM": "Customer scenario: approved custom multipliers (limits are "
    "validated by the frozen Core).",
}


def default_exposed() -> dict:
    return {
        "selected_scenario_id": "S1",
        "master_seed": DEFAULT_MASTER_SEED,
        "simulation_hours": DEFAULT_HORIZON_HOURS,
        "demo_target": DEFAULT_DEMO_TARGET,
        "run_cap": DEFAULT_RUN_CAP,
        "custom_arrivals": APPROVED_CUSTOM_LIMITS["arrivals_multiplier"]["default"],
        "custom_icu": APPROVED_CUSTOM_LIMITS["icu_capacity_multiplier"]["default"],
        "custom_discharge": APPROVED_CUSTOM_LIMITS["discharge_multiplier"]["default"],
        "custom_approved": False,
        "page": "Home",
        "selected_run": None,
        "repro_comparison": None,
        "busy": False,
        "last_demo_summary": None,
    }


def ensure_state() -> None:
    for key, value in default_exposed().items():
        st.session_state.setdefault(key, value)


def current_custom_profile() -> dict:
    limits = APPROVED_CUSTOM_LIMITS
    return {
        "arrivals_multiplier": float(
            st.session_state.get("custom_arrivals", limits["arrivals_multiplier"]["default"])
        ),
        "icu_capacity_multiplier": float(
            st.session_state.get("custom_icu", limits["icu_capacity_multiplier"]["default"])
        ),
        "discharge_multiplier": float(
            st.session_state.get("custom_discharge", limits["discharge_multiplier"]["default"])
        ),
    }


def set_page(page: str) -> None:
    """Request a page transition.

    Only the non-widget ``page`` key (the navigation source of truth) is
    written here. The widget-bound ``page_radio`` key is intentionally NOT
    written: writing a widget key after that widget has been instantiated in
    the same run raises ``StreamlitWidgetAlreadyInstantiatedError``. The
    sidebar radio is instead kept in sync (before its instantiation) in
    ``app._sync_page_radio``.
    """
    st.session_state["page"] = page
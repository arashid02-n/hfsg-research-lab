"""Gate 2B acceptance-flow tests (streamlit AppTest, real Core execution).

These tests exercise the REAL frozen HFSG Core through the Lab UI:

    1. navigation smoke: all 10 pages render without app exceptions;
    2. acceptance flow: Run Simulation (S1, seed, horizon, small target)
       -> live Core generation+validation recorded to the Result Store;
       then Validation / Reproducibility Center "Re-run with Same Seed"
       -> REAL identical Core re-run -> the UI reports REPRODUCIBILITY MATCH.

The small default target (1,100 patients) keeps the live Core runs fast
(measured ~4-5 s per run on this machine) while remaining a real
generation->validation->reproducibility pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.core_live

LAB = Path(__file__).resolve().parents[1]
APP = str(LAB / "app.py")
DEFAULT_TIMEOUT = 180.0

PAGES = [
    "Home",
    "Scenario Builder",
    "Run Simulation",
    "Results Dashboard",
    "Scenario Comparison",
    "Synthetic Patient Explorer",
    "Validation / Reproducibility Center",
    "Export / Run Summary",
    "Academic Quick Demo",
    "About / System Information",
]


def _app() -> AppTest:
    return AppTest.from_file(APP, default_timeout=DEFAULT_TIMEOUT)


def _goto(at: AppTest, page: str) -> AppTest:
    nav = next(r for r in at.radio if r.key == "page_radio")
    nav.set_value(page).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_ten_pages_render() -> None:
    at = _app().run()
    assert not at.exception
    for page in PAGES:
        _goto(at, page)
        assert at.session_state["page"] == page


def _click_button(at: AppTest, label: str) -> AppTest:
    btn = next(b for b in at.button if b.label == label)
    btn.click().run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_button_navigation_paths() -> None:
    """Programmatic navigation (set_page + rerun) must not raise
    StreamlitWidgetAlreadyInstantiatedError for page_radio."""
    at = _app().run()
    assert not at.exception

    # Home -> Scenario Builder (button)
    at = _click_button(at, "Open Scenario Builder")
    assert at.session_state["page"] == "Scenario Builder"

    # Scenario Builder -> Run Simulation (button)
    at = _click_button(at, "Open Run Simulation")
    assert at.session_state["page"] == "Run Simulation"

    # Scenario Builder -> Academic Quick Demo (button)
    at = _goto(at, "Scenario Builder")
    at = _click_button(at, "Open Quick Demo")
    assert at.session_state["page"] == "Academic Quick Demo"

    # Home -> Academic Quick Demo (button)
    at = _goto(at, "Home")
    at = _click_button(at, "Open Academic Quick Demo")
    assert at.session_state["page"] == "Academic Quick Demo"

    # Radio navigation still works after programmatic navigation
    at = _goto(at, "Export / Run Summary")
    assert at.session_state["page"] == "Export / Run Summary"


def test_acceptance_flow_run_then_reproduce_match() -> None:
    at = _goto(_app().run(), "Run Simulation")

    # Configure a small live run: S1, seed 20260805, 720 h, target 1,100.
    number_inputs = at.number_input
    assert len(number_inputs) == 4, "seed/horizon/run-cap/target expected"
    number_inputs[0].set_value(20260805)
    number_inputs[1].set_value(720.0)
    number_inputs[2].set_value(60)
    number_inputs[3].set_value(1100)
    at.run()
    assert not at.exception

    run_button = next(b for b in at.button if b.label == "Run Simulation (live, validated)")
    run_button.click().run()
    assert not at.exception
    assert any("Run recorded in the Result Store" in s.value for s in at.success)

    label = at.session_state["selected_run"]
    assert label.startswith("lab-S1-")
    outcome = at.session_state["last_outcome"]
    assert outcome["status"] == "VALIDATED"
    assert outcome["scenario"] == "S1"

    # Go to the Validation / Reproducibility Center and re-run with same seed.
    at = _goto(at, "Validation / Reproducibility Center")
    rerun = next(b for b in at.button if b.label == "Re-run with Same Seed")
    rerun.click().run()
    assert not at.exception, [e.value for e in at.exception]

    success_text = [s.value for s in at.success]
    assert any("REPRODUCIBILITY MATCH" in s for s in success_text), success_text

    comparison = at.session_state["repro_comparison"]
    assert comparison["overall_match"] is True
    assert comparison["status"]["MATCH"] is True
    assert comparison["scenario_id"] == "S1"
    assert comparison["original_label"] == label
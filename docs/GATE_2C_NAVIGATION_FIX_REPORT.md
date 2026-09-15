# GATE 2C — Navigation Fix Report

**Date:** 2026-09-14

## Root cause

`research_lab/ui/state.py` `set_page()` wrote to the widget-bound session key
`page_radio` (`st.session_state["page_radio"] = page`) after the sidebar radio
(`app.py`, `key="page_radio"`) had already been instantiated in the same
Streamlit run. Streamlit raises
`StreamlitWidgetAlreadyInstantiatedError` when a widget key is modified after
that widget is created, which crashed navigation triggered by in-page buttons
(e.g. "Scenario Builder → Open Run Simulation").

## Files changed

- `app.py` — radio now uses an `on_change` callback; a `_sync_page_radio()`
  step runs **before** the radio is instantiated; the post-radio
  `page = page_radio` assignment was removed.
- `research_lab/ui/state.py` — `set_page()` now writes only the non-widget
  `page` key.
- `tests/test_acceptance_flow.py` — added `test_button_navigation_paths`.

## Navigation architecture fix

Single source of truth = the non-widget `st.session_state["page"]` key.

- **User clicks the radio** → `on_change` callback copies `page_radio` → `page`.
- **Programmatic navigation** (`set_page`) → writes only `page`, then
  `st.rerun()`; on the next run `_sync_page_radio()` copies `page` →
  `page_radio` **before** the radio widget is created (the only safe time to
  write a widget key).
- No code path writes `page_radio` after its widget is instantiated.

## All widget-bound session-state writes audited

Every widget key in the Lab UI was enumerated and checked for programmatic
writes:

| Widget key | Written programmatically? | Status |
|---|---|---|
| `page_radio` (sidebar radio) | was written in `set_page()` | **fixed** (now only `page`, synced pre-instantiation) |
| `rs_scenario` (Run Simulation selectbox) | no (read into `selected_scenario_id`) | safe |
| `sb_scenario` (Scenario Builder selectbox) | no (read into `selected_scenario_id`) | safe |
| `qd_scenario` (Quick Demo selectbox) | no (read into `demo_scenario`) | safe |
| `run_select` (recorded-run selectbox, via `select_run`) | no (writes non-widget `selected_run`/`selected_*_run`) | safe |
| all `st.button(..., key=...)` keys | no | safe |
| all `st.number_input` keys (auto) | no (results written to non-widget keys) | safe |

No other widget-bound session-state key is written after instantiation.

## Navigation tests

New `test_button_navigation_paths` (AppTest) exercises real button clicks:

- Home → Scenario Builder (button) ✓
- Scenario Builder → Run Simulation (button) ✓
- Scenario Builder → Academic Quick Demo (button) ✓
- Home → Academic Quick Demo (button) ✓
- Radio navigation after programmatic navigation (Export / Run Summary) ✓

No `StreamlitWidgetAlreadyInstantiatedError` is raised on any path.

## Lab test result

`11 passed` (unit + AppTest navigation + acceptance flow).

## Core regression result

`177 passed` — **CORE REGRESSION: PASS**.

## Frozen Core verification

`CORE MODIFICATION: NONE` — Core HEAD `affe7c8` unchanged; `git diff` empty
(only pre-existing untracked `data/`). Model, patient generation, event
generation, validation, reconciliation, seeds, and scenarios are unchanged.

## Corrected ZIP SHA-256

The fresh SHA-256 for the corrected `HFSG_Academic_Demo_v1.0.zip` is recorded
in the delivered `SHA256SUMS` file (generated after the final build and
shipped alongside the ZIP).

## Status

```
GATE 2C — PENDING PROJECT OWNER FINAL SURFACE ACCEPTANCE
```

Windows Surface acceptance is NOT claimed here; the Project Owner will run the
corrected ZIP on the Surface.

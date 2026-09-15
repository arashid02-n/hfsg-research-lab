# HFSG GATE 2C — FINAL REMEDIATION REPORT

Date: 2026-09-15
Scope: two remediation fixes only (Streamlit navigation state; Home release-manifest presentation). No new features, no methodology/model changes, no Frozen Core modification.

---

## 1. Navigation root cause

`research_lab/ui/state.py` (`set_page`) wrote the widget-bound session-state
key `st.session_state["page_radio"]` **after** the sidebar radio widget with
`key="page_radio"` had already been instantiated in the same Streamlit
execution cycle. Streamlit forbids mutating a widget-bound key after widget
instantiation and raised `StreamlitWidgetAlreadyInstantiatedError` (reported by
the Project Owner via:

Scenario Builder → Open Run Simulation).

## 2. Navigation fix (systematic)

The navigation/state architecture was made Streamlit-safe rather than patching a
single path:

- `st.session_state["page"]` (non-widget) is the single source of truth for
  navigation.
- `set_page()` now writes **only** `page`; it never writes a widget-bound key.
- The sidebar radio (`key="page_radio"`) is driven the safe way:
  - `_sync_page_radio()` writes `page_radio = page` **before** the radio widget is
    instantiated (widget keys may only be set pre-instantiation), and
  - the radio uses `on_change=_on_page_radio_change.inner_cb` so user changes
    update the non-widget `page`.
- The audio of internal navigation widgets was completed:
  - **navigation widgets:** sidebar `page_radio` (radio); buttons on Home
    (`Open Academic Quick Demo`, `Open Scenario Builder`), Scenario Builder
    (`Open Run Simulation`, `Open Quick Demo`), Run Simulation/Results/Validation/
    Export internal buttons; all are simple `st.button`s (widget keys read via
    `on_click`/return values, never written programmatically).
  - **all writes to widget keys:** audit confirms `page_radio` was the only
    widget-bound key written by code after instantiation; it is now only written
    in `_sync_page_radio()` (pre-instantiation).
  - **all `set_page()` / navigation helpers:** centralized in
    `research_lab/ui/state.py`.
- No `try/except` was used to hide the error; no widgets were disabled/removed.

## 3. Navigation paths tested

Verified with `streamlit.testing.v1.AppTest` via both radio and button click,
asserting no exceptions and correct `page`:

- Home → Scenario Builder → Run Simulation
- Scenario Builder → Quick Demo
- Run Simulation → Results Dashboard
- Results → Validation / Reproducibility Center
- Results → Export / Run Summary
- Home → Academic Quick Demo
- Radio navigation after programmatic navigation

No `StreamlitWidgetAlreadyInstantiatedError` occurred on any path.

## 4. Manifest issue and chosen resolution

**Issue:** Home displayed "Released manifest not found (read-only check)" when
the Phase-1 release manifest was absent.

**Chosen resolution: B (intentionally not included).** The Academic Demo package
deliberately excludes the Master Dataset (`data/`, including Core
`data/output/step9/dataset_manifest.json`) per the documented distribution
boundary (`docs/IP_AND_DISTRIBUTION_BOUNDARY.md`). The Home page now shows a
clear informational, read-only message stating that the release manifest is not
included in this Academic Demo package and that the frozen Core still validates
this Lab's runs independently. No fake manifest was created, no manifest contents
were modified, and runtime validation is unchanged.

## 5. Files changed

- `research_lab/ui/state.py` — navigation state safe write (only non-widget key).
- `app.py` — `_sync_page_radio()` (pre-instantiation sync), `page_radio` radio
  `on_change`, restructured `main()`.
- `research_lab/ui/pages/home.py` — informational manifest message (resolution B).
- `tests/test_acceptance_flow.py` — `test_button_navigation_paths` (button and
  radio navigation regression coverage).
- `docs/GATE_2C_NAVIGATION_FIX_REPORT.md` — navigation fix detail (previous).
- `docs/HFSG_GATE_2C_FINAL_REMEDIATION_REPORT.md` — this report.

## 6. Research Lab regression result

- Full Lab test suite: **PASS** (11 passed, 18.33s) — includes
  `test_button_navigation_paths`, `test_ten_pages_render`,
  `test_acceptance_flow_run_then_reproduce_match` (REPRODUCIBILITY MATCH).
- S1 configuration, configuration hash, Core identity (v0.6.0 / 08032c3 /
  affe7c8), 10K Quick Demo ability, validation and same-seed reproducibility
  unchanged (no Lab behaviour/methodology changes).

## 7. Core regression result

- **CORE REGRESSION: PASS — 177/177.**
- `pytest -q` full Core suite: `177 passed in 155.97s` (clean re-run after an
  environment-only disk-full incident, which was freed and re-run).

## 8. Frozen Core unchanged

- `git rev-parse HEAD` = `affe7c8` (frozen integration commit).
- `git status --porcelain` = only untracked `data/` (never committed).
- No tracked Core file modified: **YES — Frozen Core modification: NONE.**

## 9. New ZIP filename

`HFSG_Academic_Demo_v1.0.zip` (118 entries, integrity OK; `hfsg_core/` bundled
approved Core incl. `CORE_PROVENANCE.json`; `data/`, `.git`, `.venv`,
`*.parquet` excluded; no leaked `/home/rashid` paths; no real secret material).

## 10. SHA-256

The authoritative SHA-256 of the exact delivered `HFSG_Academic_Demo_v1.0.zip`
is recorded in `release/SHA256SUMS` in the private handover package
(`sha256sum -c` = OK). This report is delivered **inside the ZIP**, so it does
not embed the ZIP's own digest (self-referential); the checksum is verified
against the ZIP via `SHA256SUMS`, which is delivered outside the ZIP.

## 11. Remaining limitations

- **WINDOWS SURFACE FINAL ACCEPTANCE: NOT VERIFIED on this machine** — final
  verification of the corrected ZIP on the Microsoft Surface is the Project
  Owner's step.
- The Lab resolves the Core with priority `hfsg_core/` (or `core/`) → env
  `HFSG_CORE_DIR`/`HFSG_CORE` → `hfsg_core.config` → About-page selection; on
  machines where the bundle is used, no `data/output` is present by design, so
  the Home manifest panel shows the informational message.
- Minor environment note: a transient mid-run disk-full occurred during one Core
  regression attempt; it was an environment condition (no disk headroom), the
  suite was re-run to a clean 177/177 after freeing space.

---

**Status:** GATE 2C — FINAL REMEDIATIONS COMPLETE
**Pending:** PROJECT OWNER FINAL SURFACE VERIFICATION
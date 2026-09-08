# Gate 2B — Implementation Report

**Date:** 2026-09-08
**Status:** GATE 2B — READY FOR ACCEPTANCE REVIEW
**App version:** HFSG Research Lab v1.0.0
**Frozen Core:** HFSG Core v0.6.0 — Phase-1 validated baseline `08032c3`; current frozen integration commit `affe7c8`

---

## 1. Scope delivered

A complete Streamlit application ("HFSG Research Lab") layered on the frozen
HFSG Core through a thin adapter. It implements the nine approved pages
exactly as specified in Gate 1:

| # | Page | Purpose |
|---|------|---------|
| 1 | Home | Identity lineage, Live Demo vs Validated Release distinction |
| 2 | Scenario Builder | S1–S8 / CUSTOM selection, approved CUSTOM multipliers |
| 3 | Run Simulation | live scenario batch: generate → validate → record |
| 4 | Results Dashboard | census, flows, events, occupancy (real data) |
| 5 | Scenario Comparison | side-by-side recorded runs + Core scenario_comparison.csv |
| 6 | Synthetic Patient Explorer | filter/drill real synthetic patient records |
| 7 | Validation / Reproducibility Center | Core report + **Re-run with Same Seed** MATCH/FAIL |
| 8 | Export / Run Summary | job inputs provenance + Result Store zip export |
| 9 | Academic Quick Demo | quick (10k) / extended (25k) live validated demo |

## 2. Approved-scope enforcement

Only the approved EXPOsed controls are user-adjustable; everything else is
**INTERNAL / FROZEN** and shown read-only:

- scenario `S1`…`S8` / `CUSTOM`;
- master seed (default `20260805`);
- simulation horizon (default `720` h);
- target patients (Quick Demo `10,000`; Extended Demo `25,000`);
- run cap (default `60` planned runs per scenario);
- CUSTOM multipliers with **frozen-Core enforced limits**:
  arrivals `0.5–2.0` (def `1.25`), ICU capacity `0.5–1.5` (def `1.00`),
  discharge `0.5–2.0` (def `1.10`).

`CUSTOM arrivals_wave` is intentionally **NOT AVAILABLE IN CURRENT CORE** and
is surfaced as such in the UI (approved limits set `enabled: false`).

Forbidden items (chatbot / LLM / TrustDx / FHIR / EHR / clinical AI /
authentication / cloud / API / database server / new Core parameters / any
Core change) are **not present** in the delivered code.

## 3. Architecture (no model logic in the Lab)

The Lab contains **no model equations**. All simulation behaviour comes from
the frozen Core public APIs, called through `research_lab/adapter.py`:

- `hfsg.config.ConfigurationLoader` — config loading and validation;
- `hfsg.scenarios.ScenarioManager` / `configuration_hash` — scenario
  resolution, CUSTOM limit validation, canonical hashing;
- `hfsg.seeds.derive_child_seed` — child-seed policy;
- `hfsg.batch.BatchRunner` / `validate_batch_outputs` — bounded-memory
  generation + validation.

The runtime Configuration is built with `ConfigurationLoader.from_data(...)`
over a deep copy of the frozen `config/base.yaml`, touching **only** the
approved controls, then validated by the frozen Core. The frozen repo, its
configuration and its tests are never modified. Identity is verified at
runtime against the frozen repository (version, HEAD, baseline presence,
tracked-file cleanliness).

## 4. Files delivered

```
app.py                     Streamlit entry point
START_HFSG                 one-click launcher
requirements-lab.txt       Lab runtime + dev dependencies
README.md                  install/start + acceptance flow
pytest.ini                 markers
research_lab/
  __init__.py, identity.py, adapter.py, fingerprint.py,
  result_store.py, reproducibility.py
  ui/__init__.py, components.py, state.py, services.py
  ui/pages/                home, scenario_builder, run_simulation,
                           results_dashboard, scenario_comparison,
                           patient_explorer, validation_center,
                           export, quick_demo
scripts/
  start_hfsg.sh            launcher implementation
  ui_demo.py               acceptance-demo driver + screenshots
tests/
  test_lab_services.py     fast unit tests (identity, adapter, fingerprints,
                           comparator on real Gate 2A stores)
  test_acceptance_flow.py  AppTest: 9-page render + live run +
                           "Re-run with Same Seed" REPRODUCIBILITY MATCH
bench/ proof/              Gate 2A artifacts (updated to the package layout)
reports/                   this and the other Gate 2B reports
screenshots/               11 acceptance-demo screenshots
```

## 5. Tests executed

| Suite | Result |
|-------|--------|
| Lab unit + service tests (`tests/test_lab_services.py`) | 8 passed |
| Lab acceptance-flow tests (`tests/test_acceptance_flow.py`) | 2 passed |
| Full Lab suite | 10 passed in ~16 s |
| **Frozen Core regression** (before Gate 2B) | 177 passed in 152.16 s |
| **Frozen Core regression** (after Gate 2B) | 177 passed in 157.63 s |

The frozen Core suite result is identical before and after; the Core working
tree contains **no tracked modifications** (only the pre-existing untracked
`data/` directory). See `CORE_REGRESSION_REPORT.md`.

## 6. Acceptance evidence

The acceptance flow was driven in a real headless Chromium against the live
Streamlit server; every step used real Core data (no mocks). The 10k Quick
Demo produced `10,622` patients / `31,653` events — exactly the documented
Gate 2A S1-10k benchmark counts — and the "Re-run with Same Seed" action
reproduced it bit-for-bit (see `DEMO_ACCEPTANCE_TEST_REPORT.md`).

## 7. Decisions and open items

- Sidebar-radio routing chosen over `st.navigation` for AppTest testability.
- Running from the UI executes one scenario batch at a time (no parallelism);
  machine limits (2 cores, ~3.7 GB RAM) match the documented Gate 2A budget.
- No `DECISION_REQUIRED` or `SPEC_CONFLICT` is outstanding for this
  component. The app leaves the product at **GATE 2B — READY FOR ACCEPTANCE
  REVIEW**; it does not claim acceptance, a Released label, or clinical
  validity.
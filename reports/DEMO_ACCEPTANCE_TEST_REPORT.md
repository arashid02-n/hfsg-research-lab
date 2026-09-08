# Gate 2B — Demo Acceptance Test Report

A real end-to-end acceptance demo was executed in a headless Chromium browser
against the live HFSG Research Lab (Streamlit server). **Every step used real
frozen-Core data; nothing was mocked.**

---

## 1. Environment

| Item | Value |
|---|---|
| App | HFSG Research Lab v1.0.0 (`app.py`, Streamlit 1.63.0) |
| Core | HFSG Core v0.6.0 — validated baseline `08032c3`; frozen commit `affe7c8` |
| Config | `/home/rashid/projects/hfsg/config/base.yaml` |
| Browser driver | Playwright, headless Chromium, 1440×900 |
| Machine | 2 CPU cores, ~3.7 GB RAM |
| Date | 2026-09-08 |

## 2. Acceptance flow executed (observed results)

| # | Step | Page / action | Observed result |
|---|---|---|---|
| 1 | Select Scenario | Scenario Builder (S1 default) | S1 preset multipliers shown (frozen) |
| 2 | Configure | Quick Demo: seed `20260805`, horizon `720 h`, Quick Demo target `10,000` | controls accepted; CUSTOM not selected |
| 3 | Run 10K | "Run Quick Demo (live, validated)" | **Demo complete** — live Core generation + validation |
| 4 | Validate | Validation / Reproducibility Center | `validation_status: VALIDATED` (Core report table rendered) |
| 5 | Dashboard | Results Dashboard | census charts, flow chart, events by type, occupancy vs capacity rendered |
| 6 | Patient Explorer | Synthetic Patient Explorer | real synthetic patient filter + timeline rendered |
| 7 | Re-run with Same Seed | Validation / Reproducibility Center button | second identical Core execution → **REPRODUCIBILITY MATCH** |
| 8 | Compare | Scenario Comparison | side-by-side runs table + census overlay |
| 9 | Export | Export / Run Summary | **Export ready** zip of the re-run Result Store |

## 3. Live run results

Both executions used identical inputs: `S1`, `master_seed=20260805`,
`slow horizon=720 h`, `target_patients=10,000`, run cap 60.

| Run store | Patients | Events | Validation |
|---|---|---|---|
| `demo-S1-20260908-172818-0` (original) | **10,622** | **31,653** | VALIDATED |
| `rerun-S1-20260908-172914-0` (same seed) | **10,622** | **31,653** | VALIDATED |

> These totals exactly reproduce the documented Gate 2A benchmark point
> **S1-10K: 10,622 patients / 31,653 events** (seed 20260805) — independent
> confirmation that the UI path runs the same pipeline as the benchmark.

## 4. Reproducibility comparison (real values)

Effective configuration hash (**S1, identity**): `e460cf544c622cfa495fa6cfe69a68605e9d57cd82ad95ba6df07e539006ced8`
— identical on both executions.

| Run | child seed (A=B) | patients A=B | events A=B | max\|MBE\| A=B |
|---|---|---|---|---|
| 0 | `276456660741356034` | 1199 | 3549 | 0.0 |
| 1 | `1058164793264608762` | 1199 | 3565 | 0.0 |
| 2 | `5286311076552809590` | 1192 | 3530 | 0.0 |
| 3 | `3125675021271633734` | 1159 | 3482 | 0.0 |
| 4 | `7772821530225387842` | 1152 | 3433 | 0.0 |
| 5 | `817008895474398956` | 1211 | 3611 | 0.0 |
| 6 | `1513068997524123011` | 1155 | 3437 | 0.0 |
| 7 | `6753276407700429733` | 1172 | 3509 | 0.0 |
| 8 | `5425386346784787015` | 1183 | 3537 | 0.0 |
| **Total** | — | **10,622** | **31,653** | 0.0 |

Per-run, per-field verdicts — configuration hash, child seed, patient count,
event count, `max_abs_mbe`, validation status — were **MATCH** for all 9 runs.
Output **fingerprints** (31 Parquet/CSV/JSON artifacts; volatile fields
normalised per MODEL.md §28) were all **MATCH**.

## 5. Screenshots captured

| File | Page |
|---|---|
| `01_home.png` | Home |
| `02_scenario_builder.png` | Scenario Builder |
| `03_quick_demo_configured.png` | Academic Quick Demo (configured) |
| `04_quick_demo_result.png` | Demo result (live run) |
| `05_results_dashboard.png` | Results Dashboard |
| `06_patient_explorer.png` | Synthetic Patient Explorer |
| `07_validation_center.png` | Validation / Reproducibility Center |
| `08_reproducibility_match.png` | **REPRODUCIBILITY MATCH** |
| `09_scenario_comparison.png` | Scenario Comparison |
| `10_export.png` | Export / Run Summary |
| `11_home_final.png` | Home (final) |

## 6. Demo artifacts

- Result Stores: `results/demo-S1-*/` (original) and `results/rerun-S1-*/`
  (re-run), each containing the full Core output bundle + `job_spec.json`,
  and the exported zip.
- Reproducibility evidence:
  `results/validation_evidence/rerun-S1-20260908-172914-0_comparison.json`.

## 7. Result

The recorded acceptance demo completed **exit code 0** with the full path
`Select Scenario → Configure → Run 10K → Generate → Validate → Dashboard →
Patient Explorer → Re-run with Same Seed → Reproducibility MATCH → Compare →
Export`.

**DEMO ACCEPTANCE TEST: PASS** — verified against the frozen HFSG Core only.
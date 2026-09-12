# Gate 2B — UI ↔ Core Traceability Report

**Purpose:** trace every user-visible Lab control and displayed figure to a
frozen HFSG Core entry point, and assert that the Lab contains **no model
logic** and does **not** modify the Core.

---

## 1. Frozen Core entry points used

| Core symbol (frozen repo, HEAD `affe7c8`) | Role in the Lab |
|---|---|
| `hfsg.config.ConfigurationLoader.load / from_data` | load + validate frozen `config/base.yaml`; validate runtime-config copies |
| `hfsg.scenarios.ScenarioManager` `.scenario_ids/.scenario_definition/.effective_configuration/.validate_custom` | scenario resolution; CUSTOM approved-limit enforcement; effective configuration |
| `hfsg.scenarios.configuration_hash` | canonical effective-config hash shown/recorded |
| `hfsg.seeds.derive_child_seed` | child-seed policy (recorded) |
| `hfsg.batch.BatchRunner(config, out_dir, target_patients, planned_runs_per_scenario, scenario_ids, master_seed).run()` | bounded-memory live generation |
| `hfsg.batch.validate_batch_outputs(out_dir)` | bounded-memory validation |
| Core Parquet/manifest report files | all dashboard/explorer/export figures |

## 2. Page-by-page traceability

| UI page / control | Lab code | Frozen Core source of the value | Model logic in Lab? |
|---|---|---|---|
| Home — lineage statement | `research_lab/identity.py` | runtime verification of repo `__version__`/HEAD/baseline | no |
| Home — Live Demo vs Validated Release | `ui/pages/home.py` | read-only `data/output/step9/dataset_manifest.json` | no |
| Scenario Builder — scenario list + presets | `ui/pages/scenario_builder.py` | `ScenarioManager.scenario_ids/scenario_definition` | no |
| Scenario Builder — CUSTOM sliders | `ui/pages/scenario_builder.py` | `ScenarioManager.validate_custom` enforces limits | no |
| Scenario Builder — effective-hash preview | `ui/pages/scenario_builder.py` | `configuration_hash(effective_configuration(...))` | no |
| Run Simulation — execute | `research_lab/ui/services.py → adapter.run_job` | `BatchRunner` generation → `validate_batch_outputs` | no |
| Results Dashboard — census/flows/events/occupancy | `ui/pages/results_dashboard.py` | Core `aggregate_timeseries`/`patients`/`patient_events` Parquet + frozen `capacities` | no |
| Patient Explorer — filters + timeline | `ui/pages/patient_explorer.py` | Core `patients`/`patient_events` Parquet | no |
| Validation Center — report table | `ui/pages/validation_center.py` | Core `validation_report.json` checks | no |
| Validation Center — Re-run with Same Seed | `research_lab/reproducibility.py` | identical job through `BatchRunner` + `validate_batch_outputs`; comparison of Core results | no |
| Export — job spec / manifest / zip | `ui/pages/export.py`, `research_lab/result_store.py` | `job_spec.json` (Lab provenance) + Core manifest/report files | no |
| Quick Demo | `ui/pages/quick_demo.py` | same trace as Run Simulation | no |

## 3. Runtime configuration path

1. `ConfigurationLoader.load(config/base.yaml)` — frozen default.
2. Lab copies the loaded model dict deep (`copy.deepcopy`).
3. Only approved controls may differ: `simulation_hours` (preserved `int`
   when integral, so an identity run hashes exactly like the frozen default)
   and, for `CUSTOM`, the multiplier profile.
4. `ConfigurationLoader.from_data(...)` **validates** the built config; for
   `CUSTOM` the profile is pre-checked by `ScenarioManager.validate_custom`.
5. The resulting `Configuration` is handed unchanged to `BatchRunner`.

The frozen config file is never written.

## 4. Four invariants reinforced by the Lab

1. **No model logic** — grep of `research_lab/` finds no engine equations;
   only orchestration and presentation.
2. **Integerized quotas untouched** — the Lab never reads or rewrites
   `patient_events` quota_flow; the Core's Largest-Remainder + seeded tie
   break stands.
3. **Volatile-field policy (MODEL.md §28)** — `research_lab/fingerprint.py`
   normalizes the documented volatile columns/keys (`simulation_id`,
   `created_at`; `batch_id`, `dataset_id`, `generation_timestamp`,
   `configuration_hash`, `recomputed_configuration_hash`) **only at
   comparison time**; no Core output is rewritten.
4. **Core integrity** — the app verifies version `0.6.0`, HEAD `affe7c8`,
   validated baseline `08032c3` present, and a clean tracked working tree
   before rendering reports.

## 5. Verification performed

- `git -C <HFSG_CORE> status --porcelain` → only pre-existing
  untracked `data/` (no tracked modifications).
- Frozen Core suite: 177 passed before and 177 passed after Gate 2B
  (`CORE_REGRESSION_REPORT.md`).
- Lab tests exercise the real Core (no mocks), including a live
  generation→validation→re-run cycle (`DEMO_ACCEPTANCE_TEST_REPORT.md`).
# HFSG Research Lab — Known Limitations

Documented, accepted limitations of the Gate 2B implementation. The Lab does
not hide or compensate for these; where relevant the UI surfaces them.

## 1. Product / scope limits (by design, Phase 1)

- **No clinical validity.** "SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL
  PATIENT DATA — NOT CLINICALLY VALIDATED." Research/education use only.
- **No Released datasets from the Lab.** Live Demo runs are labelled
  `VALIDATED` at most; only the frozen Core's Phase 1 dataset
  (`data/output/step9`) carries the `RELEASED` label, and the Lab only reads
  it.
- **Exposed controls only.** Everything except scenario / seed / horizon /
  target / run cap / CUSTOM multipliers is internal and frozen.
- **No Expanded Scope.** No chatbot/LLM/TrustDx/FHIR-EHR/clinical-AI/cloud/
  API/auth/database-server features exist.

## 2. Core-related limits

- **`CUSTOM arrivals_wave` not available.** The approved
  `custom_parameter_limits.arrivals_wave.enabled=false` in the frozen core
  disables it; the Scenario Builder displays "CUSTOM arrivals_wave is NOT
  AVAILABLE IN CURRENT CORE". Enabling it requires a Core change, which is
  out of scope.
- **Frozen-Core CLI defect (not fixed).** `scripts/run_step9.py --mode
  validate` passes `scenario_ids=` but `validate_batch_outputs` expects
  `schedule=`; the Lab avoids the CLI entirely and calls
  `validate_batch_outputs` directly. The Core is frozen and unmodified.
- **Volatile batch-scoped fields.** The batch `dataset_manifest.json`
  `configuration_hash` is batch-scoped (it summarises `used_configuration.yaml`
  which embeds the volatile `batch_id`) and therefore differs between two
  executions. Per MODEL.md §28 the Lab's fingerprints and comparisons
  normalise these documented volatile fields (`simulation_id`, `created_at`,
  `batch_id`, `dataset_id`, `generation_timestamp`, `configuration_hash`,
  `recomputed_configuration_hash`). The per-run effective configuration hash
  (e.g. identity S1 = `e460cf54…`) is deterministic and always compared
  directly.

## 3. Machine / performance limits

- **Volumes.** Quick Demo 10k ≈ 36 s, 25k ≈ 80 s (measured S1); the UI shows
  "Extended / Slower Demo" for 25k. Volume from the UI is limited by the
  run cap (default 60 planned runs); reaching ~100k patients from the UI
  requires raising the run cap, and the 1M Phase 2 Scale Qualification target
  is deferred per the 2026-09-05 Project Owner decision.
- **Memory.** Recording, display and fingerprinting load whole Parquet files
  into RAM one at a time. The Core itself stays bounded-memory; the Lab's
  patient explorer buffers the full patients frame for filtering (~10k patients
  fit comfortably; the 100k+ Batch is best examined with the Core CLI or the
  export bundle rather than the browser).
- **Disk.** Each 10k run records ~1.1 MB + validation overhead; recorded runs
  accumulate in `results/` (gitignored). The 2026-09-08 workstation had
  ~700 MB free; keep headroom when recording many large runs.

## 4. UI-behavioural limits

- **One run at a time.** A "busy" guard prevents concurrent runs from the UI;
  generation and validation block the app session during execution.
- **Run labels are auto-generated.** The Run Simulation page shows the label
  field as disabled; auto labels (`lab-S1-<timestamp>-<seq>`, `demo-…`,
  `rerun-…`) guarantee uniqueness.
- **Comparison is per-run-index.** Reproducibility comparison aligns both
  executions by `run_index`; both always use identical inputs, so counts of
  runs match.
- **Export download cap.** Browser download is offered for zips ≤ 100 MB;
  larger results are retrievable at the printed path.

## 5. Process limits

- **No acceptance claimed.** This deliverable stops at
  "GATE 2B — READY FOR ACCEPTANCE REVIEW". Acceptance, release and scale
  qualification are out of the Lab's control and not implied by its output.
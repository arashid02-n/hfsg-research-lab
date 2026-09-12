# Known Limitations

Documented, accepted limitations of the HFSG Research Lab (Gate 2C). The Lab
does not hide or compensate for these; where relevant the UI surfaces them.

## 1. Product / scope limits (by design, Phase 1)

- **No clinical validity.** "SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL
  PATIENT DATA — NOT CLINICALLY VALIDATED." Research/education use only.
- **No Released datasets from the Lab.** Live Demo runs are labelled
  `VALIDATED` at most; only the frozen Core's Phase 1 dataset carries the
  `RELEASED` label, and the Lab only reads it.
- **Exposed controls only.** Everything except scenario / seed / horizon /
  target / run cap / CUSTOM multipliers is internal and frozen.
- **No Expanded Scope.** No chatbot/LLM/TrustDx/FHIR-EHR/clinical-AI/cloud/
  API/auth/database-server features exist.

## 2. Core-related limits

- **`CUSTOM arrivals_wave` not available.** The approved
  `custom_parameter_limits.arrivals_wave.enabled=false` in the frozen Core
  disables it; the Scenario Builder shows "CUSTOM arrivals_wave is NOT
  AVAILABLE IN CURRENT CORE". Enabling it requires a Core change, which is
  out of scope.
- **Frozen-Core CLI defect (not fixed).** `scripts/run_step9.py --mode
  validate` passes `scenario_ids=` but `validate_batch_outputs` expects
  `schedule=`; the Lab avoids the CLI entirely and calls
  `validate_batch_outputs` directly. The Core is frozen and unmodified.
- **Volatile batch-scoped fields.** The batch `dataset_manifest.json`
  `configuration_hash` is batch-scoped and differs between two executions.
  Per MODEL.md §28 the Lab normalises these documented volatile fields. The
  per-run effective configuration hash (e.g. identity S1 = `e460cf54…`) is
  deterministic and always compared directly.
- **Core identity requires a git checkout.** The identity check (version
  `0.6.0`, baseline `08032c3`, frozen commit `affe7c8`) uses `git`; a Core
  copied *without* its `.git` history cannot be fully verified and live runs
  are blocked. Supply the Core as a git checkout.

## 3. Portability limits (Gate 2C)

- **Core is external.** The Lab does not bundle the HFSG Core or the Master
  Dataset (see `IP_AND_DISTRIBUTION_BOUNDARY.md`). A Core must be supplied
  via `hfsg_core/`, `HFSG_CORE_DIR`, `hfsg_core.config`, or the About page.
- **Independent Windows acceptance not yet executed.** The clean-machine and
  offline checks were run on the developer's Linux environment; a physical
  Windows-laptop acceptance run is pending (see
  `PORTABILITY_ACCEPTANCE_REPORT.md`). PASS is not claimed until it is run.

## 4. Machine / performance limits

- **Volumes.** Quick Demo 10k ≈ 36 s, 25k ≈ 80 s (measured S1). Reaching
  ~100k patients from the UI requires raising the run cap; the 1M Phase 2
  Scale Qualification target is deferred per the 2026-09-05 Project Owner
  decision.
- **Memory.** Recording, display and fingerprinting load whole Parquet files
  into RAM one at a time. The Core stays bounded-memory; the browser-based
  patient explorer is comfortable at 10k, and the 100k+ Batch is best examined
  with the Core CLI or the export bundle.
- **Disk.** Each 10k run records ~1.1 MB; recorded runs accumulate in
  `results/` (git-ignored). The launcher enforces a 256 MiB free-disk floor.

## 5. UI-behavioural limits

- **One run at a time.** A "busy" guard prevents concurrent runs; generation
  and validation block the app session during execution.
- **Run labels are auto-generated** (`lab-…`, `demo-…`, `rerun-…`) to
  guarantee uniqueness.
- **Comparison is per-run-index**, aligned by `run_index` across two identical
  executions.
- **Export download cap.** Browser download is offered for zips ≤ 100 MB;
  larger results are retrievable at the printed path.

## 6. Process limits

- **No acceptance claimed.** This deliverable stops at
  "GATE 2C — READY FOR FINAL ACCEPTANCE REVIEW". Final acceptance, release
  and scale qualification are issued by the Project Owner, not by this work.

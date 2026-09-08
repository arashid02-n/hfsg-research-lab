#!/usr/bin/env python3
"""Gate 2A - Minimal Integration Proof + Reproducibility Proof.

Runs the Research Lab Adapter twice with IDENTICAL inputs
(S1, config/base.yaml, master_seed 20260805, run_index 0 only):

    run A -> runs/min_integration_proof   (the live integration proof run)
    run B -> runs/repro_B                 (identical re-run)

then compares the two Result Stores:

    - configuration hash (effective configuration, Core function)
    - child seed (Core seed policy)
    - patient count, event count
    - validation status result
    - data fingerprints: SHA-256 over the written Parquet rows with the
      documented volatile `simulation_id` (and `created_at`) columns
      NORMALIZED/excluded (context.py: "Volatile fields ... MUST be excluded
      or normalized in reproducibility comparisons", MODEL.md section 28).
      Core code is not modified to do this; normalization is applied only
      at comparison time by the Lab proof harness.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_lab.adapter import ResearchLabAdapter  # noqa: E402

LAB = Path(__file__).resolve().parents[1]
VOLATILE_COLUMNS = ["simulation_id", "created_at"]
VOLATILE_JSON_KEYS = {
    "batch_id",          # batch-chronological Operational id (checkpoint)
    "dataset_id",        # timestamped Dataset id
    "generation_timestamp",
    "configuration_hash",  # manifest hash is over used_configuration.yaml
    # which embeds the volatile batch_id -> batch-scoped, not reproducible;
    "recomputed_configuration_hash",  # same property
}

MASTER_SEED = 20260805
SCENARIO = "S1"
TARGET = 1000
PLANNED = 1

RUN_A = LAB / "runs" / "min_integration_proof"
RUN_B = LAB / "runs" / "repro_B"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_fingerprint(parquet_path: Path) -> str:
    """SHA-256 over normalized rows (volatile columns excluded)."""
    frame = pd.read_parquet(parquet_path)
    frame = frame.drop(
        columns=[c for c in VOLATILE_COLUMNS if c in frame.columns]
    ).reset_index(drop=True)
    blob = frame.to_parquet(compression="zstd")
    return hashlib.sha256(blob).hexdigest()


def _strip_volatile(obj):
    if isinstance(obj, dict):
        return {
            key: _strip_volatile(value)
            for key, value in obj.items()
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(obj, list):
        return [_strip_volatile(item) for item in obj]
    return obj


def json_normalized_fingerprint(path: Path) -> str:
    """SHA-256 over the JSON artifact with documented volatile keys removed."""
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(_strip_volatile(data), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def artifact_fingerprints(out_dir: Path) -> tuple[dict, dict]:
    """Fingerprint the deterministic data artifacts of a Result Store.

    Returns (fingerprints, method_notes): parquet rows are hashed with the
    volatile columns excluded; JSON artifacts with volatile keys removed.
    """
    fingerprints: dict = {}
    notes: list[str] = []
    for pattern in (
        "patients/scenario_id=*/part-*.parquet",
        "patient_events/scenario_id=*/part-*.parquet",
        "aggregate_timeseries/scenario_id=*/part-*.parquet",
        "simulation_summary.parquet",
    ):
        for path in sorted(out_dir.glob(pattern)):
            key = str(path.relative_to(out_dir))
            fingerprints[key] = normalized_fingerprint(path)
    notes.append(
        "Parquet rows: SHA-256 with volatile columns "
        f"{VOLATILE_COLUMNS} excluded (context.py / MODEL.md section 28)."
    )
    for name in ("scenario_comparison.csv",):
        path = out_dir / name
        if path.is_file():
            fingerprints[name] = sha256_file(path)
    notes.append("scenario_comparison.csv: raw-byte SHA-256 (no volatile fields).")
    for name in ("validation_report.json", "dataset_manifest.json"):
        path = out_dir / name
        if path.is_file():
            fingerprints[name] = json_normalized_fingerprint(path)
    notes.append(
        "JSON artifacts: SHA-256 over normalized JSON with documented "
        f"volatile keys {sorted(VOLATILE_JSON_KEYS)} removed."
    )
    return fingerprints, notes


def main() -> int:
    adapter = ResearchLabAdapter()

    print(f"[1/3] live integration proof run -> {RUN_A}")
    proof = adapter.run_job(
        SCENARIO, RUN_A,
        target_patients=TARGET,
        planned_runs_per_scenario=PLANNED,
        master_seed=MASTER_SEED,
        run_label="min-integration-proof",
    )
    print(f"[2/3] identical reproducibility re-run -> {RUN_B}")
    repro = adapter.run_job(
        SCENARIO, RUN_B,
        target_patients=TARGET,
        planned_runs_per_scenario=PLANNED,
        master_seed=MASTER_SEED,
        run_label="repro-B",
    )
    assert proof.runs and repro.runs, "expected exactly one run per store"
    pa_, pb_ = proof.runs[0], repro.runs[0]

    print("[3/3] comparing the two Result Stores...")
    fa, notes = artifact_fingerprints(RUN_A)
    fb, _ = artifact_fingerprints(RUN_B)

    comparison = {
        "scenario_id": SCENARIO,
        "master_seed": MASTER_SEED,
        "config": "config/base.yaml (frozen)",
        "run_index": 0,
        "fields": {
            "configuration_hash": {
                "A": proof.effective_configuration_hash,
                "B": repro.effective_configuration_hash,
                "MATCH": proof.effective_configuration_hash
                == repro.effective_configuration_hash,
            },
            "child_seed": {
                "A": pa_.child_seed,
                "B": pb_.child_seed,
                "MATCH": pa_.child_seed == pb_.child_seed,
            },
            "patient_count": {
                "A": pa_.patient_count,
                "B": pb_.patient_count,
                "MATCH": pa_.patient_count == pb_.patient_count,
            },
            "event_count": {
                "A": pa_.event_count,
                "B": pb_.event_count,
                "MATCH": pa_.event_count == pb_.event_count,
            },
            "validation_status": {
                "A": proof.validation_status,
                "B": repro.validation_status,
                "MATCH": proof.validation_status == repro.validation_status,
            },
            "max_abs_mbe": {
                "A": pa_.max_abs_mbe,
                "B": pb_.max_abs_mbe,
                "MATCH": pa_.max_abs_mbe == pb_.max_abs_mbe,
            },
            "reconciliation_issues": {
                "A": pa_.reconciliation_issues,
                "B": pb_.reconciliation_issues,
                "MATCH": pa_.reconciliation_issues == pb_.reconciliation_issues,
            },
            "event_quota_mismatches": {
                "A": pa_.event_quota_mismatches,
                "B": pb_.event_quota_mismatches,
                "MATCH": pa_.event_quota_mismatches
                == pb_.event_quota_mismatches,
            },
        },
        "fingerprints": {
            "file": [],
        },
    }
    all_matched = True
    for key in sorted(set(fa) | set(fb)):
        match = key in fa and key in fb and fa[key] == fb[key]
        all_matched &= match
        comparison["fingerprints"]["file"].append(
            {
                "file": key,
                "sha256_A": fa.get(key),
                "sha256_B": fb.get(key),
                "MATCH": match,
            }
        )
    comparison["fingerprints"]["all_data_files_match"] = all_matched
    comparison["fingerprints"]["method"] = notes

    proof_path = LAB / "bench" / "results_proof_and_repro.json"
    proof_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    all_ok = all(v["MATCH"] for v in comparison["fields"].values()) and all_matched
    print(f"REPRODUCIBILITY: {'ALL MATCH' if all_ok else 'FAILURES PRESENT'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
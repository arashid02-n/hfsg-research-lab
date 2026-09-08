"""Output fingerprinting for the Lab (reproducibility comparison).

The fingerprint method follows MODEL.md section 28 and ``src/hfsg/context.py``:
volatile operational fields (``simulation_id``, ``created_at``) are excluded /
normalised at comparison time. Core code is NOT modified to produce these
fingerprints.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

VOLATILE_COLUMNS = ["simulation_id", "created_at"]
VOLATILE_JSON_KEYS = {
    "batch_id",
    "dataset_id",
    "generation_timestamp",
    "configuration_hash",
    "recomputed_configuration_hash",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_fingerprint(parquet_path: Path) -> str:
    """SHA-256 over normalized rows (volatile columns excluded)."""
    import pandas as pd

    frame = pd.read_parquet(parquet_path)
    frame = frame.drop(
        columns=[c for c in VOLATILE_COLUMNS if c in frame.columns]
    ).reset_index(drop=True)
    blob = frame.to_parquet(compression="zstd")
    return hashlib.sha256(blob).hexdigest()


def _strip_volatile(obj: Any) -> Any:
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
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(_strip_volatile(data), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_fingerprints(out_dir: Path) -> Tuple[Dict[str, str], List[str]]:
    """Fingerprint the deterministic artifacts of a Result Store.

    Returns (fingerprints, method_notes).
    """
    out_dir = Path(out_dir)
    fingerprints: Dict[str, str] = {}
    notes: List[str] = []

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
        f"{VOLATILE_COLUMNS} excluded (MODEL.md section 28)."
    )

    csv_path = out_dir / "scenario_comparison.csv"
    if csv_path.is_file():
        fingerprints["scenario_comparison.csv"] = sha256_file(csv_path)
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
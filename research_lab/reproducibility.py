"""Reproducibility comparator: "Re-run with Same Seed" for the Validation /
Reproducibility Center.

Re-runs the exact original job (same scenario, configuration incl. horizon,
master seed, target patients, run cap, custom profile) into a fresh Result
Store and compares the two executions side-by-side per run index.

The comparison fields are the frozen-Core results read from the two stores:
configuration hash, child seed, patient count, event count, validation result
and output fingerprints (volatile fields normalised per MODEL.md section 28).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .adapter import ResearchLabAdapter
from .fingerprint import run_fingerprints
from .result_store import RunStore


class ReproducibilityComparator:
    def __init__(self, adapter: ResearchLabAdapter, store: RunStore) -> None:
        self.adapter = adapter
        self.store = store

    def rerun_same_seed(self, original_label: str) -> Dict[str, Any]:
        """Run the exact original job again and compare both Result Stores."""
        original_dir = self.store.out_dir(original_label)
        spec = self.store.job_spec(original_label)
        if not original_dir.is_dir() or not spec:
            raise KeyError(f"no run found for label {original_label!r}")
        scenario = spec["scenario_id"]

        rerun_label = self.store.new_label(scenario, prefix="rerun")
        rerun_dir = self.store.out_dir(rerun_label)

        outcome = self.adapter.run_job(
            scenario,
            rerun_dir,
            target_patients=int(spec["target_patients"]),
            planned_runs_per_scenario=int(spec["planned_runs_per_scenario"]),
            master_seed=int(spec["master_seed"]),
            simulation_hours=float(spec["simulation_hours"]),
            custom_profile=dict(spec["custom_profile"])
            if spec.get("custom_profile")
            else None,
            run_label=rerun_label,
        )

        comparison = self.compare(original_dir, rerun_dir, scenario)
        comparison["original_label"] = original_dir.name
        comparison["rerun_label"] = rerun_label
        comparison["rerun_status"] = outcome.validation_status
        return comparison

    # -- comparison -------------------------------------------------------
    def compare(
        self, a_dir: Path, b_dir: Path, scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        a_summary = self._read_summary(a_dir)
        b_summary = self._read_summary(b_dir)
        scenario_id = scenario_id or (str(a_summary["scenario_id"].iloc[0]) if a_summary is not None and not a_summary.empty else "?")

        rows: List[Dict[str, Any]] = []
        n_a = len(a_summary) if a_summary is not None else 0
        n_b = len(b_summary) if b_summary is not None else 0
        n = max(n_a, n_b)

        for i in range(n):
            ra = self._row(a_summary, i)
            rb = self._row(b_summary, i)
            rows.append(
                {
                    "run_index": i,
                    "configuration_hash": {
                        "A": ra.get("configuration_hash"),
                        "B": rb.get("configuration_hash"),
                        "MATCH": ra.get("configuration_hash") == rb.get("configuration_hash"),
                    },
                    "child_seed": {
                        "A": ra.get("child_seed"),
                        "B": rb.get("child_seed"),
                        "MATCH": ra.get("child_seed") == rb.get("child_seed"),
                    },
                    "patient_count": {
                        "A": ra.get("total_patients"),
                        "B": rb.get("total_patients"),
                        "MATCH": ra.get("total_patients") == rb.get("total_patients"),
                    },
                    "event_count": {
                        "A": ra.get("total_events"),
                        "B": rb.get("total_events"),
                        "MATCH": ra.get("total_events") == rb.get("total_events"),
                    },
                    "max_abs_mbe": {
                        "A": ra.get("max_abs_mbe"),
                        "B": rb.get("max_abs_mbe"),
                        "MATCH": ra.get("max_abs_mbe") == rb.get("max_abs_mbe"),
                    },
                }
            )

        status_a = RunStore.report_status_dir(a_dir)
        status_b = RunStore.report_status_dir(b_dir)

        fa, notes_a = run_fingerprints(a_dir)
        fb, notes_b = run_fingerprints(b_dir)
        fingerprint_rows = []
        all_files_match = True
        for key in sorted(set(fa) | set(fb)):
            match = key in fa and key in fb and fa[key] == fb[key]
            all_files_match &= match
            fingerprint_rows.append(
                {
                    "file": key,
                    "sha256_A": fa.get(key),
                    "sha256_B": fb.get(key),
                    "MATCH": bool(match),
                }
            )

        return {
            "scenario_id": scenario_id,
            "status": {
                "A": status_a,
                "B": status_b,
                "MATCH": status_a == status_b,
            },
            "runs": rows,
            "all_run_fields_match": all(
                all(v.get("MATCH") for v in row.values() if isinstance(v, dict) and "MATCH" in v)
                for row in rows
            ),
            "fingerprints": {
                "files": fingerprint_rows,
                "all_data_files_match": all_files_match,
                "method": notes_a or notes_b,
            },
            "overall_match": (
                status_a == status_b
                and all_rows_match(rows)
                and all_files_match
            ),
        }

    @staticmethod
    def _read_summary(dir_path: Path) -> Optional[pd.DataFrame]:
        path = dir_path / "simulation_summary.parquet"
        if not path.is_file():
            return None
        return pd.read_parquet(path)

    @staticmethod
    def _row(df: Optional[pd.DataFrame], index: int) -> Dict[str, Any]:
        if df is None or index >= len(df):
            return {
                "configuration_hash": None,
                "child_seed": None,
                "total_patients": None,
                "total_events": None,
                "max_abs_mbe": None,
            }
        row = df.iloc[index]
        out = {}
        for key in ("configuration_hash", "child_seed", "total_patients", "total_events", "max_abs_mbe"):
            out[key] = row.get(key) if key in row.index else None
        return out


def all_rows_match(rows: List[Dict[str, Any]]) -> bool:
    for row in rows:
        for key, value in row.items():
            if isinstance(value, dict) and "MATCH" in value and not value["MATCH"]:
                return False
    return True
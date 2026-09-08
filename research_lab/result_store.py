"""Lab Result Store: independent directory of recorded runs.

Each recorded run lives in ``<root>/<label>/`` and contains the frozen Core
output bundle plus the Lab ``job_spec.json``. The Lab never writes into the
frozen Core's ``data/output``; the Validated Phase 1 Release is only ever READ.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .adapter import JobSpec

APP_LABEL_PREFIX = "lab"
DEMO_LABEL_PREFIX = "demo"


class RunStore:
    """Indexes and reads Result Store runs for the Streamlit UI."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # -- index ------------------------------------------------------------
    def _iter_runs(self) -> List[Dict[str, Any]]:
        runs: List[Dict[str, Any]] = []
        for spec_path in sorted(self.root.glob("*/job_spec.json")):
            label = spec_path.parent.name
            with spec_path.open("r", encoding="utf-8") as handle:
                spec = json.load(handle)
            runs.append({"label": label, "out_dir": spec_path.parent, "spec": spec})
        runs.sort(key=lambda r: r.get("spec", {}).get("created_at", ""), reverse=True)
        return runs

    def list_runs(self) -> List[Dict[str, Any]]:
        """Recorded runs with live-read status/counts, newest first."""
        rows: List[Dict[str, Any]] = []
        for run in self._iter_runs():
            label = run["label"]
            spec = run["spec"]
            summary = self._load_summary(run["out_dir"])
            patients = int(summary["total_patients"].sum()) if summary is not None and not summary.empty else None
            events = int(summary["total_events"].sum()) if summary is not None and not summary.empty else None
            status = self.report_status(label)
            rows.append(
                {
                    "label": label,
                    "out_dir": str(run["out_dir"]),
                    "scenario_id": spec.get("scenario_id"),
                    "run_index": "0" if summary is not None and not summary.empty else "-",
                    "master_seed": spec.get("master_seed"),
                    "simulation_hours": spec.get("simulation_hours"),
                    "target_patients": spec.get("target_patients"),
                    "custom_profile": spec.get("custom_profile"),
                    "config_hash": self._effective_hash(run["out_dir"]),
                    "patients": patients,
                    "events": events,
                    "validation_status": status,
                    "created_at": spec.get("created_at"),
                    "is_demo": label.startswith(DEMO_LABEL_PREFIX),
                }
            )
        return rows

    def get(self, label: str) -> Optional[Dict[str, Any]]:
        for row in self.list_runs():
            if row["label"] == label:
                return row
        return None

    def out_dir(self, label: str) -> Path:
        return self.root / label

    def job_spec(self, label: str) -> Optional[Dict[str, Any]]:
        path = self.out_dir(label) / "job_spec.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # -- run creation -----------------------------------------------------
    def new_label(self, scenario_id: str, prefix: str = APP_LABEL_PREFIX) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        seq = 0
        while True:
            label = f"{prefix}-{scenario_id}-{stamp}-{seq}"
            if not self.out_dir(label).exists():
                return label
            seq += 1

    # -- content readers --------------------------------------------------
    def _load_summary(self, out_dir: Path) -> Optional[pd.DataFrame]:
        path = out_dir / "simulation_summary.parquet"
        if not path.is_file():
            return None
        return pd.read_parquet(path)

    def summary(self, label: str) -> Optional[pd.DataFrame]:
        return self._load_summary(self.out_dir(label))

    def aggregate(self, label: str) -> pd.DataFrame:
        frames = []
        for path in sorted(self.out_dir(label).glob("aggregate_timeseries/scenario_id=*/part-*.parquet")):
            frames.append(pd.read_parquet(path))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def patients(self, label: str) -> pd.DataFrame:
        frames = []
        for path in sorted(self.out_dir(label).glob("patients/scenario_id=*/part-*.parquet")):
            frames.append(pd.read_parquet(path))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def events(self, label: str) -> pd.DataFrame:
        frames = []
        for path in sorted(self.out_dir(label).glob("patient_events/scenario_id=*/part-*.parquet")):
            frames.append(pd.read_parquet(path))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def validation_report(self, label: str) -> Optional[Dict[str, Any]]:
        path = self.out_dir(label) / "validation_report.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def dataset_manifest(self, label: str) -> Optional[Dict[str, Any]]:
        path = self.out_dir(label) / "dataset_manifest.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def report_status(self, label: str) -> str:
        return self.report_status_dir(self.out_dir(label))

    @staticmethod
    def report_status_dir(out_dir: Path) -> str:
        report = out_dir / "validation_report.json"
        if not report.is_file():
            return "UNKNOWN"
        data = json.loads(report.read_text(encoding="utf-8"))
        return str(data.get("validation_status", "UNKNOWN"))

    def _effective_hash(self, out_dir: Path) -> Optional[str]:
        report = out_dir / "validation_report.json"
        if not report.is_file():
            return None
        data = json.loads(report.read_text(encoding="utf-8"))
        return data.get("checks", {}).get("manifest", {}).get("recomputed_configuration_hash")

    # -- export -----------------------------------------------------------
    def export_zip(self, label: str, export_dir: str | Path) -> Path:
        """Bundle a run's Result Store into a single zip (deterministic order)."""
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        target = export_dir / f"{label}.zip"
        store_root = self.out_dir(label)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(store_root.rglob("*")):
                if path.is_file():
                    zf.write(path, arcname=str(path.relative_to(store_root)))
        return target

    @staticmethod
    def info() -> Dict[str, str]:
        from .identity import LINEAGE_STATEMENT

        return {"statement": LINEAGE_STATEMENT}


def read_scenario_override_summary(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Human-readable effective-scenario summary for the UI."""
    scenario = spec.get("scenario_id")
    custom = spec.get("custom_profile")
    summary: Dict[str, Any] = {"scenario_id": scenario}
    if scenario == "CUSTOM" and custom:
        summary["effective_settings"] = custom
    return summary
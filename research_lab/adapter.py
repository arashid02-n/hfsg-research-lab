"""Research Lab Adapter — thin orchestration layer over the frozen HFSG Core.

Gate 2A: Research Lab Adapter -> Frozen HFSG Core -> S1 -> Live Generation ->
Validation -> Result Store.
Gate 2B: same Adapter, extended with the two Lab-side runtime drivers the UI
needs, while remaining a thin orchestration layer:

    - runtime Configuration construction (approved EXPOsed Lab controls only):
        * simulation horizon override  (frozen default 720 h)
        * CUSTOM parameter profile     (frozen approved limits)
      Both are validated by the frozen Core (ConfigurationLoader.from_data /
      ScenarioManager.validate_custom); the frozen config file is never edited.
    - Result Store bookkeeping (job_spec.json) so "Re-run with Same Seed" can
      reconstruct the exact original inputs.

THE ADAPTER CONTAINS NO MODEL LOGIC. It does not re-implement any model
equation, the Aggregate Flow Engine, the Integer Flow Allocator, the Patient
Generator, the Patient Event Generator, Reconciliation, or Validation. It only
orchestrates the frozen Core's public entry points:

    hfsg.config.ConfigurationLoader        (load/validate config)
    hfsg.scenarios.ScenarioManager         (effective configuration, CUSTOM limits)
    hfsg.scenarios.configuration_hash      (effective config hash)
    hfsg.seeds.derive_child_seed           (child-seed bookkeeping)
    hfsg.batch.BatchRunner                 (bounded-memory generation)
    hfsg.batch.validate_batch_outputs      (bounded-memory validation)

Frozen Core repository / configuration / tests are NOT modified.
"""

from __future__ import annotations

import copy
import json
import resource
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- import the frozen Core (never modified), resolved portably ----------
# The Core directory is resolved at runtime (bundled -> env -> local config ->
# user-selected). No developer-specific path is hard-coded. The Core modules
# are imported inside ResearchLabAdapter.__init__ so that a missing Core
# surfaces a friendly CoreNotFoundError instead of an ImportError traceback.
from .core import CoreNotFoundError, resolve_core_dir
from .identity import LINEAGE_STATEMENT

FROZEN_HORIZON_HOURS = 720.0


@dataclass(frozen=True)
class RunOutcome:
    """One completed simulation run, as reported by the frozen Core."""

    simulation_id: str
    scenario_id: str
    run_index: int
    master_seed: int
    child_seed: int
    patient_count: int
    event_count: int
    max_abs_mbe: float
    reconciliation_issues: int
    event_quota_mismatches: int
    configuration_hash: str


@dataclass(frozen=True)
class JobSpec:
    """Exact Lab job inputs, persisted to the Result Store (job_spec.json)."""

    lab_run_label: str
    scenario_id: str
    master_seed: int
    target_patients: int
    planned_runs_per_scenario: int
    simulation_hours: float
    custom_profile: Optional[Dict[str, Any]]
    frozen_config_source: str
    frozen_core_statement: str
    engine_version: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lab_run_label": self.lab_run_label,
            "scenario_id": self.scenario_id,
            "master_seed": self.master_seed,
            "target_patients": self.target_patients,
            "planned_runs_per_scenario": self.planned_runs_per_scenario,
            "simulation_hours": self.simulation_hours,
            "custom_profile": dict(self.custom_profile)
            if self.custom_profile
            else None,
            "frozen_config_source": self.frozen_config_source,
            "frozen_core_statement": self.frozen_core_statement,
            "engine_version": self.engine_version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobSpec":
        return cls(**data)


@dataclass(frozen=True)
class BatchOutcome:
    """Overall outcome of one Adapter job (one scenario batch)."""

    run_label: str
    scenario_id: str
    master_seed: int
    target_patients: int
    planned_runs_per_scenario: int
    simulation_hours: float
    batch_id: str
    out_dir: Path
    runs: List[RunOutcome]
    cumulative_patients: int
    cumulative_events: int
    generation_elapsed_seconds: float
    validation_elapsed_seconds: float
    peak_rss_bytes: int
    output_size_bytes: int
    validation_report: Dict[str, Any]
    effective_configuration_hash: str
    job_spec: JobSpec

    @property
    def validation_status(self) -> str:
        return self.validation_report.get("validation_status", "UNKNOWN")

    @property
    def critical_failures(self) -> List[str]:
        return self.validation_report.get("critical_failures", [])

    @property
    def max_abs_mbe(self) -> float:
        return max((r.max_abs_mbe for r in self.runs), default=0.0)

    @property
    def total_reconciliation_issues(self) -> int:
        return sum(r.reconciliation_issues for r in self.runs)

    @property
    def total_event_quota_mismatches(self) -> int:
        return sum(r.event_quota_mismatches for r in self.runs)

    @property
    def child_seeds(self) -> List[int]:
        return [r.child_seed for r in self.runs]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_label": self.run_label,
            "scenario_id": self.scenario_id,
            "master_seed": self.master_seed,
            "target_patients": self.target_patients,
            "planned_runs_per_scenario": self.planned_runs_per_scenario,
            "simulation_hours": self.simulation_hours,
            "batch_id": self.batch_id,
            "out_dir": str(self.out_dir),
            "runs": [
                {
                    "simulation_id": r.simulation_id,
                    "scenario_id": r.scenario_id,
                    "run_index": r.run_index,
                    "master_seed": r.master_seed,
                    "child_seed": r.child_seed,
                    "patient_count": r.patient_count,
                    "event_count": r.event_count,
                    "max_abs_mbe": r.max_abs_mbe,
                    "reconciliation_issues": r.reconciliation_issues,
                    "event_quota_mismatches": r.event_quota_mismatches,
                    "configuration_hash": r.configuration_hash,
                }
                for r in self.runs
            ],
            "cumulative_patients": self.cumulative_patients,
            "cumulative_events": self.cumulative_events,
            "generation_elapsed_seconds": self.generation_elapsed_seconds,
            "validation_elapsed_seconds": self.validation_elapsed_seconds,
            "peak_rss_bytes": self.peak_rss_bytes,
            "output_size_bytes": self.output_size_bytes,
            "validation_status": self.validation_status,
            "critical_failures": self.critical_failures,
            "max_abs_mbe": self.max_abs_mbe,
            "total_reconciliation_issues": self.total_reconciliation_issues,
            "total_event_quota_mismatches": self.total_event_quota_mismatches,
            "effective_configuration_hash": self.effective_configuration_hash,
            "job_spec": self.job_spec.to_dict(),
        }


class ResearchLabAdapter:
    """Calls the frozen HFSG Core exactly as the approved CLI does.

    The only inputs that differ from the approved defaults are the approved
    EXPOsed Lab controls (scenario, master seed, horizon, target patients, run
    cap, CUSTOM multipliers) — every one of them is validated by the frozen
    Core before a run starts.
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        core_dir: str | Path | None = None,
    ) -> None:
        core_dir = Path(core_dir) if core_dir else resolve_core_dir()
        if core_dir is None:
            raise CoreNotFoundError(
                "HFSG Core not found. Place an approved Core in the "
                "`hfsg_core/` folder, set HFSG_CORE_DIR, or select the Core "
                "location on the About / System Information page."
            )
        self.core_dir = core_dir
        self.core_src = core_dir / "src"
        if str(self.core_src) not in sys.path:
            sys.path.insert(0, str(self.core_src))

        # Lazy frozen-Core import (inside __init__ so a missing Core is a
        # friendly CoreNotFoundError, not a module-level ImportError).
        import hfsg  # noqa: F401  frozen Core (version only)
        from hfsg.batch import BatchRunner, validate_batch_outputs  # frozen Core
        from hfsg.config import Configuration, ConfigurationLoader  # frozen Core
        from hfsg.scenarios import ScenarioManager, configuration_hash  # frozen Core
        from hfsg.seeds import derive_child_seed  # frozen Core

        self._hfsg = hfsg
        self._BatchRunner = BatchRunner
        self._validate_batch_outputs = validate_batch_outputs
        self._Configuration = Configuration
        self._ConfigurationLoader = ConfigurationLoader
        self._ScenarioManager = ScenarioManager
        self._configuration_hash = configuration_hash
        self._derive_child_seed = derive_child_seed

        config_path = config_path or str(core_dir / "config" / "base.yaml")
        self.loader = self._ConfigurationLoader()
        self.frozen_config = self.loader.load(config_path)
        self.manager = self._ScenarioManager(self.frozen_config)
        self.frozen_config_path = Path(config_path)

    # -- frozen-Core knowledge surfaced without reimplementation ----------
    def scenario_ids(self) -> List[str]:
        return list(self.manager.scenario_ids())

    def has_scenario(self, scenario_id: str) -> bool:
        return scenario_id in self.manager.scenario_ids()

    def scenario_definition(self, scenario_id: str) -> Dict[str, Any]:
        return self.manager.scenario_definition(scenario_id)

    def custom_limits(self) -> Dict[str, Any]:
        return dict(
            self.frozen_config.data.get("scenarios", {}).get(
                "custom_parameter_limits", {}
            )
        )

    def frozen_defaults(self) -> Dict[str, Any]:
        return {
            "simulation_hours": float(self.frozen_config.simulation_hours),
            "master_seed": int(self.frozen_config.reproducibility["master_seed"]),
            "capacities": dict(self.frozen_config.data.get("capacities", {})),
            "initial_conditions": dict(
                self.frozen_config.data.get("initial_conditions", {})
            ),
        }

    def validate_custom(self, profile: Dict[str, Any]) -> None:
        """Delegate to the frozen ScenarioManager approved-limit check."""
        self.manager.validate_custom(profile)

    # -- runtime Configuration (approved Lab controls only) ---------------
    def runtime_config(
        self,
        scenario_id: str,
        simulation_hours: Optional[float] = None,
        custom_profile: Optional[Dict[str, Any]] = None,
    ) -> Configuration:
        """Build a validated runtime Configuration without touching the frozen
        config. Only the approved EXPOsed controls may differ from the frozen
        defaults; validation is delegated to the frozen Core loader."""
        data = copy.deepcopy(self.frozen_config.data)

        horizon = (
            float(simulation_hours)
            if simulation_hours is not None
            else float(self.frozen_config.simulation_hours)
        )
        if horizon <= 0:
            raise ValueError(f"simulation_hours must be > 0, got {horizon}")
        # Preserve the frozen config's integer type for integral horizons so
        # an identity run hashes exactly like the frozen default (720 vs 720.0).
        data["simulation_hours"] = int(horizon) if horizon.is_integer() else horizon

        if scenario_id == "CUSTOM" and custom_profile is not None:
            self.manager.validate_custom(custom_profile)  # frozen Core check
            data["scenarios"]["definitions"]["CUSTOM"] = dict(custom_profile)

        # Validated by the frozen Core configuration validator.
        return self.loader.from_data(data, source=str(self.frozen_config_path))

    def effective_configuration_hash(
        self,
        scenario_id: str,
        simulation_hours: Optional[float] = None,
        custom_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Delegates to the Core's canonical effective-config hash."""
        runtime = self.runtime_config(scenario_id, simulation_hours, custom_profile)
        manager = self._ScenarioManager(runtime)
        return self._configuration_hash(manager.effective_configuration(scenario_id))

    def child_seed(self, master_seed: int, scenario_id: str, run_index: int) -> int:
        """Delegates to the Core seed policy (hfsg-child-seed-v1)."""
        return self._derive_child_seed(master_seed, scenario_id, run_index)

    # -- one job: generate -> validate -> Result Store --------------------
    def run_job(
        self,
        scenario_id: str,
        out_dir: str | Path,
        *,
        target_patients: int,
        planned_runs_per_scenario: int,
        master_seed: Optional[int] = None,
        simulation_hours: Optional[float] = None,
        custom_profile: Optional[Dict[str, Any]] = None,
        run_label: str = "",
    ) -> BatchOutcome:
        if not self.has_scenario(scenario_id):
            raise ValueError(
                f"unknown scenario {scenario_id!r}; known: {self.scenario_ids()}"
            )
        if custom_profile is not None:
            self.manager.validate_custom(custom_profile)  # frozen Core check

        runtime = self.runtime_config(scenario_id, simulation_hours, custom_profile)
        out_dir = Path(out_dir)

        # 1) LIVE GENERATION (frozen Core, bounded memory, one run at a time)
        started = time.perf_counter()
        runner = self._BatchRunner(
            runtime,
            out_dir,
            target_patients=int(target_patients),
            planned_runs_per_scenario=int(planned_runs_per_scenario),
            scenario_ids=[scenario_id],
            master_seed=master_seed,
        )
        records = runner.run()
        runner.write_artifacts(validation_status="VALIDATION")
        generation_elapsed = time.perf_counter() - started
        master_seed_used = int(runner.master_seed)

        # 2) VALIDATION (frozen Core, bounded memory)
        vstarted = time.perf_counter()
        report = self._validate_batch_outputs(out_dir)
        validation_elapsed = time.perf_counter() - vstarted

        # 3) RESULT STORE bookkeeping: reflect the validation outcome in the
        #    authoritative manifest and persist the Lab validation report.
        m_path = out_dir / "dataset_manifest.json"
        if m_path.is_file():
            with m_path.open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)
            manifest["validation_status"] = report["validation_status"]
            with m_path.open("w", encoding="utf-8") as handle:
                json.dump(manifest, handle, indent=2)
        report["elapsed_seconds"] = None  # keep frozen-report determinism
        (out_dir / "validation_report.json").write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )

        # 4) Lab job spec (exact inputs, for "Re-run with Same Seed").
        label = run_label or out_dir.name
        spec = JobSpec(
            lab_run_label=label,
            scenario_id=scenario_id,
            master_seed=master_seed_used,
            target_patients=int(target_patients),
            planned_runs_per_scenario=int(planned_runs_per_scenario),
            simulation_hours=float(runtime.simulation_hours),
            custom_profile=dict(custom_profile) if custom_profile else None,
            frozen_config_source=str(self.frozen_config_path),
            frozen_core_statement=LINEAGE_STATEMENT,
            engine_version=self._hfsg.__version__,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        (out_dir / "job_spec.json").write_text(
            json.dumps(spec.to_dict(), indent=2), encoding="utf-8"
        )

        outcomes = [
            RunOutcome(
                simulation_id=r.simulation_id,
                scenario_id=r.scenario_id,
                run_index=r.run_index,
                master_seed=r.master_seed,
                child_seed=r.child_seed,
                patient_count=r.patient_count,
                event_count=r.event_count,
                max_abs_mbe=r.max_abs_mbe,
                reconciliation_issues=r.reconciliation_issues,
                event_quota_mismatches=r.event_quota_mismatches,
                configuration_hash=r.configuration_hash,
            )
            for r in records
        ]

        return BatchOutcome(
            run_label=label,
            scenario_id=scenario_id,
            master_seed=master_seed_used,
            target_patients=int(target_patients),
            planned_runs_per_scenario=int(planned_runs_per_scenario),
            simulation_hours=float(runtime.simulation_hours),
            batch_id=runner._batch_id,
            out_dir=out_dir,
            runs=outcomes,
            cumulative_patients=runner.cumulative_patients,
            cumulative_events=runner.cumulative_events,
            generation_elapsed_seconds=generation_elapsed,
            validation_elapsed_seconds=validation_elapsed,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            output_size_bytes=_directory_size(out_dir),
            validation_report=report,
            effective_configuration_hash=self.effective_configuration_hash(
                scenario_id, simulation_hours, custom_profile
            ),
            job_spec=spec,
        )


def _directory_size(path: Path) -> int:
    """Recursive total file size in bytes of a Result Store directory."""
    total = 0
    for p in Path(path).rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total
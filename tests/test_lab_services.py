"""Unit tests for the Lab's non-UI services (fast, no live Core runs).

Covers: identity verification, adapter scenario/custom-limit delegation,
effective-configuration hashing, fingerprints, and the reproducibility
comparator on the real Gate 2A recorded stores.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from research_lab.adapter import ResearchLabAdapter
from research_lab.identity import verified_identity
from research_lab.fingerprint import run_fingerprints
from research_lab.result_store import RunStore
from research_lab.reproducibility import ReproducibilityComparator

LAB = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def adapter() -> ResearchLabAdapter:
    return ResearchLabAdapter()


def test_identity_verification_ok() -> None:
    identity = verified_identity()
    assert identity["engine_version"] == "0.6.0"
    assert identity["head_commit"] == "affe7c8"
    assert identity["baseline_commit_present"] is True
    assert identity["tracked_files_modified"] is False
    assert identity["core_integrity_ok"] is True


def test_scenario_ids_and_defaults(adapter: ResearchLabAdapter) -> None:
    assert adapter.scenario_ids() == ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "CUSTOM"]
    defaults = adapter.frozen_defaults()
    assert defaults["simulation_hours"] == 720
    assert defaults["master_seed"] == 20260805


def test_effective_hash_matches_frozen_default(adapter: ResearchLabAdapter) -> None:
    # Identity run: no overrides -> must equal the recorded Gate 2A S1 hash.
    assert adapter.effective_configuration_hash("S1").startswith(
        "e460cf544c622cfa495fa6cfe69a68605e9d57cd82ad95ba6df07e539006ced8"
    )


def test_custom_profile_limits(adapter: ResearchLabAdapter) -> None:
    adapter.validate_custom(
        {"arrivals_multiplier": 1.25, "icu_capacity_multiplier": 1.0, "discharge_multiplier": 1.1}
    )
    with pytest.raises(Exception):
        adapter.validate_custom({"arrivals_multiplier": 2.5})
    with pytest.raises(Exception):
        adapter.validate_custom({"arrivals_wave": {"enabled": True, "factor": 2.0}})
    with pytest.raises(Exception):
        adapter.validate_custom({"not_a_parameter": 1.0})


def test_custom_effective_hash_changes(adapter: ResearchLabAdapter) -> None:
    base = adapter.effective_configuration_hash("S1")
    custom = adapter.effective_configuration_hash(
        "CUSTOM",
        custom_profile={"arrivals_multiplier": 1.25, "icu_capacity_multiplier": 1.0, "discharge_multiplier": 1.1},
    )
    assert custom != base


def test_gate2a_stores_reproduce(gate2a_stores) -> None:
    a_dir, b_dir = gate2a_stores
    comparator = ReproducibilityComparator(ResearchLabAdapter(), RunStore(LAB / "runs"))
    result = comparator.compare(a_dir, b_dir, "S1")
    assert result["overall_match"] is True
    assert result["status"]["A"] == "VALIDATED"
    assert result["status"]["B"] == "VALIDATED"
    assert all(r["patient_count"]["MATCH"] for r in result["runs"])
    assert result["fingerprints"]["all_data_files_match"] is True


def test_fingerprint_method_notes(gate2a_stores) -> None:
    fingerprints, notes = run_fingerprints(gate2a_stores[0])
    assert notes, "method notes must be recorded for provenance"
    assert any(k.startswith("patients/") for k in fingerprints)
    assert all(len(v) == 64 for v in fingerprints.values())


def test_algo_disclaimer() -> None:
    # Guard against silently labeling an assumption as PAPER provenance.
    from research_lab.ui.state import APPROVED_CUSTOM_LIMITS

    assert APPROVED_CUSTOM_LIMITS["arrivals_multiplier"] == {
        "min": 0.5, "max": 2.0, "default": 1.25
    }
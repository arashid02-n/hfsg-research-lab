"""Frozen HFSG Core lineage — single, verified identity statement.

Standard statement used throughout the Lab UI and documentation:

    HFSG Core v0.6.0 — Phase-1 validated baseline 08032c3;
    current frozen integration commit affe7c8

Every value is verified against the resolved Core repository at runtime (the
Core directory is resolved portably — see ``research_lab/core.py``), so the UI
can never display a contradictory or stale Core reference.

The reference constants below are only ever DISPLAYED after verification; they
are never used to authorise a live run on their own. A live run is authorised
only when ``core_integrity_ok`` is True against the actual resolved Core.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .core import resolve_core_dir

EXPECTED_VERSION = "0.6.0"
VALIDATED_BASELINE_COMMIT = "08032c3"
FROZEN_INTEGRATION_COMMIT = "affe7c8"

LINEAGE_STATEMENT = (
    "HFSG Core v0.6.0 — Phase-1 validated baseline 08032c3; "
    "current frozen integration commit affe7c8"
)


def _git(core_dir: Path, *args: str) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(core_dir), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = (out.stdout or "").strip()
        return text or None
    except (OSError, subprocess.SubprocessError):
        return None


def _read_version(core_dir: Path) -> Optional[str]:
    init = core_dir / "src" / "hfsg" / "__init__.py"
    if not init.is_file():
        return None
    m = re.search(r'__version__\s*=\s*"([^"]+)"', init.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def _not_found_identity() -> Dict[str, Any]:
    return {
        "statement": LINEAGE_STATEMENT,
        "engine_version": None,
        "version_match": False,
        "expected_version": EXPECTED_VERSION,
        "validated_baseline_commit": VALIDATED_BASELINE_COMMIT,
        "baseline_commit_present": False,
        "frozen_integration_commit": FROZEN_INTEGRATION_COMMIT,
        "head_commit": None,
        "head_matches_frozen": False,
        "tracked_files_modified": None,
        "core_dir": None,
        "core_found": False,
        "core_integrity_ok": False,
        "error": "HFSG Core not found.",
    }


def verified_identity(core_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Verify the lineage constants against the resolved Core repository.

    If ``core_dir`` is omitted it is resolved portably (bundled -> env ->
    local config). When no Core is available the returned identity reports
    ``core_found=False`` / ``core_integrity_ok=False`` with a friendly error,
    and callers must block live runs.
    """
    if core_dir is None:
        core_dir = resolve_core_dir()
    if core_dir is None:
        return _not_found_identity()

    core_dir = Path(core_dir)
    head = _git(core_dir, "rev-parse", "HEAD")
    baseline_ok = (
        _git(core_dir, "rev-parse", "--verify", f"{VALIDATED_BASELINE_COMMIT}^{{commit}}")
        is not None
    )
    dirty = _git(core_dir, "status", "--porcelain") or ""
    version = _read_version(core_dir)

    head_short = head[:7] if head else None
    tracked_dirty = any(
        line and not line.startswith("??") for line in dirty.splitlines()
    )

    return {
        "statement": LINEAGE_STATEMENT,
        "engine_version": version,
        "version_match": version == EXPECTED_VERSION,
        "expected_version": EXPECTED_VERSION,
        "validated_baseline_commit": VALIDATED_BASELINE_COMMIT,
        "baseline_commit_present": bool(baseline_ok),
        "frozen_integration_commit": FROZEN_INTEGRATION_COMMIT,
        "head_commit": head_short,
        "head_matches_frozen": head_short is not None
        and head_short == FROZEN_INTEGRATION_COMMIT,
        "tracked_files_modified": tracked_dirty,
        "core_dir": str(core_dir),
        "core_found": True,
        "core_integrity_ok": (
            version == EXPECTED_VERSION
            and bool(baseline_ok)
            and head_short == FROZEN_INTEGRATION_COMMIT
            and not tracked_dirty
        ),
    }

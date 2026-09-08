"""Frozen HFSG Core lineage — single, verified identity statement.

Standard statement used throughout the Lab UI and documentation:

    HFSG Core v0.6.0 — Phase-1 validated baseline 08032c3;
    current frozen integration commit affe7c8

Every value is verified against the frozen repository at runtime, so the UI
can never display a contradictory or stale Core reference.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

FROZEN_CORE_DIR = Path("/home/rashid/projects/hfsg")
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


def verified_identity() -> Dict[str, Any]:
    """Verify the lineage constants against the frozen repository."""
    head = _git(FROZEN_CORE_DIR, "rev-parse", "HEAD")
    baseline_ok = _git(FROZEN_CORE_DIR, "rev-parse", "--verify",
                       f"{VALIDATED_BASELINE_COMMIT}^{{commit}}") is not None
    dirty = _git(FROZEN_CORE_DIR, "status", "--porcelain") or ""
    version = _read_version(FROZEN_CORE_DIR)

    head_short = head[:7] if head else None
    tracked_dirty = any(line and not line.startswith("??") for line in dirty.splitlines())

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
        "core_dir": str(FROZEN_CORE_DIR),
        "core_integrity_ok": (
            version == EXPECTED_VERSION
            and baseline_ok
            and head_short == FROZEN_INTEGRATION_COMMIT
            and not tracked_dirty
        ),
    }
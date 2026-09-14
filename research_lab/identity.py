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

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .core import resolve_core_dir

EXPECTED_VERSION = "0.6.0"
VALIDATED_BASELINE_COMMIT = "08032c3"
FROZEN_INTEGRATION_COMMIT = "affe7c8"

# Packaged-Core provenance file, written by scripts/build_package.py when the
# approved frozen Core is bundled. It records the identity facts that were
# verified against the git checkout at build time, so the Lab can verify the
# Core identity on a machine where `git` is not installed.
PROVENANCE_FILE = "CORE_PROVENANCE.json"

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


def _read_provenance(core_dir: Path) -> Optional[Dict[str, Any]]:
    path = core_dir / PROVENANCE_FILE
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


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
        "verification_method": "none",
        "core_dir": None,
        "core_found": False,
        "core_integrity_ok": False,
        "error": "HFSG Core not found.",
    }


def verified_identity(core_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Verify the lineage constants against the resolved Core.

    Verification is git-based when a git checkout is available; otherwise it
    falls back to the packaged ``CORE_PROVENANCE.json`` (written at build time
    from the verified frozen checkout). This keeps the identity check
    meaningful on machines where ``git`` is not installed, without weakening
    it: the provenance file is only ever produced by the build from a verified
    frozen Core, and the package integrity is protected by SHA256SUMS.
    """
    if core_dir is None:
        core_dir = resolve_core_dir()
    if core_dir is None:
        return _not_found_identity()

    core_dir = Path(core_dir)
    version = _read_version(core_dir)
    provenance = _read_provenance(core_dir)

    head = _git(core_dir, "rev-parse", "HEAD")
    toplevel = _git(core_dir, "rev-parse", "--show-toplevel")
    # Only trust git when the Core directory is its own git repository root
    # (otherwise `git` would silently report a *parent* repo's HEAD).
    own_git_repo = (
        head is not None
        and toplevel is not None
        and Path(toplevel).resolve() == core_dir.resolve()
    )
    git_baseline_ok = (
        _git(core_dir, "rev-parse", "--verify", f"{VALIDATED_BASELINE_COMMIT}^{{commit}}")
        is not None
    ) if own_git_repo else False
    dirty = (_git(core_dir, "status", "--porcelain") or "") if own_git_repo else ""
    tracked_dirty = any(
        line and not line.startswith("??") for line in dirty.splitlines()
    )

    if own_git_repo:
        # Git checkout available — authoritative.
        method = "git"
        head_short = head[:7]
        baseline_present = bool(git_baseline_ok)
    elif provenance is not None:
        # Packaged Core (no git) — use build-time provenance.
        method = "provenance"
        head_short = (
            (str(provenance.get("frozen_integration_commit", "")) or "")[:7]
            or None
        )
        baseline_present = (
            provenance.get("validated_baseline_commit") == VALIDATED_BASELINE_COMMIT
        )
        tracked_dirty = False  # packaged Core is immutable by construction
    else:
        method = "none"
        head_short = None
        baseline_present = False

    return {
        "statement": LINEAGE_STATEMENT,
        "engine_version": version,
        "version_match": version == EXPECTED_VERSION,
        "expected_version": EXPECTED_VERSION,
        "validated_baseline_commit": VALIDATED_BASELINE_COMMIT,
        "baseline_commit_present": baseline_present,
        "frozen_integration_commit": FROZEN_INTEGRATION_COMMIT,
        "head_commit": head_short,
        "head_matches_frozen": head_short == FROZEN_INTEGRATION_COMMIT,
        "tracked_files_modified": tracked_dirty,
        "verification_method": method,
        "core_dir": str(core_dir),
        "core_found": True,
        "core_integrity_ok": (
            version == EXPECTED_VERSION
            and baseline_present
            and head_short == FROZEN_INTEGRATION_COMMIT
            and not tracked_dirty
        ),
    }

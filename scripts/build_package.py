#!/usr/bin/env python3
"""Build the HFSG Academic Demo release package (Lab + private Core, no data).

Produces:

    release/HFSG_Academic_Demo_v1.0/     the portable package
    release/HFSG_Academic_Demo_v1.0.zip  the zipped package
    release/SHA256SUMS                   sha256 of every package file

The package ships the Research Lab and its documentation. When the approved
frozen HFSG Core is present in the local (git-ignored) ``hfsg_core/`` folder,
it is bundled into the PRIVATE package only — never committed and never
published. The Master Dataset is always excluded. The build verifies the Core
identity (v0.6.0 / baseline 08032c3 / frozen commit affe7c8) and refuses to
bundle a Core that does not match, then writes ``CORE_PROVENANCE.json`` so the
Lab can verify identity on machines without git.

Usage:
    python scripts/build_package.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = LAB_ROOT / "release"
PKG = RELEASE_ROOT / "HFSG_Academic_Demo_v1.0"
PKG_NAME = "HFSG_Academic_Demo_v1.0"

ROOT_DOCS = ("README_FIRST.txt", "INSTALLATION_GUIDE.md", "DEMO_GUIDE.md")

EXPECTED_VERSION = "0.6.0"
VALIDATED_BASELINE_COMMIT = "08032c3"
FROZEN_INTEGRATION_COMMIT = "affe7c8"
PROVENANCE_FILE = "CORE_PROVENANCE.json"


def _copy_tree(src: Path, dst: Path, excludes: tuple[str, ...] = ()) -> None:
    if not src.exists():
        return
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".pytest_cache", "results", "runs",
            *excludes,
        ),
        dirs_exist_ok=True,
    )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tree_sha256(paths: list[Path]) -> str:
    """Deterministic sha256 over a set of files (sorted relative paths)."""
    h = hashlib.sha256()
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(f for f in sorted(p.rglob("*")) if f.is_file())
        elif p.is_file():
            files.append(p)
    for f in sorted(files):
        rel = f.resolve().name if not f.parent else f.name
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        with f.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def _is_core_dir(path: Path) -> bool:
    return (path / "src" / "hfsg" / "__init__.py").is_file() and (
        path / "config" / "base.yaml"
    ).is_file()


def _read_version(core_dir: Path) -> str | None:
    init = core_dir / "src" / "hfsg" / "__init__.py"
    if not init.is_file():
        return None
    m = re.search(r'__version__\s*=\s*"([^"]+)"', init.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def _git(core_dir: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(core_dir), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (out.stdout or "").strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _core_provenance(core_dir: Path) -> dict:
    """Verify the Core identity at build time and return its provenance.

    Refuses to bundle a Core whose identity cannot be confirmed against the
    approved reference (version 0.6.0, baseline 08032c3, frozen affe7c8).
    """
    version = _read_version(core_dir)
    head = _git(core_dir, "rev-parse", "HEAD")
    baseline_ok = (
        _git(core_dir, "rev-parse", "--verify", f"{VALIDATED_BASELINE_COMMIT}^{{commit}}")
        is not None
    )

    problems = []
    if version != EXPECTED_VERSION:
        problems.append(f"version {version!r} != {EXPECTED_VERSION!r}")
    if head is None or head[:7] != FROZEN_INTEGRATION_COMMIT:
        problems.append(
            f"HEAD {head!r} != frozen commit {FROZEN_INTEGRATION_COMMIT!r}"
        )
    if not baseline_ok:
        problems.append(f"baseline {VALIDATED_BASELINE_COMMIT!r} not present")

    if problems:
        raise RuntimeError(
            "APPROVED CORE NOT LOCATED / identity mismatch — refusing to "
            "bundle hfsg_core/. " + "; ".join(problems)
        )

    return {
        "project": "HFSG",
        "core_version": version,
        "validated_baseline_commit": VALIDATED_BASELINE_COMMIT,
        "frozen_integration_commit": FROZEN_INTEGRATION_COMMIT,
        "head_commit": head,
        "source_sha256": _tree_sha256(
            [core_dir / "src", core_dir / "config"]
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build() -> Path:
    if PKG.exists():
        shutil.rmtree(PKG)
    PKG.mkdir(parents=True, exist_ok=True)

    # Core Lab application
    shutil.copy2(LAB_ROOT / "app.py", PKG / "app.py")
    _copy_tree(LAB_ROOT / "research_lab", PKG / "research_lab")

    # Launchers + scripts
    shutil.copy2(LAB_ROOT / "START_HFSG", PKG / "START_HFSG")
    shutil.copy2(LAB_ROOT / "START_HFSG.bat", PKG / "START_HFSG.bat")
    _copy_tree(LAB_ROOT / "scripts", PKG / "scripts")

    # Requirements
    _copy_tree(LAB_ROOT / "requirements", PKG / "requirements")

    # Documentation (root guides + docs/)
    for name in ROOT_DOCS:
        src = LAB_ROOT / "docs" / name
        if src.exists():
            shutil.copy2(src, PKG / name)
    _copy_tree(LAB_ROOT / "docs", PKG / "docs")
    for name in ROOT_DOCS:
        (PKG / "docs" / name).unlink(missing_ok=True)

    # hfsg_core/: bundle the privately supplied approved Core ONLY if it is
    # present locally AND its identity verifies. It is git-ignored, never
    # committed, and never published. When absent, ship the placeholder.
    supplied_core = LAB_ROOT / "hfsg_core"
    (PKG / "hfsg_core").mkdir(exist_ok=True)
    if _is_core_dir(supplied_core):
        provenance = _core_provenance(supplied_core)
        # Bundle ONLY the approved Core source/config — never its dataset
        # (data/), environment (.venv), git history (.git), or generated
        # parquet. The .git directory is excluded because identity is verified
        # via the provenance file on the target machine.
        _copy_tree(
            supplied_core,
            PKG / "hfsg_core",
            excludes=(
                "data", ".venv", "*.parquet", ".pytest_cache", "__pycache__",
                ".git",
            ),
        )
        (PKG / "hfsg_core" / PROVENANCE_FILE).write_text(
            json.dumps(provenance, indent=2), encoding="utf-8"
        )
        print(
            f"Bundled approved Core {provenance['core_version']} "
            f"({provenance['head_commit'][:7]}) into hfsg_core/"
        )
    else:
        (PKG / "hfsg_core" / "README.txt").write_text(
            "Place your approved HFSG Core here.\n\n"
            "This folder must contain:\n"
            "  src/hfsg/__init__.py\n"
            "  config/base.yaml\n\n"
            "The Core is NOT distributed with the Lab (see "
            "docs/IP_AND_DISTRIBUTION_BOUNDARY.md).\n"
            "Alternatives: set HFSG_CORE_DIR, or select the Core on the "
            "About / System Information page.\n",
            encoding="utf-8",
        )

    # Demo reference metadata (NOT the dataset)
    (PKG / "demo_release").mkdir(exist_ok=True)
    (PKG / "demo_release" / "release_reference.json").write_text(
        json.dumps(
            {
                "note": (
                    "Reference metadata only — the Master Dataset is NOT "
                    "included in this package."
                ),
                "release_id": "HFSG-DS-STD8-2026-20260905-120702",
                "scenarios": [
                    "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "CUSTOM",
                ],
                "total_patients": 109119,
                "total_events": 316010,
                "aggregate_rows": 58320,
                "validation_status": "VALIDATED",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (PKG / "demo_release" / "README.txt").write_text(
        "demo_release/\n\n"
        "Contains approved academic REFERENCE metadata about the validated "
        "Phase-1 release (scenario pack, row counts, validation status).\n\n"
        "It does NOT contain the Master Dataset. The dataset is produced by "
        "the Lab's Live Demo runs, which are labelled VALIDATED (never "
        "RELEASED).\n",
        encoding="utf-8",
    )

    # Empty runtime folders
    (PKG / "outputs").mkdir(exist_ok=True)
    (PKG / "outputs" / ".gitkeep").write_text("", encoding="utf-8")
    (PKG / "logs").mkdir(exist_ok=True)
    (PKG / "logs" / ".gitkeep").write_text("", encoding="utf-8")

    return PKG


def zip_package(pkg: Path) -> tuple[Path, Path]:
    zip_path = RELEASE_ROOT / f"{PKG_NAME}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pkg.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(RELEASE_ROOT)))
    return zip_path, RELEASE_ROOT / "SHA256SUMS"


def write_sums(zip_path: Path, sums_path: Path) -> None:
    lines = [f"{_sha256(zip_path)}  {zip_path.name}"]
    for path in sorted(PKG.rglob("*")):
        if path.is_file():
            rel = str(path.relative_to(RELEASE_ROOT))
            lines.append(f"{_sha256(path)}  {rel}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    pkg = build()
    zip_path, sums_path = zip_package(pkg)
    write_sums(zip_path, sums_path)
    print(f"Package : {pkg}")
    print(f"ZIP     : {zip_path}")
    print(f"SHA256  : {sums_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

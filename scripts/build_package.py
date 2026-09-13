#!/usr/bin/env python3
"""Build the HFSG Academic Demo release package (Lab only — no Core, no data).

Produces:

    release/HFSG_Academic_Demo_v1.0/     the portable package
    release/HFSG_Academic_Demo_v1.0.zip  the zipped package
    release/SHA256SUMS                   sha256 of every package file

The package ships ONLY the Research Lab and its documentation. The HFSG Core
and the Master Dataset are excluded (see IP_AND_DISTRIBUTION_BOUNDARY.md).
The ``hfsg_core/`` folder is an empty placeholder the Project Owner fills with
their own approved Core.

Usage:
    python scripts/build_package.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = LAB_ROOT / "release"
PKG = RELEASE_ROOT / "HFSG_Academic_Demo_v1.0"
PKG_NAME = "HFSG_Academic_Demo_v1.0"

ROOT_DOCS = ("README_FIRST.txt", "INSTALLATION_GUIDE.md", "DEMO_GUIDE.md")


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


def _is_core_dir(path: Path) -> bool:
    return (path / "src" / "hfsg" / "__init__.py").is_file() and (
        path / "config" / "base.yaml"
    ).is_file()


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

    # hfsg_core/: bundle the privately supplied Core ONLY if it is present
    # locally. It is git-ignored, never committed, and never published. When
    # absent, ship the empty placeholder with instructions instead.
    supplied_core = LAB_ROOT / "hfsg_core"
    (PKG / "hfsg_core").mkdir(exist_ok=True)
    if _is_core_dir(supplied_core):
        # Bundle ONLY the approved Core source/config — never its dataset
        # (data/), environment (.venv), or generated parquet.
        _copy_tree(
            supplied_core,
            PKG / "hfsg_core",
            excludes=("data", ".venv", "*.parquet", ".pytest_cache", "__pycache__"),
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

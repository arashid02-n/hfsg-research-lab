#!/usr/bin/env python3
"""HFSG Research Lab — project-local environment bootstrap.

Run with ANY base Python (Windows: `py -3` / `python`; macOS/Linux:
`python3`). It guarantees the Lab never depends on a globally installed
Python environment for project dependencies:

    1. create  .venv                (if missing)
    2. install requirements         (into .venv, on first run only)
    3. re-execute scripts/launcher.py with the .venv interpreter

Every failure is printed as a human-readable "HFSG STARTUP FAILED" message
with a Reason and an Action. Exit codes are propagated so START_HFSG.bat and
START_HFSG can keep the console window open on error.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = os.name == "nt"

VENV_DIR = LAB_ROOT / ".venv"
VENV_PY = VENV_DIR / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
MARKER = VENV_DIR / ".hfsg_deps_ok"
REQUIREMENTS = LAB_ROOT / "requirements" / "requirements.txt"
LAUNCHER = LAB_ROOT / "scripts" / "launcher.py"


def _fail(reason: str, action: str, code: int) -> int:
    print("")
    print("=" * 62)
    print("HFSG STARTUP FAILED")
    print("")
    print(f"Reason: {reason}")
    print("")
    print(f"Action: {action}")
    print("=" * 62)
    return code


def create_venv() -> Path:
    print("Creating project-local environment (.venv) ...")
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    if not VENV_PY.is_file():
        raise RuntimeError(f"venv interpreter not found after creation: {VENV_PY}")
    return VENV_PY


def ensure_dependencies(py: Path) -> None:
    if MARKER.is_file():
        return
    if not REQUIREMENTS.is_file():
        raise RuntimeError(f"requirements file not found: {REQUIREMENTS}")
    print("Installing dependencies into .venv (first run only) ...")
    subprocess.check_call(
        [
            str(py),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(REQUIREMENTS),
        ]
    )
    MARKER.write_text("ok\n", encoding="utf-8")


def main() -> int:
    try:
        py = VENV_PY if VENV_PY.is_file() else create_venv()
        ensure_dependencies(py)
    except Exception as exc:
        return _fail(
            str(exc),
            "Ensure you have an internet connection for the first run, "
            "then double-click START_HFSG.bat again.",
            1,
        )

    return subprocess.call([str(py), str(LAUNCHER), *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())

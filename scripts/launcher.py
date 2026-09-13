#!/usr/bin/env python3
"""HFSG Research Lab — portable pre-flight launcher.

Runs the pre-flight checks then starts the Streamlit app. Called by
START_HFSG (bash) and START_HFSG.bat (Windows) so that "double-click" works
on Windows and `./START_HFSG` works on macOS/Linux with one shared,
portable implementation.

Pre-flight checks (all errors are human-readable, never a traceback):
  1. Python interpreter / runtime
  2. required dependencies (streamlit, pandas, pyarrow, PyYAML, numpy)
  3. required local files         (app.py, research_lab/, launcher)
  4. HFSG Core availability       (portable resolution)
  5. HFSG Core identity           (version / baseline / frozen commit)
  6. writable results directory
  7. sufficient free disk
  8. a free local port

Exit codes:
  0  app started and exited normally
  2  HFSG Core not found
  3  HFSG Core identity mismatch (LIVE RUN BLOCKED)
  4  missing dependency / missing local files / environment problem
  5  insufficient disk / unwritable output directory / no free port
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))

MIN_FREE_BYTES = 256 * 1024 * 1024  # 256 MiB comfortable headroom
REQUIRED_DEPENDENCIES = (
    ("streamlit", "streamlit"),
    ("pandas", "pandas"),
    ("pyarrow", "pyarrow"),
    ("yaml", "PyYAML"),
    ("numpy", "numpy"),
)
DEFAULT_PORT = 8501
MAX_PORT = 8550


def _say(message: str) -> None:
    print(message)


def _fail(message: str, code: int) -> int:
    print("")
    print("=" * 62)
    print("HFSG STARTUP FAILED")
    print("")
    print(message)
    print("=" * 62)
    return code


def check_local_files() -> None:
    required = {
        "app.py": LAB_ROOT / "app.py",
        "research_lab/": LAB_ROOT / "research_lab" / "__init__.py",
        "scripts/launcher.py": LAB_ROOT / "scripts" / "launcher.py",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        _fail(
            "Required Lab files are missing: " + ", ".join(missing) + ".\n\n"
            "The Academic Demo package appears incomplete.",
            4,
        )
        sys.exit(4)


def check_dependencies() -> None:
    missing = []
    for import_name, display in REQUIRED_DEPENDENCIES:
        try:
            __import__(import_name)
        except Exception:
            missing.append(display)
    if missing:
        joined = ", ".join(missing)
        _fail(
            f"Required dependencies are missing: {joined}.\n\n"
            "The project-local .venv is incomplete. Re-run "
            "START_HFSG.bat / START_HFSG so bootstrap.py can (re)install "
            "them, or install manually with:\n"
            "    python -m pip install -r requirements/requirements.txt",
            4,
        )
        sys.exit(4)


def check_core() -> None:
    from research_lab.core import resolve_core_dir
    from research_lab.identity import verified_identity

    core_dir = resolve_core_dir()
    if core_dir is None:
        _fail(
            "HFSG Core not found.\n\n"
            "Expected location:\n"
            "    hfsg_core/\n\n"
            "Action:\n"
            "    Place the approved HFSG Core in the hfsg_core directory "
            "next to this app and restart HFSG.\n\n"
            "A valid Core contains `src/hfsg/__init__.py` and "
            "`config/base.yaml`. (Alternatives: set the HFSG_CORE_DIR "
            "environment variable, or select the Core on the About / "
            "System Information page.)",
            2,
        )
        sys.exit(2)

    identity = verified_identity(core_dir)
    if not identity.get("core_integrity_ok"):
        reason = identity.get("error") or (
            "version/baseline/frozen-commit mismatch or modified Core files"
        )
        _fail(
            "LIVE RUN BLOCKED — incompatible HFSG Core detected.\n\n"
            f"Reason: {reason}\n\n"
            "Expected identity:\n"
            f"    {identity['statement']}\n\n"
            "Action:\n"
            "    Replace the Core with the approved frozen checkout and "
            "restart HFSG. Live runs are disabled until the Core matches.",
            3,
        )
        sys.exit(3)

    _say(f"HFSG Core verified: {identity['statement']}")
    _say(f"  Core directory: {core_dir}")


def check_output_dir() -> None:
    results = LAB_ROOT / "results"
    try:
        results.mkdir(parents=True, exist_ok=True)
        probe = results / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError:
        _fail(
            f"Output directory is not writable: {results}\n\n"
            "Make sure the HFSG folder is not read-only and you have write "
            "permission, then retry.",
            5,
        )
        sys.exit(5)


def check_disk() -> None:
    free = shutil.disk_usage(LAB_ROOT).free
    if free < MIN_FREE_BYTES:
        _fail(
            f"Insufficient free disk: {free / (1024 ** 3):.2f} GiB available.\n\n"
            f"At least {MIN_FREE_BYTES / (1024 ** 3):.0f} GiB free is "
            "recommended to record a Live Demo run.",
            5,
        )
        sys.exit(5)
    _say(f"Free disk: {free / (1024 ** 3):.2f} GiB")


def find_free_port() -> int:
    for port in range(DEFAULT_PORT, MAX_PORT + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    _fail(f"No free port in range {DEFAULT_PORT}-{MAX_PORT}.", 5)
    sys.exit(5)


def launch(port: int) -> int:
    import streamlit  # noqa: F401  (already checked)

    app_path = LAB_ROOT / "app.py"
    _say(f"Starting HFSG Research Lab on http://localhost:{port} ...")
    _say("Your browser should open automatically. Keep this window open.")
    _say("Press Ctrl+C here to stop the Lab.")
    print("")
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--browser.gatherUsageStats",
            "false",
        ]
    )


def main() -> int:
    _say("HFSG Research Lab — pre-flight check")
    _say(f"  Python: {sys.version.split()[0]}")
    _say(f"  Lab directory: {LAB_ROOT}")
    check_local_files()
    check_dependencies()
    check_core()
    check_output_dir()
    check_disk()
    port = find_free_port()
    _say("Pre-flight complete. Launching app.")
    return launch(port)


if __name__ == "__main__":
    sys.exit(main())

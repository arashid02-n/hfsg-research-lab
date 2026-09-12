#!/usr/bin/env python3
"""HFSG Research Lab — portable pre-flight launcher.

Runs the pre-flight checks then starts the Streamlit app. Called by
START_HFSG (bash) and START_HFSG.bat (Windows) so that "double-click" works
on Windows and `./START_HFSG` works on macOS/Linux with one shared,
portable implementation.

Pre-flight checks (all errors are human-readable, never a traceback):
  1. Python interpreter / runtime
  2. required dependencies (streamlit, pandas, pyarrow, PyYAML, numpy)
  3. HFSG Core availability      (portable resolution)
  4. HFSG Core identity          (version / baseline / frozen commit)
  5. writable results directory
  6. sufficient free disk
  7. a free local port

Exit codes:
  0  app started and exited normally
  2  HFSG Core not found
  3  HFSG Core identity mismatch (LIVE RUN BLOCKED)
  4  missing dependency / environment problem
  5  insufficient disk / unwritable output directory
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
    print(message)
    print("=" * 62)
    return code


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
            f"Missing required dependencies: {joined}.\n\n"
            "Install them once (e.g. in a terminal):\n"
            "    python -m pip install -r requirements/requirements.txt\n"
            "then double-click START_HFSG.bat again.",
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
            "Provide the approved HFSG Core one of these ways:\n"
            "  1. Copy the Core into the `hfsg_core/` folder next to this app\n"
            "  2. Set the HFSG_CORE_DIR environment variable to the Core path\n"
            "  3. Run the app and choose the Core on the About / System\n"
            "     Information page (writes hfsg_core.config)\n\n"
            "A valid Core contains `src/hfsg/__init__.py` and\n"
            "`config/base.yaml`.",
            2,
        )
        sys.exit(2)

    identity = verified_identity(core_dir)
    if not identity.get("core_integrity_ok"):
        reason = identity.get("error") or (
            "version/baseline/frozen-commit mismatch or modified Core files"
        )
        _fail(
            f"LIVE RUN BLOCKED — incompatible HFSG Core detected.\n\n"
            f"Core directory: {core_dir}\n"
            f"Reason: {reason}\n\n"
            "Expected identity:\n"
            f"  {identity['statement']}\n\n"
            "Provide the approved frozen Core checkout and retry.",
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
    check_dependencies()
    check_core()
    check_output_dir()
    check_disk()
    port = find_free_port()
    _say("Pre-flight complete. Launching app.")
    return launch(port)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# start_hfsg.sh — start the HFSG Research Lab on macOS/Linux.
#
# Finds a base Python interpreter, then delegates to scripts/bootstrap.py
# (which creates/uses a project-local .venv, installs dependencies on first
# run, and launches the pre-flight + app). No developer-specific paths.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PY=""
for candidate in "$(command -v python3 || true)" "$(command -v python || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "HFSG STARTUP FAILED" >&2
    echo "Reason: Python was not found." >&2
    echo "Action: install Python 3.10+ and retry." >&2
    exit 1
fi

exec "$PY" "$LAB_DIR/scripts/bootstrap.py" "$@"

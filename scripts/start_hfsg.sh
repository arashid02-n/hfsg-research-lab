#!/usr/bin/env bash
# start_hfsg.sh — start the HFSG Research Lab on macOS/Linux.
#
# Delegates all pre-flight checks and startup to the portable Python launcher
# (scripts/launcher.py). No developer-specific paths are hard-coded.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PY=""
for candidate in \
    "$LAB_DIR/.venv/bin/python" \
    "$(command -v python3 || true)" \
    "$(command -v python || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "START_HFSG: no Python interpreter found." >&2
    echo "Create a Lab virtualenv and install the dependencies, then retry:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    exit 1
fi

exec "$PY" "$LAB_DIR/scripts/launcher.py" "$@"

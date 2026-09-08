#!/usr/bin/env bash
# start_hfsg.sh — start the HFSG Research Lab Streamlit app on a local host.
#
# Environment choice (first available wins):
#   1. <lab>/.venv/bin/python        (recommended: dedicated Lab venv)
#   2. /home/rashid/projects/hfsg/.venv/bin/python   (frozen Core venv)
#   3. python3 on PATH
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=""
for candidate in \
    "$LAB_DIR/.venv/bin/python" \
    "/home/rashid/projects/hfsg/.venv/bin/python" \
    "$(command -v python3 || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PY="$candidate"
        break
    fi
done
if [ -z "$PY" ]; then
    echo "START_HFSG: no Python interpreter found." >&2
    echo "Create <lab>/.venv or install to a Core venv, then retry." >&2
    exit 1
fi

echo "HFSG Research Lab using Python: $PY"
exec "$PY" -m streamlit run "$LAB_DIR/app.py" "$@"
# Windows Compatibility Audit

**Date:** 2026-09-14
**Scope:** Research Lab / Academic Demo layer (`research_lab/`, `app.py`, `scripts/`).
**Excluded:** the frozen HFSG Core (not modified).

## Confirmed original blocker

| File | Line | Finding |
|---|---|---|
| `research_lab/adapter.py` | 35 | `import resource` (module level) |

`resource` is POSIX-only; it is absent from standard Windows Python, so
importing the Lab crashed the Streamlit app (`ModuleNotFoundError`), which in
turn caused the browser "Connection error" symptom.

## Fix

`import resource` was removed from module scope. Peak-memory measurement is
now performed by a guarded helper `_peak_rss_bytes()` that imports `resource`
inside a `try/except (ImportError, AttributeError, OSError)` and returns
`None` when the mechanism is unavailable (e.g. Windows). The Lab reports
"Peak RAM: NOT AVAILABLE" instead of failing to start, and the application
remains fully functional without precise peak-memory measurement.

## Additional Unix-specific findings (full sweep)

The entire Lab layer was searched for Unix-only assumptions. Results:

| Dependency / assumption | Where | Purpose | Windows impact | Action |
|---|---|---|---|---|
| `import resource` (POSIX) | `research_lab/adapter.py` | peak-RSS measurement | **import crash** | guarded import + `None` fallback |
| `import fcntl` | — not found | — | — | none |
| `import pwd / grp` | — not found | — | — | none |
| `import termios / tty / pty` | — not found | — | — | none |
| `import signal` / `os.kill` / `os.fork` / `os.uname` | — not found | — | — | none |
| `multiprocessing` / `ctypes` | — not found | — | — | none |
| `os.getuid` / `os.getgid` / `os.geteuid` / `os.getegid` | — not found | — | — | none |
| hard-coded `/home/…`, `/tmp/…`, `/var/…`, `/dev/…`, `/usr/bin`, `/bin/sh` | — not found | — | — | none |
| shell commands (`chmod`, `chown`, `ln -s`, `bash -c`) | — not found | — | — | none |
| `git` via `subprocess` | `research_lab/identity.py`, `scripts/build_package.py` | Core identity verification | `git` may be absent | already guarded (`try/except OSError`) + `CORE_PROVENANCE.json` fallback for the packaged Core |
| path separators / filesystem | throughout | paths | — | uses `pathlib.Path` (cross-platform) |
| venv interpreter path | `scripts/bootstrap.py` | `.venv` | — | already `os.name == "nt"` aware (`Scripts/python.exe` vs `bin/python`) |
| shebangs `#!/usr/bin/env python3` | scripts | — | harmless (comments on Windows) | none |

## Result

```
No known unconditional Unix-only runtime dependency remains in the
Research Lab layer.
```

The only true blocker (`import resource`) is fixed, and every other
platform-specific reference is either absent, already guarded, or uses
cross-platform APIs.

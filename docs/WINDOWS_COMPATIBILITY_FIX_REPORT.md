# Windows Compatibility Fix Report

**Date:** 2026-09-14
**Gate:** 2C — final Windows compatibility fix

## 1. Original failure

After a successful launch, the Surface showed the Streamlit browser falling
into a "Connection error / CONNECTING" state.

## 2. Exact file / line

`research_lab/adapter.py`, line 35.

## 3. Root cause

`import resource` at module scope. `resource` is POSIX-only and is not
available on standard Windows Python, so importing the Lab raised
`ModuleNotFoundError: No module named 'resource'`, crashing the Streamlit
process. The browser "Connection error" was a consequence, not a networking
problem.

## 4. Fix implemented

Removed the module-level `import resource`. Peak-memory measurement now uses
a guarded helper, `_peak_rss_bytes()`, that imports `resource` inside a
`try/except (ImportError, AttributeError, OSError)` and returns `None` when
unavailable. The `BatchOutcome.peak_rss_bytes` field is now `Optional[int]`.
On Windows the Lab reports "Peak RAM: NOT AVAILABLE" and remains fully
functional.

## 5. Other platform-specific findings

See `WINDOWS_COMPATIBILITY_AUDIT.md`. No other unconditional Unix-only
runtime dependency was found. `git` usage is already guarded with a
`CORE_PROVENANCE.json` fallback, and all filesystem paths use `pathlib.Path`.

## 6. Files changed

- `research_lab/adapter.py` — guarded `resource` import; `peak_rss_bytes`
  made optional; `_peak_rss_bytes()` helper added.
- `docs/WINDOWS_COMPATIBILITY_AUDIT.md` — new audit.
- `docs/WINDOWS_COMPATIBILITY_FIX_REPORT.md` — this report.

## 7. Frozen Core verification

- Core identity: `HFSG Core v0.6.0`, baseline `08032c3`, frozen `affe7c8`.
- **CORE MODIFICATION: NONE** (`git diff` empty; HEAD unchanged).

## 8. Tests performed

- Lab test suite: `10 passed`.
- `import research_lab.adapter` succeeds; `_peak_rss_bytes()` returns a value
  on Linux (measurement mechanism intact).
- Frozen Core regression: `177 passed` (see `FINAL_CORE_REGRESSION_REPORT.md`).

## 9. Test results

| Test | Result |
|---|---|
| Lab unit + acceptance tests | PASS (10/10) |
| Adapter import (no unconditional `resource`) | PASS |
| Peak-RAM measurement on Linux | PASS (value returned) |
| Peak-RAM on Windows | NOT VERIFIED (returns `None` by construction) |
| Core regression | PASS (177/177) |

## 10. Linux/macOS compatibility consideration

The change is additive: on POSIX systems `_peak_rss_bytes()` still returns the
measured peak RSS exactly as before. No Linux/macOS behaviour is removed.

## 11. Windows compatibility result

`WINDOWS COMPATIBILITY FIX: COMPLETE` (by construction and local verification;
the physical Surface re-run remains the Project Owner's step).

## 12. Remaining limitations

- Precise peak-RAM is not reported on Windows (surfaced as "NOT AVAILABLE").
- Final Surface acceptance is **PENDING PROJECT OWNER ACCEPTANCE** — not
  claimed here.

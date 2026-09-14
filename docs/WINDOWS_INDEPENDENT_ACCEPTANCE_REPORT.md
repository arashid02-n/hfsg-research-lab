# Windows Independent Acceptance Report

**Date:** 2026-09-13
**Gate:** 2C — final acceptance fixes
**Acceptance machine:** Microsoft Surface (Project Owner's)

## Status

```
WINDOWS_INDEPENDENT_ACCEPTANCE: NOT VERIFIED
```

This is **not** a PASS. The final sequence must be re-run on the Microsoft
Surface by the Project Owner after the launcher fixes below. This report
records (a) the previously observed failures, (b) the fixes applied, and
(c) the exact values measured on a clean Linux environment used only to
validate the fix logic. Windows-specific values are left **NOT VERIFIED** and
must be filled in from the actual Surface run.

---

## 1. Previously observed failures (Project Owner's Surface review)

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | Double-clicking `START_HFSG.bat` made the window disappear; error "`. was unexpected at this time.`" | Batch script had parenthesised `echo (...)` text inside an `if (...)` block; the `)` prematurely closed the block. | Rewrote `START_HFSG.bat` (quoted/restructured, no unquoted parentheses in blocks, `pause` on every failure). |
| 2 | Global Python dependency execution failed with `WinError 2` (dependencies not installed globally) | Launcher assumed dependencies were installed globally. | New `scripts/bootstrap.py` creates/uses a project-local `.venv` and installs dependencies into it automatically. |
| 3 | `HFSG STARTUP FAILED — HFSG Core not found. Expected location: hfsg_core/` | The Academic Demo package did not contain the approved/frozen Core (`hfsg_core/` held only a placeholder). | The package now bundles the **approved frozen Core** into `hfsg_core/` (verified identity `0.6.0` / `08032c3` / `affe7c8`), with `CORE_PROVENANCE.json` so identity is verified even without git. See `CORE_IDENTITY_REPORT.md`. |

## 2. Fixes applied

- **`START_HFSG.bat`** — finds a base Python (`py -3` then `python`), runs
  `scripts\bootstrap.py`, keeps the window open (`pause`) on any non-zero exit,
  and returns a useful exit code.
- **`scripts/bootstrap.py`** (new, cross-platform) — creates `.venv` if
  missing, installs `requirements/requirements.txt` into `.venv` on first run,
  then re-executes `scripts/launcher.py` with the `.venv` interpreter.
- **`scripts/launcher.py`** — pre-flight now also checks *required local
  files*, and every failure is printed as `HFSG STARTUP FAILED` with
  `Reason` / `Expected location` / `Action`.
- **Private Core integration** — `scripts/build_package.py` bundles
  `hfsg_core/` into the package **only** when the approved Core is present
  locally (git-ignored, never committed/published); dataset (`data/`), `.venv`
  and `*.parquet` are always excluded.

## 3. Verification performed (clean Linux environment — proxy only)

The Python bootstrap + launcher logic (identical on Windows) was exercised on
a clean Linux environment under `/tmp` with no developer paths:

| Check | Result |
|---|---|
| auto `.venv` creation from a base interpreter | VERIFIED |
| dependency install into `.venv` | VERIFIED |
| Core discovered from `hfsg_core/` (bundled) | VERIFIED |
| Core identity (`0.6.0`, `08032c3`, `affe7c8`) | VERIFIED |
| pre-flight → app launch (Uvicorn/Streamlit) | VERIFIED |
| dataset/`.venv`/parquet excluded from package | VERIFIED |

**Note:** this is a Linux proxy of the fix logic, NOT the Microsoft Surface
acceptance test. It is not a substitute for §10.

## 4. Acceptance metrics

| Metric | Windows Surface | Clean Linux proxy (this host) |
|---|---|---|
| OS | NOT VERIFIED | Linux Ubuntu 24.04 |
| CPU | NOT VERIFIED | Intel Xeon (Skylake) 2 vCPU |
| RAM | NOT VERIFIED | ~3.7 GB |
| Free disk | NOT VERIFIED | ~1.1 GB |
| Python version | NOT VERIFIED (owner saw 3.12.4) | 3.12.3 |
| Installation time | NOT VERIFIED | n/a (auto `.venv`) |
| `.venv` creation time | NOT VERIFIED | VERIFIED (auto) |
| Dependency install time | NOT VERIFIED | VERIFIED (auto, cached) |
| Startup time | NOT VERIFIED | VERIFIED (launch OK) |
| Core discovery | NOT VERIFIED | VERIFIED (`hfsg_core/`, extracted package root) |
| Core identity | NOT VERIFIED | VERIFIED (provenance, no git) |
| Browser launch | NOT VERIFIED | VERIFIED (server up) |
| 10K generation time | NOT VERIFIED | 9.10 s |
| Validation time | NOT VERIFIED | 23.13 s |
| Patients generated | NOT VERIFIED | 10,622 |
| Events generated | NOT VERIFIED | 31,653 |
| Peak RAM | NOT VERIFIED | ~1.46 GB |
| Output size | NOT VERIFIED | ~1.06 MB |
| Reproducibility (Same Seed) | NOT VERIFIED | MATCH (Lab AppTest, real Core) |
| Export | NOT VERIFIED | VERIFIED (zip build) |
| Offline | NOT VERIFIED | PASS (proxy-blocked network) |
| Restart | NOT VERIFIED | n/a |

## 5. Acceptance matrix

Status on the Microsoft Surface is **NOT VERIFIED** until the Project Owner
runs the sequence on the actual machine.

| Test | Status (Surface) |
|---|---|
| START_HFSG.bat | NOT VERIFIED |
| Automatic .venv | NOT VERIFIED |
| Dependency bootstrap | NOT VERIFIED |
| Python detection | NOT VERIFIED |
| Pre-flight | NOT VERIFIED |
| Core Discovery | NOT VERIFIED |
| Core Identity | NOT VERIFIED |
| Browser launch | NOT VERIFIED |
| S1 | NOT VERIFIED |
| 10K Live Generation | NOT VERIFIED |
| Validation | NOT VERIFIED |
| Dashboard | NOT VERIFIED |
| Patient Explorer | NOT VERIFIED |
| Same Seed | NOT VERIFIED |
| Comparison | NOT VERIFIED |
| Export | NOT VERIFIED |
| Offline | NOT VERIFIED |
| Restart | NOT VERIFIED |

## 6. Required next step (Project Owner)

Run the full §10 sequence on the Microsoft Surface using the rebuilt package
and fill in the Windows column above. Then:

- If the full sequence succeeds: set `WINDOWS_INDEPENDENT_ACCEPTANCE: PASS`.
- Otherwise: set `WINDOWS_INDEPENDENT_ACCEPTANCE: FAIL` and record the exact
  failure.

There is no partial PASS for this final test.

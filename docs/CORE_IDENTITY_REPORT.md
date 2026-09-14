# Core Identity Report

**Date:** 2026-09-14
**Gate:** 2C — final blocker fix (private Core packaging)

## Identity (verified)

```
HFSG Core v0.6.0
Validated Baseline: 08032c3
Frozen Integration Commit: affe7c8
```

## Provenance / exact source

The approved frozen Core was located in the frozen Core repository checkout
(`arashid02-n/hfsg`, HEAD `affe7c80c17eec717940d07764ea608b0e0f4d3c`), whose
`src/hfsg/__init__.py` declares version `0.6.0` and whose git history contains
the validated baseline `08032c3`. This is the exact reference required by the
Research Lab — no substitution, no "newest main", no other project copy.

| Field | Value |
|---|---|
| Core version | `0.6.0` |
| Validated baseline commit | `08032c3` (present in git history) |
| Frozen integration commit | `affe7c8` (HEAD at packaging) |
| HEAD (full) | `affe7c80c17eec717940d07764ea608b0e0f4d3c` |
| Source integrity hash (`src/` + `config/`) | `36a16c78212cac97293c24f19fab6569b4b0dfb0abcb8fe44580d587b4120f56` |

## Files included in the package (`hfsg_core/`)

- `src/hfsg/` — all 18 Core modules (engine, patients, events, validation,
  reconciliation, quota, batch, config, scenarios, seeds, simulation, output,
  pipeline, units, context, validation_report, patient_validation, `__init__`).
- `config/base.yaml` — approved parameter configuration.
- `scripts/`, `tests/`, `requirements.txt`, `requirements-lock.txt`.
- Documentation and manifests (`MODEL.md`, `PRODUCT.md`, `ARCHITECTURE.md`,
  `OPERATIONS.md`, `AGENTS.md`, `FREEZE_MANIFEST.json`, etc.).
- `CORE_PROVENANCE.json` — build-time identity record (this file).

**Excluded (by design):** `data/` (Master Dataset), `.venv`, `.git`,
`__pycache__`, `*.parquet`, `.pytest_cache`.

## Core discovery path

The Lab resolves the Core in priority order (see `research_lab/core.py`):

1. `hfsg_core/` adjacent to the Lab (the packaged Core) — **used here**;
2. environment variable `HFSG_CORE_DIR`;
3. `hfsg_core.config`;
4. Core directory selected on the About / System Information page.

No developer absolute path is involved.

## Verification method

- **Git checkout (developer environment):** identity is verified with `git`
  (HEAD = `affe7c8`, baseline `08032c3` present, no modified tracked files).
- **Packaged Core (target machine, no git):** identity is verified against
  `CORE_PROVENANCE.json`, which is written at build time only after the build
  independently confirms the same facts against the git checkout. The build
  **refuses** to bundle a Core that does not match
  (`APPROVED CORE NOT LOCATED / identity mismatch`).
- Either way, `core_integrity_ok` gates live runs; a mismatch shows
  **LIVE RUN BLOCKED**.

## Distribution status

```
CORE DISTRIBUTION:
PRIVATE ACADEMIC PACKAGE ONLY

PUBLIC GITHUB:
CORE NOT INCLUDED
```

The Core is bundled only into the private `HFSG_Academic_Demo_v1.0.zip` for
the Project Owner's academic demonstration. It is git-ignored in the Research
Lab repository and is never committed, never pushed, and never attached to a
public GitHub release. The Master Dataset is never included anywhere.

**Result: Core identity verified; private-package-only distribution.**

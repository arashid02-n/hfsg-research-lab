# Final Core Regression Report

**Date:** 2026-09-13 (re-run after final Gate 2C acceptance fixes)
**Gate:** 2C
**Core repository:** `arashid02-n/hfsg` (frozen)

## Result

```
177 passed in 173.78s
```

## Integrity verification

| Check | Result |
|---|---|
| Frozen Core HEAD | `affe7c8` (unchanged) |
| Tracked files changed (after Gate 2C) | **NO** (`git diff` empty, `git diff --check` clean) |
| Untracked files | only pre-existing `data/` (git-ignored dataset) |
| Core regression | **PASS** (177/177) |

Gate 2C made changes **only** in the Research Lab repository. No HFSG Core
file was modified — model logic, patient generation, event generation,
validation, reconciliation, seed semantics, and scenario semantics are all
unchanged. The Core's own regression suite still passes.

**Result: CORE REGRESSION: PASS (177/177).**

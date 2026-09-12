# Core Identity Report

**Date:** 2026-09-12
**Reference identity (verified against the actual repository):**

```
HFSG Core v0.6.0 — Phase-1 validated baseline 08032c3;
current frozen integration commit affe7c8
```

## Verification results (runtime, resolved Core)

The Lab verifies the reference above against the actual resolved Core before
displaying it, and blocks live runs when the check fails. On the developer
workstation (Core resolved via the portable mechanism):

| Field | Expected | Observed | OK |
|---|---|---|---|
| Engine version | `0.6.0` | `0.6.0` (`src/hfsg/__init__.py`) | yes |
| Validated baseline commit | `08032c3` | present in git history | yes |
| Frozen integration commit (HEAD) | `affe7c8` | `affe7c8` | yes |
| Tracked files modified | none | none | yes |
| **core_integrity_ok** | true | **true** | **yes** |

Method: `research_lab/identity.py` `verified_identity()` — reads the version
from `src/hfsg/__init__.py`, and uses `git -C <core> rev-parse HEAD`,
`rev-parse --verify 08032c3^{commit}`, and `status --porcelain` to confirm
the baseline is present, the HEAD equals the frozen integration commit, and
no tracked file is modified.

## Where the identity is shown

- **About / System Information** page (full identity + LIVE RUN BLOCKED
  reasoning when incompatible).
- The sidebar banner (verified / blocked / not-found) on every page.
- The launcher pre-flight check (`scripts/launcher.py`).

## Incompatible / missing Core behaviour

- **Core not found:** "HFSG Core not found." — live runs disabled.
- **Incompatible Core:** "LIVE RUN BLOCKED — incompatible HFSG Core
  detected." with the reason, and live runs disabled.
- A valid Core is required before any Live Run executes.

---

**Result: Core identity reference verified and enforced at runtime.**

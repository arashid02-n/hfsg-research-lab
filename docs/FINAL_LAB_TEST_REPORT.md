# Final Lab Test Report

**Date:** 2026-09-12
**Gate:** 2C
**Command:** `python -m pytest -q` (Lab root)

## Result

```
10 passed in 14.73s
```

## Coverage

| Test | Purpose |
|---|---|
| `test_identity_verification_ok` | Core identity (`0.6.0`, `08032c3`, `affe7c8`) verified against the resolved Core |
| `test_scenario_ids_and_defaults` | adapter exposes S1–S8/CUSTOM and frozen defaults (720 h, seed 20260805) |
| `test_effective_hash_matches_frozen_default` | identity S1 hash equals `e460cf54…` (no drift) |
| `test_custom_profile_limits` | CUSTOM multiplier limits enforced by the frozen Core (incl. rejected arrivals_wave) |
| `test_custom_effective_hash_changes` | CUSTOM profile changes the effective hash |
| `test_gate2a_stores_reproduce` | real Gate 2A recorded stores still reproduce (overall MATCH, VALIDATED) |
| `test_fingerprint_method_notes` | output fingerprints recorded with provenance notes |
| `test_algo_disclaimer` | approved CUSTOM limits unchanged |
| `test_ten_pages_render` | all 10 pages (incl. About / System Information) render without exception |
| `test_acceptance_flow_run_then_reproduce_match` | live Core run → validation → Re-run with Same Seed → REPRODUCIBILITY MATCH |

All tests run against the portable Core resolution (the Core is located via
the same mechanism the app uses: bundled → `HFSG_CORE_DIR` → `hfsg_core.config`).

**Result: PASS.**

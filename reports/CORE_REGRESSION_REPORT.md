# Gate 2B — Core Regression Report

**Method:** run the frozen HFSG Core test suite twice — once immediately
before and once immediately after the Gate 2B implementation work — and verify
the frozen repository remains untouched (version, HEAD, baseline, working-tree
cleanliness).

---

## 1. Environment

| Item | Value |
|---|---|
| Core repo | `/home/rashid/projects/hfsg` |
| HEAD | `affe7c80c17eec717940d07764ea608b0e0f4d3c` (commit `affe7c8`) |
| Validated baseline | `08032c3` |
| Engine version | `0.6.0` |
| Python | 3.12.3 (`.venv` numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1) |
| Command | `python -m pytest -q` from the Core repo root |

## 2. Results

| Run | When | Result |
|---|---|---|
| **Before** Gate 2B | 2026-09-08 (start of work) | **177 passed** in `152.16 s` |
| **After** Gate 2B | 2026-09-08 (implementation complete) | **177 passed** in `157.63 s` |

Both runs are the same suite (`177 passed`), confirming no behavioural
change to the frozen Core.

## 3. Repository-integrity evidence

`git status --porcelain` in the Core repo after Gate 2B:

```
?? data/         (pre-existing untracked directory — also present before Gate 2B)
```

- **No tracked file modifications** — the frozen Core tree is untouched.
- HEAD unchanged at `affe7c8`; `src/hfsg/__init__.py` still `0.6.0`.
- The Lab's runtime identity check (`research_lab/identity.py`) re-verifies
  version, HEAD, baseline presence and tracked cleanliness on every app load
  and reports `core_integrity_ok`.

## 4. Conclusion

The frozen HFSG Core is unaffected by Gate 2B. Its full test suite passes
identically before and after; the only repository change in the Core checkout
is the long-standing untracked `data/` directory, which the Lab never writes
to.

**Regression status: PASS (177/177 before, 177/177 after).**
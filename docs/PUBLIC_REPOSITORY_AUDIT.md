# Public Repository Audit

**Date:** 2026-09-12
**Scope:** public repositories `arashid02-n/hfsg-research-lab` and
`arashid02-n/hfsg` (the private `arashid02-n/hfsg-handover` is out of scope
for the public-audit but was noted).

This audit was performed against the actual repositories before the Gate 2C
release. Findings are factual and every remediation is listed.

---

## 1. Secrets / credentials

- **Result: NONE found.** Scanned every tracked file in both public
  repositories for private keys (`BEGIN RSA/OPENSSH/EC/DSA PRIVATE KEY`),
  AWS keys, GitHub tokens, generic `password=` assignments, and `.env` /
  credential / token / `.pem` / `.key` / `.p12` filenames.
- No `.env`, credential, token, secret, or private-key files are tracked.

## 2. Private paths / personal information (developer-specific)

- **Finding:** the Lab repository contained a developer absolute path
  (`<DEVELOPER_HOME>/projects/hfsg`) in **runtime code** and in recorded
  evidence/reports (a personal/developer-specific path in a public repo).
- **Remediation (Gate 2C):**
  - Runtime code (`research_lab/adapter.py`, `research_lab/identity.py`,
    `research_lab/ui/pages/home.py`, `scripts/start_hfsg.sh`) rewritten to
    resolve the Core portably — no absolute path remains.
  - New `research_lab/core.py` implements bundled→env→config→user-selectable
    resolution; new `scripts/launcher.py` performs pre-flight checks.
  - `bench/bench_one.py` made portable (resolves Core directory at runtime).
  - Historical recorded evidence (`bench/results_*.json`) and historical
    reports (`reports/CORE_REGRESSION_REPORT.md`,
    `reports/DEMO_ACCEPTANCE_TEST_REPORT.md`,
    `reports/UI_TO_CORE_TRACEABILITY_REPORT.md`) redacted: the developer path
    was replaced with `<HFSG_CORE>` / `<DEVELOPER_HOME>` placeholders.
  - `.gitignore` extended so the local `hfsg_core.config`, a bundled
    `hfsg_core/`, `outputs/`, and `logs/` can never be committed.
- **Verification:** `git grep -n "rashid"` over tracked files now returns only
  the legitimate GitHub account reference in the Core repo's own clone URL
  (`arashid02-n/hfsg.git`) — not a developer filesystem path.

## 3. Large internal datasets / Master Dataset

- **Result: NONE in public repositories.**
- The released Master Dataset (`data/output/step9`, ~12 MB, ~109k patients /
  ~316k events) is git-ignored in the Core repository and is present in no
  public repository.
- No `.parquet`, `.zip`, `.pkl`, `.npz`, `.onnx`, `.h5` files are tracked in
  either public repository.
- The only dataset-derived artifacts committed to the Lab are small
  reproducibility-evidence JSON summaries (comparison metadata, not data).

## 4. Unauthorized Core source

- The Core source is present in `arashid02-n/hfsg` (PUBLIC) by the Project
  Owner's own repository. The Lab repository does **not** copy any Core
  source; it is git-ignored via `hfsg_core/` and `core/`.

## 5. Temporary / developer artifacts

- Verified not tracked: `__pycache__`, `.pytest_cache`, `.venv`, `*.pyc`,
  `node_modules/`, `screenshots/.cache/`, `runs/`, `bench/runs/`, generated
  `results/*` (except committed `validation_evidence/` JSON), `outputs/`,
  `logs/`.
- `git status` is clean after Gate 2C; no untracked temporary files are
  staged.

## 6. Post-cleanup verification

- `git grep` for `home/rashid` in the Lab repository: **0 matches**.
- Secrets scan: **0 matches**.
- Dataset/large-file scan: **0 matches**.
- All tracked files were reviewed via `git ls-files` (see the Gate 2C commit).

---

**Audit result: PASS.** No secrets, no private developer paths, no datasets,
no unauthorized Core source, and no temporary artifacts remain in the public
repositories after the Gate 2C cleanup.

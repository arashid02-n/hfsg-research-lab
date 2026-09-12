# Portability Acceptance Report

**Date:** 2026-09-12
**Status:** partial — clean-machine portability VERIFIED on a clean Linux
environment; **independent Windows-laptop acceptance NOT YET EXECUTED**.

Per the acceptance criteria, independent-machine PASS is claimed only when it
has actually been run on a machine different from the developer workstation
(preferably a Windows laptop, ~8 GB RAM). That run has **not** been performed
here and is therefore reported as **PENDING**, not PASS.

---

## 1. What was actually tested (clean-machine, this host)

To verify the Lab has no hidden developer dependency, a **clean-machine
environment** was created entirely under `/tmp` (a non-developer path):

- Fresh Python virtual environment (created from scratch, not the developer
  venv), dependencies installed from `requirements/requirements.txt`.
- The Lab copied to `/tmp/hfsg-clean-machine/lab` **without** any local
  config, results, or venv.
- The HFSG Core copied (git checkout) to `/tmp/hfsg-clean-machine/core` and
  located only via the `HFSG_CORE_DIR` environment variable.
- No developer cache, no pre-existing Result Stores, no uncommitted files.

### Measured environment

| Item | Value |
|---|---|
| OS | Linux (Ubuntu 24.04, kernel 6.8.0-134-generic) x86_64 |
| CPU | Intel Xeon (Skylake), 2 vCPU |
| RAM | ~3.7 GB total |
| Python | 3.12.3 |
| Free disk at test | ~1.1 GB |

### Results

| Check | Result |
|---|---|
| Core resolved from a non-developer path | PASS (`/tmp/hfsg-clean-machine/core`) |
| Core identity verified (`0.6.0`, `08032c3`, `affe7c8`) | PASS |
| No `<DEVELOPER_HOME>` (or any developer path) in the Lab copy | PASS (grep = 0) |
| Fresh venv, no developer venv used | PASS |
| No pre-existing Result Stores | PASS (fresh `results/`) |
| Live demo S1 / 10,000 | PASS — 10,622 patients / 31,653 events / VALIDATED |
| Generation time | 9.10 s |
| Validation time | 23.13 s |
| Peak RAM | ~1.46 GB |
| Output size | ~1.06 MB (one 10k run) |
| Configuration hash | `e460cf54…` (matches identity) |

## 2. Independent Windows-laptop acceptance flow (PENDING)

The full §10 flow (Install → double-click `START_HFSG.bat` → browser opens →
Select S1 → 10K → Run → Validate → Dashboard → Patient Explorer → Re-run with
Same Seed → MATCH → Export → Close → Restart) has **not** been executed on a
separate Windows machine and is therefore **not claimed**.

The exact procedure for the Project Owner / tester is provided in
`INSTALLATION_GUIDE.md` and `DEMO_GUIDE.md`.

## 3. Conclusion

Clean-machine portability (no developer paths, venv, cache, or pre-existing
stores) is **PASS** on a clean Linux environment. Independent-machine
(Windows) acceptance remains **PENDING** and is not claimed as PASS.

# HFSG Research Lab

Synthetic hospital-flow scenario generation — a **research / education**
instrument (no clinical use) that layers a thin Streamlit UI on the **frozen
HFSG Core** (v0.6.0) without modifying any model, configuration or validation.

> **SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL PATIENT DATA — NOT CLINICALLY
> VALIDATED. RESEARCH / EDUCATION USE ONLY.**

## What it does

- **10 pages**: Home · Scenario Builder · Run Simulation · Results Dashboard ·
  Scenario Comparison · Synthetic Patient Explorer · Validation /
  Reproducibility Center · Export / Run Summary · Academic Quick Demo ·
  About / System Information.
- Executes **live, validated** runs through the frozen Core
  (generation → validation → Result Store) in a bounded-memory pipeline.
- **Scenario Builder** exposes *only* the approved controls: S1–S8 / CUSTOM
  selection and the CUSTOM multipliers (arrivals 0.5–2.0, ICU capacity
  0.5–1.5, discharge 0.5–2.0) — enforced by the frozen Core.
- **Validation / Reproducibility Center**: shows the frozen-Core validation
  report and runs **"Re-run with Same Seed"** — a real second execution of the
  exact same job — reporting `MATCH`/`FAIL` side-by-side for configuration
  hash, child seed, patient count, event count, validation result and output
  fingerprints (volatile fields normalised per MODEL.md section 28).
- **About / System Information**: verified Core identity and the portable Core
  location control. An incompatible or missing Core blocks live runs.

## Requirements

- An **approved HFSG Core** checkout (supplied separately — see below).
- Python 3.10+ with the packages in `requirements/requirements.txt`.
- ~2 GB free RAM for the 10k-patient Quick Demo; 25k = Extended / Slower Demo.

## Where the HFSG Core comes from

The Lab does **not** bundle the HFSG Core (see `IP_AND_DISTRIBUTION_BOUNDARY.md`).
It resolves the Core at startup in this order:

1. `hfsg_core/` (or `core/`) inside this directory — drop the Core here;
2. environment variable `HFSG_CORE_DIR`;
3. this directory's `hfsg_core.config` file;
4. a Core directory selected on the About / System Information page.

A valid Core contains `src/hfsg/__init__.py` and `config/base.yaml`.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

(Windows: `python -m venv .venv` then `.venv\Scripts\pip install -r requirements\requirements.txt`.)

## Start

- **Windows:** double-click `START_HFSG.bat`.
- **macOS / Linux:** run `./START_HFSG`.

The pre-flight check (Python, dependencies, Core availability and identity,
disk, port) runs automatically, then the app starts and the browser opens at
http://localhost:8501 (or the first free port).

## Acceptance demo flow (all real, none mocked)

1. **Select Scenario** — Scenario Builder (`S1` … `S8` / `CUSTOM`).
2. **Configure** — master seed (default `20260805`), horizon (default `720` h);
   CUSTOM multipliers for custom scenarios.
3. **Run 10K** — Academic Quick Demo (Quick Demo = 10,000 patients) or Run
   Simulation; the frozen Core generates and validates live.
4. **Validate** — Validation / Reproducibility Center shows the Core report.
5. **Dashboard** — Results Dashboard (census, flows, events, occupancy).
6. **Patient Explorer** — drill into real synthetic patient records.
7. **Re-run with Same Seed** — reproducible `MATCH` across configuration hash,
   child seed, patient/event counts, validation result, fingerprints.
8. **Compare** — Scenario Comparison across recorded runs.
9. **Export** — zip the Result Store.

## Tests

```bash
python -m pytest -q                        # unit + AppTest + small live flow
python -m pytest tests/test_acceptance_flow.py   # live acceptance flow
```

The Lab test suite requires a resolvable Core (via the same portable
resolution as the app). The frozen Core's own regression suite is run
separately, from the Core repository root.

## Layout

- `app.py` — Streamlit entry point.
- `research_lab/` — Lab package (core resolution, identity, adapter,
  fingerprint, result store, reproducibility, `ui/` with components/state and
  the 10 pages).
- `scripts/launcher.py` — portable pre-flight + startup launcher.
- `bench/`, `proof/` — Gate 2A benchmark + integration/reproducibility proofs.
- `tests/` — Lab test suite.
- `screenshots/` — UI screenshots (Gate 2B deliverable).
- `docs/` — installation, demo guide, and release documentation.

## Provenance

The Lab only **reads** the frozen Core (identity verified at runtime: version
`0.6.0`, validated baseline `08032c3`, frozen integration commit `affe7c8`).
Runs are recorded under `results/`; only small reproducibility evidence is
committed. The frozen Core repository, its config and its test suite are
never modified.

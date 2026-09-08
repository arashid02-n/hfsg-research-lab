# HFSG Research Lab

Synthetic hospital-flow scenario generation — a **research / education**
instrument (no clinical use) that layers a thin Streamlit UI on the **frozen
HFSG Core** (v0.6.0) without modifying any model, configuration or validation.

> **SYNTHETIC, SCENARIO-DRIVEN DATA — NOT REAL PATIENT DATA — NOT CLINICALLY
> VALIDATED. RESEARCH / EDUCATION USE ONLY.**

## What it does

- **9 pages**: Home · Scenario Builder · Run Simulation · Results Dashboard ·
  Scenario Comparison · Synthetic Patient Explorer · Validation /
  Reproducibility Center · Export / Run Summary · Academic Quick Demo.
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
- **Exports**: zip bundle of any recorded run's Result Store.

## Requirements

- The **frozen HFSG Core** checkout at `/home/rashid/projects/hfsg`
  (launcher also accepts a core venv at `/home/rashid/projects/hfsg/.venv`).
- Python 3.12 (3.10+ compatible) with the packages in `requirements-lab.txt`.
- ~2 GB free RAM for the 10k-patient Quick Demo (measured ≈ 36 s on a 2-core
  3.7 GB machine); 25k = Extended / Slower Demo (≈ 80 s).

## Installation

```bash
cd <this repository root>
# create a dedicated environment (optional but recommended)
python3 -m venv .venv
.venv/bin/pip install -r requirements-lab.txt

# into the frozen Core venv instead (also fine):
# /home/rashid/projects/hfsg/.venv/bin/pip install -r requirements-lab.txt
```

## Start

```bash
./START_HFSG                      # one-click launcher (root)
# or
./scripts/start_hfsg.sh
# or directly
python -m streamlit run app.py
```

Then open the printed local URL (default http://localhost:8501).

## Acceptance demo flow (all real, none mocked)

1. **Select Scenario** — Scenario Builder (`S1` … `S8` / `CUSTOM`).
2. **Configure** — master seed (default `20260805`), horizon (default
   `720` h); CUSTOM multipliers for custom scenarios.
3. **Run 10K** — Academic Quick Demo (Quick Demo = 10,000 patients) or Run
   Simulation; the frozen Core generates and validates live.
4. **Validate** — Validation / Reproducibility Center shows the Core report.
5. **Dashboard** — Results Dashboard (census, flows, events, occupancy).
6. **Patient Explorer** — drill into real synthetic patient records.
7. **Re-run with Same Seed** — reproducible `MATCH` across configuration
   hash, child seed, patient/event counts, validation result, fingerprints.
8. **Compare** — Scenario Comparison across recorded runs.
9. **Export** — zip the Result Store.

## Tests

```bash
python -m pytest -q                # unit + AppTest navigation + small live flow
python -m pytest tests/test_acceptance_flow.py   # live acceptance flow (~14 s)
```

Core regression (frozen repository, run from its own root):

```bash
cd /home/rashid/projects/hfsg && python -m pytest -q
```

## Layout

- `app.py` — Streamlit entry point.
- `research_lab/` — Lab package (identity, adapter, fingerprint, result
  store, reproducibility, `ui/` with components/state and the 9 pages).
- `bench/`, `proof/` — Gate 2A benchmark + integration/reproducibility proofs.
- `tests/` — Lab test suite.
- `screenshots/` — UI screenshots (Gate 2B deliverable).

## Provenance

The Lab only **reads** the frozen Core (identity verified at runtime: version
`0.6.0`, validated baseline `08032c3`, frozen integration commit `affe7c8`).
Runs are recorded under `results/`; only small reproducibility evidence is
committed. The frozen Core repository, its config and its test suite are
never modified.
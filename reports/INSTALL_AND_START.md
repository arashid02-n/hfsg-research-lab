# HFSG Research Lab — Installation and Start

The Lab is a thin Streamlit front-end over the **frozen HFSG Core**. It does
**not** install or modify the Core.

## Requirements

- The frozen HFSG Core checkout at `/home/rashid/projects/hfsg` with its
  environment (or any Python 3.10+ environment with the Lab dependencies).
- Disk: ~150 KB per 10k run recorded; RAM: ~150 MB peak per run (Core
  bounded-memory pipeline; ~2 GB free RAM is comfortable).

## 1. Install dependencies

```bash
cd <this repository root>
python3 -m venv .venv
.venv/bin/pip install -r requirements-lab.txt
```

or install into the frozen-Core venv:

```bash
/home/rashid/projects/hfsg/.venv/bin/pip install -r requirements-lab.txt
```

## 2. Start the app

```bash
./START_HFSG
# or
./scripts/start_hfsg.sh
# or directly
python -m streamlit run app.py
```

Open the printed local URL (default `http://localhost:8501`). If port 8501 is
busy the first time, pass one explicitly:

```bash
python -m streamlit run app.py --server.port 8505
```

## 3. Acceptance demo (recommended path)

1. **Scenario Builder** — pick S1 (default) or any Standard-8 / CUSTOM.
2. **Academic Quick Demo** — keep "Quick Demo (recommended)" (10,000
   patients, ≈ 36 s) or choose "Extended / Slower Demo" (25,000, ≈ 80 s).
3. Click **Run Quick Demo (live, validated)** and wait for "Demo complete".
4. **Results Dashboard** → **Patient Explorer**.
5. **Validation / Reproducibility Center** → click **Re-run with Same Seed**
   and wait for **REPRODUCIBILITY MATCH**.
6. **Scenario Comparison** → **Export / Run Summary** → Build export zip.

## 4. Tests

```bash
python -m pytest -q                                  # all Lab tests (~16 s)
python -m pytest tests/test_acceptance_flow.py       # live flow (~14 s)
python -m pytest tests/test_lab_services.py          # fast unit tests
```

## 5. Screenshots

```bash
# start the server (see §2), then in another shell:
python scripts/ui_demo.py --base http://localhost:8501 --out screenshots
```

`scripts/ui_demo.py` drives the full acceptance flow in headless Chromium and
writes `screenshots/01_*.png … 11_*.png`; it exits 0 only when the
REPRODUCIBILITY MATCH is displayed.

## 6. Notes

- Every run is recorded under `results/<label>/` with its `job_spec.json`
  (exact inputs) so any recorded run can be re-executed identically.
- The app reads the frozen Core's released dataset read-only; it never writes
  into `/home/rashid/projects/hfsg/data/output`.
- Live Demo runs are labelled **VALIDATED**, never **RELEASED** — the Released
  label belongs only to the frozen Core's Phase 1 dataset.
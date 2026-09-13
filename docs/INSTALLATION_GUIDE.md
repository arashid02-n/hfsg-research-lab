# HFSG Research Lab — Installation Guide

This guide installs and starts the **HFSG Research Lab** on a clean machine
(Windows is the primary target; macOS/Linux are also supported).

The Lab is a Streamlit application that drives the **frozen HFSG Core**.
The Core is a separate, owner-supplied component — see "Where the Core comes
from" below.

---

## 1. What you need

| Requirement | Detail |
|---|---|
| Operating system | Windows 10/11 (primary), macOS, or Linux |
| Python | 3.10 or newer (Windows: install from python.org, tick **Add Python to PATH**) |
| HFSG Core | An approved frozen Core checkout (see step 2) |
| Disk | ~1 GB free (code + dependencies + recorded runs) |
| RAM | ~2 GB free for the 10k-patient demo |

## 2. Provide the HFSG Core (one-time)

The Lab does **not** bundle the Core. Place your approved Core so the Lab can
find it — any one of these is enough (they are checked in this order):

1. **Easiest:** copy the Core into the `hfsg_core/` folder next to the app.
   The folder must contain `src/hfsg/__init__.py` and `config/base.yaml`.
2. Set the environment variable `HFSG_CORE_DIR` to the Core path.
3. On first start, the About / System Information page lets you pick the Core
   path; it is remembered in `hfsg_core.config`.

> The Core is never copied into the public package (see
> `IP_AND_DISTRIBUTION_BOUNDARY.md`).

## 3. Install dependencies (automatic)

No manual step is required. On first launch, `START_HFSG.bat` / `START_HFSG`
runs `scripts/bootstrap.py`, which:

1. creates a project-local `.venv` (if missing),
2. installs `requirements/requirements.txt` into `.venv` (first run only),
3. starts the Lab with the `.venv` interpreter.

This means the Lab **never** depends on globally installed Python packages.

Manual fallback (optional, for advanced users):

```bash
# Windows
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements\requirements.txt

# macOS / Linux
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements/requirements.txt
```

## 4. Start (every day, one click)

- **Windows:** double-click `START_HFSG.bat`.
- **macOS / Linux:** double-click `START_HFSG` (or run `./START_HFSG`).

The launcher runs pre-flight checks automatically:

| Check | Failure message (example) |
|---|---|
| Python present | "Python was not found." |
| Dependencies | "Missing required dependencies: streamlit, …" |
| Core availability | "HFSG Core not found." |
| Core identity | "LIVE RUN BLOCKED — incompatible HFSG Core detected." |
| Writable output dir | "Output directory is not writable." |
| Free disk | "Insufficient free disk." |
| Free port | (auto-selects the first free port from 8501) |

If every check passes, the Lab starts and your browser opens automatically at
`http://localhost:8501` (or the first free port shown in the console).

## 5. Verify the Core identity

Open **About / System Information**. It shows the verified identity:

```
HFSG Core v0.6.0 — Phase-1 validated baseline 08032c3;
current frozen integration commit affe7c8
```

If the resolved Core does not match, live runs are blocked and the page
explains why.

## 6. Run the 10-minute demo

See `DEMO_GUIDE.md`. In short: Home → Academic Quick Demo → Run Quick Demo
(10,000 patients) → Validation → Re-run with Same Seed (expect **MATCH**) →
Export.

---

**Troubleshooting:** every startup error is written in plain language (not a
Python traceback) with the fix. If the app does not start, read the last
message in the console window and follow the instruction shown.

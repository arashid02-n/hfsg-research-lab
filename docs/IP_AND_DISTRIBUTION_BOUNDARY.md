# IP & Distribution Boundary

**Date:** 2026-09-12
**Status:** Gate 2C — release/portability/packaging boundary
**Prepared for:** Project Owner final acceptance review

This document records the verified IP / distribution boundary for the
HFSG Research Lab academic release. It is derived from inspection of the
actual repositories (not from prior assumptions).

---

## 1. Actual repository state (verified)

| Repository | Visibility | Branch | HEAD (at audit) | Contents |
|---|---|---|---|---|
| `arashid02-n/hfsg` (HFSG Core) | **PUBLIC** | `main` | `affe7c8` | Core source (`src/hfsg/`), `scripts/`, `tests/`, `config/base.yaml`, docs/manifests. **No dataset** (`data/output/` is git-ignored). |
| `arashid02-n/hfsg-research-lab` (Research Lab) | **PUBLIC** | `main` | `c379415` (pre-Gate 2C) | Lab code, docs, screenshots, reproducibility evidence. **No Core, no dataset.** |
| `arashid02-n/hfsg-handover` (Handover) | **PRIVATE** | `main` | `5dc03ff` | Gate 1–2B reports + a copy of the Lab (Gate 2B snapshot). |

## 2. What is currently public

**A. HFSG Core source is ALREADY publicly present** on GitHub
(`arashid02-n/hfsg`, PUBLIC). This is a factual observation, **not** a
distribution grant.

**B. Research Lab assets** are public (`arashid02-n/hfsg-research-lab`):
`research_lab/`, `app.py`, `scripts/`, `tests/`, `bench/`, `proof/`,
`screenshots/`, `docs/`, `requirements/`.

**C. HFSG Core source:** publicly present — see §2.A.

**D. The complete Master Dataset is NOT publicly present.** The released
dataset (`data/output/step9`, ~109k patients / ~316k events) is git-ignored
in the Core repository and is present in no public repository.

## 3. Ownership and licensing (verified)

- HFSG-owned source code, config, documentation and generated data are the
  Project Owner's property. The Core declares the license identifier
  **`HFSG-EULA-1.0`** (stated in `src/hfsg/pipeline.py` and the dataset
  manifest), but **no full EULA/license text is distributed** in any
  repository yet (see `THIRD_PARTY_AND_IP_PROVENANCE.md` §8).
- Third-party dependencies (numpy, pandas, pyarrow, PyYAML; streamlit,
  pytest, playwright) are permissively licensed open source; they are
  **imported, not vendored**.
- The cited scientific article is referenced for provenance only and is
  **not bundled or redistributed**.

## 4. What the Academic Package MAY include

- Research Lab code, launchers, `requirements/`, documentation, screenshots,
  and reproducibility **evidence** (small JSON summaries).
- A small `demo_release/` **reference summary** (scenario-pack labels, counts,
  configuration-hash references) marked as reference metadata — **not** the
  dataset itself.

## 5. What the Academic Package MUST NOT include

- **HFSG Core source** (proprietary `HFSG-EULA-1.0`; public visibility is
  NOT permission to redistribute — bundling requires Project Owner
  authorization).
- **The Master Dataset** (any part of `data/output/`).
- Any new license/EULA text (not authored or authorized here).

## 6. What requires Project Owner authorization

1. Bundling / redistributing the HFSG Core source inside a package or ZIP.
2. Bundling any part of the Master Dataset.
3. Publishing a license / EULA for the Lab or Core.

## 7. Approved mechanism (implemented)

Because the Core is not bundled, the Lab resolves an **external** Core at
runtime (priority order, see `INSTALLATION_GUIDE.md`):

1. `hfsg_core/` (or `core/`) adjacent to the Lab (the Project Owner drops
   their own approved Core here);
2. environment variable `HFSG_CORE_DIR`;
3. `hfsg_core.config` file;
4. Core directory selected on the About / System Information page.

The Academic package ships with an **empty** `hfsg_core/` placeholder and
clear instructions, so it is usable on a machine where the Project Owner has
supplied their approved Core.

---

**Conclusion:** The Academic package is Lab-only. It neither copies the Core
nor the Master Dataset. Public GitHub visibility is treated strictly as
visibility, never as a redistribution authorization.

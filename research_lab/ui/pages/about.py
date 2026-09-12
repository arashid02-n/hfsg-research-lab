"""About / System Information page.

Displays the verified HFSG Core identity, the resolved Core location, and the
runtime environment. This is the single place where the Core location can be
selected and persisted (portable external-Core mechanism).

If no Core is resolved the page explains exactly how to provide one. If an
incompatible Core is detected the page shows LIVE RUN BLOCKED and why.
"""

from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

import streamlit as st

from ...core import is_core_dir, resolve_core_dir, save_core_dir, LAB_ROOT
from ...identity import LINEAGE_STATEMENT, verified_identity
from ..components import disclaimer, page_header


def _resolve() -> Path | None:
    return resolve_core_dir()


def render() -> None:
    page_header(
        "About / System Information",
        "Verified HFSG Core identity, Core location and runtime environment.",
    )
    identity = verified_identity()

    st.subheader("HFSG Core identity")
    st.info(f"**Lineage:** {identity['statement']}")

    if identity["core_found"]:
        if identity["core_integrity_ok"]:
            st.success("Core identity verified — live runs are authorised.")
        else:
            st.error(
                "**LIVE RUN BLOCKED** — the resolved Core does not match the "
                "approved reference. Live runs are disabled until a compatible "
                "Core is provided."
            )
            with st.expander("Identity verification details"):
                st.json(identity)
    else:
        st.error(
            "**HFSG Core not found.** Live runs are disabled. Provide the "
            "approved Core using one of the methods below."
        )

    st.markdown("---")
    st.subheader("Core location (portable resolution)")
    st.markdown(
        "The Lab never hard-codes a Core path. The Core is resolved in this "
        "order:\n"
        "1. `hfsg_core/` (or `core/`) inside this Lab directory — drop the "
        "approved Core here;\n"
        "2. environment variable `HFSG_CORE_DIR`;\n"
        "3. this Lab's `hfsg_core.config` file (set by the selection below);\n"
        "4. the Core directory you select on this page."
    )
    current = _resolve()
    if current is not None:
        st.markdown(f"**Resolved Core:** `{current}`")
    else:
        st.markdown("**Resolved Core:** *none*")

    with st.form("core_location_form"):
        candidate = st.text_input(
            "Core directory (must contain `src/hfsg/__init__.py` and "
            "`config/base.yaml`)",
            value=str(current) if current else "",
            placeholder="e.g. C:\\HFSG\\hfsg  or  /opt/hfsg",
        )
        submitted = st.form_submit_button("Set Core location")
    if submitted:
        candidate = candidate.strip()
        if not candidate:
            st.warning("Enter a Core directory first.")
        elif not is_core_dir(candidate):
            st.error(
                f"Not a valid HFSG Core directory: `{candidate}` "
                "(expected `src/hfsg/__init__.py` and `config/base.yaml`)."
            )
        else:
            saved = save_core_dir(candidate)
            st.success(f"Core location saved: `{saved}` — restart to reload.")
            st.caption(
                "Note: the saved path is written to `hfsg_core.config` in the "
                "Lab directory. Re-running the app will pick it up."
            )

    st.markdown("---")
    st.subheader("System information")
    total, _used, free = shutil.disk_usage(LAB_ROOT)
    rows = [
        ("Python", f"{sys.version.split()[0]} ({platform.python_implementation()})"),
        ("Streamlit", st.__version__),
        ("Platform", f"{platform.system()} {platform.release()} ({platform.machine()})"),
        ("Lab directory", str(LAB_ROOT)),
        ("Results directory", str(LAB_ROOT / "results")),
        ("Free disk", f"{free / (1024 ** 3):.2f} GiB"),
    ]
    for label, value in rows:
        st.markdown(f"**{label}:** {value}")

    st.markdown("---")
    st.caption(
        f"Identity reference: {LINEAGE_STATEMENT}. Live-run status is derived "
        "from the actual resolved Core, never from these labels alone."
    )
    disclaimer()

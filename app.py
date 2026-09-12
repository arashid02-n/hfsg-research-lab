"""HFSG Research Lab — Streamlit app entry point.

Layers a Streamlit UI on the frozen HFSG Core through the thin Lab Adapter
(no model logic). Sidebar-radio routing keeps the app easy to test with
``streamlit.testing.v1.AppTest``.
"""

from __future__ import annotations

import streamlit as st

from research_lab.ui import APP_PAGES
from research_lab.ui.pages import RENDERERS
from research_lab.ui.state import ensure_state
from research_lab.identity import verified_identity

st.set_page_config(page_title="HFSG Research Lab", page_icon="🏥", layout="wide")

ensure_state()


def sidebar() -> None:
    with st.sidebar:
        st.title("HFSG Research Lab")
        st.caption("Non-clinical synthetic flow researcher / educator tool.")
        st.radio("Page", APP_PAGES, key="page_radio", label_visibility="collapsed")
        st.session_state["page"] = st.session_state["page_radio"]
        st.markdown("---")
        identity = verified_identity()
        label = identity["statement"]
        st.markdown(f"**Core:** {label}")
        if identity["core_integrity_ok"]:
            st.caption("Core verified.")
        elif identity["core_found"]:
            st.error("LIVE RUN BLOCKED — incompatible Core.")
        else:
            st.error("Core not found — LIVE RUN BLOCKED.")
        busy = st.session_state.get("busy", False)
        if busy:
            st.warning("Work in progress — do not close this tab.")
        else:
            st.caption("Idle.")
        st.markdown("---")
        st.caption(
            "SYNTHETIC DATA — NOT REAL PATIENT DATA — NOT CLINICALLY "
            "VALIDATED. Research / education use."
        )


def main() -> None:
    sidebar()
    renderer = RENDERERS[st.session_state["page"]]
    renderer()


if __name__ == "__main__":
    main()
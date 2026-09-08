"""HFSG Research Lab UI package (Streamlit)."""

__all__ = ["services", "components", "state", "pages", "APP_PAGES"]

from . import services, state, components, pages  # noqa: F401

APP_PAGES = [
    "Home",
    "Scenario Builder",
    "Run Simulation",
    "Results Dashboard",
    "Scenario Comparison",
    "Synthetic Patient Explorer",
    "Validation / Reproducibility Center",
    "Export / Run Summary",
    "Academic Quick Demo",
]
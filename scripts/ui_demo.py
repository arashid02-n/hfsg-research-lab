#!/usr/bin/env python3
"""Gate 2B — live acceptance-demo driver + UI screenshot capture.

Starts against an already-running Research Lab Streamlit server (default
http://localhost:8501) and drives the REAL acceptance flow in a real browser
(headless Chromium via Playwright):

    Home -> Scenario Builder -> (Academic Quick Demo) Run 10k live
      -> Results Dashboard -> Patient Explorer
      -> Validation / Reproducibility Center -> "Re-run with Same Seed"
      -> REPRODUCIBILITY MATCH -> Scenario Comparison -> Export -> Home

Each page is captured to screenshots/<NN_<page>.png.

Usage:
    python scripts/ui_demo.py [--base http://localhost:8501] [--out screenshots]

Exit code 0 only if the demo completes and the reproducibility match is shown.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

LAB = Path(__file__).resolve().parents[1]


class DemoTimedOut(RuntimeError):
    pass


class DemoDriver:
    def __init__(self, page: Page, out_dir: Path) -> None:
        self.page = page
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def goto_page(self, name: str) -> None:
        # Click the sidebar radio label (scoping to the sidebar avoids the
        # Streamlit radio input being intercepted by its overlay label).
        self.page.locator('section[data-testid="stSidebar"]').get_by_text(
            name, exact=True
        ).first.click()
        self.page.wait_for_timeout(1800)

    def screenshot(self, name: str) -> Path:
        path = self.out_dir / name
        self.page.screenshot(path=str(path))
        print(f"  screenshot -> {path}")
        return path

    def wait_text(self, text: str, timeout: float = 120.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                locator = self.page.get_by_text(text, exact=False).first
                if locator.count() and locator.is_visible():
                    return
            except Exception:
                pass
            self.page.wait_for_timeout(1000)
        raise DemoTimedOut(f"timed out waiting for text {text!r}")

    def click_radio(self, name: str) -> None:
        self.page.get_by_text(name, exact=True).first.click()
        self.page.wait_for_timeout(1000)

    def click_button(self, name: str) -> None:
        self.page.get_by_role("button", name=name).first.click()


def run(base_url: str, out_dir: Path) -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        driver = DemoDriver(page, out_dir)

        page.goto(base_url, wait_until="load", timeout=60_000)
        driver.wait_text("HFSG Research Lab")
        driver.screenshot("01_home.png")

        driver.goto_page("Scenario Builder")
        driver.screenshot("02_scenario_builder.png")

        driver.goto_page("Academic Quick Demo")
        driver.click_radio("Quick Demo (recommended)")
        driver.screenshot("03_quick_demo_configured.png")

        print("starting live 10k Quick Demo (Core generation + validation)...")
        driver.click_button("Run Quick Demo (live, validated)")
        driver.wait_text("Demo complete", timeout=360.0)
        driver.screenshot("04_quick_demo_result.png")

        driver.goto_page("Results Dashboard")
        driver.wait_text("Census by unit over time")
        driver.screenshot("05_results_dashboard.png")

        driver.goto_page("Synthetic Patient Explorer")
        driver.screenshot("06_patient_explorer.png")

        driver.goto_page("Validation / Reproducibility Center")
        driver.wait_text("Frozen-Core validation report")
        driver.screenshot("07_validation_center.png")

        print("starting 'Re-run with Same Seed' (identical Core execution)...")
        driver.click_button("Re-run with Same Seed")
        driver.wait_text("REPRODUCIBILITY MATCH", timeout=420.0)
        driver.screenshot("08_reproducibility_match.png")

        driver.goto_page("Scenario Comparison")
        driver.screenshot("09_scenario_comparison.png")

        driver.goto_page("Export / Run Summary")
        driver.wait_text("Build export zip")
        driver.click_button("Build export zip")
        driver.wait_text("Export ready", timeout=60.0)
        driver.screenshot("10_export.png")

        driver.goto_page("Home")
        driver.screenshot("11_home_final.png")

        browser.close()
    print("ACCEPTANCE DEMO + SCREENSHOTS COMPLETE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8501")
    parser.add_argument("--out", default=str(LAB / "screenshots"))
    args = parser.parse_args()
    try:
        return run(args.base, Path(args.out))
    except (DemoTimedOut, Exception) as exc:  # noqa: BLE001 - driver reports
        print(f"DEMO FAILED: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
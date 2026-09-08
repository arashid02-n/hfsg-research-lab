"""UI pages (sidebar-radio routing targets)."""

from . import (
    home,
    scenario_builder,
    run_simulation,
    results_dashboard,
    scenario_comparison,
    patient_explorer,
    validation_center,
    export,
    quick_demo,
)

RENDERERS = {
    "Home": home.render,
    "Scenario Builder": scenario_builder.render,
    "Run Simulation": run_simulation.render,
    "Results Dashboard": results_dashboard.render,
    "Scenario Comparison": scenario_comparison.render,
    "Synthetic Patient Explorer": patient_explorer.render,
    "Validation / Reproducibility Center": validation_center.render,
    "Export / Run Summary": export.render,
    "Academic Quick Demo": quick_demo.render,
}
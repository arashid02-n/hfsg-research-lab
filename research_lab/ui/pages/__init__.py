"""UI pages (sidebar-radio routing targets).

Pages that require a resolved, identity-verified HFSG Core are wrapped with
``require_core`` so a missing/incompatible Core surfaces a friendly
"LIVE RUN BLOCKED" message instead of a traceback.
"""

from ..services import require_core
from . import (
    about,
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
    "Scenario Builder": require_core(scenario_builder.render),
    "Run Simulation": require_core(run_simulation.render),
    "Results Dashboard": require_core(results_dashboard.render),
    "Scenario Comparison": scenario_comparison.render,
    "Synthetic Patient Explorer": patient_explorer.render,
    "Validation / Reproducibility Center": require_core(validation_center.render),
    "Export / Run Summary": export.render,
    "Academic Quick Demo": require_core(quick_demo.render),
    "About / System Information": about.render,
}

========================================================================
 HFSG RESEARCH LAB  v1.0  —  READ ME FIRST
========================================================================

1. WHAT THIS IS
   HFSG Research Lab is a small desktop web app that runs a hospital-flow
   simulation and generates SYNTHETIC patient data for teaching and research.

   IMPORTANT:
     - The data are SYNTHETIC (simulated). They are NOT real patient data.
     - They are NOT clinically validated.
     - They are for RESEARCH / EDUCATION use only.

2. HOW TO INSTALL (automatic)
   - Install Python 3.10+ (Windows: tick "Add Python to PATH").
   - Copy your approved HFSG Core into the "hfsg_core" folder next to this
     app (the folder that contains "src/hfsg/__init__.py" and
     "config/base.yaml"). Alternatively set the HFSG_CORE_DIR environment
     variable, or pick the Core path on the About / System Information page.
   - On first launch the launcher automatically creates a project-local
     ".venv" and installs the dependencies into it. No manual pip step and
     no globally installed packages are required.

   Full details:  INSTALLATION_GUIDE.md

3. HOW TO LAUNCH (one click, every day)
   - Windows:   double-click  START_HFSG.bat
   - macOS/Linux:  run  ./START_HFSG
   The app starts and your browser opens automatically.

4. HOW TO RUN THE 10K ACADEMIC DEMO
   - Home -> Academic Quick Demo -> Run Quick Demo (live, validated).
   - Then: Results Dashboard -> Synthetic Patient Explorer ->
     Validation / Reproducibility Center -> Re-run with Same Seed (expect
     "REPRODUCIBILITY MATCH") -> Scenario Comparison -> Export.

5. WHERE THE DEMO GUIDE IS
   See  DEMO_GUIDE.md  for the 10-minute university demonstration script.

6. EXTERNAL CORE SETUP (if applicable)
   The Lab does NOT bundle the HFSG Core. If you have not placed a Core yet,
   the launcher prints "HFSG Core not found." — follow step 2 above.
   See  IP_AND_DISTRIBUTION_BOUNDARY.md  for why the Core is kept separate.

7. SUPPORT DOCUMENTS (in the docs/ folder)
   - INSTALLATION_GUIDE.md         how to install and start
   - DEMO_GUIDE.md                 10-minute demonstration
   - KNOWN_LIMITATIONS.md          what the Lab does and does not do
   - IP_AND_DISTRIBUTION_BOUNDARY.md  what may be distributed
   - PUBLIC_REPOSITORY_AUDIT.md    repository cleanliness audit
   - WINDOWS_INDEPENDENT_ACCEPTANCE_REPORT.md
   - PORTABILITY_ACCEPTANCE_REPORT.md
   - OFFLINE_TEST_REPORT.md
   - CORE_IDENTITY_REPORT.md
   - FINAL_LAB_TEST_REPORT.md
   - FINAL_CORE_REGRESSION_REPORT.md

========================================================================
 SYNTHETIC DATA — NOT REAL PATIENT DATA — NOT CLINICALLY VALIDATED
 RESEARCH / EDUCATION USE ONLY
========================================================================

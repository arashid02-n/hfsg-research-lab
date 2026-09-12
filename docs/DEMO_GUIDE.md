# HFSG — 10-Minute University Demonstration

A short, non-technical walkthrough of the HFSG Research Lab for a classroom or
visitor. Everything below uses the default settings so the whole flow takes
about 10 minutes.

> **The data are SYNTHETIC — simulated, scenario-driven numbers. They are NOT
> real patients and NOT clinically validated.** They exist to demonstrate
> hospital-flow modelling in teaching and research.

---

## 1. What HFSG is — (1 min)

HFSG simulates how patients flow through a hospital over a 30-day window:
arrivals, emergency care, general wards, and intensive care. A tiny "Core"
engine applies the model equations; the Research Lab is the friendly window
onto it. You press buttons; the Core generates thousands of synthetic patient
records, validates them, and reports results.

## 2. Select the scenario — (30 s)

Open **Scenario Builder** (left sidebar). The default is **S1 — Normal
Operation**. Leave it. (For another visit: S2–S8 model busier weeks, crises,
ICU losses, etc.; CUSTOM lets you change approved multipliers.)

## 3. Run the 10K demo — (~1 min)

Open **Academic Quick Demo** (left sidebar). Keep **Quick Demo (recommended)**
= 10,000 patients, master seed `20260805`, horizon `720` hours.

Click **Run Quick Demo (live, validated)**. In about a minute the frozen Core
generates and validates the synthetic cohort. You will see:

- ~10,600 patients, ~31,600 events, status **VALIDATED**.

(There is also an **Extended / Slower Demo** at 25,000 patients for a longer
look — not needed for the 10-minute tour.)

## 4. Dashboard — (2 min)

Open **Results Dashboard**. Show the census curves, the flows between units,
and the events over time. Point out that the numbers come from the model's
mass balance, not from a real hospital feed.

## 5. Patient Explorer — (1 min)

Open **Synthetic Patient Explorer**. Pick any recorded run and scroll a few
individual synthetic patients and their event timelines (arrival, transfer,
discharge). Emphasise: each row is a generated patient, no real person.

## 6. Validation — (1 min)

Open **Validation / Reproducibility Center**. Show the Core's own validation
report: mass balance, integer allocation, no negative stocks, chronological
events — all PASS.

## 7. Re-run with Same Seed — (1 min)

On the same page, click **Re-run with Same Seed**. HFSG runs the *exact same*
job a second time and compares every field. Result: **REPRODUCIBILITY MATCH**
— same configuration hash, same patient and event counts, identical output
files. This is the reproducibility story: same seed → same hospital.

## 8. Scenario Comparison — (1 min)

Open **Scenario Comparison** to compare recorded runs side by side, then
**Export / Run Summary** to download a zip bundle of a run's outputs.

## 9. Research collaboration — (1–2 min)

Close with the offer: *"If this is useful to your course or lab, we can work
with you to run the scenarios you care about and to extend the demonstration
to your teaching needs."*

---

**Total: ~10 minutes.** First-time machine setup is covered in
`INSTALLATION_GUIDE.md`; the one-click launcher is `START_HFSG.bat`.

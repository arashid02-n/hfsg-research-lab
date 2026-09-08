#!/usr/bin/env python3
"""Benchmark harness (Gate 2A) - one benchmark point via the Research Lab
Adapter on the frozen HFSG Core. Emits a single JSON metrics record.

Usage:
  python bench_one.py SCENARIO TARGET OUT_DIR [--planned N] [--seed N]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_lab.adapter import ResearchLabAdapter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario")
    parser.add_argument("target", type=int)
    parser.add_argument("out", help="Result Store directory for this point")
    parser.add_argument("--planned", type=int, default=60)
    parser.add_argument("--seed", type=int, default=20260805)
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    adapter = ResearchLabAdapter()
    outcome = adapter.run_job(
        args.scenario,
        args.out,
        target_patients=args.target,
        planned_runs_per_scenario=args.planned,
        master_seed=args.seed,
        run_label=args.label,
    )
    record = outcome.to_dict()
    record.update(
        {
            "core_repo": "/home/rashid/projects/hfsg",
            "core_commit": "affe7c8",
            "config": "/home/rashid/projects/hfsg/config/base.yaml",
        }
    )
    print(json.dumps(record, indent=2))
    return 0 if outcome.validation_status == "VALIDATED" else 1


if __name__ == "__main__":
    sys.exit(main())
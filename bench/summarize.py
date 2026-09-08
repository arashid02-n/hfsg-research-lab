import json

files = [
    "results_S1-1K.json",
    "results_S1-2K.json",
    "results_S1-5K.json",
    "results_S1-10K.json",
    "results_S1-25K.json",
    "results_S3-10K.json",
]
hdr = (
    f"{'pt':>9} {'s':>3} {'runs':>4} {'pat':>7} {'evt':>8} {'gen':>6} "
    f"{'val':>6} {'tot':>6} {'RSS':>7} {'out':>7} {'status':>9} {'mbe':>5} "
    f"{'recon':>5} {'quota':>5}"
)
print(hdr)
for f in files:
    r = json.load(open(f))
    n = len(r["runs"])
    print(
        f"{r['target_patients']:>9} {r['scenario_id']:>3} {n:>4} "
        f"{r['patients']:>7} {r['events']:>8} "
        f"{r['generation_elapsed_seconds']:>6.2f} "
        f"{r['validation_elapsed_seconds']:>6.2f} "
        f"{r['total_elapsed_seconds']:>6.2f} "
        f"{r['peak_rss_bytes']/1e6:>7.1f} "
        f"{r['output_size_bytes']/1e3:>7.1f} "
        f"{r['validation_status']:>9} {r['max_abs_mbe']:>5} "
        f"{r['reconciliation_issues']:>5} {r['event_quota_mismatches']:>5}"
    )